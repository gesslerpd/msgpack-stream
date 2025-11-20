class ExtType:
    __slots__ = ("code", "data")

    def __init__(self, code: int, data: bytes):
        self.code = code
        self.data = data

    def __eq__(self, other):
        if isinstance(other, ExtType):
            return self.code == other.code and self.data == other.data
        return False
