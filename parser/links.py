import httpx
from lxml import html
import sys
import os
import html5_parser

import mimetype

## config

use_counters = True

## end config

## httpx
httpx_client = httpx.Client(http2=True)

if __name__ == "__main__":
    assert len(sys.argv) > 2

    if len(sys.argv) > 2:
        url = sys.argv[1]
        outfile = sys.argv[2]

    body = httpx_client.get(url, follow_redirects=True).content

    # html parsing
    tree = html5_parser.parse(body, treebuilder="lxml_html", fallback_encoding="utf-8")

    if os.path.exists(outfile):
        value = input("Output file already exists! Overwrite? [Y/n] ")
        if value == "Y" or "y":
            os.remove(outfile)
        else:
            exit()

    with open(outfile, "a") as outstream:
        volume = None
        counter_volume = 0
        counter_chapter = 0

        os.makedirs("Text/", exist_ok=True)

        title = tree.xpath("/html/body/div[1]//h1")[0].text

        ## cover
        img = tree.xpath('//*[@id="Info"]/div[1]/div[1]/div/div[1]/div/img')[-1]
        imgsrc = img.get("src")
        if len(imgsrc) > 0:
            os.makedirs("Images/", exist_ok=True)

            imgurl = None
            if imgsrc[0] == "/":
                imgurl = "http://tl.rulate.ru{}".format(imgsrc)
            else:
                imgurl = imgsrc

            raw = httpx_client.get(imgurl, follow_redirects=True)
            if raw.content[0:15] != b"<!DOCTYPE html>":
                # imgname = 'cover' + mimetype.file_extension(raw.content)
                imgname = "%s%s" % ("cover", mimetype.file_extension(raw.content))
                open("Images/{}".format(imgname), "wb").write(raw.content)

                ## cover.xhtml
                open("Text/ccover.xhtml", "w").write(
                    '<?xml version="1.0" encoding="utf-8"?>\n'
                    '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                    " <head>\n"
                    "  <title>Обложка</title>\n"
                    " </head>\n"
                    " <body>\n"
                    '  <div style="text-align: center; padding: 0pt; margin: 0pt;">\n'
                    '   <img src="../Images/{0}" alt="x{0}"/>\n'
                    "  </div>\n"
                    " </body>\n"
                    "</html>\n".format(imgname)
                )

        ## main?
        for td in tree.xpath('//*[@id="Chapters"]/tbody/tr/td'):
            ## volumes
            st = td.xpath("strong")
            if len(st) > 0:
                volume = st[0].text
                if use_counters:
                    counter_volume += 1
                    counter_chapter = 0
                    open("Text/chapter-{}-0.xhtml".format(counter_volume), "w").write(
                        '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                        " <head>\n"
                        "  <title>{}</title>\n"
                        " </head>\n"
                        " <body>\n"
                        '  <h1 style="text-align: center;">{}</h1>\n'
                        " </body>\n"
                        "</html>\n".format(volume, volume)
                    )

            ## chapters
            a = td.xpath("a")
            if len(a) > 0:
                if a[0].get("class") != "btn btn-small btn-info":
                    link = a[0].get("href")
                    if use_counters:
                        counter_chapter += 1
                        outstream.write(
                            '"https://tl.rulate.ru{}", "Text/chapter-{}-{}.xhtml"\n'.format(
                                link, counter_volume, counter_chapter
                            )
                        )

                    else:
                        name = a[0].text
                        outstream.write(
                            '"https://tl.rulate.ru{}", "Text/chapter-{}-{}.xhtml"\n'.format(
                                link, volume.replace(" ", "_"), name.replace(" ", "_")
                            )
                        )
