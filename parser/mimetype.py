def file_extension(text):
    ## jpeg/jpg
    if text[0:4] == b"\xFF\xD8\xFF\xE0":
        return ".jpg"
    elif text[0:4] == b"\xFF\xD8\xFF\xDB":
        return ".jpg"
    elif text[0:4] == b"\xFF\xD8\xFF\xEE":
        return ".jpg"
    elif text[0:4] == b"\xFF\xD8\xFF\xE1":
        return ".jpg"
    elif text[0:4] == b"\xFF\xD8\xFF\xE2":
        return ".jpg"

    ## webp
    elif text[8:12] == b"WEBP":
        return ".webp"

    ## png
    elif text[0:4] == b"\x89PNG":
        return ".png"

    ## fallback jpg
    elif text[0:3] == b"\xFF\xD8\xFF":
        return ".jpg"

    ## else
    else:
        return None
