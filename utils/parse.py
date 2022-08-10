import requests
from bs4 import BeautifulSoup
import uuid

from ebooklib import epub


def parseImg(book, content):
    soup = BeautifulSoup(content, "html.parser")
    for img in soup.select('img'):
        img_src = img.attrs['src']
        img_id = str(uuid.uuid1())
        if not img_src.startswith('http'):
            img_src = 'http:' + img_src
        try:
            r = requests.get(img_src)
            img['src'] = img_id
            epub_image = epub.EpubImage()
            epub_image.content = r.content
            epub_image.id = img_id
            epub_image.file_name = img_id
            epub_image.media_type = 'image/jpg'
            book.add_item(epub_image)
        except Exception as e:
            print('图片下载失败 ' + img.attrs['src'])
            print(e)
    return soup.prettify()
