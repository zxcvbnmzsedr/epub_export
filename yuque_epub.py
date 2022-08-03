import argparse
import json
import os
import re
import uuid
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from ebooklib import epub


def add_book(cookie, yuque_main_url, book):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'cookie': cookie
    }

    resp = requests.get(url=yuque_main_url,
                        headers=headers)

    content_regx = r'(?<=decodeURIComponent\(\").*?(?=\"\))'
    conent_json_str = unquote(re.search(content_regx, resp.content.decode()).group(0))
    content_json = json.loads(conent_json_str)
    tocs = content_json['book']['toc']
    i = 0
    for toc in tocs:
        u_id = toc['uuid']
        toc_url = yuque_main_url + '/' + toc['url']
        headers['referer'] = yuque_main_url + '/' + toc_url
        toc_content_result = requests.get(url=toc_url,
                                          headers=headers)
        toc_content_result_str = unquote(re.search(content_regx, toc_content_result.content.decode()).group(0))
        toc_content = json.loads(toc_content_result_str)
        toc_content_html = toc_content['doc']['_cachedContent']['_cache_decrypted_body']
        title = toc_content['doc']['title']
        i = i + 1
        print(f"正在下载 {title} 剩余 {i}/{len(tocs)}")
        toc_content_html = toc_content_html.replace('<!doctype html>', '')

        soup = BeautifulSoup(toc_content_html, "html.parser")

        for img in soup.select('img'):
            img_src = img.attrs['src']
            try:
                if img.has_attr('id'):
                    img_id = 'img' + img.attrs['id']
                    r = requests.get(img_src, headers)
                else:
                    img_id = str(uuid.uuid1())
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

        s = html_template(f'<h1>{title}</h1>{soup.prettify()}')
        # 修改html中的图片，整到本地环境中
        c1 = epub.EpubHtml(title=title, content=s, file_name=u_id + '.xhtml', lang='en')
        # add chapter
        book.add_item(c1)
        book.spine.append(c1)

    toc_tree = toc_list_to_tree(tocs)
    book_add_toc_tree(book, toc_tree)
    # result = book_add_toc_tree2(toc_tree)
    # print(result)
    # book.toc = result


# def book_add_toc_tree2(toc_tree):
#     results = []
#     for toc in toc_tree:
#
#         if toc['children']:
#             results.append(
#                 (
#                     epub.Link(title=toc['title'], href=toc['uuid'] + '.xhtml'),
#                     book_add_toc_tree2(toc['children'])
#                 )
#             )
#
#         else:
#             results.append(
#                 epub.Link(title=toc['title'], href=toc['uuid'] + '.xhtml')
#             )
#     return results


def book_add_toc_tree(book, toc_tree):
    for toc in toc_tree:
        if toc['children']:
            toc_child_chapter = []
            for toc_child in toc['children']:
                u_id = toc_child['uuid']
                title = toc_child['title']
                toc_child_chapter.append(epub.Link(u_id + '.xhtml', title, u_id))
            book.toc.append(
                (
                    epub.Link(title=toc['title'], href=toc['uuid'] + '.xhtml'),
                    toc_child_chapter
                )
            )
        else:
            book.toc.append(epub.Link(title=toc['title'], href=toc['uuid'] + '.xhtml', uid=toc['uuid']))


def toc_list_to_tree(data):
    root = []
    node = []

    # 初始化数据，获取根节点和其他子节点list
    for d in data:
        if d.get("parent_uuid") == '':
            root.append(d)
        else:
            node.append(d)
    # 查找子节点
    for p in root:
        add_node(p, node)

    # 无子节点
    if len(root) == 0:
        return node

    return root


def add_node(p, node):
    # 子节点list
    p["children"] = []
    for n in node:
        if n.get("parent_uuid") == p.get("uuid"):
            p["children"].append(n)

    # 递归子节点，查找子节点的节点
    for t in p["children"]:
        if not t.get("children"):
            t["children"] = []
        t["children"].append(add_node(t, node))

    # 退出递归的条件
    if len(p["children"]) == 0:
        return


def html_template(html):
    template = open("yuyuqe.html", 'rb').read().decode()
    h = template.replace('{0}', html)

    def filter_emoji(desstr, restr=''):
        # 过滤表情
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)

    return filter_emoji(h)


def parse(name, cookie, url):
    file_name = "download/" + name + '.epub'
    if os.path.exists(file_name):
        print(name + " 已经存在,跳过下载")
        return
    book = epub.EpubBook()

    book.set_identifier(name)
    book.set_title(name)
    book.set_language('cn')

    book.add_author(name)
    book.spine.append('nav')
    add_book(cookie, url, book)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)

    # write to the file
    epub.write_epub(file_name, book, {})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cookie',
                        help='Cookie')

    parser.add_argument('-n', '--name',
                        help='Name the docset explicitly')
    parser.add_argument('-d', '--destination',
                        dest='path',
                        default='',
                        help='Put the resulting docset into PATH')
    parser.add_argument('-i', '--icon',
                        dest='filename',
                        help='Add PNG icon FILENAME to docset')
    parser.add_argument('-p', '--index-page',
                        help='Set the file that is shown')
    parser.add_argument('url',
                        help='Directory containing the HTML documents')
    results = parser.parse_args()

    parse(results.name, results.cookie, results.url)
