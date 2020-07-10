import os
import time
import urllib.request, json
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

curpath = os.path.dirname(os.path.abspath("__file__"))
current_file = 'tcf_top_sites.csv'

all_sites = pd.read_csv(curpath + '/' + current_file, sep=",")
tcfv1 = []
tcfv2 = []
tcfv2_cmp = []

with urllib.request.urlopen('https://cmplist.consensu.org/v2/cmp-list.json') as url:
    cmpjson = json.loads(url.read().decode())

for index, row in all_sites.head(100).iterrows():
    chrome_path = r'/usr/local/bin/chromedriver' #path from 'which chromedriver'
    #driver = webdriver.Chrome(executable_path=chrome_path)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    print('checking ' + row['url'])
    driver.get(row['url'])
    time.sleep(1)
    tcfv1.append(driver.execute_script("return (typeof window.__cmp !== \"undefined\")"))
    tcfapi_exists = driver.execute_script("return (typeof window.__tcfapi !== \"undefined\")")
    tcfv2.append(tcfapi_exists)
    cmpname = ''
    if(tcfapi_exists):
        driver.execute_script(
            " (window.__tcfapi('getTCData', 2, (tcData, success) => {window.tcfv2_cmp_id = (tcData.cmpId);}, [501]))")
        time.sleep(1)
        cmpid = driver.execute_script("return window.tcfv2_cmp_id")
        if(cmpid is not None):
            cmpname = cmpjson['cmps'][str(cmpid)]['name']
    tcfv2_cmp.append(cmpname)
    driver.close()

all_sites['tcfv1'] = pd.Series(tcfv1)
all_sites['tcfv2'] = pd.Series(tcfv2)
all_sites['tcfv2_cmp'] = pd.Series(tcfv2_cmp)

all_sites.to_csv(curpath + '/' + current_file,index=False)
