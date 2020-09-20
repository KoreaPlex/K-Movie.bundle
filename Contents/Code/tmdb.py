import re
try:
    import requests
    plex = False
except:
    import urllib, unicodedata, traceback, re
    plex = True

from korean import koreans
def is_korean(w):
  if w == None or len(w) == 0: return False
  for index in range(len(w)):
    if w[index] in koreans:
      return True
  return False


#tmdb_meta(metadata_id = code.replace('tmdb_','').strip(), lang = 'ko', existing_metadata = metadata, force=False , daum_to_tmdb = True)
# {u'poster_path': u'/bhNHCeJDFDaB00A46AoCw2mggdE.jpg', u'production_countries': [{u'iso_3166_1': u'NL', u'name': u'Netherlands'}, {u'iso_3166_1': u'PL', u'name': u'Poland'}, {u'iso_3166_1': u'UA', u'name': u'Ukraine'}, {u'iso_3166_1': u'GB', u'name': u'United Kingdom'}, {u'iso_3166_1': u'US', u'name': u'United States of America'}], u'revenue': 0, u'overview': u'\uc6b0\ud06c\ub77c\uc774\ub098 \ud0a4\uc608\ud504\uc5d0\uc11c \ube44\ubc00 \uc784\ubb34\ub97c \uc218\ud589\ud558\ub358 \uc601\uad6d MI6 \uc694\uc6d0 \ub9c8\ud2f4\uc740, \uc2e4\uc218\ub85c \uc0ac\ub791\ud558\ub294 \uc5ec\uc778 \uc62c\uac00\ub97c \ucd1d\uc73c\ub85c \uc8fd\uc774\uac8c \ub41c\ub2e4.  MI6\uc5d0\uc11c \ub098\uc628 \ub4a4 \ub538 \ub9ac\uc2a4\uc640 \ud568\uaed8 \uc601\uad6d \ub7f0\ub358\uc5d0\uc11c \uaca9\ud22c\uc640 \uc220\uc9d1 \ubcf4\ub514\uac00\ub4dc\ub97c \ud558\uba70 \uc0dd\ud65c\uc744 \uc601\uc704\ud558\ub358 \ub9c8\ud2f4\uc740 12\ub144\uc774 \uc9c0\ub09c \uc9c0\uae08\uae4c\uc9c0 \uc62c\uac00\uc758 \ud658\uc601\uc...
def tmdb_meta(metadata_id , lang = 'ko' , metadata = None, force = False, daum_to_tmdb = False):
    Log('TMDB Metadata Inserting.....')
    base_url = 'https://api.themoviedb.org/3/movie/' + str(metadata_id) + '?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR'
    json_kr = j = JSON.ObjectFromURL(base_url)
    json_en = JSON.ObjectFromURL('https://api.themoviedb.org/3/movie/' + str(metadata_id) + '?api_key=b2f505af2cb75d692419696af851e517&language=en-US')
    if is_korean(j['title']):
        metadata.title = j['title']
    else:
        metadata.title = json_en['title']

    try:
        metadata.year = int(j['release_date'][:4])
    except:
        try:metadata.year = int(json_en['release_date'][:4])
        except:pass
    Log(j['overview'])
    if j['overview']:
        metadata.summary = j['overview']
    else:
        metadata.summary = HTTP.Request(Prefs['server_url'] + '/translate',
                             values=dict(text=json_en['overview'], app_name='k_movie', apikey=Prefs['apikey']))
        Log(metadata.summary)
    metadata.id = 'tmdb_'+metadata_id
    try:metadata.original_title = j['original_title']
    except:pass
    try:poster_path = 'https://image.tmdb.org/t/p/w500' + j['poster_path']
    except:poster_path = ""
    try:metadata.posters[poster_path] = Proxy.Preview(HTTP.Request(poster_path), sort_order=0)
    except:pass
    try:art_path = 'https://image.tmdb.org/t/p/original' + j['backdrop_path']
    except:art_path = ""
    try:metadata.art[art_path] = Proxy.Preview(HTTP.Request(art_path), sort_order=0)
    except:pass
    try:imdb_code = j['imdb_id']
    except:imdb_code=None

    metadata.genres.clear()
    metadata.countries.clear()

    for genre in j['genres']:
        metadata.genres.add(genre['name'].encode('utf-8').strip())

    for c in j['production_countries']:
        metadata.countries.add(c['name'].encode('utf-8').strip())

    tmp = j['release_date']
    match = re.compile(r'\d{4}\-\d{2}\-\d{2}').match(tmp)
    if match:
        metadata.originally_available_at = Datetime.ParseDate(match.group(0).replace('-', '')).date()

    metadata.duration = j['runtime']
    #metadata.content_rating = str(j['vote_average'])
    metadata.rating = float(j['vote_average'])
    Log(imdb_code)
    if Prefs['imdb_rating_text_and_collection'] != "" and imdb_code != None and imdb_code.count('tt') > 0:
        imdb_url = 'https://www.imdb.com/title/%s' % imdb_code
        root = HTML.ElementFromURL(imdb_url)
        imdb_rating = root.xpath('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/div[1]/strong/span')[0].text_content()
        metadata.rating_image = 'imdb://image.rating'
        metadata.rating = float(imdb_rating)
        tmp = Prefs['imdb_rating_text_and_collection']
        tmp = tmp.split(',')
        tmp = [item.split('[') for item in tmp]
        score = float(imdb_rating)
        for item in tmp:
            if float(item[0].split('~')[0]) <= score <= float(item[0].split('~')[1]):
                metadata.collections.add('🟨 ' + item[1].replace(']', '').strip())
                break


    base_url_for_credit = "https://api.themoviedb.org/3/movie/"+metadata_id+"/credits?api_key=b2f505af2cb75d692419696af851e517"
    jc = JSON.ObjectFromURL(base_url_for_credit)
    metadata.roles.clear()
    Log(jc)
    for role in jc['cast']:
        if 'department' in role : continue
        meta_role = metadata.roles.new()
        if 'character' in role:
            try:
                tr_ko = HTTP.Request(Prefs['server_url'] + '/translate',
                                     values=dict(text=role['character'], app_name='k_movie', apikey=Prefs['apikey']))
                meta_role.role = tr_ko
            except:
                pass
        if 'name' in role:
            tr_ko = HTTP.Request(Prefs['server_url'] + '/translate',
                                 values=dict(text=role['name'], app_name='k_movie', apikey=Prefs['apikey']))
            meta_role.name = tr_ko
        if 'profile_path' in role:
            try:meta_role.photo = 'https://image.tmdb.org/t/p/w185' + role['profile_path']
            except:pass


    metadata.directors.clear()
    for role in jc['crew']:
        if 'job' in role and 'direct' in role['job'].lower():
            Log('director : %s' %(role))
            meta_director = metadata.directors.new()
            meta_director.name = HTTP.Request(Prefs['server_url'] + '/translate',
                                 values=dict(text=role['name'], app_name='k_movie', apikey=Prefs['apikey']))
            try:meta_director.photo = 'https://image.tmdb.org/t/p/w185' + role['profile_path']
            except:pass

    metadata.producers.clear()
    for role in jc['crew']:
        if 'job' not in role: continue
        if 'produc' in role['department'].lower():
            meta_producer = metadata.producers.new()
            meta_producer.name = HTTP.Request(Prefs['server_url'] + '/translate',
                                 values=dict(text=role['name'], app_name='k_movie', apikey=Prefs['apikey']))
            try:meta_producer.photo = 'https://image.tmdb.org/t/p/w185' + role['profile_path']
            except:pass

    metadata.writers.clear()
    for role in jc['crew']:
        if 'role' not in role: continue
        if 'writ' in role['department'].lower():
            meta_writer = metadata.writers.new()
            meta_writer.name = HTTP.Request(Prefs['server_url'] + '/translate',
                                 values=dict(text=role['name'], app_name='k_movie', apikey=Prefs['apikey']))
            try:meta_writer.photo = 'https://image.tmdb.org/t/p/w185' + role['profile_path']
            except:pass

    return j


def title_renamer_for_tmdb(text):
    text = text.replace('~' , ' ')
    text = text.replace('～' , ' ')
    return text.strip()

import unicodedata
from movie import title_renamer
class tmdb:
    def search_list(self , name, year, lang='en' , enc=True):
        Log('name : %s | type : %s' % (name , type(name)))
        #name = unicodedata.normalize('NFKD' , name).encode('utf-8' , 'ignore')
        Log('name : %s | type : %s' % (title_renamer_for_tmdb(title_renamer(name)), type(name)))
        name = urllib.quote(title_renamer_for_tmdb(title_renamer(name)))
        Log(name)
        if lang == "en":
            base_url = u'https://api.themoviedb.org/3/search/movie?api_key=b2f505af2cb75d692419696af851e517&language=en-US&query=' + name + u'&page=1&include_adult=true&year=' + str(
                year)
            if plex == False:
                res = requests.get(base_url)
                j = res.json()['results']
            else:
                j = JSON.ObjectFromURL(base_url)['results']
        elif lang == 'ko':
            base_url = 'https://api.themoviedb.org/3/search/movie?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR&query=' + name + '&page=1&include_adult=true&year=' + str(
                year)
            Log('Base Url : %s' % base_url)
            if plex == False:
                res = requests.get(base_url)
                j = res.json()['results']
            else:
                j = JSON.ObjectFromURL(base_url)['results']
        Log(j)
        return j

    def search(self, name, year, lang='en'):
        name = urllib.quote(name)
        if lang == "en":
            base_url = 'https://api.themoviedb.org/3/search/movie?api_key=b2f505af2cb75d692419696af851e517&language=en-US&query='+name+'&page=1&include_adult=true&year='+str(year)
            if plex == False:
                res = requests.get(base_url)
                j = res.json()['results'][0]
            else:
                j = JSON.ObjectFromURL(base_url)['results'][0]
        elif lang == 'ko':
            base_url = 'https://api.themoviedb.org/3/search/movie?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR&query=' + name + '&page=1&include_adult=true&year=' + str(year)
            if plex == False:
                res = requests.get(base_url)
                j = res.json()['results'][0]
            else:
                j = JSON.ObjectFromURL(base_url)['results'][0]

        c = self.find_in_tmdb_Collection(movie=j)
        return j , c

    def find_in_tmdb_Collection(self, movie):
        ID = movie['id']
        base_url = 'https://api.themoviedb.org/3/movie/' + str(ID) + '?api_key=b2f505af2cb75d692419696af851e517&language=en-US'
        if plex == False:
            res = requests.get(base_url)
            j = res.json()
        else:
            j = JSON.ObjectFromURL(base_url)
        collectionID = ""
        try:
            collectionID = j['belongs_to_collection']['id']
        except:
            pass
        if collectionID != "":
            base_url = 'https://api.themoviedb.org/3/collection/' + str(collectionID) + '?api_key=b2f505af2cb75d692419696af851e517&language=ko-KR'
            if plex == False:
                coll_res = requests.get(base_url)
                jc = coll_res.json()
            else:
                jc = JSON.ObjectFromURL(base_url)
        try:
            return jc
        except:
            return ""

if __name__ == '__main__':
    a , b= tmdb().search('deadpool 2' , year=2018)
    a