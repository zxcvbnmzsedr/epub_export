import argparse
import os
import re
import uuid
from os.path import dirname, basename, join, splitext, abspath

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

from utils.parse import parseImg


def add_book(url, book):
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    epub_list = os.walk(join(PROJECT_ABSOLUTE_PATH, url))
    epub_html_list = []
    for path, dir_list, file_list in epub_list:
        for file_name in file_list:
            epub_path = os.path.join(path, file_name)
            # r, cover = main(epub_path, out_path)
            if os.path.splitext(epub_path)[-1] == ".html":
                epub_html_list.append({
                    'title': os.path.splitext(os.path.basename(epub_path))[0],
                    'path': epub_path
                })
    # 获取书籍目录
    epub_html_list.sort(key=lambda x: x['title'])

    # 生成目录
    i = 0
    all_count = len(epub_html_list)
    for session in epub_html_list:
        title = session['title']
        i = i + 1
        print(f'get section {title}   {title} 剩余 {i}/{all_count}')
        title = title.replace('/', '_')
        content = open(session['path']).read()
        content = parseImg(book, content)
        soup = BeautifulSoup(content, "html.parser")
        soup = soup.select_one(".article-con")
        s = html_template(f'{html_template(soup.prettify())}')
        # 修改html中的图片，整到本地环境中
        c1 = epub.EpubHtml(title=title, content=s, file_name=title + '.xhtml', lang='en')
        # add chapter
        book.add_item(c1)
        book.spine.append(c1)
        book.toc.append(c1)


def html_template(html):
    template = open("imooc_local/template.html", 'rb').read().decode()
    h = template.replace('{0}', html)

    def filter_emoji(desstr, restr=''):
        # 过滤表情
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    return filter_emoji(h)


def parse(name, url, cover_url):
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_name = join(PROJECT_ABSOLUTE_PATH, "download/imooc/" + name + '.epub')
    if os.path.exists(file_name):
        print(name + " 已经存在,跳过下载")
        return

    book = epub.EpubBook()

    book.set_identifier(name)
    book.set_title(name)
    book.set_language('cn')
    if cover_url:
        book.set_cover('cover', requests.get(cover_url).content)
    book.add_author(name)
    book.spine.append('nav')
    add_book(url, book)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = open('juejing/style.css')
    nav_css = epub.EpubItem(uid="style", file_name="style/style.css", media_type="text/css", content=style.read())

    book.add_item(nav_css)

    epub.write_epub(file_name, book, {})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cookie',
                        help='Cookie')
    parser.add_argument('-n', '--name',
                        help='Name the docset explicitly')
    parser.add_argument('--cover_url',
                        help='Set the file that is shown')
    parser.add_argument('url',
                        help='Directory containing the HTML documents')
    results = parser.parse_args()

    parse(results.name, results.url, results.cover_url)
