# coding: utf-8

import sys, requests, json, urllib
import os

# 转换视频id
def convert2Int(v_id):
  return int(v_id.split('_')[0])

# 记录已经处理的最大视频id
def recordMaxId(name, v_max_id):
  file = os.path.abspath('../data/' + name + '/downloaded_maxid')
  with open(file, 'w') as f:
    f.write(v_max_id)

# 获取已经处理的最大视频id
def getMaxId(name):
  file = os.path.abspath('../data/' + name + '/downloaded_maxid')
  if os.path.exists(file):
    with open(file, 'r') as f:
      return convert2Int(f.read())
  return 0

# 根据已处理的最大视频id 获得最新的video list
def getVideoList(name, max_id_int):
  list = []

  basic_url = 'http://instagram.com/' + urllib.quote_plus(name) + '/media'

  print basic_url
  r = requests.get(basic_url)

  if not r.ok:
    return False

  re = json.loads(r.text)
  if len(re['items']) == 0:
    return False
  else:
    v_max_id = re['items'][0]['id']

  for item in re['items']:
    if convert2Int(item['id']) <= max_id_int:
      return v_max_id, list

    if item['type'] == 'video':
      if item['caption'] is not None:
        desc = item['caption']['text']
      else:
        desc = ''
      list.append({'desc': desc, 'id': item['id'], 'url': item['alt_media_url'], 'ts': item['created_time']})

  is_more = re['more_available']
  if is_more:
    max_id = re['items'][-1]['id']

  while (is_more):
    url = basic_url + '?max_id=' + max_id
    print url
    r = requests.get(url)
    if not r.ok:
      return False
    
    re = json.loads(r.text)
    for item in re['items']:
      if convert2Int(item['id']) <= max_id_int:
        return v_max_id, list

      if item['type'] == 'video':
        if item['caption'] is not None:
          desc = item['caption']['text']
        else:
          desc = ''
        list.append({'desc': desc, 'id': item['id'], 'url': item['alt_media_url'], 'ts': item['created_time']})

    max_id = re['items'][-1]['id']
    is_more = re['more_available']

  return v_max_id, list

# 创建目录
def createDirectory(name):
  directory = os.path.abspath('../data/' + name)
  if not os.path.exists(directory):
    os.makedirs(directory)

# 下载视频
def downloadVideo(name, url, v_id):
  file = os.path.abspath('../data/' + name + '/' + v_id + '.mp4')
  if os.path.exists(file):
    return False

  f = open(file, 'wb')
  r = requests.get(url)
  if r.ok:
    f.write(r.content)

# 记录视频list
def recordVideo(name, list):
  file = os.path.abspath('../data/' + name + '/videos.json')
  f = open(file, 'w')
  f.write(json.dumps(list))

# 更新视频list
def updateVideo(name, list):
  file = os.path.abspath('../data/' + name + '/videos.json')
  with open(file, 'r+') as f:
    list_old = json.load(f)
    list_new = list + list_old
    f.seek(0)
    json.dump(list_new, f)
    f.truncate()


if __name__  == '__main__':
  f = open('../conf/user.txt')
  names = f.readlines()
  for name in names:
    name = name.strip()
    print name
    max_id_int = getMaxId(name)
    createDirectory(name)
    res = getVideoList(name, max_id_int)
    print res
    if res:
      v_max_id, list = res
      list.reverse()
      for l in list:
        downloadVideo(name, l['url'], l['id'])
        # 每个视频下载结束 记录已经处理的最大视频id
        recordMaxId(name, l['id'])
      if max_id_int == 0:
        recordVideo(name, list)
      else:
        updateVideo(name, list)
      # 处理结束 记录已经处理的最大instagram_photo_id [不一定是视频]
      recordMaxId(name, v_max_id)
