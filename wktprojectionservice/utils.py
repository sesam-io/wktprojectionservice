# -*- coding: utf-8 -*-

import os
import errno
import unicodedata
import re
import uuid
import math


def utmToLatLng(zone, easting, northing, northernHemisphere=True):
    if not northernHemisphere:
        northing = 10000000 - northing

    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))

    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

    if not northernHemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

    return (latitude, longitude)



def is_sequence(arg):
    """ Checks if "arg" is a proper sequence or not (i.e. list, tuple..) """
    return not hasattr(arg, "strip") and (hasattr(arg, "__getitem__") or hasattr(arg, "__iter__"))


def randomSubject():
    return uuid.uuid4().urn


def randomID():
    return str(uuid.uuid4())


def stringToFilename(s):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    s = str(unicodedata.normalize('NFKD', s).encode('ascii', 'ignore'))
    s = re.sub('[^\w\s-]', '', s).strip().lower()
    return re.sub('[-\s]+', '-', s)


def assertDir(path, rootdir=None):
    """ Make sure the given directory/ies exists in the given or current path """

    if is_sequence(path):
        for p in path:
            assertDir(p, rootdir=rootdir)
    else:
        if not rootdir:
            rootdir = os.path.realpath(os.path.curdir)

        if not os.path.isabs(path):
            path = rootdir + os.sep + path
        
        if os.path.isdir(path):
            return

        # python 2.x is stupid.
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(rootdir + os.sep + path):
                pass
            else:
                raise


def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    res = ""

    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            char.encode(encoding, 'strict')
        except UnicodeError:
            if ord(char) <= 0xFFFF:
                res += '\\u%04X' % ord(char)
            else:
                res += '\\U%08X' % ord(char)
        else:
            res += char

    return res


def escape_literal(literal):
    """ Escape the string literal as per NTriples rules """
    literal = literal.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"').replace('\r', '\\r').replace('\v', '')
    literal = _xmlcharref_encode(literal, "ascii")
    return literal



def getCurrDir():
    """ Get the current directory """
    return os.path.realpath(os.path.curdir)

