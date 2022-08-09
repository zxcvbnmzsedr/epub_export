import yaml
import juejing.juejing_epub
import yuque.yuque_epub
import xiaozhuanlan.xiaozhuanlan_epub

if __name__ == '__main__':
    with open("config.yaml", "r") as f:
        ayml = yaml.load(f.read(), Loader=yaml.Loader)
        print("load config success " + str(ayml))
        if 'juejing' in ayml:
            juejing_config = ayml['juejing']
            cookie = juejing_config['cookie']
            for book in juejing_config['books']:
                print('开始下载掘金 ' + book['name'])
                juejing.juejing_epub.parse(name=book['name'], cookie=juejing_config['cookie'], book_id=book['book_id'],
                                           cover_url=book.get('cover_url'))
        if 'yuque' in ayml:
            juejing_config = ayml['yuque']
            cookie = juejing_config['cookie']
            for book in juejing_config['books']:
                print('开始下载语雀 ' + book['name'])
                yuque.yuque_epub.parse(name=book['name'], cookie=juejing_config['cookie'], url=book['url'],
                                       cover_url=book['cover_url'])
        if 'xiaozhuanlan' in ayml:
            juejing_config = ayml['xiaozhuanlan']
            cookie = juejing_config['cookie']
            for book in juejing_config['books']:
                print('开始下载小专栏 ' + book['name'])
                xiaozhuanlan.xiaozhuanlan_epub.parse(name=book['name'], cookie=juejing_config['cookie'],
                                                     url=book['url'],
                                                     cover_url=book['cover_url'])
