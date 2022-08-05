import argparse
import os
import re
import uuid

import requests
from bs4 import BeautifulSoup
from ebooklib import epub


def add_book(cookie, book_id, book):
    # 获取书籍目录
    result = requests.post(
        url='https://api.juejin.cn/booklet_api/v1/booklet/get?',
        json={
            'booklet_id': book_id
        }
    ).json()
    # 生成目录
    i = 0
    all_count = len(result['data']['sections'])
    for session in result['data']['sections']:
        section_id = session['section_id']
        title = session['title']
        title = title.replace('/', '_')
        i = i + 1
        print(f'get section {title}   {section_id} 剩余 {i}/{all_count}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'cookie': cookie
        }
        # 生成章节
        section_info = requests.post(
            url='https://api.juejin.cn/booklet_api/v1/section/get',
            json={
                'section_id': section_id
            },
            headers=headers
        ).json()
        section = section_info['data']['section']
        content = section['content']
        soup = BeautifulSoup(content, "html.parser")

        for img in soup.select('img'):
            img_src = img.attrs['src']
            img_id = str(uuid.uuid1())
            if not img_src.startswith('http'):
                img_src = 'http:' + img_src
            try:
                r = requests.get(img_src)
                # open(doc_path + "/" + img_id, 'wb').write(r.content)
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

        s = html_template(f'<h1>{title}</h1>{html_template(soup.prettify())}')
        # 修改html中的图片，整到本地环境中
        c1 = epub.EpubHtml(title=title, content=s, file_name=section_id + '.xhtml', lang='en')
        # add chapter
        book.add_item(c1)
        book.spine.append(c1)
        book.toc.append(c1)


def html_template(html):
    template = open("juejing/template.html", 'rb').read().decode()
    h = template.replace('{0}', html)

    def filter_emoji(desstr, restr=''):
        # 过滤表情
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    return filter_emoji(h)


def parse(name, cookie, book_id, cover_url):
    file_name = "download/" + name + '.epub'
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
    add_book(cookie, book_id, book)

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
    parser.add_argument('book_id',
                        help='Directory containing the HTML documents')
    results = parser.parse_args()

    parse(results.name, results.cookie, results.book_id,results.cover_url)
