#! /bin/env python3
from base64 import b64encode
import sys
from posix import urandom
b = urandom(256)
k = b64encode(b)
if __name__ == '__main__':
    sys.stdout.write(str(k, encoding='utf8'))
