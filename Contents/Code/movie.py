# -*- coding: utf-8 -*-
import urllib, unicodedata, traceback
from api_daum_movie import MovieSearch
import re
import time

def title_renamer(text):
    tmp = re.compile('ova' , re.I)
    text = re.sub(tmp , '' , text).strip()
    text = text.replace('~' , ' ') # 다음 애니메 # 테일즈 오브 베스페리아 ～더 퍼스트 스트라이크～ ～
    text = text.replace('～', ' ')
    return text.strip()

def searchMovie(results, media, lang , manual=False):
    Log('SEARCH : [%s] [%s]' % (title_renamer(media.name), media.year))
    movie_year = media.year
    movie_name = unicodedata.normalize('NFKC', unicode(title_renamer(media.name))).strip()
    match = Regex(r'^(?P<name>.*?)[\s\.\[\_\(](?P<year>\d{4})').match(movie_name)
    
    if match:
        movie_name = match.group('name').replace('.', ' ').strip()
        movie_name = re.sub(r'\[(.*?)\]', '', movie_name )
        movie_year = match.group('year')
    is_include_kor, movie_list = MovieSearch.search_movie(movie_name, movie_year)
    #Log(movie_list)
    for data in movie_list:
        #Log(data)
        try:
            meta_id = data['id']
            if Prefs['include_time_info']:
                meta_id += '_%s' % int(time.time())
            results.Append(MetadataSearchResult(id=meta_id, name=data['title'], year=int(data['year']), score=data['score'], lang=lang))
        except Exception as e: 
            Log('Exception:%s', e)
            Log(traceback.format_exc())
    if len(movie_list) == 0 : return
    else: return movie_list
    '''Log('Manual Check')
    if manual == True:
      Log("Manual is True")
      True_result = []
      for result in results[0:3]:
        try:
          """id = re.findall('(tt[0-9]+)', result.id)[0]
          secret = Cipher.Crypt('%s%s' % (id, CINE_SECRET), 'rand0mn3ss123')
          queryJSON = JSON.ObjectFromURL(CINE_JSON % (id, secret), sleep=1.0)
          if not queryJSON.has_key('errors') and queryJSON.has_key('posters'):"""
          #thumb_url = queryJSON['posters'][0]['thumbnail_location']
          Log('thumb inserting...')
          result.thumb = 'https://image.tmdb.org/t/p/original/pSLlzA8bJWaLjrm7F7IAhJiHNVi.jpg'
          Log('thumb is %s' % str(result.thumb))
        except:
          pass'''
