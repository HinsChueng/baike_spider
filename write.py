import json
import os

from bs4 import BeautifulSoup

from common.file import write_to_excel, dict_to_list
from spider import BaiduHandler

PATH = '/Users/joeyon/Desktop/files/修正后的-json'

baidu = BaiduHandler()


def write_one(filename):
    keyword = filename.rstrip('.json')

    with open(PATH + '/' + filename) as f:
        try:
            json_data = json.loads(f.read())
            write_to_excel('/Users/joeyon/Desktop/files/分词后的数据-excel' + '/' + keyword + '.xlsx',
                           *dict_to_list(keyword, **json_data))

        except json.decoder.JSONDecodeError:
            print(filename)


def write_many():
    for filename in os.listdir(PATH):
        write_one(filename)


if __name__ == '__main__':
    # write_one('阿贝宽胸蝇虎.json')
    write_many()
