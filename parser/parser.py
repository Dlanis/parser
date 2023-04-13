import httpx
from lxml import etree
import re
import sys
import xxhash
import time
import os
import csv
from concurrent.futures import ThreadPoolExecutor as ThreadPool
from concurrent.futures import ProcessPoolExecutor as ProcessPool
import html5_parser

import relist
import mimetype

## config

enable_h1 = False  # enable h1 parsing
enable_images = True  # enable image parsing
ignore_fontsize = True  # Ignore 'font-size' in style
enable_overwrite = False  # enable file overwriting
enable_image_overwrite = False  # enable image file overwriting

## end config

## httpx
httpx_client = httpx.Client(http2=True)

## prepare regexs
regexs = list(list())
ignore_fontsize_regex = None
list_regex = None


def prepare():
    ## Global
    global regexs
    global ignore_fontsize_regex
    global list_regex

    ## Make it local
    regexs_append = regexs.append
    re_compile = re.compile
    local_relist = relist.relist

    for reg in local_relist:
        regexs_append([re_compile(reg[0]), reg[1]])

    ignore_fontsize_regex = re_compile(R"""font-size:\s*[\d.,]{0,16}p[xt];{0,1}""")
    list_regex = re.compile(
        R'''"([^{'\s}]+)",\s*"([^\n]+)"'''
    )  # delete after move to csv


## end prepare regexs


def img_work(img):
    if img is not None:
        imgsrc = img.get("src")
        if len(imgsrc) > 0:
            os.makedirs("Images/", exist_ok=True)

            imgurl = None
            if imgsrc[0] == "/":
                imgurl = "https://tl.rulate.ru{}".format(imgsrc)
            else:
                imgurl = imgsrc

            request = httpx_client.get(imgurl, follow_redirects=True)
            raw = request.content

            if request.status_code == httpx.codes.OK:
                if raw[0:15] != b"<!DOCTYPE html>":

                    imgname = "{}{}".format(
                        xxhash.xxh3_64_hexdigest(raw), mimetype.file_extension(raw)
                    )

                    ## overwrite checking
                    if os.path.exists("Images/{}".format(imgname)):
                        print(
                            "Image file '{}' already exists! ".format(imgname), end=""
                        )

                        if enable_image_overwrite:
                            print("overwrite.")

                            open("Images/{}".format(imgname), "wb").write(raw)

                        else:
                            print("skip.")
                    else:
                        open("Images/{}".format(imgname), "wb").write(raw)

                    img.set("src", "../Images/{}".format(imgname))
                    img.set("style", "")
                    img.set("alt", "x{}".format(imgname))

                    # add text-align
                    div = img.getparent()
                    div.set("style", "text-align: center;")

                else:
                    img.getparent().remove(img)
            else:
                print("Bad request! {}", request.http_version)


def parse(url, outfile):
    ## overwrite checking
    if os.path.exists(outfile):
        print("Output file already exists! ", end="")
        if enable_overwrite:
            print("overwrite.")
            os.remove(outfile)
        else:
            print("skip.")
            return

    # body =  #.decode('utf-8').replace('&#160;', ' ')

    # html parsing
    tree = html5_parser.parse(
        httpx_client.get(url, follow_redirects=True).content, fallback_encoding="utf-8"
    )

    ## title checking
    h1 = tree.xpath("//*/h1")
    if len(h1) > 0:
        temp = h1[0].text.split(" / ")
        if len(temp) > 1:
            title = temp[1].split(": ")
        else:
            print("Invalid h1! assert at len(temp) > 1.")
            return
    else:
        print("Invalid h1! assert at len(h1) > 0.")
        return

    ## end

    ## create outfile xml root
    xml_root = etree.fromstring(
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
        "<head>"
        "<title>{}</title>"
        "</head>"
        "</html>".format(title[0])
    )

    xml_body = etree.SubElement(xml_root, "body")

    if enable_h1:
        xml_body.append(
            etree.fromstring('<h1 style="text-align: center;">{}</h1>'.format(title[0]))
        )

    if len(title) > 1:
        xml_body.append(etree.fromstring("<h2>{}</h2>".format(title[1])))

    else:
        h2 = tree.xpath("//*/h2")
        if h2[0].text is not None:
            xml_body.append(etree.fromstring("<h2>{}</h2>".format(h2[0].text)))

    content_text = tree.xpath('//*[@class="content-text"]')

    if len(content_text) > 0:
        content_text = content_text[0]

        ## Image pre-processing
        if enable_images:
            images = content_text.xpath(".//img")
            img_pool = ThreadPool(max_workers=16)
            img_pool.map(img_work, images)
            img_pool.shutdown()

        xml_body.append(content_text)

        ## Final text printing
        text = etree.tostring(
            xml_root,
            encoding=str,
            with_tail=False,
            method="xml",
        )

        re_sub = re.sub

        if ignore_fontsize:
            text = re_sub(ignore_fontsize_regex, "", text)

        for reg in regexs:
            text = re_sub(reg[0], reg[1], text)

        xml_root = etree.fromstring(text)

    etree.indent(xml_root, space=" ")

    ## write file
    open(outfile, "wb").write(
        etree.tostring(
            xml_root,
            doctype="<!DOCTYPE html>",
            encoding="UTF-8",
            method="xml",
            pretty_print=True,
            with_tail=False,
            xml_declaration=True,
        ),
    )


def work(line):
    data = list_regex.findall(line)[0]  # move to csv

    if len(data) == 2:
        print(data[1] + ":")
        parse(data[0], data[1])
    else:
        print("Invalid line! {}".format(line))


def parselist(listfile):
    file1 = open(listfile, "r")
    Lines = file1.readlines()

    start = time.monotonic()

    pool = ProcessPool(max_workers=12)  # 8
    result = pool.map(work, Lines)
    pool.shutdown()

    now = time.monotonic()

    print("Elapsed: {:.4}".format(now - start))


if __name__ == "__main__":
    if len(sys.argv) == 3:
        prepare()

        if sys.argv[1] == "--list":
            parselist(sys.argv[2])
        else:
            url = sys.argv[1]
            outfile = sys.argv[2]
            parse(url, outfile)

    else:
        print("Error invalid arguments!")
