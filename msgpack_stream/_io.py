import io


class container(dict):

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def pack(typ, obj):
    stream = io.BytesIO()
    typ.pack(stream, obj)
    data = stream.getvalue()
    stream.close()
    return data


def unpack(typ, data):
    stream = io.BytesIO(data)
    obj = typ.unpack(stream)
    extra_data = stream.read()
    if extra_data:
        raise RuntimeError('too much data', extra_data)
    stream.close()
    return obj
