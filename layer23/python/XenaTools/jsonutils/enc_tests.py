""" This module contains tests for the bytearray utility functions
"""

import enc_bytearray
import unittest

class TestByteArray(unittest.TestCase):

    def test_decoder_test(self):
        encstring = "EiM0RVZnAAAAAAAA//8="
        exp_result = bytearray([0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff])
        decarray = enc_bytearray.decode_bytearray(encstring)

        self.assertTrue(len(exp_result) == len(decarray))

        for index in range(len(decarray)):
            self.assertTrue(exp_result[index] == decarray[index])

    def test_encoder_test(self):
        decarray = bytearray([0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff])
        exp_encstring = "EiM0RVZnAAAAAAAA//8="
        encstring = enc_bytearray.encode_bytearray(decarray)

        self.assertTrue(len(exp_encstring) == len(encstring))
        self.assertTrue(exp_encstring == encstring)


if __name__ == '__main__':
    unittest.main()