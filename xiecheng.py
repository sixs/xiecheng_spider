#-*-encoding:UTF-8-*-
import requests
import re
import execjs
import json
from bs4 import BeautifulSoup
import time
import os


#封装函数
def getData(city1,city2,date,proxy):

      #构造代理
      proxy={
        "https":proxy
      }

      session=requests.Session()

      #获取加密js
      indexUrl="http://flights.ctrip.com/booking/"+city1+"-"+city2+"-day-1.html?DDate1="+date
      headers1={
            "Host":"flights.ctrip.com",
            "Origin":"http://www.ctrip.com",
            "Upgrade-Insecure-Requests":"1",
            "Proxy-Connection":"keep-alive",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
            }
      req1=session.get(indexUrl,headers=headers1,proxies=proxy,verify=False)
      try:
        cookie=req1.headers["Set-Cookie"]
      except:
        fp=open("./data/"+date+"log.txt","a")
        fp.write(str(count1)+" "+str(count2)+" "+city1+"-"+city2+":"+"获取cookie失败\n")
        fp.close()
        return
      return_data=req1.text
      js_match=re.findall('var fn=(.*?)var jsonCallback',return_data)
      js=''
      indexUrl=''
      para=''
      if(js_match):
            indexJs=js_match[0]
            js+='r = n.replace(/^[\s\xA0]+|[\s\xA0]+$/g, "");'
            js+='c = t.split(".")[1];t = "0." + c.substring(1, c.length - 1);u = r.split("&");'
            js+='h = r.indexOf("rk=") >= 0 || r.indexOf("rt=") >= 0 ? u.splice(u.length - 2, 1)[0] : u.pop();'
            js+='u.push("CK=");h = h.split("=")[1];'
            js+='var fn='+indexJs
            js=js.replace('if(!window.location.href){return;}','')
            js=js.replace('t.open(\'GET\', ','lastUrl= (')
            js=js.replace(', !0);',');')
            js=js.replace('t.send(null);','')
            js="function ajaxRequest(n,t){"+js
            url_match=re.findall('var url = "(.*?)";',return_data)
            if(url_match):
                  indexUrl="http:"+url_match[0]
                  print(indexUrl)
            else:
                  print("未匹配到对应url信息")
            para_match=re.findall('ajaxRequest\(url(.*?)\'\);',return_data)
            if(para_match):
                  para=para_match[0]
            else:
                  print("未匹配到对应参数信息")
            js="function getUrl(){var i='';var lastUrl='';var url='"+indexUrl+"';"+js+"ajaxRequest(url"+para+"');return lastUrl;}"

            #执行加密js得到加密后的url
            ctx=execjs.compile(js)
            dataUrl=(ctx.call("getUrl"))
            #dataUrl="http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?DCity1="+str(city1)+"&ACity1="+str(city2)+"&SearchType=S&DDate1="+str(date)+"&IsNearAirportRecommond=0"
            print(dataUrl)
            headers2={
                  "Accept":"*/*",
                  "Accept-Encoding":"gzip, deflate, sdch",
                  "Accept-Language":"zh-CN,zh;q=0.8",
                  "Cache-Control":"no-cache",
                  "Connection":"keep-alive",
                  "Host":"flights.ctrip.com",
                  "Referer":indexUrl,
                  "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
                  "Pragma":"no-cache",
                  "Connection":"keep-alive"
                  }
            cookie={
                "Cookie":cookie
            }
            req2=session.get(dataUrl,headers=headers2,proxies=proxy,verify=False,cookies=cookie)
            req2.encoding="gb2312"

            #从获取的数据中提取有用数据
            try:
              info=json.loads(req2.text)
              fis = info['fis']
              #print(info)
              info_list = []
              for i in fis:
                  slist = []
                  slist.append(i['fn'])
                  slist.append(str(i['dcn']))
                  slist.append(str(i['dpbn']))
                  slist.append(str(i['acn']))
                  slist.append(str(i['apbn']))
                  slist.append(str(i['dt']))
                  slist.append(str(i['at']))
                  slist.append(str(i['lp']))

                  info_list.append(slist)

              #存入文件
              try:
                    if(len(info_list)):
                          fp=open("./data/"+date+"/"+city1+"-"+city2+".json","w")
                          fp.write(json.dumps(info_list))
                          fp.close()
                          print("存入文件成功")
                    else:
                          print("不存在机票信息")
              except:
                    #log文件
                    fp=open("./data/"+date+"log.txt","a")
                    fp.write(str(count1)+" "+str(count2)+" "+city1+"-"+city2+":"+"存入文件失败\n")
                    fp.close()
                    print("存入文件失败")
            except:
              fp=open("./data/"+date+"log.txt","a")
              fp.write(str(count1)+" "+str(count2)+" "+city1+"-"+city2+":"+"获取数据失败\n")
              fp.close()
              print("获取数据失败")
      else:
            fp=open("./data/"+date+"log.txt","a")
            fp.write(str(count1)+" "+str(count2)+" "+city1+"-"+city2+":"+"未匹配到对应js代码\n")
            fp.close()
            print("未匹配到对应js代码")

def main():
	#输入时间
	date=input("输入时间(如2017-05-07):")

	#创建文件夹，存储数据
	if(not os.path.exists("./data/")):
	  os.makedirs("./data/")
	if(not os.path.exists("./data/"+date+"/")):
	  os.makedirs("./data/"+date+"/")

	#获取所有城市
	fp=open("./city.json","r")
	all_city=fp.read()
	fp.close()
	all_city=json.loads(all_city)

	#代理
	proxies=["119.5.1.24:808","222.85.50.44:808","140.250.170.110:808","115.221.114.148:808","58.218.196.126:808","222.85.50.72:808","222.76.118.240:808"]


	for count1 in range(215):
	  for count2 in range(215):
	    if(count1 != count2):
	        city1=all_city[count1]["code"]
	        city2=all_city[count2]["code"]
	        proxy=proxies[count2%len(proxies)]
	        print(count1,count2,city1,city2)
	        getData(city1,city2,date,proxy)
	        #切换代理
	        if(count2%len(proxies)==6):
	          print("sleep 3 秒")
	          #sleep 1s,控制频率
	          time.sleep(1)

if __name__ == '__main__':
	main()