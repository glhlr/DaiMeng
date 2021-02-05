# -*- coding:UTF-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse,unquote
import json
import urllib
import jieba.posseg as pseg
import re
import transformers
import torch
import os

import argparse

from datetime import datetime

import logging
from transformers.modeling_gpt2 import GPT2Config, GPT2LMHeadModel
from transformers import BertTokenizer

import torch.nn.functional as F

PAD = '[PAD]'
pad_id = 0


def set_interact_args():
    """
    Sets up the training arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='0', type=str, required=False, help='生成设备')
    parser.add_argument('--temperature', default=1, type=float, required=False, help='生成的temperature')
    parser.add_argument('--topk', default=8, type=int, required=False, help='最高k选1')
    parser.add_argument('--topp', default=0, type=float, required=False, help='最高积累概率')
    parser.add_argument('--model_config', default='config/model_config_dialogue_small.json', type=str, required=False,
                        help='模型参数')
    parser.add_argument('--log_path', default='data/interacting.log', type=str, required=False, help='interact日志存放位置')
    parser.add_argument('--voca_path', default='vocabulary/vocab_small.txt', type=str, required=False, help='选择词库')
    parser.add_argument('--dialogue_model_path', default='dialogue_model', type=str, required=False, help='对话模型路径')
    parser.add_argument('--save_samples_path', default="sample/", type=str, required=False, help="保存聊天记录的文件路径")
    parser.add_argument('--repetition_penalty', default=5.0, type=float, required=False,
                        help="重复惩罚参数，若生成的对话重复性较高，可适当提高该参数")
    parser.add_argument('--seed', type=int, default=None, help='设置种子用于生成随机数，以使得训练的结果是确定的')
    parser.add_argument('--max_len', type=int, default=25, help='每个utterance的最大长度,超过指定长度则进行截断')
    parser.add_argument('--max_history_len', type=int, default=5, help="dialogue history的最大长度")
    parser.add_argument('--no_cuda', action='store_true', help='不使用GPU进行预测')
    return parser.parse_args()


def create_logger(args):
    """
    将日志输出到日志文件和控制台
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')

    # 创建一个handler，用于写入日志文件
    file_handler = logging.FileHandler(
        filename=args.log_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    # 创建一个handler，用于将日志输出到控制台
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k > 0: keep only top k tokens with highest probability (top-k filtering).
            top_p > 0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        From: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
    """
    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        # torch.topk()返回最后一维最大的top_k个元素，返回值为二维(values,indices)
        # ...表示其他维度由计算机自行推断
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value  # 对于topk之外的其他元素的logits值设为负无穷

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)  # 对logits进行递减排序
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits



def gpt_talk(text):
    try:
        if args.save_samples_path:
            samples_file.write("user:{}\n".format(text))
        history.append(tokenizer.encode(text))
        input_ids = [tokenizer.cls_token_id]  # 每个input以[CLS]为开头

        for history_id, history_utr in enumerate(history[-args.max_history_len:]):
            input_ids.extend(history_utr)
            input_ids.append(tokenizer.sep_token_id)
        curr_input_tensor = torch.tensor(input_ids).long().to(device)
        generated = []
        # 最多生成max_len个token
        for _ in range(args.max_len):
            outputs = model(input_ids=curr_input_tensor)
            next_token_logits = outputs[0][-1, :]
            # 对于已生成的结果generated中的每个token添加一个重复惩罚项，降低其生成概率
            for id in set(generated):
                next_token_logits[id] /= args.repetition_penalty
            next_token_logits = next_token_logits / args.temperature
            # 对于[UNK]的概率设为无穷小，也就是说模型的预测结果不可能是[UNK]这个token
            next_token_logits[tokenizer.convert_tokens_to_ids('[UNK]')] = -float('Inf')
            filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=args.topk, top_p=args.topp)
            # torch.multinomial表示从候选集合中无放回地进行抽取num_samples个元素，权重越高，抽到的几率越高，返回元素的下标
            next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
            if next_token == tokenizer.sep_token_id:  # 遇到[SEP]则表明response生成结束
                break
            generated.append(next_token.item())
            curr_input_tensor = torch.cat((curr_input_tensor, next_token), dim=0)
            # his_text = tokenizer.convert_ids_to_tokens(curr_input_tensor.tolist())
            # print("his_text:{}".format(his_text))
        history.append(generated)
        text = tokenizer.convert_ids_to_tokens(generated)
        print("chatbot:" + "".join(text))

        if args.save_samples_path:
            samples_file.write("chatbot:{}\n".format("".join(text)))
        return ('小萌::' + "".join(text))
    except KeyboardInterrupt:
        if args.save_samples_path:
            samples_file.close()

class HttpServer_RequestHandler(BaseHTTPRequestHandler):
    '''
    GET请求响应函数。
    先解析页面请求参数。获取请路径、query参数串
    把query参数串转换为dict结构
    调用函数，获取页面代码
    输出页面代码
    '''


    def do_GET(self):

        # 解析网页输入参数
        # url解析。结果：ParseResult(scheme='', netloc='', path='/interface', query='key=ssss', fragment='')
        # 结构为元组
        queryPath = urlparse(self.path)
        # 访问路径。。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        path = unquote(queryPath.path, 'utf-8')
        # query请求数据串。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        # 把串转换成字典格式。输入：key=ssss& 输出：{'key': 'ssss'}
        queryString = self.__queryStringParse(unquote(queryPath.query, 'utf-8'))
        # 由于是GET提交。其POST请求的数据为空。仅用于调用参数
        queryForm = {}
        # 获取输出html代码
        responseText = gpt_talk(queryString['question'])
        # 输出页面代码
        responseText = '{"rc": 0,"answer": "' + responseText + '"}'
        self.__responseWrite(responseText)



    '''
    POST请求响应函数。
    先解析页面请求参数。获取请路径、FORM参数（dict结构）
    调用函数，获取页面代码
    输出页面代码
    '''

    def do_POST(self):
        # 解析网页输入参数
        # url解析。结果：ParseResult(scheme='', netloc='', path='/interface', params='', query='', fragment='')
        # 结构为元组
        queryPath = urlparse(self.path)
        # 访问路径。。URL格式的字符串（%E4%B8%AD%E5%8D%8E%E4）转换成UTF-8
        path = unquote(queryPath.path, 'utf-8')
        # 由于是POST提交。其GET请求的数据为空。仅用于调用参数
        queryString = {}
        # 获取POST提交的数据
        # {'key': ['aaaaa'], 'key2': ['aaaaa2222']}
        # 结构为字典
        length = int(self.headers['Content-Length'])
        queryForm = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        # 获取输出html代码
        responseText = gpt_talk(queryString)
        # 输出页面代码
        responseText = '{"rc": 0,"answer": "' + responseText + '"}'
        self.__responseWrite(responseText)

    # 网页输出函数
    # 参数：输出的页面HTML代码，字符串
    def __responseWrite(self, responseText):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(responseText.encode("UTF-8")) #encoding="utf-8"
            print('rrrrrr\n',responseText)
        except IOError:
            self.send_error(404, 'File Not Found: ')

    # queryString解析。
    # 输入参数：queryString串。"key=ssss&key2=ssss222&key3=ssss333"
    # 返回结果：{'key': 'ssss', 'key2': 'ssss222', 'key3': 'ssss333'} 结构为：dict
    def __queryStringParse(self, queryString):
        querstr = queryString.replace("=", "':'")
        querstr = querstr.replace("&", "','")
        if querstr == "":
            querstr = "{}"
        else:
            querstr = "{'" + querstr + "'}"
        dict = eval(querstr)
        return dict


# http服务启动函数
args = set_interact_args()
logger = create_logger(args)
# 当用户使用GPU,并且GPU可用时
args.cuda = torch.cuda.is_available() and not args.no_cuda
device = 'cuda' if args.cuda else 'cpu'
logger.info('using device:{}'.format(device))
os.environ["CUDA_VISIBLE_DEVICES"] = args.device
tokenizer = BertTokenizer(vocab_file=args.voca_path)
model = GPT2LMHeadModel.from_pretrained(args.dialogue_model_path)
model.to(device)
model.eval()
if args.save_samples_path:
    if not os.path.exists(args.save_samples_path):
        os.makedirs(args.save_samples_path)
    samples_file = open(args.save_samples_path + '/samples.txt', 'a', encoding='utf8')
    samples_file.write("聊天记录{}:\n".format(datetime.now()))
    # 存储聊天记录，每个utterance以token的id的形式进行存储
history = []
print('开始和chatbot聊天，输入CTRL + Z以退出')
path1 = os.path.abspath('.')  # 表示当前所处的文件夹的绝对路径
print("httpServer.py绝对路径：" + path1)
port = 8111
address = "192.168.1.17"
server_address = (address, port)
httpd = HTTPServer(server_address, HttpServer_RequestHandler)
print("http服务已启动..." + address + ":" + str(port))
httpd.serve_forever()








