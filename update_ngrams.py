import json

from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions, helpers

# rollback recent changes to serializer that choke on unicode$
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

def update_by_query(index,doc_type,body):
    es.update_by_query(index=index,doc_type=doc_type,body=body,request_timeout=600,scroll_size=100000,conflicts='proceed',slices='auto')


def create_body(index,type):
    body={
        "script": {
            "source": "ctx._source.type="+type,
            "lang":"painless"
        },
    }
    print(body)
    update_by_query(index,'_doc',body)

create_body(index='medline-bigrams',type='bigrams')
create_body(index='medline-trigrams',type='trigrams')

#just use curl

"""
curl -X POST "localhost:9200/medline-bigrams/_update_by_query" -H 'Content-Type: application/json' -d'
{
  "script": {
    "source": "ctx._source.type= params.type",
    "lang": "painless",
    "params": {"type":"bigram"}
  }
}
'
"""
