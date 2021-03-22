import re
import sys
import math
import redis
import pickle
from collections import defaultdict
from nltk.stem.porter import PorterStemmer

from utils import *

import enchant


class SearchEngine:

    def __init__(self, pool_title, pool_desc, pool_record, pool_meta, preprocessor):
        self.__pool_title = pool_title
        self.__pool_desc = pool_desc
        self.__pool_record = pool_record
        self.__pool_meta = pool_meta
        self.__preprocessor = preprocessor

        self.init_tmp()

    @func_log
    def search(self, command, search_desc=True):
        # get connection
        conn_title = redis.Redis(connection_pool=self.__pool_title)
        conn_meta = redis.Redis(connection_pool=self.__pool_meta)

        # N
        self.N = int(conn_meta.get("N"))

        # process input query
        query_title = self.__preprocessor.preprocess(command, use_stop_words=False)

        self.query_title += query_title

        # title
        for item in query_title:
            result = conn_meta.hget("df_title", item)
            self.__df_title[item] = result if result is not None else 0

        # search
        candidates = self.__search_candidates(conn_title, query_title)
        result_title = self.__judge_phrase("title", candidates, query_title)

        result_desc = None
        # desc
        if search_desc:
            conn_desc = redis.Redis(connection_pool=self.__pool_desc)
            query_desc = self.__preprocessor.preprocess(command, use_stop_words=True)
            self.query_desc += query_desc

            for item in query_desc:
                result = conn_meta.hget("df_description", item)
                self.__df_desc[item] = result if result is not None else 0

            candidates = self.__search_candidates(conn_desc, query_desc)
            result_desc = self.__judge_phrase("desc", candidates, query_desc)

            result_desc -= result_title

        return result_title, result_desc

    @func_log
    def get_records(self, id_list):
        # get connection
        conn_record = redis.Redis(connection_pool=self.__pool_record)

        result = conn_record.mget(id_list)
        return result

    def __search_candidates(self, conn, query):
        candidates = set()

        for i, word in enumerate(query):
            if i == 0:
                candidates = set(conn.hkeys(word))
            candidates &= set(conn.hkeys(word))

        return candidates

    def __judge_phrase(self, which, candidates, query):
        pool = self.__pool_title if which == "title" else self.__pool_desc
        conn = redis.Redis(connection_pool=pool)

        tf_dic = self.__tf_title if which == "title" else self.__tf_desc

        result = set()

        pipe = conn.pipeline(False)
        for candidate in candidates:
            for word in query:
                pipe.hget(word, candidate)
        execute = pipe.execute()

        for i, candidate in enumerate(candidates):
            index_list = execute[i * len(query): (i + 1) * len(query)]
            index_list = [pickle.loads(x) for x in index_list]

            if self.__if_phrase(0, 0, index_list):
                result.add(candidate)
                for index, item in enumerate(query):
                    tf_dic[candidate][item] = len(index_list[index])

        return result

    def __if_phrase(self, i, pre, idx_list):
        if len(idx_list) == 1:
            return True

        if i >= len(idx_list):
            return False

        flag = False
        for j in range(len(idx_list[i])):
            cur = idx_list[i][j]
            if i == len(idx_list) - 1 and int(cur) == int(pre) + 1:
                return True
            elif (i > 0 and int(cur) == int(pre) + 1) or i == 0:
                flag |= self.__if_phrase(i + 1, cur, idx_list)
        return flag

    @func_log
    def rank(self, records, which):
        n = self.N
        items = self.query_title if which == "title" else self.query_desc

        scores = []
        for record in records:
            score = 0
            for item in items:
                tf = int(self.__get_tf(record, item, which))
                df = int(self.__get_df(item, which))
                if tf == 0 or df == 0:
                    continue
                score += (1 + math.log10(tf)) * math.log10(n / df)
            scores += [[record, score]]
        scores = sorted(scores, key=(lambda x: -x[1]))

        return scores

    def __get_tf(self, record, item, which):
        tf_dic = self.__tf_title if which == "title" else self.__tf_desc
        try:
            return tf_dic[record["asin"].encode(encoding='UTF-8')][item]
        except:
            return 0

    def __get_df(self, item, which):
        df_dic = self.__df_title if which == "title" else self.__df_desc

        try:
            return df_dic[item]
        except:
            return 0

    def init_tmp(self):
        self.__tf_title = defaultdict(dict)
        self.__tf_desc = defaultdict(dict)
        self.__df_title = {}
        self.__df_desc = {}
        self.query_title = []
        self.query_desc = []
        self.N = 0


class Preprocessor:

    def __init__(self, regex, stop_words_path):
        """
        Init the object
        :param regex: The regex for preprocessing
        :param stop_words_path: The path of stop words file
        """
        self.regex = regex
        self.stop_words = self.load_stop_words(stop_words_path)

    def load_stop_words(self, path):
        """
        Load stop words from the given path
        :param path: The path of stop words file
        :return: A list of stop words
        """
        with open(path, "r", encoding='utf-8-sig') as f:
            stop_words = f.read()
        stop_words = stop_words.split('\n')
        return stop_words

    def preprocess(self, text, use_lowercase=True, use_stop_words=False, use_stemmer=True):
        """
        Preprocess the text
        :param text: The text need to be preprocessed
        :param use_lowercase: If use lowercase
        :param use_stop_words: If delete stop words
        :param use_stemmer: If implement stemmer
        :return: A list of preprocessed words
        """
        processed = re.findall(self.regex, text)

        if use_lowercase:
            processed = [w.lower() for w in processed]

        if use_stop_words:
            processed = [w for w in processed if w not in self.stop_words]

        if use_stemmer:
            porter_stemmer = PorterStemmer()
            processed = [porter_stemmer.stem(w) for w in processed]
            # processed = [stem(w) for w in processed]
        return processed


class Trie:
    def __init__(self, root_file=None):
        if root_file is None:
            self.root = {}  # 这里用一个字典存储
        else:
            with open(root_file, "rb") as f:
                self.root = pickle.load(f)
        self.end_of_word = '^'  # 用#标志一个单词的结束

    # 构建前缀树
    def insert(self, word: str):
        node = self.root
        # word_split = word.split()
        for char in word:
            node = node.setdefault(char, {})
        node[self.end_of_word] = self.end_of_word

    # 查找是否有一个单词是这个前缀开始的
    def startsWith(self, prefix: str):
        node = self.root
        prefix = prefix.split()
        prefix = " ".join(prefix)
        for char in prefix:
            if char not in node:
                return False
            if char in node:
                node = node[char]

        def get_completion_words(pre_string, cur_node):
            word_list = []
            if cur_node == '^':
                word_list.append(pre_string)
                return word_list
            for key in list(cur_node):
                word_list.extend(get_completion_words(pre_string + str(key), cur_node[key]))
            return word_list

        return get_completion_words(prefix, node)

    # 输入查询前缀，输出查询结果
    def search(self, pre_search):
        select_list = self.startsWith(pre_search.lower())
        final = []
        for i in range(0, 10):
            try:
                temp = select_list[i][:-1]
            except:
                break
            final.append(temp)
        return final

    def dump(self, file):
        sys.setrecursionlimit(1000000)
        with open(file, "wb+") as f:
            pickle.dump(file, self.root)
        sys.setrecursionlimit(998)


class errorChecker:

    def __init__(self):
        """
        Init the object
        :param punc: The regexp contains all punctuations except '/\-_~'
        :param punc1: The regexp contains punctuations '/\-_~'
        :param checker: An enchant Dict that is used for spellchecking. The word list used in this Dict is a customized
        word list that contains tokens from all titles.
        """
        self.punc = r'[!"#\$%&()*+,.:;<=>?@[\]^`{|}]'
        self.punc1 = r'[/\-_~]'
        self.checker = enchant.request_pwl_dict("static/title_tokens.txt")

    def correction(self, content):
        """
        Perform spell checking on the given content (title), and return the corrected version.
        :param content: String    Content to be corrected.
        :return: String    the corrected content.
        """

        # customized preprocess for given content.
        a = content.lower()
        a = a.split()
        words = []

        # Remove punctuations in self.punc only.
        for word in a:
            x = re.sub(self.punc, "", word)
            if re.search(self.punc1, x) is not None:
                result = re.split(self.punc1, x)
                for item in result:
                    if item != "":
                        words.append(item)
            else:
                words.append(x)

        # For each word in given content, apply spell checking.
        result = ""
        for word in words:
            if not self.checker.check(word):
                sugglst = self.checker.suggest(word)
                if len(sugglst) > 0:
                    word = sugglst[0]
            result += word + " "

        return result[:-1]
