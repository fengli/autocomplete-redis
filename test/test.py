#-*-coding:utf-8-*-
from autocomplete import Autocomplete
import os
import unittest

class testAutocomplete (unittest.TestCase):
  def setUp (self):
    self.items=['{"score": "9", "id": "1", "title": "轻轻地你走了"}', \
                '{"score": "8", "id": "2", "title": "正如你轻轻地来"}', \
                '{"score": "8.5", "id": "3", "title": "你挥一挥衣袖，不带走一片云彩"}']
    self.index_mapping={'term':'title',
                        'id':'id',
                        }
    self.a=Autocomplete(jsonitems=self.items,mapping=self.index_mapping)
    self.a.rebuild_index ()

  def test_initilize_from_filename (self):
    testfile = os.path.abspath('test/input.json')
    a=Autocomplete(filename=testfile)
    a.rebuild_index ()
    results=a.search_query (u'你 轻轻')
    self.assertEqual(len(results),2)
    self.assertEqual(results[0]['id'],'1')
    self.assertEqual(results[1]['id'],'2')

  def test_search_query1 (self):
    results=self.a.search_query (u'你 轻轻')
    self.assertEqual(len(results),2)
    self.assertEqual(results[0]['id'],'1')
    self.assertEqual(results[1]['id'],'2')

  def test_search_query2 (self):
    results=self.a.search_query (u'轻轻')
    self.assertEqual(len(results),2)
    self.assertEqual(results[0]['id'],'1')
    self.assertEqual(results[1]['id'],'2')

  def test_search_query3 (self):
    results=self.a.search_query (u'你 带走')
    self.assertEqual(len(results),1)
    self.assertEqual(results[0]['id'],'3')

  def test_search_query4 (self):
    results=self.a.search_query (u'你挥一挥衣袖，不带走一片云彩')
    self.assertEqual(len(results),1)
    self.assertEqual(results[0]['id'],'3')

  def test_index_mapping (self):
    self.index_mapping={
      'term':lambda x:x.get('title')+x.get('id'),
      'id':'id',
      }
    self.a=Autocomplete(jsonitems=self.items,mapping=self.index_mapping)
    self.a.rebuild_index ()
    results=self.a.search_query (u'1')
    self.assertEqual(len(results),1)
    self.assertEqual(results[0]['id'],'1')
    results=self.a.search_query (u'2')
    self.assertEqual(len(results),1)
    self.assertEqual(results[0]['id'],'2')

if __name__=='__main__':
  unittest.main ()
