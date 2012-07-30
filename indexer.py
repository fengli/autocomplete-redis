#-*- coding:utf-8 -*-

import redis
import simplejson
import mmseg

r = redis.Redis ("localhost")
mmseg.Dictionary.load_dictionaries()

database='database:book'
indexbase='index:book'

def rebuild_index (items):
  del_index ()
  build_index (items)

def del_index ():
  prefixs = r.smembers (indexbase)
  for prefix in prefixs:
    r.delete('%s:%s'%(indexbase,prefix))
  r.delete(indexbase)
  r.delete(database)

def build_index (items):
  """
  Build index for items.
  """
  for item in items:
    add_item (item)

def add_item (item):
  """
  Create index for ITEM.
  """
  r.hset (database, item['id'], simplejson.dumps(item))
  for prefix in prefixs_for_term (item['term']):
    r.sadd (indexbase, prefix)
    r.zadd ('%s:%s'%(indexbase,prefix),item['id'], item['score'])

def del_item (item):
  """
  Delete ITEM from the index
  """
  pass

def prefixs_for_term (term):
  """
  Get prefixs for TERM.
  """
  prefixs=[]
  tokens=mmseg.Algorithm(term)
  for token in tokens:
    word = token.text
    for i in xrange (1,len(word)+1):
      prefixs.append(word[:i])

  return prefixs

def search_query (prefix):
  ids=r.zrange ('%s:%s'%(indexbase,prefix), 0, 5)
  if not ids: return ids
  return r.hmget(database, *ids)

def load_items ():
  items= (
    {'id':'1', 'term': u'轻轻地你走了', 'score': '9'},
    {'id':'2', 'term': u'正如你轻轻地来', 'score': '8'},
    {'id':'3', 'term': u'你挥一挥衣袖，不带走一片云彩', 'score': '8.5'},
    )
  rebuild_index (items)
