import os

LOG_PATH = 'logs'

# 文件存储目录
# 动物名录表 存放目录
SOURCE_FILE_PATH = '动物名录.xls'

# html 存放目录
HTML_PATH = '/Users/joeyon/Desktop/files/原始网页'

# 修正后 json 存放目录
JSON_VERIFIED_PATH = '/Users/joeyon/Desktop/files/分词后的数据-json'
JSON_VERIFIED_PATH = '/Users/joeyon/PycharmProjects/tmp/2-分词后的数据-json'

# 原始 excel 存放目录
ORIGIN_EXCEL_PATH = '/Users/joeyon/Desktop/files/原始数据-excel'

# 分词后的 excel 存放目录
SLICED_EXCEL_PATH = '/Users/joeyon/Desktop/files/分词后的数据-excel'

# 每次请求等待时间
WAIT_TIME = (0, 5)

for p in [HTML_PATH, JSON_VERIFIED_PATH, ORIGIN_EXCEL_PATH, SLICED_EXCEL_PATH]:
    if not os.path.exists(p):
        os.makedirs(p)
