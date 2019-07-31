# # ffxiv-classic-text-dump

仅为了从ffxiv 1.x的客户端内导出文本(包括中文)，用于考古、娱乐、休闲、健脑... 

## 使用环境
目前仅支持python3，python2无法正常工作。
依赖项应该只有lxml，具体请参见requirements.txt

## 内容物简要说明
- utils.py
主要包括bytearray的一些转换函数以及一个UTF8的处理函数

- xml_decode.py
解密客户端内加密的xml文件，算法感谢[SeventhUmbral](https://github.com/jpd002/SeventhUmbral)的大佬

- data_types.py
主要定义了xml内容相关的一些结构，继续感谢[SeventhUmbral](https://github.com/jpd002/SeventhUmbral)的大佬

- data_utiles.py
主要的文件内容导出函数集，不解释

- export_sheets.py
导出基于01/03/00/00.DAT内的各文本文件

- export_new_xml.py
导出上述之外，检索到的疑似xml（加密状态）的文件及其指向内容
需要new_xml_list.txt作为文件索引，可由find_all_xmls.py生成

- specials.json
由于文本中有各种非可读的占位符和特殊内容（比如对话框换页、换行，或者玩家名字替换等），均尝试在这里记录，并在收集足够内容后，尝试在dump时进行替换


## 使用配置
需要配置data_utils.py内的BASE_DATA_PATH，以指向你本地FFXIV 1.x客户端中的data目录
