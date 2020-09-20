import os, json
from collections import OrderedDict
#import requests
try:
    import requests
    plex = False
    Log.Info('requests imported')
except:
    import urllib, unicodedata, traceback, re
    plex = True
    Log.Info('requests not imported')
from time import sleep

def search(keyword , year):
    movie_name = urllib.quote(keyword.encode('utf8'))
    Log.Info(str(keyword) + " : " + movie_name)
    j = JSON.ObjectFromURL('https://auto-movie.naver.com/ac?q_enc=UTF-8&st=1&r_lt=1&n_ext=1&t_koreng=1&r_format=json&r_enc=UTF-8&r_unicode=0&r_escape=1&q=%s' % (movie_name) , encoding="UTF-8")
    Log.Info(str(j))
    items = j['items'][0]
    result = [{'title' : item[0][0].encode('utf-8') , 'date' : item[1][0] , 'actors' : item[2][0].encode('utf-8') , 'poster' : item[3][0] , 'code' : item[5][0] , 'type' : item[6][0].encode('utf-8')} for item in items if item[6][0].encode('utf-8') == "movie"]

    for item in result:
        try:
            if item['title'] == keyword and int(year) == int(item['date'][:4]) : # 100% 일치
                return item
        except:
            continue

    # 년도 1년정도 차이날 수 있음.
    for item in result:
        try:
            if item['title'] == keyword and abs(int(year) - int(item['date'][:4])) <= 1 : # 95% 일치한다고 가정
                return item
        except:
            continue

    # 이후 체크과정은 나중에 추가하던가 한다.
    # https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query=%EC%98%81%ED%99%94+
    result = {}
    try:
        movie_name = urllib.quote(str('영화 ' + keyword).encode('utf8'))
        html = HTML.ElementFromURL('https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query=%s' % movie_name , encoding="UTF-8")
        try:res_title = html.xpath('//a[@class="area_text_title"]')[0].text_content()
        except:res_title = ""
        try:res_original_title = html.xpath('//div[@class="sub_title"]/span[@class="txt"]')[0].text_content()
        except:res_original_title = ""
        try:res_year = html.xpath('//div[@class="sub_title"]/span[@class="txt"]')[1].text_content()
        except:res_year = ''
        try:res_poster = html.xpath('//a[@class="thumb _item"]/img[@class="_img"]')[0].get('src')
        except:res_poster = ""
        try:res_code = html.xpath('//a[@class="area_text_title"]')[0].get('href').replace('https://movie.naver.com/movie/bi/mi/basic.nhn?code=','').strip()
        except:res_code = ""
        try:result = {'title' : res_title , 'data' : res_year+'0101' if res_year != "" else "" , 'actors' : '' , 'poster' : res_poster , 'code' : res_code , 'type' : 'movie'}
        except Exception as e:
            Log('Naver error Level 2 : %s'%e)
    except Exception as e :
        Log('Naver error Level 1 : %s' % e)
    Log('naver result : %s ' % result)
    if abs(int(res_year) - int(year)) <= 1 : # 일단 이 정도만
        return result

def overview(code):
    html = HTML.ElementFromURL("https://movie.naver.com/movie/bi/mi/point.nhn?code=" + code)
    try:story1 = html.xpath('//h5[@class="h_tx_story"]')[0].text_content() + '\n'
    except:story1 = ""
    try:
        story2 = html.xpath('//p[@class="con_tx"]')[0].text_content()
    except:
        story2 = ""
    result = story1 + story2
    result = result.replace('&nbsp','').strip()
    return result

def bracket_change(text):
    text = text.replace('<' , '〈')
    text = text.replace('>' , '〉')
    return text

def critics(code):
    html = HTML.ElementFromURL("https://movie.naver.com/movie/bi/mi/point.nhn?code="+code)
    Log.Info(str("네이버 평론 Major 시작"))
    reporters = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[2]/ul/li/div[1]')
    Log.Info(str(reporters))
    # reporters part
    result = []
    for i, v in enumerate(reporters):
        try:
            wname = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[2]/ul/li[%s]/div[1]/dl/dt/a' % str( i+1 ))[0].text_content()
            wtext = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[2]/ul/li[%s]/div[1]/dl/dd' % str(i + 1))[0].text_content()
            wscore = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[2]/ul/li[%s]/div[2]/div/div/em' % str(i + 1))[0].text_content()
            result.append({'name' : wname , 'score' : wscore , 'text' : wtext})
            Log.Info(str(i))
            Log.Info('이름 : ' + str(wname))
            Log.Info('내용 : ' + str(bracket_change(wtext)))
            Log.Info('점수 : ' + str(wscore))
        except:
            continue

    reporters = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li')
    for i, v in enumerate(reporters):
        try:
            Log.Info(str(i))
            wname = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li[%s]/div[2]/dl/dd' % str(i + 1))[0].text_content().replace('|', '').strip()
            Log.Info('이름 : ' + str(wname))
            wtext = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li[%s]/div[2]/p' % str(i + 1))[0].text_content()
            Log.Info('내용 : ' + str(bracket_change(wtext)))
                                #//*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li/div[2]/p
            #                    //*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li[3]/div[1]/em
            #                    //*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li[5]/div[1]/em
            wscore = html.xpath('//*[@id="content"]/div[1]/div[4]/div[4]/div/div[3]/div/ul/li[%s]/div[1]/em' % str( i+1 ))[0].text_content()
            Log.Info('점수 : ' + str(wscore))
            result.append({'name' : wname , 'score' : wscore , 'text' : wtext})
        except:
            continue
    return result

