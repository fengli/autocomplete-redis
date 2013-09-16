autocomplete-redis
============

autocomplete-redis 是基于redis的自动补全，他会自动索引你要自动补全的句子，然后根据你的输入返回包含这个输入的句子。这儿有一个完整的演示实例： http://readpi.com ,索引了一些书的名字。

安装
---------

* 安装pip(如果没有安装过的话)： `easy_install pip`

* 安装pymmseg中文分词： `pip install -e git+https://github.com/pluskid/pymmseg-cpp.git#egg=pymmseg-dev` 依赖pymmseg中文分词，安装之。

* 安装autocomplete-redis： `pip install -e git+https://github.com/fengli/autocomplete-redis.git#egg=autocomplete-dev` 

快速使用
----------
* 假设你有如下需要索引的json文本 input.json:

```python
   {"score": "9", "id": "1", "term": "轻轻地你走了"}
   {"score": "8", "id": "2", "term": "正如你轻轻地来"}
   {"score": "8.5", "id": "3", "term": "你挥一挥衣袖，不带走一片云彩"}
```
score是返回结果排序的rank值，最大的值最靠前。

* 建立索引和查询

```python
   a=Autocomplete(filename="input.json", modelname="whateveryouwant")
   a.rebuild_index ()
   results=a.search_query (u'你 轻轻')
   [{"score": "9", "id": "1", "term": "轻轻地你走了"}, {"score": "8", "id": "2", "term": "正如你轻轻地来"}]
```
   filename是你要索引的文件名，modelname是一个在redis数据库中唯一的名字，你可以跟你的应用起名。

详细的说明
------------

autocomplete-redis的输入可以是list, json文档或者django中的model类。

* 输入list

```python
    items=['{"score": "9", "id": "1", "term": "轻轻地你走了"}', \
           '{"score": "8", "id": "2", "term": "正如你轻轻地来"}', \
           '{"score": "8.5", "id": "3", "term": "你挥一挥衣袖，不带走一片云彩"}']
    a=Autocomplete(jsonitems=items, modelname="whateveryouwant")
    a.search_query (u'轻轻')
```

* 输入json文件, 比如input.json如下：

```python
   {"score": "9", "id": "1", "term": "轻轻地你走了"}
   {"score": "8", "id": "2", "term": "正如你轻轻地来"}
   {"score": "8.5", "id": "3", "term": "你挥一挥衣袖，不带走一片云彩"}

   a=Autocomplete(filename="input.json", modelname="whateveryouwant")
   a.rebuild_index ()
   results=a.search_query (u'你 轻轻')
   print results
   [{"score": "9", "id": "1", "term": "轻轻地你走了"}, {"score": "8", "id": "2", "term": "正如你轻轻地来"}]
```
   filename是json文件的路径，modelname是确定你redis数据库中唯一的名字。

* 输入是django中的model

  比如在你的app booklist中你有一个model定义为

```python  
  class book (models.Model):
    term=models.CharField (max_length=200)
    score=models.IntegerField (default=0)
    id=models.IntegerField ()
```

   你可以这样建立索引：

```python   
   a=Autocomplete (app_label='booklist',model_label='book')
   a.rebuild_index()
```

   搜索可以：

```python   
   results=a.search_query (u'你是')
```
   app_label是你的app的名字,model_label是你要索引model的名字。这儿不需要modelname，这个autocomplete-redis会自动根据model_label生成。

* 你可能会需要一个mapping

在以上的例子中，所有的dictionary输入都有固定的键值：score用来给返回的查询结果进行排序，id是返回结果的id值，term是要查询的句子本身。如果你要修改这些默认的值，比如你有input.json：

```python
   {"score": "9", "pk": "1", "title": "轻轻地你走了", "author":"徐志摩"}
   {"score": "8", "pk": "2", "title": "正如你轻轻地来","author":"徐志摩"}
   {"score": "8.5", "pk": "3", "title": "你挥一挥衣袖，不带走一片云彩","author":"徐志摩"}
```
   这时你只需要传递一个额外的参数，

   ```python
   mapping={'id':'pk','term':'title','score':'score'}
   ```

   将你的键值映射到这三个键值来。这个mapping也可以是函数，比如

```python
   mapping = {
    'id':'pk',
    'term':lambda x:' '.join([x['title'],x['author']]),
    'score':lambda x:x['score'],
    }
```
    在这个例子中，可以这样使用

```python    

    a=Autocomplete (filename="input.json",modelname="whateveryouwant",mapping=mapping)
    a.rebuild_index ()
    a.search_query (u'徐志摩')

```

所有可能的参数
---------------

```python

class Autocomplete (object):
  def __init__ (self, redisaddr="localhost", modelname="book",
                limits=5, cached=True, mapping=None, filename=None,
                jsonitems=None, app_label=None, model_label=None, fields=None):

```

* redisaddr: 你的redis实例的地址
* modelname: redis数据库中你这组索引的唯一名字 (在索引数据库的时候不需要提供)
* limits: 返回的结果数
* cached: 是否cache多个键值组合的结果
* mapping: mapping你的字典key值到'term','score'和'id'
* filename: 你的json文件的路径 (只有在json文件模式下使用)
* jsonitems: 要索引的list. (只有在输入list的时候使用)
* app_lable,model_label: (只有在索引model的时候使用)
* fileds: 你希望索引model中的哪些fields (只有在索引model的时候使用)，默认索引全部的fields.

Bring to you by:
----------------

* 阅读派：http://readpi.com
