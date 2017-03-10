#! /usr/bin/env python
#-*- encoding:utf-8 -*-

import sys
import re
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs
from textrank4zh import TextRank4Sentence


def get_textrank(filename, filtername):
    # replace the items to blackspace
    parten = "“|”|'|-|\"".decode('utf-8')
    parten1 = "—|~".decode('utf-8')
    
    # get the filter to delete sentences
    filters = readfilters(filtername)
    
    # filter out unsuitable symbols
    filtersbegin = "【】）,|，§」*.》☆☆（：＊——······※o(*≧▽≦)ツ"
    filtersend = "~T_T-\(≧▽≦)/,.·^_^b★★★★"
    
    # record the results
    newline = ""
    with codecs.open(filename, 'r', 'gbk') as f:
    	for line in f.readlines():
            data = line.strip().split(',')
            
            # to make preprocessing for descriptions
            desc = re.sub(parten, "",data[5])
            desc = re.sub(parten1, ",", desc)
            
            # to get summary
            summary = get_summary(data[1], desc, filters).lstrip(filtersbegin).rstrip(filtersend)
            summary = handle(summary).lstrip(filtersbegin)
            # delete space     
            summary = summary.replace(" ", "")
            if len(summary) == 0:
                summary = data[1]
            newline += data[0] + '\t' + data[1] + '\t' + data[2] + '\t' + data[3] + '\t' + data[4] + '\t' + \
                       summary + '\t' + data[5] + '\t' + data[6] + '\n'
    
    savefile = codecs.open(sys.argv[1], 'a', 'gbk')
    savefile.write(newline)
    savefile.close()

def get_summary(title, data, filters):
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=data, lower=True, source = 'all_filters')  
    summary = ""
    
    # use the top 8 sentences sorted by weight
    items = tr4s.get_key_sentences(num = 8, sentence_min_len = 2)
    
    # thses are two loops to produce summary
    for i in xrange(len(items)):
        summary = ""
        length = 0
        index = 0
        preindex = 0
        if filter_sentences(items[i].sentence, filters) and len(items[i].sentence) != 0 and len(items[i].sentence) <= 30:
            summary = items[i].sentence
            preindex = items[i].index
            index = items[i].index
            length = len(items[i].sentence)
        else:
            break
        for j in xrange(len(items) - i - 1):
            if filter_sentences(items[i + j + 1].sentence, filters) and len(items[i + j + 1].sentence) != 0 and length + len(items[i + j + 1].sentence) <= 30:
                if preindex - 1 == items[i + j + 1].index:
                    summary = items[i + j + 1].sentence + '，' + summary
                    preindex -= 1
                elif index + 1 == items[i + j + 1].index:
                    summary = summary + '，' + items[i + j + 1].sentence
                    index += 1
                    
            # to stop the loop when length of summary is larger than 10
            if len(summary) >= 10:
                break

        if len(summary) >= 10:
            break 
        
    # use "," to split sentences to get summary
    if len(summary) == 0 or len(summary) < len(title):
        summary = get_summary_douhao(title, data, filters)
    
    # 
    if len(summary) <= 12:
        summary = ""
        
        # to get top 20 sentences and sort them by index
        items = tr4s.get_key_sentences(num = 20, sentence_min_len = 2)
        items = sorted(items, key=lambda item:item["index"])
        
        # get the first sentence which length is longer than 15 and less than 32
        for item in items:
            if filter_sentences(item.sentence, filters) and len(item.sentence) >= 12 and len(item.sentence) <= 30:
                summary = item.sentence
                break     
    
    # to drop the last ","
    summary= summary.rstrip('，')

    # set summary with the title if summary is none after above two processing
    if len(summary) == 0:
        summary = title
    
    return summary


"""
get_summary_douhao
    This function uses "," delimiter to split sentence with textrank4sentence
    Three parameters are artile title, description and the filters
"""

def get_summary_douhao(title, data, filters):
    # make up new delimiters which includes the ","
    delimiters = ['?', '!', ',', ';', '，','？', '！', '。', '……', '…', '-', '【', '】', '\n']    
    tr4s = TextRank4Sentence(delimiters)
    tr4s.analyze(text=data, lower=True, source = 'all_filters')  

    summary = ""
    
    # get the top 20 sentences
    items = tr4s.get_key_sentences(num = 20, sentence_min_len = 2)
    
    for i in xrange(len(items)):
        summary = ""
        length = 0
        index = 0
        preindex = 0
        if filter_sentences(items[i].sentence, filters) and len(items[i].sentence) != 0 and len(items[i].sentence) <= 30:
            summary = items[i].sentence
            preindex = items[i].index
            index = items[i].index
            length = len(items[i].sentence)
        else:
            break
        for j in xrange(len(items) - i - 1):
            if filter_sentences(items[i + j + 1].sentence, filters) and len(items[i + j + 1].sentence) != 0 and length + len(items[i + j + 1].sentence) <= 30:
                if preindex - 1 == items[i + j + 1].index:
                    summary = items[i + j + 1].sentence + '，' + summary
                    preindex -= 1
                elif index + 1 == items[i + j + 1].index:
                    summary = summary + '，' + items[i + j + 1].sentence
                    index += 1
        
            if len(summary) >= 12:
                break

        if len(summary) >= 12:
            break 
  
    # make sure that length of summary larger than 12
    if len(summary) <= 12:
        summary = ""
        # sort the sentences by index
        items = sorted(items, key=lambda item:item["index"])
        count = 0
        # get upto max 4 sentences to makeup the summary
        for item in items:
            if filter_sentences(item.sentence, filters) and len(item.sentence) != 0 and len(item.sentence) <= 25 and count < 4:
                summary += item.sentence + '，'
                count += 1
                if len(summary) > 15 or count >= 4:
                    break
    return summary


def readfilters(filename):
    filters = []
    with codecs.open(filename, 'r') as f:
        for line in f.readlines():
            data = line.strip()
            filters.append(data)
    return filters

def filter_sentences(item, filters):
    isfliter = True 
    parten = '\d{8,11}'
    tmp = re.sub(parten, "", item)
    if len(tmp) == 0:
        isfliter = False
        return isfliter
    for key in filters:
        if key.decode('utf-8') in item:
            # print key, item
            isfliter = False
            break
    return isfliter   

def handle(summary):
    if "》" in summary:
        index1 = summary.index("》")
        if "《" in summary:
            index2 = summary.index("《")
            if index2 + 1 == index1:
                summary = summary[:index2] + summary[index1 + 1:]
            elif index1 - index2 >= 2:
                pass
            else:
                 summary = summary[index1 + 1: index2]
        else:
            summary = summary[index1 + 1:]
    else:
        if "《" in summary:
            index1 = summary.index("《")
            summary = summary[:index1]
    
    if "）" in summary:
        index1 = summary.index("）")
        if "（" in summary:
            index2 = summary.index("（")
            if  index1 -index2 == 1:
                summary = summary[:index2] + summary[index1 + 1:]
            elif index1 - index2 >= 2:
                pass
            else:
                summary = summary[index1 + 1 : index2]       
        else:
            summary = summary[index1 + 1:]
    else:
        if "（" in summary:
            index1 = summary.index("（")
            summary = summary[:index1]
    
    if "." in summary:
        index1 = summary.index('.')
        if summary[index1 - 4 : index1 - 1] == '，' :
            summary = summary.replace('.', "")
        else:
            summary = summary[:index1] + '，' + summary[index1:].replace('.', "") 
  
    if "·" in summary:
        index1 = summary.index('·')
        if summary[index1 - 4 : index1 - 1] == '，' :
            summary = summary.replace('·', "")
        else:
            summary = summary[:index1] + '，' + summary[index1:].replace('·', "") 
    return summary

if __name__ == "__main__":
    filename = "../data/manhua.1000"
    filtername = 'filters'
    get_textrank(filename, filtername)
    print "over"
