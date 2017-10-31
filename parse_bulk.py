#!/usr/bin/python

import sys
import re
from datetime import datetime
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions, helpers
import logging
logging.basicConfig(filename='parse.log',level=logging.INFO)

# rollback recent changes to serializer that choke on unicode
class JSONSerializerPython2(serializer.JSONSerializer):
        def dumps(self, data):
                # don't serialize strings
                if isinstance(data, compat.string_types):
                        return data
                try:
                        return json.dumps(data, default=self.default, ensure_ascii=True)
                except (ValueError, TypeError) as e:
                        raise exceptions.SerializationError(data, e)

es = Elasticsearch(serializer=JSONSerializerPython2())  # use default of localhost, port 9200

with open(sys.argv[1], 'r') as f:
        data=f.read()

recs = data.split("<PubmedArticle>");
# drop preamble
recs.pop(0)

articles = []

for r in recs:
        pmid = re.findall('<PMID Version="1">(.*?)</PMID>', r)
        if pmid:
                pmid = pmid[0]
        else:
                pmid = ""
                        
        title = re.findall('<ArticleTitle>(.*?)</ArticleTitle>', r)
        if title:
                title = title[0]
        else:
                title = ""
        abstract = re.findall('<AbstractText .*?>(.*?)</AbstractText', r)
        if abstract:
                abstract = unicode(abstract[0], "utf-8")
        else:
                abstract = ""
        articles.append({'_index': 'medline', '_type': 'article', "_id": pmid, "_op_type": 'index', '_source': {"title": title, "abstract": abstract, "timestamp": datetime.now().isoformat()}})

res = helpers.bulk(es, articles, raise_on_exception=False)

logging.info(datetime.now().isoformat() + " imported " + str(res[0]) + " records from " + sys.argv[1])
