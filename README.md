# 导出平台内容到EPUB

## 安装虚拟环境和依赖
```shell
git clone https://github.com/zxcvbnmzsedr/py_epub.git
cd py_epub
python3 -m venv penv
cd penv && source ./bin/activate && cd ..
python3 install -r requirements.txt
```
## 语雀

```shell
python yuque_epub.py -c cookie -n 名称 语雀知识库的url地址
```

## 掘金

```shell
python juejing_epub.py -c cookie -n 名称 book_id
```

当然，用命令行导入cookie有点麻烦
所以也可以用config文件进行导入

```yaml
juejing:
  cookie: ''
  books:
    - name: MySQL是怎样运行的
      book_id: '6844733769996304392'

yuque:
  cookie: ''
  books:
    - name: Java面试指南
      url: 'https://www.yuque.com/books/share/04ac99ea-7726-4adb-8e57-bf21e2cc7183'
```

```shell
python main.py
```