#local media assets agent
import os, string, re, unicodedata
  
extras_list = []

def FindShowDir(dirs):
  final_dirs = {}
  for dir in dirs:
    final_dirs[dir] = True
    try:
      parent = os.path.split(dir)[0]
      final_dirs[parent] = True
    except:pass
  
  if final_dirs.has_key(''):
    del final_dirs['']
  return final_dirs
  

def AddExtra(extras, extra_type, extra_title, extra_path):
  if extra_path in extras_list:
    Log('Extra %s has already been added', extra_title)

  else:
    sort_title = extra_title
    image = ''
    IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'tiff', 'gif', 'jp2']
    (file,ext) = os.path.splitext(extra_path)
    for img in IMAGE_EXTS:
      thumbnail = file+"."+img
      if os.path.isfile(thumbnail):
        Log('inline thumbnail found for file %s', extra_path)
        image = "file://"+thumbnail
        break
    #if image_data is not None: #unfortunately no support for data uris; so can't think of a way to allow images embedded in mp4
      #image = "data:image/jpeg;base64,"+image_data.encode('base64').replace('\n','')

    extra_path = unicodedata.normalize('NFC',unicode(extra_path)) # This works for me, but the full function def unicodize(s) in helpers.py in the Plex Local Media agent may be needed for servers on other platforms - to be confirmed
    Log('Found %s extra: %s' % (extra_type, extra_title))
    extras.append({'type' : extra_type, 'title' : extra_title, 'sort_title' : sort_title, 'file' : extra_path, 'thumb' : image})
    extras_list.append(extra_path)
  
  
def FindExtras(media_title, metadata, paths, basename=None):
  # Do a quick check to make sure we've got the extra types available in this framework version,
  # and that the server is new enough to support them.
  #
  
  try: 
    t = InterviewObject()
    if Util.VersionAtLeast(Platform.ServerVersion, 0,9,9,13):
      find_extras = True
    else:
      find_extras = False
      Log('Not adding extras: Server v0.9.9.13+ required')
  except NameError, e:
    Log('Not adding extras: Framework v2.5.0+ required')
    find_extras = False
    
  if find_extras:
    extra_type_map = {'trailer' : TrailerObject,
                'deleted' : DeletedSceneObject,
                'behindthescenes' : BehindTheScenesObject,
                'interview' : InterviewObject,
                'scene' : SceneOrSampleObject,
                'featurette' : FeaturetteObject,
                'short' : ShortObject,
                'other' : OtherObject,
                'extra' : OtherObject}
    VIDEO_EXTS          = ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'm2t', 'm2ts', 'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nsv', 'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob', 'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'webm']
    for path in paths:
      #path = helpers.unicodize(path) 
      extras = []
      re_strip = Regex('[\W ]+')
      
      Log('Looking for local extras in path: '+ path)      
      for folder in os.listdir(path):
        d = os.path.join(path,folder)
        if(os.path.isdir(d)):
          for key in extra_type_map.keys():
            if re_strip.sub('', folder.lower()).startswith(key):
              for f in os.listdir(d):
                Log(f)
                (fn, ext) = os.path.splitext(f)
                if not fn.startswith('.') and ext[1:].lower() in VIDEO_EXTS and (not basename or os.path.basename(path) == basename):                  
                  AddExtra(extras, key, fn, os.path.join(d, f))

      # Look for filenames following the "-extra" convention and a couple of other special cases.
      for f in os.listdir(path):
        (fn, ext) = os.path.splitext(f)

        # Files named exactly 'trailer'.
        if (fn.lower() == 'trailer') and not fn.startswith('.') and ext[1:] in VIDEO_EXTS and not basename:
          Log('Found trailer extra, renaming with title: ' + media_title)
          AddExtra(extras, key, media_title, os.path.join(path, f))

        # Files following the "-extra" convention.
        else:
          for key in extra_type_map.keys():
            if not fn.startswith('.') and fn.endswith('-' + key) and ext[1:] in VIDEO_EXTS and ((not basename) or fn.startswith(basename) or os.path.basename(path) == basename):
              title = '-'.join(fn.split('-')[:-1])
              if(basename and not (title == basename) and title.startswith(basename)):
                title = "".join(title.rsplit(basename))
                # remove any leading spaces or dashes
                while(title[0] in (' ','-')):
                  title = title[1:]
              AddExtra(extras, key, title, os.path.join(path, f))
  
      # Make sure extras are sorted alphabetically and by type.
      type_order = ['trailer', 'behindthescenes', 'interview', 'deleted', 'scene', 'sample', 'featurette', 'short', 'other', 'extra']
      extras.sort(key=lambda e: e['sort_title'])
      extras.sort(key=lambda e: type_order.index(e['type']))
      
      for extra in extras:
        metadata.extras.add(extra_type_map[extra['type']](title=extra['title'],file=extra['file'], thumb=extra['thumb']))
        Log(extra['file'])
      
      Log('added %d extras' % len(metadata.extras))
      Log('finished')


def update(metadata, media):
  #make sure the extras list is fresh each time
  del extras_list[:]
  dirs = {}
  for s in media.seasons:
    #Log('Current Season %s', s)
    metadata.seasons[s].index = int(s)
    for e in media.seasons[s].episodes:
      episodeMetadata = metadata.seasons[s].episodes[e]
      episodeMedia = media.seasons[s].episodes[e].items[0]
      directory = os.path.dirname(episodeMedia.parts[0].file)
      dirs[directory] = True
      
  Log('directories are: %s', string.join(dirs, ", "))
  
  showfolder = False;
  season_names = ['season','specials'] #default plex season folder names
  for d in dirs:
    if os.path.basename(d).lower().startswith(tuple(season_names)):
      Log("%s is a Season Folder", os.path.basename(d))
    else:
      Log("Folder name, %s doesn't include \"Season\", \"Specials\" (or any alternative specified in settings) so it must be a Show Folder", os.path.basename(d))
      showfolder = True;

  if(showfolder == False):
    try: dirs = FindShowDir(dirs)
    except: dirs = []
  
  Log('directory to search for extras: %s', string.join(dirs, ", "))

  FindExtras(media.title, metadata, dirs)