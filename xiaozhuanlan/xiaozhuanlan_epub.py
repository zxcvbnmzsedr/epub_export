import argparse
import os
import re
import uuid
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from ebooklib import epub


def parseNext(url, href_list, next_ids, headers, parent_content):
    toc_list_content = BeautifulSoup(parent_content, "html.parser")
    for post_link in toc_list_content.select("a[class~=topic-body-link]"):
        href_list.append(post_link.attrs['href'])

    for next_id in toc_list_content.select("[class~=xzl-topic-item]"):
        next_ids.append(next_id.attrs['data-topic-id'])

    next_request = requests.get(url, params={
        'load_more': True,
        'ids[]': next_ids
    }, headers=headers).content
    if '{"error":true}' in str(next_request):
        return
    parseNext(url, href_list, next_ids, headers, next_request)


def add_book(cookie, url, book):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'cookie': cookie
    }
    # 获取书籍目录
    result = requests.get(
        url=url,
        headers=headers
    )
    href_list = []
    parseNext(url, href_list, [], headers, result.content)
    # 生成目录
    i = 0
    all_count = len(href_list)
    for session in href_list:
        session_href = urljoin(url, session)
        i = i + 1
        # 生成章节
        section_info = requests.get(
            url=session_href,
            headers=headers
        ).content
        content_soup = BeautifulSoup(section_info, "html.parser")
        title = content_soup.select_one('.topic-title').text.strip()
        title = title.replace('/', '_')
        print(f'get section {title}   {session_href} 剩余 {i}/{all_count}')
        content = content_soup.select_one('#xzl-topic-content').prettify()
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
        section_id = session.replace('/', '_')
        c1 = epub.EpubHtml(title=title, content=s, file_name=section_id + '.xhtml', lang='en')
        # add chapter
        book.add_item(c1)
        book.spine.append(c1)
        book.toc.append(c1)


def html_template(html):
    template = open("xiaozhuanlan/template.html", 'rb').read().decode()
    h = template.replace('{0}', html)

    def filter_emoji(desstr, restr=''):
        # 过滤表情
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    return filter_emoji(h)


def parse(name, cookie, url, cover_url):
    file_name = "download/xiaozhuanlan/" + name + '.epub'
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
    add_book(cookie, url, book)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = open('xiaozhuanlan/style.css')
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

    parse(results.name, results.cookie, results.url, results.cover_url)
