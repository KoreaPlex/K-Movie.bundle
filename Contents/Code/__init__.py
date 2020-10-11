# -*- coding: utf-8 -*-
# Daum Movie
 
import urllib, unicodedata, traceback, re
# 추가
import watcha
import tmdb
import naver
from chapterdb import PlexChapterDBAgent
import re, time, unicodedata, hashlib, types


FREEBASE_URL = 'https://meta.plex.tv/m/%s?lang=%s&ratings=1&reviews=1&extras=1'
PLEXMOVIE_URL = 'https://meta.plex.tv'
PLEXMOVIE_BASE = 'movie'

# CineMaterial
CINE_ROOT = 'https://api.cinematerial.com'
CINE_JSON = '%s/1/request.json?imdb_id=%%s&key=plex&secret=%%s&width=720&thumb_width=100.' % CINE_ROOT
CINE_SECRET = '157de27cd9815301d29ab8dcb2791bdf'

DAUM_MOVIE_SRCH   = "http://movie.daum.net/data/movie/search/v2/%s.json?size=20&start=1&searchText=%s"

DAUM_MOVIE_DETAIL = "http://movie.daum.net/data/movie/movie_info/detail.json?movieId=%s"
DAUM_MOVIE_CAST   = "http://movie.daum.net/data/movie/movie_info/cast_crew.json?pageNo=1&pageSize=100&movieId=%s"
DAUM_MOVIE_PHOTO  = "http://movie.daum.net/data/movie/photo/movie/list.json?pageNo=1&pageSize=100&id=%s"

# os

OS_API = 'http://api.opensubtitles.org/xml-rpc'
OS_PLEX_USERAGENT = 'plexapp.com v9.0'
SUBTITLE_EXT = ['utf', 'utf8', 'utf-8', 'sub', 'srt', 'smi', 'rt', 'ssa', 'aqt', 'jss', 'ass', 'idx']



# Extras.
IVA_ASSET_URL = 'iva://api.internetvideoarchive.com/2.0/DataService/VideoAssets(%s)?lang=%s&bitrates=%s&duration=%s&adaptive=%d&dts=%d'
TYPE_ORDER = ['primary_trailer', 'trailer', 'behind_the_scenes', 'interview', 'scene_or_sample']
IVA_LANGUAGES = {-1   : Locale.Language.Unknown,
                  0   : Locale.Language.English,
                  12  : Locale.Language.Swedish,
                  3   : Locale.Language.French,
                  2   : Locale.Language.Spanish,
                  32  : Locale.Language.Dutch,
                  10  : Locale.Language.German,
                  11  : Locale.Language.Italian,
                  9   : Locale.Language.Danish,
                  26  : Locale.Language.Arabic,
                  44  : Locale.Language.Catalan,
                  8   : Locale.Language.Chinese,
                  18  : Locale.Language.Czech,
                  80  : Locale.Language.Estonian,
                  33  : Locale.Language.Finnish,
                  5   : Locale.Language.Greek,
                  15  : Locale.Language.Hebrew,
                  36  : Locale.Language.Hindi,
                  29  : Locale.Language.Hungarian,
                  276 : Locale.Language.Indonesian,
                  7   : Locale.Language.Japanese,
                  13  : Locale.Language.Korean,
                  324 : Locale.Language.Latvian,
                  21  : Locale.Language.Norwegian,
                  24  : Locale.Language.Persian,
                  40  : Locale.Language.Polish,
                  17  : Locale.Language.Portuguese,
                  28  : Locale.Language.Romanian,
                  4   : Locale.Language.Russian,
                  105 : Locale.Language.Slovak,
                  25  : Locale.Language.Thai,
                  64  : Locale.Language.Turkish,
                  493 : Locale.Language.Ukrainian,
                  50  : Locale.Language.Vietnamese}

from tv import searchTV, updateTV
from movie import searchMovie

server_url = Prefs['server_url']
try:
  if server_url[-1] == '/' :
    server_url = Prefs['server_url'][:-1]
    Log('SERVER BASE URL Automatically modified')
except:
  server_url = ""

try:
  if server_url == "":
    server_url = "http://103.208.222.5:23456"
except:
  pass


@route('/version') 
def version():
    return '2020-07-27'

def Start():
    #HTTP.CacheTime = CACHE_1HOUR * 12
    HTTP.Headers['Accept'] = 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    #HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['User-Agent'] = OS_PLEX_USERAGENT
    #HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    HTTP.Headers['Accept-Language'] = 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    HTTP.Headers['Cookie'] = Prefs['cookie']



    ####################################################################################################
"""
def searchDaumMovie(cate, results, media, lang):
  media_name = media.name
  media_name = unicodedata.normalize('NFKC', unicode(media_name)).strip()
  Log.Debug("search: %s %s" %(media_name, media.year))
  data = JSON.ObjectFromURL(url=DAUM_MOVIE_SRCH % (cate, urllib.quote(media_name.encode('utf8'))))
  items = data['data']
  for item in items:
    year = str(item['prodYear'])
    title = String.DecodeHTMLEntities(String.StripTags(item['titleKo'])).strip()
    id = str(item['tvProgramId'] if cate == 'tv' else item['movieId'])
    if year == media.year:
      score = 95
    elif len(items) == 1:
      score = 80
    else:
      score = 10
    Log.Debug('ID=%s, media_name=%s, title=%s, year=%s, score=%d' %(id, media_name, title, year, score))
    results.Append(MetadataSearchResult(id=id, name=title, year=year, score=score, lang=lang))
"""
def bracket_change(text):
    if type(text) != str : return text
    text = text.replace('<' , '〈')
    text = text.replace('>' , '〉')
    return text


def update_movie_by_web(metadata, metadata_id):
  try:
      url = 'https://movie.daum.net/moviedb/main?movieId=%s' % metadata_id
      root = HTML.ElementFromURL(url)
      tags = root.xpath('//span[@class="txt_name"]')
      tmp = tags[0].text_content().split('(')
      metadata.title = urllib.unquote(tmp[0])
      if not Prefs['sort_title_korean']:
        metadata.title_sort = unicodedata.normalize('NFKD', metadata.title)
      try: metadata.original_title = root.xpath('//span[@class="txt_origin"]')[0].text_content()
      except: pass

      metadata.year = int(tmp[1][:4])
      try:
        tags = root.xpath('//div[@class="info_origin"]/a/span')
        if len(tags) == 4:
          tmp = '%s.%s' % (tags[1].text_content(), tags[3].text_content())
          metadata.rating = float(tmp)
      except: pass
      try:
        metadata.genres.clear()
        metadata.countries.clear()
        tags = root.xpath('//dl[@class="list_movie list_main"]/dd')
        for item in tags[0].text_content().split('/'):
          metadata.genres.add(item.strip())
        for item in tags[1].text_content().split(','):
          metadata.countries.add(item.strip())
        tmp = tags[2].text_content().strip()
        match = re.compile(r'\d{4}\.\d{2}\.\d{2}').match(tmp)
        if match: 
          metadata.originally_available_at = Datetime.ParseDate(match.group(0).replace('.', '')).date()
          tmp = tags[3].text_content().strip()
          if tmp.find(u'재개봉') != -1:
            tmp = tags[4].text_content().strip()
        else:
          metadata.originally_available_at = None
        match = re.compile(ur'(?P<duration>\d{2,})분[\s,]?(?P<rate>.*?)$').match(tmp)
        if match:
          metadata.duration = int(match.group('duration').strip())*60
          metadata.content_rating = String.DecodeHTMLEntities(String.StripTags(match.group('rate').strip()).strip())
      except Exception as e:
        Log('Exception:%s', e)
        Log(traceback.format_exc())

      #try: metadata.summary = String.DecodeHTMLEntities(String.StripTags(root.xpath('//div[@class="desc_movie"]/p')[0].text_content().strip()).strip())
      try:
        metadata.summary = String.DecodeHTMLEntities(String.StripTags(root.xpath('//div[@class="desc_movie"]/p')[0].text_content().strip().replace('<br>', '\n\n')).strip())
        Log('metadata.summary : %s' % metadata.summary)
      except: pass
  except Exception as e:
    Log('Exception:%s', e)
    Log(traceback.format_exc())

def tmdb_to_daum_dict(code , metadata):
    return tmdb.tmdb_meta(metadata_id = code.replace('tmdb_','').strip(), lang = 'ko', metadata = metadata, force=False , daum_to_tmdb = True)

def scrub_extra(extra, media_title):
    e = extra['extra']
    # Remove the "Movie Title: " from non-trailer extra titles.
    if media_title is not None:
        r = re.compile(media_title + ': ', re.IGNORECASE)
        e.title = r.sub('', e.title)
    # Remove the "Movie Title Scene: " from SceneOrSample extra titles.
    if media_title is not None:
        r = re.compile(media_title + ' Scene: ', re.IGNORECASE)
        e.title = r.sub('', e.title)

    # Capitalise UK correctly.
    e.title = e.title.replace('Uk', 'UK')

    return extra

def updateDaumMovie(cate, media, metadata , lang):
    try:
        Log('debug : %s' % metadata.summary) # 이미 있다고;;??
    except:
        pass
  # (1) from detail page
    watcha_only = tmdb_json_en = imdb_code = tmdb_json = daum_id = poster_url = None
    if metadata.id.count('tmdb') == 0 and metadata.id.count('watcha') == 0:
        daum = True
        daum_id = metadata_id = metadata.id.split('_')[0]
        update_movie_by_web(metadata, metadata_id)
    elif metadata.id.count('tmdb') > 0:
        daum = False
        metadata_id = metadata.id
        tmdb_json = tmdb_to_daum_dict(metadata.id , metadata)
    elif metadata.id.count('watcha') > 0:
        daum = False
        watcha_only = True
        metadata_id = metadata.id
    try: poster_url = info['photo']['fullname']
    except:pass

  # (2) cast crew

    daum_crew_init = False
    if daum == True:
        directors = list()
        producers = list()
        writers = list()
        roles = list()
        data = JSON.ObjectFromURL(url=DAUM_MOVIE_CAST % metadata_id)
        for item in data['data']:
          cast = item['castcrew']
          if cast['castcrewCastName'] in [u'감독', u'연출']:
            director = dict()
            director['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
            if item['photo']['fullname']:
              director['photo'] = item['photo']['fullname']
            directors.append(director)
          elif cast['castcrewCastName'] == u'제작':
            producer = dict()
            producer['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
            if item['photo']['fullname']:
              producer['photo'] = item['photo']['fullname']
            producers.append(producer)
          elif cast['castcrewCastName'] in [u'극본', u'각본']:
            writer = dict()
            writer['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
            if item['photo']['fullname']:
              writer['photo'] = item['photo']['fullname']
            writers.append(writer)
          elif cast['castcrewCastName'] in [u'주연', u'조연', u'출연', u'진행']:
            role = dict()
            role['role'] = cast['castcrewTitleKo']
            role['name'] = item['nameKo'] if item['nameKo'] else item['nameEn']
            if item['photo']['fullname']:
              role['photo'] = item['photo']['fullname']
            roles.append(role)
          # else:
          #   Log.Debug("unknown role: castcrewCastName=%s" % cast['castcrewCastName'])

        if directors:
          metadata.directors.clear()
          for director in directors:
            meta_director = metadata.directors.new()
            if 'name' in director:
              meta_director.name = director['name']
            if 'photo' in director:
              meta_director.photo = director['photo']
        if producers:
          metadata.producers.clear()
          for producer in producers:
            meta_producer = metadata.producers.new()
            if 'name' in producer:
              meta_producer.name = producer['name']
            if 'photo' in producer:
              meta_producer.photo = producer['photo']
        if writers:
          metadata.writers.clear()
          for writer in writers:
            meta_writer = metadata.writers.new()
            if 'name' in writer:
              meta_writer.name = writer['name']
            if 'photo' in writer:
              meta_writer.photo = writer['photo']
        if roles:
          metadata.roles.clear()
          for role in roles:
            meta_role = metadata.roles.new()
            if 'role' in role:
              meta_role.role = role['role']
            if 'name' in role:
              meta_role.name = role['name']
            if 'photo' in role:
              meta_role.photo = role['photo']
        daum_crew_init = True

    ################ LifeForWhat 추가부분

    # 리뷰 클리어
    metadata.reviews.clear()

    # 컬렉션 클리어
    metadata.collections.clear()
    Log("metadata.original_title : %s" % metadata.original_title )
    # tmdb collection 을 먼저 찾는다.
    if not tmdb_json :
        if metadata.original_title != None:
            tmdb_title_for_search = metadata.original_title
            Log('metadata.original_title : %s ' % metadata.original_title)
            if tmdb_title_for_search.count(',') > 0 :
                tmdb_title_for_search = tmdb_title_for_search.split(',')
            else:
                tmdb_title_for_search = [tmdb_title_for_search]
            tmdb_title_for_search = [item.replace('～' ,' ') for item in tmdb_title_for_search]
            tmdb_year = metadata.year
            for index, tmdb_title_for_search_part in enumerate(tmdb_title_for_search):
                tmdb_json_en = tmdb_json_ko = None
                try:
                    Log('metadata.duration : %s' % metadata.duration)
                    j, c = tmdb.tmdb().search(name=tmdb_title_for_search_part, year=tmdb_year , duration=int(metadata.duration) / 60)
                except:
                    continue
                tmdb_json_en = j
                tmp_j = JSON.ObjectFromURL('https://api.themoviedb.org/3/movie/'+str(tmdb_json_en['id'])+'?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR')
                if 'imdb_id' in tmp_j:
                    imdb_code = tmp_j['imdb_id']
                else:
                    imdb_code = None
                tmdb_json_ko, c_2 = tmdb.tmdb().search(name=tmdb_title_for_search_part, year=tmdb_year, lang='ko')
                Log('TMDB Found')
                break
            try:
                tmdb_collection = c['name']
                if tmdb_collection != "":
                    metadata.collections.add('💿 ' + tmdb_collection)
            except Exception as e:
                Log.Info('tmdb collection part error. It can be ignored. %s' % str(e))
                pass
    else:
        tmdb_id = tmdb_json['id']
        # https://api.themoviedb.org/3/movie/3690?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR
        tmdb_json_ko = JSON.ObjectFromURL('https://api.themoviedb.org/3/movie/'+str(tmdb_id)+'?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR')
        tmdb_json_en = JSON.ObjectFromURL('https://api.themoviedb.org/3/movie/'+str(tmdb_id)+'?api_key=b2f505af2cb75d692419696af851e517&language=en-US')
        try:imdb_code = tmdb_json_en['imdb_id']
        except:imdb_code = None
        try:
            tmdb_collection = tmdb.tmdb().find_in_tmdb_Collection(tmdb_json)
            if tmdb_collection != "":
                metadata.collections.add('💿 ' + tmdb_collection)
        except Exception as e:
            Log.Info('tmdb error %s' % str(e))
            pass
    # Watcha
    # 다음에서 못 찾은 경우 인물도 넣어준다.
    try:
        if not watcha_only:
            Log.Info('WATCHA SEARCHING TITLE : ' + metadata.title)
            Log.Info('WATCHA SEARCHING YEAR : ' + str(metadata.year))
            tmp_year = metadata.year
            w_cookie = Prefs['w_cookie'] if Prefs['w_cookie'] != "" else ""
            w = watcha.watcha(keyword = metadata.title, year=None if metadata.year == None else int(metadata.year), media_type='movies' , cookie = w_cookie)
        elif watcha_only: # 왓챠 메타데이터가 메인임
            Log.Info('WATCHA SEARCHING TITLE : ' + media.title)
            Log.Info('WATCHA SEARCHING YEAR : ' + str(metadata.year))
            tmp_year = metadata.year
            w_cookie = Prefs['w_cookie'] if Prefs['w_cookie'] != "" else ""
            w = watcha.watcha(keyword = media.title.replace('WATCHA  :  ','').strip(), year=None if tmp_year == None else int(tmp_year), media_type='movies' , cookie = w_cookie)
            try:data = w.info['API_INFO']
            except: # 못찾음
                w = watcha.watcha(keyword=media.title.replace('WATCHA  :  ', '').strip(),
                                  year=None if tmp_year == None else int(tmp_year), media_type='movies', year_diff_allow=1,
                                  cookie=w_cookie)
            try:metadata.title = data['title']
            except:pass
            try:metadata.year = data['year']
            except:pass
            try:metadata.title_sort = data['title']
            except:pass
            try:metadata.original_title = data['original_title']
            except:pass
            try:metadata.rating = data['rating_avg']
            except:pass
            try:
                metadata.genres.clear()
                try:
                    for item in data['genres']:
                        metadata.genres.add(item.strip())
                except:
                    pass
                metadata.countries.clear()
                try:
                    for item in data['nations']:
                        metadata.countries.add(item['name'])
                except:
                    pass
            except:
                pass
            try:metadata.summary = data['description']
            except:pass
            def ContentRatingConvert(text):
                if text.count('15') > 0 : return '15세이상관람가'
                if text.count('12') > 0 : return '12세이상관람가'

            try:metadata.content_rating = ContentRatingConvert(data['film_rating_short'])
            except:pass
        w2 = w.info
        if not daum_crew_init : # 다음에서 인물을 못 찾은 경우.
            directors = list()
            producers = list()
            writers = list()
            roles = list()
            for item in w2['출연']:
                cast = item['job']
                if cast in [u'감독', u'연출']:
                    director = dict()
                    director['name'] = item['person']['name']
                    if item['person']['photo']:
                        director['photo'] = item['person']['photo']['small']
                    directors.append(director)
                elif cast in [u'주연', u'조연', u'출연', u'진행' ,'단역' , '특별출연' ]:
                    role = dict()
                    try:role['role'] = item['character'][0]
                    except:role['role'] = ""
                    role['name'] = item['person']['name']
                    if item['person']['photo']:
                        role['photo'] = item['person']['photo']['small']
                    roles.append(role)
                # else:
                #   Log.Debug("unknown role: castcrewCastName=%s" % cast['castcrewCastName'])

            if directors:
                metadata.directors.clear()
                for director in directors:
                    meta_director = metadata.directors.new()
                    if 'name' in director:
                        meta_director.name = director['name']
                    if 'photo' in director:
                        meta_director.photo = director['photo']
            if producers:
                metadata.producers.clear()
                for producer in producers:
                    meta_producer = metadata.producers.new()
                    if 'name' in producer:
                        meta_producer.name = producer['name']
                    if 'photo' in producer:
                        meta_producer.photo = producer['photo']
            if writers:
                metadata.writers.clear()
                for writer in writers:
                    meta_writer = metadata.writers.new()
                    if 'name' in writer:
                        meta_writer.name = writer['name']
                    if 'photo' in writer:
                        meta_writer.photo = writer['photo']
            if roles:
                metadata.roles.clear()
                for role in roles:
                    meta_role = metadata.roles.new()
                    if 'role' in role:
                        meta_role.role = role['role']
                    if 'name' in role:
                        meta_role.name = role['name']
                    if 'photo' in role:
                        meta_role.photo = role['photo']
        if Prefs['w_collection_by_flavor'] == True and Prefs['w_cookie'] != "" and Prefs['w_private_point_collection_location'] == '제일 위':
            try:
                predicted_point = w.predicted_rating
                temp_string = "⭐ 왓챠 예상 별점 : %s" % str(round((predicted_point / 2) , 1) )
                metadata.collections.add(temp_string)
                Log.Info("예상별점")
                Log.Info(temp_string)
            except Exception as e :
                import traceback
                Log.Info(str(e))
                Log.Info(str(traceback.print_exc))
        Log.Info('WATCHA SEARCHED TITLE : ' + str(w2['API_INFO']['title']))
        Log.Info('WATCHA SEARCHED YEAR : ' + str(w2['API_INFO']['year']))

        for item in w2['코멘트']:
            # ⭐
            wname = ''
            wsource = u'왓챠'
            wtext = ''
            wline = ''
            wimage = ''
            offiYN = item['user']['official_user']
            if item['user']['name'] in Prefs['w_favorite_non_critics'].split(','):
                offiYN = True
            if offiYN == True:
                wname = item['user']['name']
                if wname in Prefs['black_critic']:
                    continue
                wtext = item['text']
                wimage = item['user_content_action']['rating']
                if wname != "" and wtext != "" and wimage != "":
                    meta_review = metadata.reviews.new()
                    meta_review.author = wname
                    meta_review.source = u'왓챠'
                    meta_review.text = '⭐ '+ str(bracket_change(wimage)) + ' | '+ wtext.replace('<' ,'〈').replace('>','〉')
                    meta_review.link = 'https://www.watcha.com/'
                    if float(wimage) >= float(Prefs['thresh_hold_point']):
                        meta_review.image = 'rottentomatoes://image.review.fresh'
                    else:
                        meta_review.image = 'rottentomatoes://image.review.rotten'
        # 이제 Collection 파트
        if Prefs['collection_make_watcha_by_another_users']:
            whitelist = ['수상', '아카데미', '영화제']
            blacklist_keyword = ['여성', '여자', '페미', '소장', '메모', '소장', '베스트', '내가', '나의', '최고', '본 영화', '보물', '볼 영화',
                                 '관람', '감상', '본것', '내 영화']
            blacklist_user = ['유정']
            try:
                d = {'watcha' : w2}
                # 복붙하느라...
                temp_list = d['watcha']['컬렉션']
            except:
                temp_list = []
            collections = []
            # 콜렉션용 각종 조건들을 붙인다...
            # 페미니스트가 너무 많음.. 왓챠에는..
            for coll in temp_list:
                for white in whitelist:
                    if white in coll['title'] or coll['likes_count'] > int(Prefs['w_like']):
                        collections.append(coll['title'])
                        break

            for coll in temp_list:
                if coll['likes_count'] < 100:
                    continue  # 좋아요가 100개 미만은 버린다.
                keep_going = False
                years_list = re.findall('\d{4}', coll['title'])
                try:years_list = [item for item in years_list if int(item) > 1890 and int(item) < 2030]
                except: years_list = []
                if len(years_list) > 0:
                    continue  # 년도가 들어간 건 버린다
                if keep_going == False:
                    for black in blacklist_keyword:
                        if black in coll['title'].replace('  ', ' '):
                            keep_going = True
                            break

                if keep_going == False:
                    for blackuser in blacklist_user:
                        if blackuser in coll['user']['name']:
                            keep_going = True
                            break

                if keep_going == False and coll['title'] not in collections:
                    collections.append(coll['title'])
            #Log.Error(str(collections))
            final_black_list_keyword_list = Prefs['collection_black_keyword'].split(',')
            for collection in collections:
                temp_string = collection
                if temp_string.count('수상') > 0:
                    temp_string = "🏆 " + temp_string
                elif temp_string.count('후보') > 0:
                    temp_string = "🏆 " + temp_string
                elif temp_string.count('대상') > 0:
                    temp_string = "🏆 " + temp_string
                elif temp_string.count('주연상') > 0:
                    try:
                        temp_string = "🏆 " + temp_string
                    except:
                        #Log.Info(str(temp_string))
                        pass
                else:
                    temp_string = "🎬 " + temp_string
                # 최종 블랙리스트로 거른다.
                for item in final_black_list_keyword_list:
                    if item in temp_string:
                        Log.Info(temp_string)
                        Log.Info(item)
                        temp_string = ""
                        continue
                if temp_string == "":
                    continue
                metadata.collections.add(temp_string)
    except Exception as e:
        import traceback
        Log('Exception:%s', e)
        Log(traceback.format_exc())


    if Prefs['w_collection_by_flavor'] == True and Prefs['w_cookie'] != "" and Prefs[
            'w_private_point_collection_location'] == '제일 아래':
            try:
                predicted_point = w.predicted_rating
                temp_string = "⭐ 왓챠 예상 별점 : %s" % str(round((predicted_point / 2), 1))
                metadata.collections.add(temp_string)
                Log.Info("예상별점")
                Log.Info(temp_string)
            except Exception as e:
                import traceback

                Log.Info(str(e))
                Log.Info(str(traceback.print_exc))

    # 네이버 파트
    try:
        naver_result = naver.search(keyword=metadata.title, year=int(metadata.year))
        crtics_naver = naver.critics(naver_result['code'])
    except :
        crtics_naver = []
    for item in crtics_naver:
        # ⭐
        wname = ''
        wsource = u'네이버'
        wtext = ''
        wline = ''
        wimage = ''
        wname = item['name']
        if wname in Prefs['black_critic']:
            continue
        wtext = item['text']
        wimage = item['score']
        if wname != "" and wtext != "" and wimage != "":
            meta_review = metadata.reviews.new()
            meta_review.author = wname
            meta_review.source = u'네이버'
            Log.Info(str(wtext))
            meta_review.text = '⭐ ' + str(bracket_change(wimage)) + ' | ' + wtext.replace('<' ,'〈').replace('>','〉')
            meta_review.link = 'https://www.naver.com/'
            if float(wimage) >= float(Prefs['thresh_hold_point']):
                meta_review.image = 'rottentomatoes://image.review.fresh'
            else:
                meta_review.image = 'rottentomatoes://image.review.rotten'

    # Trailer Daum 기반
    extras = []
    Log('다음 부가영상을 찾습니다. %s' % str(daum_id))
    result = []
    if daum_id:
        try:result = JSON.ObjectFromURL(server_url + '/trailer',  values=dict(metadata_id=str(daum_id) , app_name = 'k_movie' , apikey=Prefs['apikey']) , cacheTime = 0)
        except:pass

    Log('trailer result : %s' % str(result))
    """rr = []
    for item in result:
        if item not in rr:rr.append(item)
    result = rr"""
    for item in result:
        tmp = item['title']
        if Prefs['trailer_location'] == 'Proxy':
            tmpurl = item['attachments']['proxy_url']
        elif Prefs['trailer_location'] == "CDN":
            tmpurl = item['attachments']['url']
        thumb_url_req1 = 'http://img1.daumcdn.net/thumb/C141x99/?fname=http%3A%2F%2Ft1.daumcdn.net%2Ftvpot%2Fthumb%2F' + item['vid'] + '%2Fthumb.png'
        thumb_url_req2 = 'http://img1.daumcdn.net/thumb/C141x99/?fname=http%3A%2F%2Ft1.daumcdn.net%2Ftvpot%2Fthumb%2F' + item['vid'] + '%2Fthumb.jpg'
        try: # 처음부터 DB를 잘 만들었으면 됐는데..
            try:tmp_res = HTTP.Request(thumb_url_req1).content
            except Exception as e :
                if str(e).count('HTTP Error 404') > 0 : raise ValueError
            Log('url1 is okay : %s'%thumb_url_req1)
            thumb_url = thumb_url_req1
        except Exception as e:
            Log(e)
            thumb_url = thumb_url_req2
            Log('url2 is okay : %s' % thumb_url_req2)

        Log('thumb_url : %s '% thumb_url)
        if tmp.count('예고편') > 0 :
            # url="lf://cdn.discordapp.com/attachments/748003668212711485/748784552113209384/test.mp4",
            # F:\T\Contents\Movies\Trailers\Daum\42912

            extras.append({'type': 'trailer',
                       'lang': "ko",
                       'extra': TrailerObject(
                           #url = 'lf://' + item['dl_url'].replace('https://',''),
                           url='k_movie://' + tmpurl.replace('https://', ''),
                           title=item['title'],
                           thumb=thumb_url
                           )})
        else:
            extras.append({'type': 'behind_the_scenes',
                       'lang': "ko",
                       'extra': BehindTheScenesObject(
                           #url = 'lf://' + item['dl_url'].replace('https://',''),
                           url='k_movie://' + tmpurl.replace('https://', ''),
                           title=item['title'],
                        thumb=thumb_url)})

    for extra in extras:
        metadata.extras.add(extra['extra'])





    # IMDb 파트
    Log('IMDB Part Starting (Manual or Auto)')
    if Prefs['imdb_rating'] == True and metadata.original_title != None:
        True_Item = False
        Log('tmdb_json_en : %s' % tmdb_json_en)
        if tmdb_json_en in [None , False] and metadata.original_title != None:
            q = metadata.original_title.strip() if metadata.original_title.count(',') == 0 else metadata.original_title.split(',')[0].strip()
            year = metadata.year
            # https://v2.sg.media-imdb.com/suggestion/p/peninsula.json
            baseURL = "https://v2.sg.media-imdb.com/suggestion/%s/%s.json"
            try:
                data = JSON.ObjectFromURL(url=baseURL % (q[0].lower() , q.replace(' ', '_').lower() ))['d']
            except:
                data = []

            for item in data:
                try:
                    if int(item['y']) == int(year):
                        True_Item = item
                except:
                    continue
            for item in data:
                try:
                    if abs(int(item['y']) - int(year)) <= 1:
                        True_Item = item
                        break  # 1년차이까지는 괜찮아.
                except:
                    continue

        elif tmdb_json_en: # j , c = tmdb.tmdb().search(name=tmdb_title_for_search_part , year=tmdb_year)
            tmdb_id = str(tmdb_json_en['id']) # https://api.themoviedb.org/3/movie/496243?api_key=b2f505af2cb75d692419696af851e517&language=en-US
            j = JSON.ObjectFromURL('https://api.themoviedb.org/3/movie/'+tmdb_id+'?api_key=b2f505af2cb75d692419696af851e517&language=en-US')
            data = []
            True_Item = False
            if 'imdb_id' in j:
                item = {'id' : j['imdb_id']}
                imdb_code = j['imdb_id']
                True_Item = True

                if imdb_code == "" or imdb_code == None: imdb_code = True_Item = None
                Log('Found IMDb ID in TMDb Info : %s' % item)

        Log("True_Item : %s / imdb_code : %s" % (True_Item , imdb_code))
        if True_Item or imdb_code and len(imdb_code) != 0 :
            if not imdb_code : imdb_code = item['id']
            else : pass
            imdb_url = 'https://www.imdb.com/title/%s' % imdb_code

            root = HTML.ElementFromURL(imdb_url)
            try:imdb_rating = root.xpath('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/div[1]/strong/span')[0].text_content()
            except:imdb_rating = None
            try:imdb_people = root.xpath('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/a/span')[0].text_content().replace(',','')
                                         #//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/a/span
            except:imdb_people = 0

            id = re.findall('(tt[0-9]+)', imdb_code)[0]
            secret = Cipher.Crypt('%s%s' % (id, CINE_SECRET), 'rand0mn3ss123')
            queryJSON = JSON.ObjectFromURL(CINE_JSON % (id, secret), sleep=1.0)
            imdb_posters = False
            if not queryJSON.has_key('errors') and queryJSON.has_key('posters'):
                imdb_posters = queryJSON['posters']
                Log('IMDb Poster : %s' % imdb_posters)
                Log('queryJSON %s : ' % queryJSON)

            try:
                try:Log('metadata.summary : %s' % metadata.summary)
                except:pass
                imdb_overview = root.xpath('//div[@class="summary_text"]')[0].text_content()
                Log('imdb_overview : %s '  % imdb_overview)
                if imdb_overview.count(u'Add a Plot') > 0 : imdb_overview = ""
                if imdb_overview.count(u'See full summary') > 0 :
                    Log('See Full Summary, then Go to that link')
                    tmp_HTML = HTML.ElementFromURL(imdb_url + '/plotsummary') # plotsummary
                    imdb_overview = tmp_HTML.xpath('/html/body/div[3]/div/div[2]/div[3]/div[1]/section/ul[1]/li[1]/p/text()')[0]
                    Log('tt : %s' %imdb_overview)
            except Exception as e:
                Log(e)
                imdb_overview = ""
            Log('IMDb rating Start')
            Log(imdb_code)
            Log(imdb_rating)
            Log(imdb_people)
            Log(Prefs['imdb_rating_people_numbers'])
            if imdb_rating and int(imdb_people.replace(',','').strip()) >= int(Prefs['imdb_rating_people_numbers']):
                Log('IMDb rating condition start')
                metadata.rating = float(imdb_rating)
                metadata.rating_image = 'imdb://image.rating'
                if Prefs['imdb_rating_text_and_collection'] != "":
                    tmp = Prefs['imdb_rating_text_and_collection']
                    tmp = tmp.split(',')
                    tmp = [item.split('[') for item in tmp]
                    score = float(imdb_rating)
                    for item in tmp:
                        if float(item[0].split('~')[0]) <= score <= float(item[0].split('~')[1]):
                            metadata.collections.add('🟨 ' + item[1].replace(']','').strip())
                            break


    if imdb_code:
        url = FREEBASE_URL % (imdb_code[2:], 'en')
        try:
            movie = XML.ElementFromURL(url, cacheTime=0, headers={'Accept-Encoding': 'gzip'})
        except:
            movie = None
        Log(movie)

        # IMDb 기반으로 리뷰를 찾는다.
        if movie not in [None, False]:
            if len(movie.get('title')) > 0:
                title = movie.get('title')
                # Chapter
            if Prefs['plex_agent_review_add']:
                for review in movie.xpath('//review'):
                    if review.text not in [None, False, '']:
                        if not Prefs['plex_agent_review_translate']:
                            r = metadata.reviews.new()
                            r.author = review.get('critic')
                            r.source = review.get('publication')
                            r.image = 'rottentomatoes://image.review.fresh' if review.get(
                                'freshness') == 'fresh' else 'rottentomatoes://image.review.rotten'
                            r.link = review.get('link')
                            r.text = review.text
                        else:
                            r = metadata.reviews.new()
                            r.author = review.get('critic')
                            r.source = review.get('publication')
                            r.image = 'rottentomatoes://image.review.fresh' if review.get(
                                'freshness') == 'fresh' else 'rottentomatoes://image.review.rotten'
                            r.link = review.get('link')
                            r.text = HTTP.Request(server_url + '/translate',
                                                  values=dict(text=review.text, app_name='k_movie', hash=word_hash(review.text),apikey=Prefs['apikey']))

            # IMDb 기반으로 IVA extras 잡아준다
            if Prefs['if_no_trailer_in_daum'] in ['Always', 'When Nothing in daum'] and movie is not None:
                going_to_down = True
                if Prefs['if_no_trailer_in_daum'] == 'When Nothing in daum' and len(extras) > 0: going_to_down = False
                if going_to_down and imdb_code not in [None, False, '']:
                    Log('Find Trailers in Default Plex Agent')
                    TYPE_MAP = {'primary_trailer': TrailerObject,
                                'trailer': TrailerObject,
                                'interview': InterviewObject,
                                'behind_the_scenes': BehindTheScenesObject,
                                'scene_or_sample': SceneOrSampleObject}
                    xml = movie
                    extras = []
                    media_title = None
                    lang_code = 'en'
                    for extra in xml.xpath('//extra'):
                        avail = Datetime.ParseDate(extra.get('originally_available_at'))
                        lang_code = -1
                        subtitle_lang_code = int(extra.get('subtitle_lang_code')) if extra.get('subtitle_lang_code') else -1
                        spoken_lang = IVA_LANGUAGES.get(lang_code)
                        subtitle_lang = IVA_LANGUAGES.get(subtitle_lang_code)
                        include = True
                        # Exclude non-primary trailers and scenes.
                        extra_type = 'primary_trailer' if extra.get('primary') == 'true' else extra.get('type')
                        if extra_type == 'trailer' or extra_type == 'scene_or_sample':
                            include = False

                        # Don't include anything besides trailers if pref is set.
                        if extra_type != 'primary_trailer' and Prefs['only_trailers']:
                            include = False

                        if include:
                            bitrates = extra.get('bitrates') or ''
                            duration = int(extra.get('duration') or 0)
                            adaptive = 1 if extra.get('adaptive') == 'true' else 0
                            dts = 1 if extra.get('dts') == 'true' else 0

                            # Remember the title if this is the primary trailer.
                            if extra_type == 'primary_trailer':
                                media_title = extra.get('title')

                            # Add the extra.
                            if extra_type in TYPE_MAP:
                                extras.append({'type': extra_type,
                                               'lang': spoken_lang,
                                               'extra': TYPE_MAP[extra_type](url=IVA_ASSET_URL % (
                                                   extra.get('iva_id'), spoken_lang, bitrates, duration, adaptive, dts),
                                                                             title=extra.get('title'),
                                                                             year=avail.year,
                                                                             originally_available_at=avail,
                                                                             thumb=extra.get('thumb') or '')})
                            else:
                                Log('Skipping extra %s because type %s was not recognized.' % (
                                extra.get('iva_id'), extra_type))

                    # Sort the extras, making sure the primary trailer is first.
                    # extras.sort(key=lambda e: TYPE_ORDER.index(e['type']))

                    # Clean up the found extras.

                    extras = [scrub_extra(extra, media_title) for extra in extras]

                    # Add them in the right order to the metadata.extras list.
                    for extra in extras:
                        metadata.extras.add(extra['extra'])

                    Log('Added %d of %d extras.' % (len(metadata.extras), len(xml.xpath('//extra'))))
    # summary 없는 경우
    if Prefs['alternative_story'] != "":
        alternative_story_flow = Prefs['alternative_story'].split(',') # "tmdb,watcha,naver,imdb"
        for index , item in enumerate(alternative_story_flow):
            Log('metadata.summary : %s' % metadata.summary)
            #Log('metadata.summary : %s' % metadata.summary)
            if metadata.summary == None: # 잡히지 않음 , 다음은?
                if item == 'tmdb':
                    try:
                        Log('Summary Alternative : %s' % item)
                        if tmdb_json_ko['overview'] != "":
                            metadata.summary = tmdb_json_ko['overview']
                        else:
                            metadata.summary = HTTP.Request(server_url + '/translate', values=dict(text=tmdb_json_en['overview'], hash=word_hash(tmdb_json_en['overview']), app_name='k_movie', apikey=Prefs['apikey']))
                        if metadata.summary not in ['', None] and len(metadata.summary) > 3:
                            break
                    except:
                        Log("Failed")
                if item == 'watcha':
                    try:
                        Log('Summary Alternative : %s' % item)
                        metadata.summary = w2['API_INFO']['description']
                        if metadata.summary not in ['' , None] and len(metadata.summary) > 3:
                            break
                    except:
                        Log("Failed")
                if item == 'naver':
                    try:
                        Log('Summary Alternative : %s' % item)
                        tmp = naver.overview(naver_result['code'])
                        if tmp not in ['', None] and len(tmp) > 3:
                            metadata.summary = tmp
                            break
                    except:
                        Log("Failed")
                if item == 'imdb':
                    Log('Summary Alternative : %s' % item)
                    try:
                        Log('imdb_overview in alternative : %s' % imdb_overview)
                        tr_ko = HTTP.Request(server_url + '/translate', values=dict(text=imdb_overview, app_name='k_movie', hash=word_hash(imdb_overview) ,apikey=Prefs['apikey']))
                        metadata.summary = tr_ko
                        if metadata.summary not in ['', None] and len(metadata.summary) > 3:
                            break
                    except:
                        Log("Failed")

            elif is_korean(metadata.summary) == False:
                tr_ko = HTTP.Request(server_url + '/translate',
                                     values=dict(text=metadata.summary, app_name='k_movie',  hash=word_hash(metadata.summary) ,apikey=Prefs['apikey']))
                metadata.summary = tr_ko
                Log("Translated : %s " % metadata.summary)

    # 포토
    photo_flow = Prefs['poster_prefer'].split(',')
    Log(photo_flow)
    for photo_site in photo_flow:
        if photo_site == 'daum' and metadata_id.count('tmdb') == 0 and metadata_id.count('watcha') == 0:
            # (3) from photo page
            url_tmpl = DAUM_MOVIE_PHOTO
            data = JSON.ObjectFromURL(url=url_tmpl % metadata_id)
            max_poster = int(Prefs['max_num_posters'])
            max_art = int(Prefs['max_num_arts'])
            idx_poster = 0
            idx_art = 0
            for item in data['data']:
                if item['photoCategory'] == '1' and idx_poster < max_poster:
                    art_url = item['fullname']
                    if not art_url: continue
                    # art_url = RE_PHOTO_SIZE.sub("/image/", art_url)
                    idx_poster += 1
                    try:
                        metadata.posters[art_url] = Proxy.Preview(HTTP.Request(item['thumbnail']), sort_order=idx_poster)
                    except:
                        pass
                elif item['photoCategory'] in ['2', '50'] and idx_art < max_art:
                    art_url = item['fullname']
                    if not art_url: continue
                    # art_url = RE_PHOTO_SIZE.sub("/image/", art_url)
                    idx_art += 1
                    try:
                        metadata.art[art_url] = Proxy.Preview(HTTP.Request(item['thumbnail']), sort_order=idx_art)
                    except:
                        pass
            Log.Debug('Total %d posters, %d artworks' % (idx_poster, idx_art))
            if idx_poster == 0:
                if poster_url:
                    poster = HTTP.Request(poster_url)
                    try:
                        metadata.posters[poster_url] = Proxy.Media(poster)
                    except:
                        pass
            if not Prefs['poster_save']:
                break

        if photo_site == 'watcha':
            try:
                ps = w2['API_INFO']['poster']
                try:
                    metadata.posters[ps['original']] = Proxy.Preview(HTTP.Request(ps['original']), sort_order=0)
                    if not Prefs['poster_save']:
                        break
                except:
                    pass
                try:
                    metadata.posters[ps['large']] = Proxy.Preview(HTTP.Request(ps['large']), sort_order=0)
                    if not Prefs['poster_save']:
                        break
                except:
                    pass
            except:
                pass
        if photo_site == 'tmdb':
            Log('Photo : %s' % tmdb_json_en)
            try:
                try:
                    tmp_url = 'https://image.tmdb.org/t/p/w500' + tmdb_json_en['poster_path'].encode('utf-8')
                    metadata.posters[tmp_url] = Proxy.Preview(HTTP.Request(tmp_url), sort_order=0)
                    if not Prefs['poster_save']:
                        break
                except:
                    pass
            except:
                pass
        if photo_site == 'imdb':
            try:
                if imdb_posters :
                    Log('Photo : %s' % imdb_posters)
                    try:
                        try:
                            tmp_url = imdb_posters
                            metadata.posters[tmp_url] = Proxy.Preview(HTTP.Request(tmp_url), sort_order=0)
                            if not Prefs['poster_save']:
                                break
                        except:
                            pass
                    except:
                        pass
            except:pass


from korean import koreans
def is_korean(w):
  if w == None or len(w) == 0: return False
  for index in range(len(w)):
    if w[index] in koreans:
      return True
  return False

def searchMovieTMDb(results, media, lang, manual=False):
    movie_year = media.year
    movie_name = media.name #unicodedata.normalize('NFKC', unicode(media.name)).strip()
    match = Regex(r'^(?P<name>.*?)[\s\.\[\_\(](?P<year>\d{4})').match(movie_name)

    if match:
        movie_name = match.group('name').replace('.', ' ').strip()
        movie_name = re.sub(r'\[(.*?)\]', '', movie_name)
        movie_year = match.group('year')
    Log('TMDb Searching Start | Movie name : %s | Movie year : %s' % (str(movie_name) , str(movie_year)))
    if movie_year == None : movie_year = ""
    tmdb_json = tmdb.tmdb().search_list(name=movie_name, year=movie_year , lang='ko' , enc=False)
    if len(tmdb_json) == 0 : tmdb_json = tmdb.tmdb().search_list(name=movie_name, year=movie_year , lang='en' , enc=False)
    if len(tmdb_json) > 0 :
        for index , item in enumerate(tmdb_json[:10]):
            Log('enumerate course : %s '% str(item))
            try:
                tmp_year = int(item['release_date'][:4])
            except ValueError:
                tmp_year = None
            except KeyError:
                tmp_year = None
            results.Append(MetadataSearchResult(id='tmdb_'+str(item['id']), name='TMDb  :  '+item['title'], year=tmp_year, score=(85 - (index * 5)), lang=lang))
    return tmdb_json

def word_hash(word):
    word = str(word)
    text = word.encode('utf-8')
    h = hashlib.sha256()
    h.update(text)
    return str(h.hexdigest())

######################################################################################################
def checkToken(proxy, token):

  try:
    proxyCheck = proxy.NoOperation(token)

    if proxyCheck['status'] == '200 OK':
      Log('Valid token.')
      return True
    else:
      Log('Invalid Token.')
      return False

  except:
    Log('Error occured when checking token.')
    return False

def proxyLogin(proxy, username, password):

  token = proxy.LogIn(username, password, 'en', OS_PLEX_USERAGENT)['token']

  if checkToken(proxy, token):
    Log('Successful login.')
    return (True, token)
  else:
    Log('Unsuccessful login.')
    return (False, '')


def opensubtitlesProxy():
  proxy = XMLRPC.Proxy(OS_API)
  username = 'ohhyeon'
  password = '(ohhyeon3136)'

  # Check for missing token
  if 'proxyToken' not in Dict:
    # Perform login
    Log('No valid token in Dict.')
    (success, token) = proxyLogin(proxy, username, password)

    if success:
      Dict['proxyToken'] = token
      return (proxy, token)
    else:
      Dict['proxyToken'] = ''
      return (proxy, '')

  else:
    # Token already exists, check if it's still valid
    Log('Existing token found. Revalidating.')
    if Dict['proxyToken'] != '' and checkToken(proxy, Dict['proxyToken']):
      return (proxy, Dict['proxyToken'])
    else:
      # Invalid token. Re-authenticate.
      (success, token) = proxyLogin(proxy, username, password)

      if success:
        Dict['proxyToken'] = token
        return (proxy, token)
      else:
        return (proxy, '')

def statistics_search(results, media, lang, manual=False):
    part = media.items[0].parts[0]
    fullpath = part.file
    path = os.path.dirname(fullpath)
    dirname = os.path.split(path)[1]
    filename = os.path.split(fullpath)[1]
    os_hash = None
    #(proxy, token) = opensubtitlesProxy()
    for i in media.items:
        for part in i.parts:
            os_hash = part.openSubtitleHash
            #test = subtitleResponse = proxy.SearchSubtitles(token,[{'sublanguageid':'eng', 'moviehash':part.openSubtitleHash, 'moviebytesize':str(part.size)}])
            #Log('test : %s'  % test)
    tmp = dict(
                     filename=filename, filename_hash=word_hash(filename), os_hash=os_hash,
                     dirname=dirname, dirname_hash=word_hash(dirname),
                     metadata_title='', metadata_year='',
                     metadata_id='searching',
                     app_name='k_movie', apikey=Prefs['apikey'] , cacheTime=0)
    Log(tmp)
    Log("★filename : %s | os_hash : %s" % (filename , os_hash) )
    res = JSON.ObjectFromURL(server_url + '/movie_stat',
                 values=tmp
                 )
    Log(res)
    res = res['result']
    if res == [] : return
    showTitle = '%s인의 선택 | %s' %(res['manual_count'] , res['metadata_title']) # %s인의 선택 |
    Log('showTitle : %s' % showTitle)
    try:tmp_Year = int(res['metadata_year'])
    except: tmp_Year=""
    results.Append(MetadataSearchResult(id=res['metadata_id'], name=showTitle, year=tmp_Year, score=90, lang=lang))


import os
class K_MovieAgent(Agent.Movies):
    name = "K Movie"
    languages = [Locale.Language.Korean]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.xbmcnfo', 'com.plexapp.agents.opensubtitles', 'com.plexapp.agents.themoviedb']
    contributes_to = ['com.plexapp.agents.xbmcnfo' , 'com.plexapp.agents.themoviedb']
    if Prefs['fallback_agent'] == 'imdb':
        fallback_agent = 'com.plexapp.agents.imdb'
    if Prefs['fallback_agent'] == 'tmdb':
        fallback_agent = 'com.plexapp.agents.themoviedb'

    def search(self, results, media, lang, manual=False):
        if manual:Log('★ MANUAL')
        if Prefs['data_backup'] in ['Only_download' , 'Download_First_After_Searching']:
            part = media.items[0].parts[0]
            fullpath = part.file
            path = os.path.dirname(fullpath)
            dirname = os.path.split(path)[1]
            filename = os.path.split(fullpath)[1]
            Log('media_load : %s' % filename)
            try:
                tmp = JSON.ObjectFromURL(server_url + '/backup_movie_metadata',
                         values=dict(
                             filename=filename, filename_hash=word_hash(filename),
                             protocol='load',
                             app_name='k_movie', apikey=Prefs['apikey'])
                         ) # result :   {'filename' : filename , 'filename_hash' : filename_hash , 'metadata_id' : metadata_id , 'unixtime' : time.time() , 'metadata_title' : metadata_title , 'metadata_year' : metadata_year}
            except:
                tmp= []
            if 'result' in tmp:
                tmp = tmp['result']
                if tmp['metadata_id'] != "None":
                    Log(tmp)
                    results.Append(MetadataSearchResult(id=tmp['metadata_id'], name=tmp['metadata_title'], year=tmp['metadata_year'], score=100, lang=lang))
            if Prefs['data_backup'] == "Only_download":
                return # End Load시 없는 건 없다해야하나.......
        # 메타데이터 새로고침은 어떻게 고치지?
        statistics_search(results, media, lang, manual=manual) # Prefs 추가할것
        #except:pass

        self.filename = self.dirname = None
        self.media_id = False # 스캐닝 도중을 거르기 위해서
        if media.filename != None:
            tmp = basename = os.path.basename(media.filename)
            Log(tmp)
            #convert_text = unicodedata.normalize('NFKD', media.filename).encode('ascii', 'ignore')
            part = media.items[0].parts[0]
            fullpath = part.file
            path = os.path.dirname(fullpath)
            dirname = os.path.split(path)[1]
            filename = os.path.split(fullpath)[1]
            Log('filename : %s | %s' % (dirname , filename) )
        result = searchMovie(results, media, lang, manual=manual)
        Log('DAUM RESULT : %s' % result)
        #if result == None:
        result = searchMovieTMDb(results, media, lang , manual=manual)
        Log('TMDb RESULT : %s' % result)
        self.manual = self.title = self.year = self.filename = self.media_id =False
        watcha.watcha_find(results, media, lang, manual=manual)
        if manual:
            self.manual = True
            part = media.items[0].parts[0]
            fullpath = part.file
            path = os.path.dirname(fullpath)
            dirname = os.path.split(path)[1]
            filename = os.path.split(fullpath)[1]
            self.dirname = dirname
            self.filename = filename
            self.title = media.title
            self.year = media.year
        return result

    def update(self, metadata, media, lang , force=False): # 그냥 메타데이터 리프래싱인지 확인해본다.
        Log.Info("in update ID = %s" % metadata.id)
        if Prefs['data_backup'] == 'Only_backup':
            part = media.items[0].parts[0]
            fullpath = part.file
            path = os.path.dirname(fullpath)
            dirname = os.path.split(path)[1]
            filename = os.path.split(fullpath)[1]
            Log('media_backup : %s' % filename)
            HTTP.Request(server_url + '/backup_movie_metadata',
                         values=dict(
                             filename=filename, filename_hash=word_hash(filename),
                             metadata_title=metadata.title, metadata_year=str(metadata.year),
                             metadata_id=metadata.id,
                             protocol='save',
                             app_name='k_movie', apikey=Prefs['apikey'])
                         )
        refreshing = False
        try:
            if metadata.title == self.title:
                Log('Ref, 1')
                refreshing = True # 단순 리프레싱일 확률이 높다. # 그리고, 계속해서 같은 메타데이터를 선택하는 경우도 거를 수 있다.
        except:
            Log('Ref, 2')
            refreshing = True # 이 경우는 에이전트가 다시 실행된 경우..
        if metadata.id.lower().count('tmdb') > 0 :
            Log('TMDB Update')
        updateDaumMovie('movie', media, metadata , lang)
        if Prefs['sort_title_korean']:
            if metadata.title:
                metadata.title_sort = self.get_sorttitle(metadata.title)
            else:
                metadata.title_sort = self.get_sorttitle(media.title)
        try:
            Log('--check--')
            Log(self.manual)
            Log(metadata.title)
            Log(refreshing)
            if self.manual and metadata.title and not refreshing: # + 1 파트
                Log('★ Manual +1 Append')
                part = media.items[0].parts[0]
                fullpath = part.file
                path = os.path.dirname(fullpath)
                dirname = os.path.split(path)[1]
                filename = os.path.split(fullpath)[1]
                Log('self.filename : %s' % filename)
                Log('self.dirname : %s' % dirname)
                Log('metadata.title : %s' % metadata.title)
                Log('metadata.year : %s' % metadata.year)
                Log('metadata.id : %s' % metadata.id)
                HTTP.Request(server_url + '/movie_stat',
                             values=dict(
                                 filename=filename, filename_hash = word_hash(filename),
                                 dirname = dirname, dirname_hash = word_hash(dirname),
                                 metadata_title = metadata.title , metadata_year = str(metadata.year),
                                 metadata_id = metadata.id,
                                 app_name='k_movie', apikey=Prefs['apikey'])
                             )
        except:
            pass
        # 다음(next) 영화의 메타데이터 새로 고침을 방지해야
        self.manual = False


    def get_sorttitle(self, title):
        title = title.replace('TMDb : ','')
        tmp = re.compile('\d인의 선택 | ')
        title = re.sub(tmp, '',title).strip()

        # Plex Media Server는 Python 2 기반이라 유니코드 관련으로 문제가 좀 있음.
        # 해결책을 찾기 전까진 아래와 같이 하드코딩 예정
        FIRST_LETTERS = [ "가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하" ]
        CONSONANTS = [ "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ" ]
        LAST_LETTER = "힣"

        # 본래 영화제목 첫글자
        first = title.decode("utf-8")[0]

        # 제목이 한국어로 시작하는지 체크
        if first >= FIRST_LETTERS[0] and first <= LAST_LETTER:
            for i in range(0, 13):
                if i < 13:
                    if first < FIRST_LETTERS[i+1]: return CONSONANTS[i] + title
            return CONSONANTS[13] + title
        else:
            return title
