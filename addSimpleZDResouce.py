# -*- coding:utf-8 -*-
import requests
import time
import json
import re
import mysql.connector
import sys

# def isInTitle(query, title):
#     if query is None or title is None:
#         return False
#     else:
#         query = query.lower().split(' ')
#         title = re.sub('\\s+', '', title.lower())
#         eleNumQuery = len(query)
#         matchNum = 0
#         for i in xrange(eleNumQuery):
#             if query[i] in title:
#                 matchNum = matchNum+1
#         if matchNum == eleNumQuery:
#             return True
#         else:
#             return False


def getMaxMatchLen(str1, str2, posInStr1, posInStr2):
    result_len = 3
    while (posInStr1 + result_len) <= len(str1):
        tmpWd = str1[posInStr1:posInStr1 + result_len]
        if str2.find(tmpWd) < 0:
            break
        else:
            result_len = result_len + 1
    return result_len - 1

def fetchInfo(query,access_token,app_key):
    for sellerType in (2,4):
        has_sku = fetchSkuId(query,access_token,app_key,sellerType)
        if has_sku is not None:
            break
        else:
            continue
    return has_sku

def fetchSkuId(query,access_token,app_key,sellerType):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # cids1='1713'
    method = 'jd.kepler.xuanpin.search.sku'
    param_json = '{"orderField":0,"pageParam":{"pageNum":1,"pageSize":10},"queryParam":' + \
                  '{"cids1":["1713"],"keywords":"' + \
                 query + '","minPrice":0,"sellerType":'+str(sellerType)+'}}'
    url = 'https://router.jd.com/api?v=1.0&method=' + method + '&access_token=' + access_token + \
          '&app_key=' + app_key + '&format=json&timestamp=' + timestamp + '&param_json=' + param_json
    try:
        respond = requests.get(url)
        r_text = respond.text.encode('utf-8')
    except:
        print('query:' + query.encode('utf-8'))
        print('method:jd.kepler.xuanpin.search.sku connection failed')
        return None
    hjson = json.loads(r_text)
    try:
        searchcode = hjson['jd_kepler_xuanpin_search_sku_response']['searchCode']
        skucount = hjson['jd_kepler_xuanpin_search_sku_response']['skuList']['totalNum']
        skulist = hjson['jd_kepler_xuanpin_search_sku_response']['skuList']['list']
        skuListSize = len(skulist)
    except:
        print('query:' + query.encode('utf-8'))
        print('method:jd.kepler.xuanpin.search.sku "searchCode" or "totalNum" extraction failed')
        return None
    if searchcode != 0 or skucount == 0 or skulist is None or skuListSize <= 0:
        return None
    else:
        return 1


def getAccessToken():
    db_name = 'jdcommodity'
    user = 'writeuser'
    port = '15020'
    host = 'QBCommodityDistribut.mdb.mig'
    passwd = 'BPnEhp5k7UW8@u'
    table = 'jdtoken'
    sql = 'select accessToken from '+table
    accessToken=""
    try:
        cnx = mysql.connector.connect(user=user, password=passwd, host=host, port=port,database=db_name)
        cursor = cnx.cursor()
        cursor.execute(sql)
    except:
        print('db connection failed')
        return None
    else:
        try:
            for (data,) in cursor:
                if len(data)>0:
                    accessToken=data
                    break
        except:
            print('access token fetch failed')
            return None
        else:
            print accessToken
            return accessToken

if __name__ == "__main__":
    # initialize db
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    db_name = 'db_mtt_smartbox'
    user = 'writeuser'
    port = '15979'
    host = 'smartbox.mdb.mig'
    passwd = 'SmartBoxMDBWrite_2017'
    greyTable = 't_commodity_query_formalzd_resouce'

    # db_name = 'datacenter'
    # user = 'writeuser'
    # port = '15917'
    # host = 'spider.mdb.mig'
    # passwd = 'VsFsWyulh7JCBJrN'
    # greyTable = 'greyqueryzdresource'
    # badcaseTable = 'incorrectquery'

    sql = "replace into " + greyTable + "(query,title,icon,wording,org_url,update_date,sourcetype,biztype)values(%s,%s,%s,%s,%s,%s,%s,%s)"
    datalist = []
    datacnt = 0
    totdatacnt = 0

    try:
        cnx = mysql.connector.connect(user=user, password=passwd, host=host, port=port,database=db_name)
        cursor = cnx.cursor()
    except:
        print('db connection failed')
    else:
        access_token = getAccessToken()
        if access_token is None:
            sys.exit()
        app_key = '4483b22d5053445092117c42172d0b48'
        #2 search engine ad
        #1 query click table
        #3 mined according to self-built dict
        try:
            f_q = open('./'+sys.argv[1],'r')
            lines_q = f_q.readlines()
        except IOError:
            print('input file open failed')
        else:
            for line in lines_q:
                fields = line.strip().split('\t')

                query = re.sub('[%#/*&\']','',fields[0].decode('utf-8'))
                imageAddr="http://res.imtt.qq.com/SmartBoxRes/201707/0100/jd_icon.jpg"
                org_query = fields[0].strip().replace('\n', '')
                title = (u"京东图书-"+org_query.decode('utf-8')).encode('utf-8')
                org_url = 'http://kepler.jd.com/search/search?key=' + query
                update_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                source_type = 5
                biztype = 1

                has_sku = fetchInfo(query, access_token, app_key)
                if has_sku is None:
                    continue
                else:
                    pass

                wording = "m.jd.com"

                data = (query.encode('utf-8'), title, imageAddr, wording, org_url, update_date, source_type, biztype)

                datalist.append(data)
                datacnt = datacnt + 1
                totdatacnt = totdatacnt + 1
                if datacnt == 400:
                    try:
                        cursor.executemany(sql, datalist)
                        cnx.commit()
                        datalist = []
                        datacnt = 0
                        print('totdatacnt:' + str(totdatacnt))
                    except:
                        print('db SQL execution failed')
                        datalist=[]
                        datacnt = 0
                        continue

            if datacnt > 0:
                try:
                    cursor.executemany(sql, datalist)
                    cnx.commit()
                    datalist = []
                    datacnt = 0
                    print('totdatacnt:' + str(totdatacnt))
                except:
                    print('db last SQL execution failed')
                    datalist = []
                    datacnt = 0
            cnx.close()