import sys
from lxml import etree
from html5_parser import parse as html5_parse

import mimetype


class Book:
    def __init__(self):
        self.tree = etree.Element("book")

    def generate(url):
        """
        @def Book.generate
        Generate book.xml
        """
