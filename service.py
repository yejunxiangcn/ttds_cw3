import random
import redis
import pickle
from api import Preprocessor, SearchEngine
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
                print(len(id_title))
                id_title &= set(result[0])
                print(len(result[0]))
                print(len(id_title))
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


@service_log
def search_moc(query, boolean, search_desc):
    """
    :type query: str
    :type boolean: list
    :type search_desc: bool
    :rtype: list
    """
    with open("./static/search_mock.json", 'r') as f:
        data = json.load(f)
    return data["data"]["list"]


# TODO
@service_log
def completion(query):
    pass


@service_log
def completion_moc(query):
    """
    :type query: str
    :rtype: list
    """
    result = []
    for i in range(random.randint(3, 10)):
        result += [query + " " + str(i)]
    return result
