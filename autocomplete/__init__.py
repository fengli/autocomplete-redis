#-*- coding:utf-8 -*-
VERSION = '0.1'

import redis

try:
  import simplejson
except:
  from django.utils import simplejson

try:
  from django.core import serializers
  from django.db.models.loading import get_model
except:
  pass

import mmseg

class Autocomplete (object):
  """
  An example usage:

  items=['{"score": "9", "id": "1", "title": "轻轻地你走了"}', \
  '{"score": "8", "id": "2", "title": "正如你轻轻地来"}', \
  '{"score": "8.5", "id": "3", "title": "你挥一挥衣袖，不带走一片云彩"}']

  a=Autocomplete(items=items,mapping=index_mapping)
  a.rebuild_index ()
  print a.search_query (u'你 轻轻')
  print a.search_query (u'轻轻')
  print a.search_query (u'你 带走')
  
  ac=Autocomplete (items=items)
  ac.rebuild_index ()
  print a.search_query (u'你 轻轻')
  """

  def __init__ (self, redisaddr="localhost", modelname="book",
                limits=5, cached=True, mapping=None, filename=None,
                jsonitems=None, app_label=None, model_label=None, fields=None):

    self.r = redis.Redis (redisaddr)
    if model_label: modelname = model_label
    self.database='database:%s'%modelname
    self.indexbase='indexbase:%s'%modelname
    self.limits=limits
    self.fields=fields
    self.cached=True
    self.mapping=mapping
    self.filename=filename
    self.app_label=app_label
    self.model_label=model_label
    self.jsonitems=jsonitems
    mmseg.Dictionary.load_dictionaries()
    self._init_objs_auto ()

  def _init_objs_from_json_file (self):
    """
    Initialize indexed objects from file self.filename.
    Each line of the file should be one json object.
    """
    fi = open (self.filename, 'r')
    for line in fi.xreadlines ():
      yield (simplejson.loads (line))

  def _init_objs_from_model (self):
    """
    Initialize indexed objects from model with
    app.model.
    """
    mod = get_model (self.app_label, self.model_label)
    for item in mod.objects.all ():
      yield simplejson.loads(serializers.serialize ('json', item, self.fields))

  def _init_objs_from_json_lists (self):
    """
    Initialize indexed objects from a list of
    json objects.
    """
    for jsonitem in self.jsonitems:
      yield simplejson.loads (jsonitem)

  def _init_objs_auto (self):
    """
    Automatically decide which one to use as the index
    item generator.
    """
    if self.filename:
      self.item_generator = self._init_objs_from_json_file
    elif self.app_label and self.model_label:
      self.item_generator = self._init_objs_from_model
    elif self.jsonitems:
      self.item_generator = self._init_objs_from_json_lists
    else:
      raise Exception ('You have to specify the objects source you want to index.')

  def rebuild_index (self):
    self.del_index ()
    self.build_index ()

  def del_index (self):
    prefixs = self.r.smembers (self.indexbase)
    for prefix in prefixs:
      self.r.delete('%s:%s'%(self.indexbase,prefix))
    self.r.delete(self.indexbase)
    self.r.delete(self.database)

  def build_index (self):
    """
    Build index for items.
    """
    for item in self.item_generator ():
      self.add_item (item)

  def add_item (self,item):
    """
    Create index for ITEM.
    """
    self.r.hset (self.database, self._getval ('id',item), simplejson.dumps(item))
    for prefix in self.prefixs_for_term (self._getval('term',item)):
      self.r.sadd (self.indexbase, prefix)
      self.r.zadd ('%s:%s'%(self.indexbase,prefix),self._getval('id',item), self._getval('score',item))

  def _getval (self, attr, item):
    if self.mapping and self.mapping.has_key (attr):
      if callable (self.mapping[attr]):
        return self.mapping[attr] (item)
      return item[self.mapping[attr]]
    return item[attr]

  def del_item (self,item):
    """
    Delete ITEM from the index
    """
    pass

  def prefixs_for_term (self,term):
    """
    Get prefixs for TERM.
    """
    # Normalization
    term=term.lower()

    # Prefixs for term
    prefixs=[]
    tokens=mmseg.Algorithm(term)
    for token in tokens:
      word = token.text
      for i in xrange (1,len(word)+1):
        prefixs.append(word[:i])

    return prefixs

  def normalize (self,prefix):
    """
    Normalize the search string.
    """
    return prefix.lower().split()

  def search_query (self,prefix):
    search_strings = self.normalize (prefix)
    if not search_strings: return []

    cache_key = "%s:%s" % (self.indexbase, ('|').join(search_strings))

    if not self.cached or not self.r.exists (cache_key):
      self.r.zinterstore (cache_key, map (lambda x: "%s:%s"%(self.indexbase,x), search_strings))
      self.r.expire (cache_key, 10 * 60)

    ids=self.r.zrevrange (cache_key, 0, self.limits)
    if not ids: return ids
    return map(lambda x:simplejson.loads(x),
               self.r.hmget(self.database, *ids))
