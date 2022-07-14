import json
import re

from animals import MiXia, ZhiHuanChong


def split_zu(text):
    data = MiXia().slice(text)
    return data


def split_gou(text):
    return ZhiHuanChong().slice(text)


name = '中央大钩'
text = """
交接管弯曲细长，基部扩大，管长依曲度0．1 2 5—0．1 70mm，基径0．007—0．008mm，近基部管径0．002mm，端径<0．00 1 mm；支持器呈弯曲片，长0．055—0．062mm，端部分3支，一支抱住交接管，另两支一短一长，均呈弯曲状.阴道管和卵未见.
"""
for text in text.split('。'):
    text = text.replace('\n', '')
    data = split_gou(text)
    # data = split_zu(text)
    data = json.dumps(data, ensure_ascii=False)

    print(data)
