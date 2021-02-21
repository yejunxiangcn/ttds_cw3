import json
import datetime
import time
from flask import current_app
from functools import wraps


def jsonify(object):
    return json.dumps(obj=object, default=lambda x: x.__dict__, sort_keys=False, indent=2)

def func_log(function):
    def inner(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        spend = t1 - t0
        current_app.logger.info("FUNCTION \"%s\" COST: %fs" % (function.__name__, spend))
        return result

    return inner


def service_log(function):
    def inner(*args, **kwargs):
        current_app.logger.info("======================= %s START WITH: [ %s %s] =======================" %
                                (function.__name__.upper(), args, kwargs))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        spend = t1 - t0
        current_app.logger.info("======================= %s COST: [ %fs ] =======================" %
                                (function.__name__.upper(), spend))
        return result

    return inner
