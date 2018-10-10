# -*- coding:utf-8 -*-
import sys
import pandas
def analyzeResult(crawlResultFile):
    try:
        crawldata_array = pandas.read_table('./'+crawlResultFile, header=None, encoding='utf-8',
                                        delimiter="###")
    except:
        print("crawl result file reading failure")
        return None
    crawldata_array.rename(columns={0: "query", 1: "result"}, inplace=True)
    words = ['京东','天猫','淘宝','亚马逊','阿里巴巴','1号店','一号店','唯品会',
            '当当网','考拉海购','国美','苏宁','中关村在线','报价','品牌','牌子',
             '旗舰店','价格','购买','采购','批发','导购','评测','官方网站','官网','值得买','药店']
    crawldata_array2 = crawldata_array.dropna()
    queries = set(crawldata_array2[crawldata_array2["result"].str.contains('|'.join(words))].loc[:, 'query'])
    return queries
if __name__ == "__main__":
    currDate = sys.argv[1]
    inputFileName = "crawResult_"+currDate+".txt"
    selectedQueries = analyzeResult(inputFileName)
    if len(selectedQueries)>0:
        for ele in selectedQueries:
            print ele