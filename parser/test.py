# from lxml import etree
import pycurl

# import certifi
from io import BytesIO


def main():
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "https://tl.rulate.ru/book/21")
    c.setopt(c.WRITEDATA, buffer)
    # c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()

    body = buffer.getvalue()
    # Body is a byte string.
    # We have to know the encoding in order to print it to a text file
    # such as standard output.
    print(body.decode("utf-8"))


main()
