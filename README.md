autocomplete-redis
============

autocomplete-redis is a quora like automatic autocompletion based on redis.

Installation
---------

* install pip (if you haven't yet) `easy_install pip`

* install pymmseg (support for Chinese Characters)： `pip install pymmseg`

* install autocomplete-redis： `pip install -e git+https://github.com/fengli/autocomplete-redis.git#egg=autocomplete-dev` 

Quick start
----------
* Assume you have few items to index.

```python
items=[{"uid":'1', "score":9, "term": u"hello world, that's great"},
       {"uid":'2', "score":10, "term": u"what the hell or yell"},
       {"uid":'3', "score":8.5, "term":u"World is like a box of chocolate"},
      ]
```

The code for build the index and search is simple:

```python
from autocomplete import Autocomplete

#build index
au = Autocomplete ("scope")
for item in items:
  au.add_item (item)
#search
restuls = au.search_query (u'hel')

print results
[{'term': 'what the hell or yell', 'score': 10, 'uid': '2'}, {'term': "hello world, that's great", 'score': 9, 'uid': '1'}]
```


API
---------------

* Convention: the item you pass to `autocomplete` should have at least `"uid"` and `"term"`, `"score"` is optional, but it's important if you want to return based on ranking. And you could have other fields as you like.

```python
{"uid":'1', "score":9, "term": u"hello world, that's great", 'meta':"1992"}
```
  * `uid`: the unique identifier for your item
  * `score`: the returned items sorted by this value.
  * `term`: the string to be indexed.

* `def __init__ (self, scope, redisaddr="localhost", limits=5, cached=True)`

  * scope: Scope allows you to index multiple independent indexes. 
  * redisaddr: your redis address
  * limits: How many results you want to get.
  * cached: Cache multiple keys combination?

* `def del_index (self)`

Delete all the indexes. Warning: all data will be deleted.

* `def add_item (self,item)`

Add item to index.

* `def del_item (self,item)`

Delete item from index.

* `def update_item (self, item)`

Update item indexed with item['uid'] with the new version.

* `def search_query (self,prefix)`

Search in database for all items that `item['term']` included `PREFIX`

Bring to you by:
----------------

* http://readpi.com
