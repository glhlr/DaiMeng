import requests
from bs4 import BeautifulSoup
import time
 
#将百度的url转成真实的url
def convert_url(url):
    resp = requests.get(url=url,
                        headers=headers,
                        allow_redirects=False
                        )
    return resp.headers['Location']
 
#获取url
def get_url(wd):
 
    s = requests.session()
    #10为第2页，20为第三页，30为第四页，以此类推
    
    url = 'https://www.baidu.com/s'
    params = {
            "wd": wd,
            "pn": 0,
            
        }
    r = s.get(url=url, headers=headers, params=params)
    r.encoding = "utf-8"
    print(r.status_code)
    print(len(r.text),r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    for so in soup.select('#content_left .t a'):
        g_url = so.get('href')

        #time.sleep(1 + (i / 10))
 
 
if __name__ == '__main__':
    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",          # "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        "Host": "www.baidu.com",
        "Cookie":"BIDUPSID=0825DCFFE8DA23651AC173B320848B60; PSTM=1572078420; Hm_lvt_6859ce5aaf00fb00387e6434e4fcc925=1584668099,1587027046,1587033533,1587114418; H_WISE_SIDS=142208_122159_143857_142112_140842_139914_144238_143879_140632_141744_143161_143867_143943_141899_142780_144483_136861_131247_137746_138883_140259_141941_127969_140065_143996_140593_143059_140351_143470_143923_131423_144290_144479_144499_125581_107319_138596_139882_144112_143478_142427_142912_140367_138662_137756_110085; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSFRCVID=KuPsJeCCxG3HMFOu7dBK_YJ0SINzQU89awCI3J; H_BDCLCKID_SF=tR3KB4O2bRbEDTrP-trf5DCShUFsBbQT-2Q-5hOy3KO18qQO5jJfLxPmWtCjQMcwMH6PVITqbhOzhpFu-n5jHjbLjaOP; BDUSS=pna0JNN1JhT0czb0M1eExabWphYVpFT2JmVHRLdTlpNDkwNE9oUEJQck5ycjllRUFBQUFBJCQAAAAAAAAAAAEAAAANbpMKZ2xobHIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM0hmF7NIZheRW; H_PS_PSSID=1468_31123_21081_31342_30903_31217_30824_31085_31163_31195; Hm_lpvt_6859ce5aaf00fb00387e6434e4fcc925=1587220674; BDRCVFR[Ups602knC30]=mk3SLVN4HKm; delPer=0; PSINO=7; ZD_ENTRY=empty; shitong_key_id=2; shitong_data=59f9c9ac995094c429542b5c7333a02df7f196797dfb68e9b9d9680e6f20ebc52a3438cb2c8fb88a8bd780b3833b20f24dd366eeb39b6202a1dcb561126cf3a6786eb8c5b71c11951afb3b120965ef9e854c43e6e149198c7c5f43299363ac7607f78e002ae0c0d4be96e8e86a52b71a6fe6e792cf1b56c5096e324495bc5594ff24edb68b223baeae8e9e492d3963c7; shitong_sign=e76b12e0"

    }
    #wd = input("输入搜索关键字：")
    #get_url(wd)
    get_url('忽如一夜春风来')
