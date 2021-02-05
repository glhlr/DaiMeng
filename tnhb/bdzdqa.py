# !/usr/bin/python3
# coding=utf-8
'''
百度知道问答。
'''

import getPage_bdzd as getPage  # 整个项目中，请用import business.getPage as getPage
from bs4 import BeautifulSoup  # 解析html页面代码


def test():
    word = '法国的国庆日是_月14日。'
    q = Query(word)
    print("搜索词：" + word)
    print("Status:" + q["Status"])
    print("StatusDesc:" + q["StatusDesc"])
    print("Question:" + q["Question"])
    print("Answer:" + q["Answer"])


# 1、根据搜索词，获取百度知道的问题页面代码html及访问状态
# 2、解析问题页面代码。获取问题及对应链接的列表
# 3、分析问题页面，获取问题及链接
# 4、根据回答问题的链接，获取回答内容。
# 输入：待搜索词
# 输出：字典结构。结构：{"Status":"","StatusDesc":"","Question":"","Answer":""}
# 结构说明:获取页面状态字、状态描述、问题、回答内容。状态字：200为成功。问题：页面的第一个问题

def Query(word):
    # 定义返回结果:状态字、状态描述、问题、回答内容。状态字：200为成功。问题：页面的第一个问题
    resule = {"Status": "", "StatusDesc": "", "Question": "", "Answer": ""}
    # 第2条问题返回的结果。
    resule1 = {"Status": "", "StatusDesc": "", "Question": "", "Answer": ""}
    # 第3条问题返回的结果。
    resule2 = {"Status": "", "StatusDesc": "", "Question": "", "Answer": ""}
    # 1、获取百度知道的问题页面代码html及访问状态
    QuestionPage = getQuestionPage(word)
    # 2、解析问题页面代码。获取问题及对应链接的列表
    # 获取页面是否成功状态字
    QuestionStatusCode = QuestionPage['StatusCode']
    # 问题页面代码
    QuestionPageHtmlCode = QuestionPage['HtmlCode'][0]

    # 抓取问题页面成功
    if QuestionStatusCode == "200":
        resule["Status"] = QuestionStatusCode
        # 3、分析问题页面，获取问题及链接
        QuestionList = getQuestionList(QuestionPageHtmlCode)
        # 判断是否获取到了问题及链接
        if len(QuestionList) > 0:
            # question是个列表。question[0]是问题,question[1]是对应的网址
            # 在此仅处理第一条
            question = QuestionList[0]
            # 4、根据回答问题的链接，获取回答内容。
            resule = answerHandle(question)

            # 根据王子佳需求，获取3个问题的答案。问题和内容，以“+==+”号连接。2019年8月26日
            # 返回状态以第一条为准。对第2、3条的处理，不改变总的回复状态。
            # 判断是否有第2条问题
            if len(QuestionList) > 100:#改成100就是一个答案
                # 获取第2个问题的答案。根据回答问题的链接，获取回答内容。
                resule1 = answerHandle(QuestionList[1])
                resule["Question"] = resule["Question"] + "+==+" + resule1["Question"]
                resule["Answer"] = resule["Answer"] + "+==+" + resule1["Answer"]
            # 判断是否有第2条问题
            if len(QuestionList) > 200:#改成100就是一个答案
                # 获取第2个问题的答案。根据回答问题的链接，获取回答内容。
                resule2 = answerHandle(QuestionList[2])
                resule["Question"] = resule["Question"] + "+==+" + resule2["Question"]
                resule["Answer"] = resule["Answer"] + "+==+" + resule2["Answer"]


        else:
            # 没有解析出问题及链接
            resule["Status"] = "8888"
            resule["StatusDesc"] = "出错:没有搜索到相应的问题"
    else:
        resule["Status"] = QuestionStatusCode
        resule["StatusDesc"] = "出错:没有找到问题页面"
    print('**********', resule)
    return resule


# 根据问题链接，获取相关回答页面的代码
# 解析“回答问题”的页面代码。获取回答内容
# 输入：问题及对应链接列表（question）。question[0]：问题。question[1]：问题链接
# 输出：字典结构。结构：{"Status":"","StatusDesc":"","Question":"","Answer":""}
# 结构说明:获取页面状态字、状态描述、问题、回答内容。状态字：200为成功。问题：页面的第一个问题

def answerHandle(question):
    # 定义返回结果:状态字、状态描述、问题、回答内容。状态字：200为成功。问题：页面的第一个问题
    resule = {"Status": "", "StatusDesc": "", "Question": "", "Answer": ""}
    # 问题答案列表
    answer = ""
    # 根据问题链接，获取回答问题的页面代码
    answerPage = getAnswerPageHtmlCode(questionHref=question[1])
    # 解析回答问题的页面代码。获取回答内容
    AnswerStatusCode = answerPage['StatusCode']
    if AnswerStatusCode == "200":
        resule["Status"] = AnswerStatusCode
        resule["StatusDesc"] = ""
        resule["Question"] = question[0]
        resule["Answer"] = getAnswer(answerPage['HtmlCode'])
    else:
        resule["Status"] = AnswerStatusCode
        resule["StatusDesc"] = "出错:没有找到回答问题页面"
    return resule


# 根据输入的网址，获取回答问题的页面
# 返回数据{'响应状态':'', '响应页面代码':''}
# r = {'StatusCode':'', 'HtmlCode':''}
def getAnswerPageHtmlCode(questionHref):
    g = getPage.getPage()
    g.url = questionHref
    g.data = {}
    return g.requestGet()


# 解析回答问题页面。
# 输入：回答问题页面代码
# 输出：回答内容
def getAnswer(AnswerPageHtmlCode):
    '''
    原码。回答问题部份
    <div id="best-content-2968856286" accuse="aContent" class="best-text mb-10">
	    <div class="wgt-best-mask">
		    <div class="wgt-best-showbtn">
			    展开全部<span class="wgt-best-arrowdown"></span>
		    </div>
	    </div>
	    <p>回答内容1</p>
    </div>
    ------------------------------------------
    <div id="answer-content-529337078" accuse="aContent" class="answer-text mb-10 line">
	    <div class="wgt-answers-mask">
		    <div class="wgt-answers-showbtn">
			    展开全部<span class="wgt-answers-arrowdown"></span>
		    </div>
	    </div>
	    回答内容2
    </div>
    ---------------
    '''
    # 保留的最多答案数量。不是所有的答案都保存。仅保存前answersCount个
    answersCount = 3
    # 保留的字数
    charsCount = 500
    # 根据以上结构。查找到accuse="aContent"的div标签。然后获取文本
    # 以accuse="aContent"为关键字进行解析
    # 定义网页解析对象
    soup = BeautifulSoup(AnswerPageHtmlCode, 'html.parser')
    # 目的链接关键字accuse="aContent"
    key1 = "qContent"
    key2 = "aContent"
    # 查找页面中所有<a>的href属性。遍历
    # 所有回答内容.多个答案相加。取前500字。
    answers = ""
    a = 0
    for div in soup.find_all('div'):
        # 如果发现accuse="aContent" ，记录
        # get()在属性不存在的情况下会出错。故用try块
        print(div.get_text())
        try:
            if div.get('accuse') == key1 or div.get('accuse') == key2:
                # answers.append(div.get_text().replace('展开全部','').strip())
                answers = answers + div.get_text().replace('展开全部', '').strip() + "+++"
                answers=answers.replace('\u3000', '').replace('\xa0', '').replace('\n', '').replace('\r', '').replace('\\', '')
                a = a + 1
        except:
            pass  # 此句没有实际用处。不添加异常处理语句，会出现语法错误
        # 如果回答的字数达到了想要的数量，不再解析，退出。
        if len(answers) > charsCount:
            break

        # 达到想要保留的答案数量，退出。
        if a >= answersCount:
            break  #
    return answers[:charsCount]


# 从问题页面中。解析也问题和对应的页面网址
# 输入：问题页面代码
# 返回的结果是问题列表。是嵌套列表。结构是：[['text','href'],['',''],['','']]
def getQuestionList(QuestionPageHtmlCode):
    # 返回数据定义。
    # 返回的结果是问题列表
    # 是嵌套列表。结构是：[['text','href'],['',''],['','']]
    # 所有问题列表，返回变量。结构是[['text','href'],['',''],['','']]
    questions = []
    # 单个问题列表。结构['text','href']
    question = []
    # 定义网页解析对象
    soup = BeautifulSoup(QuestionPageHtmlCode, 'html.parser')
    # 目标样式
    # <a href="http://zhidao.baidu.com/question/183277304.html?fr=iks&word=%CE%AA%CA%B2%C3%B4&ie=gbk"
    # 目的链接关键字
    key1 = "http://zhidao.baidu.com/question/"
    key2 = "html?fr=iks&word="
    # 查找目的连接及文本
    # 查找页面中所有<a>的href属性。遍历
    for a in soup.find_all('a'):
        # print(href.get('href'))
        # 如果发现href="http://zhidao.baidu.com/question/" ，记录
        # get()在属性不存在的情况下会出错。故有try
        try:
            if a.get('href').find(key1) != -1 and a.get('href').find(key2) != -1:
                question = [a.get_text(), a.get('href')]
                questions.append(question)
        except:
            pass  # 此句没有实际用处。不添加异常处理语句，会出现语法错误
    # print(str(questions))
    return questions


# 根据输入的关键词，在百度知道中，获取相关问题的页面
# 返回数据{'响应状态':'', '响应页面代码':''}
# r = {'StatusCode':'', 'HtmlCode':''}
def getQuestionPage(word):
    g = getPage.getPage()
    g.url = 'https://zhidao.baidu.com/search'
    # g.url = 'https://www.baidu.com/s'
    # g.url = 'https://www.so.com/s?'
    g.data = {'lm': '0', 'rn': '10', 'pn': '0', 'fr': 'search', 'ie': 'gbk', 'word': ''}
    g.data['word'] = word
    g.dataEncoding = "gb18030"
    # g.data={}

    return g.requestGet()


if __name__ == '__main__':
    test()
