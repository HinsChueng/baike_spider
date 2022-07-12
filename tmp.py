import json

from spider import MiXia

from spider import ZhiHuanChong


def split_zu(text):
    data = MiXia().slice(text)
    return data


def split_gou(name, text):
    return ZhiHuanChong().handle_measure_info(name, text)


name = '中央大钩'
text = """

"""
for text in text.split('。'):
    data = split_gou(name, text)
    text = text.replace('\n', '')
    # data = split_zu(text)
    data = json.dumps(data, ensure_ascii=False)

    print(data)
