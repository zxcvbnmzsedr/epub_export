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