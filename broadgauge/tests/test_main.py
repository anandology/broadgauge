"""This module doesn't really test anything, but imports the main module,
which in turn imports all other modules. So, it makes sure there are no 
silly syntax errors in the code.
"""
from .. import main
import unittest

class MainTest(unittest.TestCase):
    def test_main(self):
        pass