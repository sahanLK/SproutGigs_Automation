

class QueryError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return f'Query Error: {self.msg}'


