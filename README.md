# # ffxiv-classic-text-dump

仅为了从ffxiv 1.x的客户端内导出文本(包括中文)，用于考古、娱乐、休闲、健脑... 

## 使用环境
目前仅支持python3.5+，python2无法正常工作。
依赖项应该只有lxml，具体请参见requirements.txt

## 内容物简要说明
* utils.py
主要包括bytearray的一些转换函数以及一个UTF8的处理函数

* xml_decode.py
解密客户端内加密的xml文件，算法感谢[SeventhUmbral](https://github.com/jpd002/SeventhUmbral)的大佬

* data_types.py
主要定义了xml内容相关的一些结构，继续感谢[SeventhUmbral](https://github.com/jpd002/SeventhUmbral)的大佬

* data_utiles.py
主要的文件内容导出函数集，不解释

* export_sheets.py
导出基于01/03/00/00.DAT内的各文本文件

* ~~export_new_xml.py
导出上述之外，检索到的疑似xml（加密状态）的文件及其指向内容
需要new_xml_list.txt作为文件索引，可由find_all_xmls.py生成~~
合并至export_sheets.py中

* tag_type.py
* expression_type.py
* integer_type.py
* specials.py
主要用来处理文本中的特殊字符(以0x02开头,0x03结束的数据块)，感谢[SaintCoinach](https://github.com/ufx/SaintCoinach)项目中的相关部分，这个部分基本1.x跟ARR是通用的(虽然有部分类型要自己猜或者类型不太一样的地方)

* decode_client_scripts.py
解码客户端内的脚本(lua)，虽然解码后的lua依旧是类似混淆的状态（变量名替换)。

## 使用配置
需要配置data_utils.py内的BASE_DATA_PATH，以指向你本地FFXIV 1.x客户端中的data目录

## TODO（咕咕咕清单，简称沽清）
- ~~目前导出的内容中，有较多混乱的转移字符和字符串标记等，后续计划参考[SaintCoinach](https://github.com/ufx/SaintCoinach)的做法，解析过程中采用节点树的形式，最终统一输出。~~
- ~~在前一步的基础上，将Sheet类“函数”用到的表单优先解析，并进行字典化缓存。~~
- ~~在前一步的基础上，对非变量形式引用的Sheet类（SheetJa/SheetEN/SheetFr/SheetDe目前还不太理解，而且变量类型的为主，暂时无视）进行静态文本的替换，以便于阅读。~~
- 虽然实现方式与前述不同，并未整理节点树，但后几步还是实现了。所以。就这样吧。
