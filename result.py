class R:
    def __init__(self):
        self.success = False
        self.code = 0
        self.message = ""
        self.data = dict()

    @staticmethod
    def ok():
        r = R()
        r.success = True
        r.code = 20001
        r.message = "Success"
        return r

    @staticmethod
    def error():
        r = R()
        r.success = False
        r.code = 20000
        r.message = "Fail"
        return r

    def set_message(self, message):
        self.message = message
        return self

    def set_code(self, code):
        self.code = code
        return self

    def add_data(self, key, value):
        self.data[key] = value
        return self
