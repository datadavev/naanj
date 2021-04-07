import re
import collections
import logging

_L = logging.getLogger("anvl")

class AnvlParseException(Exception):
    pass

_pattern1 = re.compile("[%:\r\n]")
_pattern2 = re.compile("[%\r\n]")
_pattern3 = re.compile("%([0-9a-fA-F][0-9a-fA-F])?")

def _decodeRewriter(m):
    if len(m.group(0)) == 3:
        return chr(int(m.group(0)[1:], 16))
    else:
        raise AnvlParseException("percent-decode error")


def _decode(s):
    return _pattern3.sub(_decodeRewriter, s)


def parse(s):
    d = collections.OrderedDict()
    k = None
    k0 = None
    lines = []
    if isinstance(s, str):
        lines = re.split("\r\n?|\n", s)
    else:
        lines = s
    for l in lines:
        if len(l) == 0:
            k = None
        elif l[0] == "#":
            pass
        elif l[0].isspace():
            if k is None:
                raise AnvlParseException("no previous label for continuation line")
            ll = _decode(l).strip()
            if ll != "":
                if d[k] == "":
                    d[k] = ll
                else:
                    d[k] += " " + ll
        else:
            if ":" not in l:
                raise AnvlParseException("no colon in line")
            k, v = [_decode(w).strip() for w in l.split(":", 1)]
            if k0 is None:
                k0 = k
            if len(k) == 0:
                raise AnvlParseException("empty label")
            if k in d:
                if not isinstance(d[k], list):
                    d[k] = [d[k], ]
                d[k].append(v)
            else:
                d[k] = v
    # if first key has a value then return a flat dict
    if len(d[k0]) > 0:
        return d
    # otherwise return a dict of dict, with first key as key to sub-dict
    dd = collections.OrderedDict()
    d.pop(k0)
    dd[k0] = d
    return dd

def parseBlocks(txt):
    """
    Generator returning parsed anvl blocks from text
    Args:
        txt:

    Returns:

    """
    block = []
    for line in re.split("\r\n?|\n", txt):
        llen = len(line)
        if llen > 0 and line[0] == '#':
            continue
        if llen == 0:
            if (len(block)) > 0:
                yield parse(block)
                block = []
        else:
            block.append(line)
    if len(block) > 0:
        yield parse(block)

