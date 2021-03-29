import random
import redis
import os
import pickle
from api import Preprocessor, SearchEngine, Trie, ErrorChecker
from utils import *

# Redis config
pool_title = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False, db=0)
pool_desc = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False, db=1)
pool_record = redis.ConnectionPool(host='localhost', port=6379, decode_responses=False, db=2)
pool_meta = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, db=3)
# Create Preprocessor
stop_words_path = "static/englishST.txt"
regex = r"\w+"
preprocessor = Preprocessor(regex, stop_words_path)

search_engine = SearchEngine(pool_title, pool_desc, pool_record, pool_meta, preprocessor)

# Trie
trie = Trie("./static/my_trie.marisa")

# ErrorChecker
errorChecker = ErrorChecker()


@service_log
def searchID(bookID):
    # init temp data
    search_engine.init_tmp()
    # get_records
    records = search_engine.get_records([bookID])
    records = [pickle.loads(record) for record in records]
    # records = [record[0] for record in records]
    return records


@service_log
def search(query, boolean, search_desc):
    # init temp data
    search_engine.init_tmp()
    # search
    results = [search_engine.search(q, search_desc) for q in query]

    id_title = set()
    id_desc = set()
    for i, result in enumerate(results):
        if i == 0:
            id_title = set(result[0])
        else:
            if boolean[i - 1] == 'AND':
                id_title &= set(result[0])
            else:
                id_title |= set(result[0])

    if search_desc:
        for i, result in enumerate(results):
            if i == 0:
                id_desc = set(result[1])
            else:
                if boolean[i - 1] == 'AND':
                    id_desc &= set(result[1])
                else:
                    id_desc |= set(result[1])

    # get records
    records = []
    records_title = search_engine.get_records(id_title)
    records_title = [pickle.loads(record) for record in records_title]
    records += search_engine.rank(records_title, "title")

    if search_desc:
        records_desc = search_engine.get_records(id_desc)
        records_desc = [pickle.loads(record) for record in records_desc]
        records += search_engine.rank(records_desc, "desc")

    records = [record[0] for record in records]
    return records


def completion(query):
    result = trie.search(query.lower())
    result.sort(key=lambda x: len(x))
    return result


@service_log
def heat_increase(query):
    conn = redis.Redis(connection_pool=pool_meta)
    conn.zincrby("heat", 1, query)


@service_log
def heat_search():
    conn = redis.Redis(connection_pool=pool_meta)
    result = conn.zrange("heat", -10, -1)[::-1]
    return result


@service_log
def correction(query):
    return errorChecker.correction(query)
