import hashlib

def md5_func(value):
    md5 = hashlib.md5("xxx".encode("utf-8"))
    md5.update(value.encode("utf-8"))
    return md5.hexdigest()