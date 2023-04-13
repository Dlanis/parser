relist = [
    [R"http://tl.rulate.ru/book/\d+/\d+", R""],
    [R"<p>\s*</p>", R""],
    [R"<p/>", R""],
    [R"background-color:[\w;#]{1,16}", R""],
    [R"color:[\w;#]{1,16}", R""],
    [R"mso-ansi-language:\s{0,1}\w{0,16};", R""],
    [R"line-height:\s{0,32}[\d%]{0,32};", R""],
    [R"font-family:\s{0,32}[\w\W]{0,32};", R""],
    [R'\s*style="\s*"', R""],
    # [R'<span>|</span>', R''],
    [R">[\s\n]*<", R"><"],
]
