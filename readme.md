### 百度百科爬虫

### 注意
本程序未对`动物名录.xls`文件做处理，有两种方法：  
* 删除无用的行，只保留自己需要解析的行
* 根据需要处理的行号，对读取excel的结果做切片处理


### 运行项目

##### 1、安装依赖:

```bash
pip install -r requirements.txt
```


##### 2、更新配置:

修改配置文件

```bash
vim config.py
```

```python
# 动物名录表 存放目录
SOURCE_FILE_PATH = '动物名录.xls'

# html 存放目录
HTML_PATH = 'files/原始网页'

# 修正后 json 存放目录
JSON_VERIFIED_PATH = 'files/分词后的数据-json'

# 原始 excel 存放目录
ORIGIN_EXCEL_PATH = 'files/原始数据-excel'

# 分词后的 excel 存放目录
SLICED_EXCEL_PATH = 'files/分词后的数据-excel'

# 每次请求等待时间
WAIT_TIME = (0, 5)
```


### 3、完善分词文件：`dictionary.txt`

1、作用：保证完整的词不被分割。  
2、用法：把需要保证完整的词添加到本文件中，每行一个词。

* 第一列：单词（必填）
* 第二列：词频（非必填，可以理解为优先级）
* 第三列：词性（非必填）


### 4、运行

1、修改`main.py`参数 --- key_word，即百度百科搜索关键字

```bash
vim main.py
```

2、执行脚本

```bash
python main.py
```


### 其他

1、运行后有问题的，统一记录在文件：`未处理列表.txt`，需要根据情况再做处理

* 格式：动物名称-问题代码
* 错误代码表：

| 错误代码 | 含义           |  
|------|--------------|
| 0    | 从文件读取并处理成功   |
| 1    | 从http读取并处理成功 |
| 2    | http错误       |
| 3    | 解析发生异常       |
| 4    | 百度验证机器人，网页异常 |
| 5    | 百度百科没有结果     |


