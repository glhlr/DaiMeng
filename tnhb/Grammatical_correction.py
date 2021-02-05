# !/usr/bin/python3
# coding=utf-8
# 语法纠错，
def correction(question,answer):
    # 问题

    #print(question)
    #print(answer)

    x_index = question.find('Ж')
    if x_index == -1:
        return answer

    AA = True
    while AA==True:

        if len(answer)>1:#答案如果是三个字以上的
            if answer[:2]==question[x_index-2:x_index]:
                answer=answer[2:]
                #print(answer)
            if answer[-2:]==question[x_index+1:x_index+3]:
                answer=answer[:-2]
                #print(answer)
            if answer[:1]==question[x_index-1:x_index]:
                answer=answer[1:]
                #print(answer)
            if answer[-1:]==question[x_index+1:x_index+2]:
                answer=answer[:-1]

        AA= False


    if x_index < len(question)-1:
        if question[x_index+1]=='朝' and answer[-1]== '代':
            answer=answer[:-1]
        elif question[x_index+1]=='代' and answer[-1]== '朝':
            answer=answer[:-1]
    print('修正后答案===',answer)
    return answer

# a='我国的第Ж个能发射'
# #b=['的第第五个个能']
# b=['五','第五','第五个','五个','的第第五个个能','五个能']
# for c in b:
#     xiuzheng_ans(a,c)
