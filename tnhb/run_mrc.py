#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Finetuning on classification tasks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import multiprocessing

# NOTE(paddle-dev): All of these flags should be
# set before `import paddle`. Otherwise, it would
# not take any effect.
os.environ['FLAGS_eager_delete_tensor_gb'] = '0'  # enable gc

import paddle.fluid as fluid
import tokenization
import reader.task_reader as task_reader
from model.ernie import ErnieConfig
from finetune.mrc import create_model, evaluate
from optimization import optimization
from utils.args import print_arguments
from utils.init import init_pretraining_params, init_checkpoint
from finetune_args import parser
from collections import namedtuple

args = parser.parse_args()
print('args::',args)


def main(args):

    global test_pyreader, reader, exe, test_prog, test_graph_vars,ernie_config,startup_prog
    ernie_config = ErnieConfig(args.ernie_config_path)
    ernie_config.print_config()

    if args.use_cuda:
        place = fluid.CUDAPlace(int(os.getenv('FLAGS_selected_gpus', '0')))
        dev_count = fluid.core.get_cuda_device_count()
    else:
        place = fluid.CPUPlace()
        dev_count = int(os.environ.get('CPU_NUM', multiprocessing.cpu_count()))
    exe = fluid.Executor(place)

    startup_prog = fluid.Program()
    if args.random_seed is not None:
        startup_prog.random_seed = args.random_seed

    if args.predict_batch_size == None:
        args.predict_batch_size = args.batch_size

    if args.do_val or args.do_test:
        test_prog = fluid.Program()
        with fluid.program_guard(test_prog, startup_prog):
            with fluid.unique_name.guard():
                test_pyreader, test_graph_vars = create_model(
                    args,
                    pyreader_name='test_reader',
                    ernie_config=ernie_config,
                    is_training=False)

        test_prog = test_prog.clone(for_test=True)

    nccl2_num_trainers = 1
    nccl2_trainer_id = 0
    exe.run(startup_prog)

def abc(test_examples = [],init_check=''):

    s_t = str (time.localtime())  #取名用
    if init_check != '':
        args.init_checkpoint = init_check
        args.ernie_config_path = 'config/ernie_config1.json'

    if test_examples == []: #想直接输入examples曾出现异常无法使用，废弃保留代码
        while True:
            break
            Example = namedtuple('Example', ['qas_id', 'question_text', 'doc_tokens','orig_answer_text', 'start_position', 'end_position'])
            example = Example(
                qas_id = s_t + str(ii) ,
                question_text=que,
                doc_tokens= tokenization.tokenize_chinese_chars(para),
                orig_answer_text=None,
                start_position=None,
                end_position=None)
            test_examples.append(example)

            break

    reader = task_reader.MRCReader(
        vocab_path=args.vocab_path,
        label_map_config=args.label_map_config,
        max_seq_len=args.max_seq_len,
        do_lower_case=args.do_lower_case,
        in_tokens=args.in_tokens,
        random_seed=args.random_seed,
        tokenizer=args.tokenizer,
        is_classify=args.is_classify,
        is_regression=args.is_regression,
        for_cn=args.for_cn,
        task_id=args.task_id,
        doc_stride=args.doc_stride,
        max_query_length=args.max_query_length)

    if args.do_train:
        if args.init_checkpoint and args.init_pretraining_params:
            print(
                "WARNING: args 'init_checkpoint' and 'init_pretraining_params' "
                "both are set! Only arg 'init_checkpoint' is made valid.")
        if args.init_checkpoint:
            init_checkpoint(
                exe,
                args.init_checkpoint,
                main_program=startup_prog,
                use_fp16=args.use_fp16)
        elif args.init_pretraining_params:
            init_pretraining_params(
                exe,
                args.init_pretraining_params,
                main_program=startup_prog,
                use_fp16=args.use_fp16)
    elif args.do_val or args.do_test:
        if not args.init_checkpoint:
            raise ValueError("args 'init_checkpoint' should be set if"
                             "only doing validation or testing!")
        init_checkpoint(
            exe,
            args.init_checkpoint,
            main_program=startup_prog,
            use_fp16=args.use_fp16)

    test_pyreader.decorate_tensor_provider(
        reader.data_generator(
            args.test_set,
            batch_size=args.batch_size,
            epoch=1,
            dev_count=1,
            shuffle=False,
            phase="test"))
    print(reader.get_examples("test"))
    mrc_result = evaluate(
        exe,
        test_prog,
        test_pyreader,
        test_graph_vars,
        "test",
        examples=reader.get_examples("test"),
        features=reader.get_features("test"),
        # examples = test_examples,
        # features=reader._convert_example_to_feature(examples=test_examples,max_seq_length=512,tokenizer=tokenization.FullTokenizer(
        # vocab_file='config/vocab.txt', do_lower_case=True),is_training =False),
        args=args)
    print('abc:mrc:return',len(mrc_result[1]))
    return mrc_result
# if __name__ == '__main__':
    #scope = fluid.core.Scope()
    #with fluid.scope_guard(scope):
        #main(args)
        #print(abc())
