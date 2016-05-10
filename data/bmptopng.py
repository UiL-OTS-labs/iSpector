#!/usr/bin/env python3

import re
import sys

def read_content(fn):
    f = open(fn, 'rb')
    content = f.read()
    f.close()
    return content.decode('utf-8')

def replace_match(m):
    return m.group(1) + 'png'

def modify(content):
    regex = re.compile(r'(\d+\.)bmp', re.MULTILINE)
    content = regex.sub(replace_match, content)
    return content

def write_to_fn(fn, content):
    f = open(fn,"w")
    f.write(content)
    f.close()


def main(strlist):
    for i in strlist:
        content = read_content(i)
        content = modify(content)
        write_to_fn(i, content)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
