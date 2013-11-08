#-*- coding:utf-8 -*-
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
from autocomplete.utils import queryset_iterator

class Autocomplete (object):
  """
  autocomplete.
  """

  def __init__ (self, scope, redisaddr="localhost", limits=5, cached=True):
    self.r = redis.Redis (redisaddr)
    self.scope = scope
    self.cached=cached
    self.limits = limits
    self.database = "database:%s" % scope
    self.indexbase = "indexbase:%s" % scope
    mmseg.Dictionary.load_dictionaries ()

  def _get_index_key (self, key):
    return "%s:%s" % (self.indexbase, key)

  def del_index (self):
    prefixs = self.r.smembers (self.indexbase)
    for prefix in prefixs:
      self.r.delete(self._get_index_key(prefix))
    self.r.delete(self.indexbase)
    self.r.delete(self.database)

  def sanity_check (self, item):
    """
    Make sure item has key that's needed.
    """
    for key in ("id","term"):
      if not item.has_key (key):
        raise Exception ("Item should have key %s"%key )

  def add_item (self,item):
    """
    Create index for ITEM.
    """
    self.sanity_check (item)
    self.r.hset (self.database, item.get('id'), simplejson.dumps(item))
    for prefix in self.prefixs_for_term (item['term']):
      self.r.sadd (self.indexbase, prefix)
      self.r.zadd (self._get_index_key(prefix),item.get('id'), item.get('score',0))

  def del_item (self,item):
    """
    Delete ITEM from the index
    """
    for prefix in self.prefixs_for_term (item['term']):
      self.r.zrem (self._get_index_key(preifx), item.get('id'))
      if not self.r.zcard (self._get_index_key(prefix)):
        self.r.delete (self._get_index_key(prefix))

  def update_item (self, item):
    self.del_item (item)
    self.add_item (item)

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
    tokens = mmseg.Algorithm(prefix.lower())
    return [token.text for token in tokens]

  def search_query (self,prefix):
    search_strings = self.normalize (prefix)

    if not search_strings: return []

    cache_key = self._get_index_key (('|').join(search_strings))

    if not self.cached or not self.r.exists (cache_key):
      self.r.zinterstore (cache_key, map (lambda x: self._get_index_key(x), search_strings))
      self.r.expire (cache_key, 10 * 60)

    ids=self.r.zrevrange (cache_key, 0, self.limits)
    if not ids: return ids
    return map(lambda x:simplejson.loads(x),
               self.r.hmget(self.database, *ids))
