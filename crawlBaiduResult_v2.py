# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time
import urllib2
import sys
import signal
headers = {'Accept': '*/*',

'Accept-Language': 'en-US,en;q=0.8',

'Cache-Control': 'max-age=0',

'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',#这种修改 UA 也有效

'Connection': 'keep-alive',

'Referer':'http://www.baidu.com/'

}
desired_capabilities= DesiredCapabilities.PHANTOMJS.copy()
for key, value in headers.iteritems():
    desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value

driver=webdriver.PhantomJS(desired_capabilities=desired_capabilities,service_args=['--ignore-ssl-errors=true','--load-images=false'])
driver.set_window_size(1920, 1200)

f_input=open('./'+sys.argv[1],'r')
f_output=open('./'+sys.argv[2],'w')

lines=f_input.readlines()
i=0
for line in lines:
    cur_url = 'https://www.baidu.com/s?wd='+urllib2.quote(line.strip().replace('\n', ''))
    try:
        driver.get(cur_url)
    except:
        print('exception in get url')
        #driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()
        driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities,
                                     service_args=['--ignore-ssl-errors=true', '--load-images=false'])
        driver.set_window_size(1920, 1200)
        continue
    i=i+1
    if i%10==0:
        print str(i)
    try:
        h3 =[]
        for j in xrange(1,10):
            h3=driver.find_element_by_id('content_left').find_elements_by_tag_name('h3')
            if len(h3)>0:
                break
            else:
                time.sleep(1)
        if h3 is None or len(h3)==0:
            continue
        else:
            for ele in h3:
                f_output.write(line.strip() + '###' + ele.text.encode('utf-8') + '\n')
    except:
        print('exception in get feed')
        #driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()
        driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities,
                                     service_args=['--ignore-ssl-errors=true', '--load-images=false'])
        driver.set_window_size(1920, 1200)
        continue
f_input.close()
f_output.close()
#
#driver.service.process.send_signal(signal.SIGTERM)
driver.quit()
# for h3 in driver.find_element_by_id('content_left').find_elements_by_tag_name('h3'):
#     print h3.text
# # f=open(u'F:/pagesource.txt','w')
# # f.write(driver.page_source.encode('utf-8'))
# # f.close()
