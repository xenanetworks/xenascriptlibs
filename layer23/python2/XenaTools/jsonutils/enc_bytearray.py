import sys
import base64

"""
This module contains methods to encode and decode byte arrays
to and from strings using base64.
"""


def decode_bytearray(encstr):
    """ Decodes the base64-encoded string to a byte array
    :param encstr: The base64-encoded string representing a byte array
    :return: The decoded byte array
    """
    decstring = base64.b64decode(encstr)

    b = bytearray()
    b.extend(decstring)
    return b


def encode_bytearray(bytearr):
    """ Encodes the byte array as a base64-encoded string
    :param bytearr: A bytearray containing the bytes to convert
    :return: A base64 encoded string
    """
    strval = "".join(map(chr, bytearr))
    encstring = base64.b64encode(strval)
    return encstring


if __name__ == '__main__':
    print "Cannot call this library directly"
    sys.exit(1)
