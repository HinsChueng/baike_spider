import re
from copy import deepcopy

from jieba import posseg

ROMAN_NUMS = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ'
NUMS = ''.join([str(i) for i in range(0, 10)])
CONN_CHARS = '几和及与至、-—－的除外'


def pack_single_sentence(text, delimiter='：'):
    item = text.lstrip('在')
    words = list(posseg.cut(item))
    i = 1

    while i < len(words) - 1:
        next_word = words[i].word
        if next_word in ROMAN_NUMS + NUMS + CONN_CHARS:
            i += 2
        else:
            break

    key = ''.join([w.word for w in words[:i]])
    value = ''.join([w.word for w in words[i:]]).lstrip('：:')

    if not key and not value:
        return {}

    return {delimiter.join([key, value]): {}}


def pack_sentence(paragraph, delimiter='：'):
    ret = dict()

    for item in re.split(r'[;；。]', paragraph):
        if not item:
            continue
        ret.update(pack_single_sentence(item, delimiter))

    return ret


def slice_habit_info(text):
    ret = dict()

    for item in re.split(r'[;；。]', text):
        if not item:
            continue

        if re.search(r'(以.*?为食)', item):
            ret[f'食物来源：{item}'] = dict()

        elif re.search(r'(模式产地)', item):
            ret[f'模式产地：{item}'] = dict()

        elif item.startswith('生活') or item.startswith('喜') or item.startswith('一般'):
            ret[f'生活环境：{item.lstrip("生活")}'] = dict()

        elif item.startswith('分布'):
            ret[f'分布范围：{item.lstrip("分布")}'] = dict()
        else:
            ret.update(pack_single_sentence(item))

    return ret


def slice_text_by_h2(h2_name, text):
    ret = dict()

    other_names = [
        '原始文献', '模式产地', '国内分布', '国外分布', '资料来源', '参考文献', '生境习性',
        '经济价值', '分布范围', '地理分布'
    ]
    if h2_name in other_names:
        for item in re.split('[；。;]', text):
            if not item:
                continue

            if '：' in item:
                ret[item] = dict()
            else:
                ret[f'{h2_name}：{item}'] = dict()

        return ret

    life_names = ['习性', '环境']
    for name in life_names:
        if name in h2_name:
            ret.update(slice_habit_info(text))
            break

    return ret


def slice_text(text):
    ret = dict()
    com = re.compile(r'(.{2,10})：.*')
    match_info = com.match(text)
    if not match_info:
        for sentence in text.split('。'):
            pack_info = pack_sentence(sentence)
            ret.update(pack_info)
    else:
        words = re.split(r'[；;。]', text)

        if len(words) < 3:
            ret[text] = {}
        else:
            key = match_info[1]
            ret[key] = dict()
            delimiter = '' if '标本' in key else '：'
            pack_info = pack_sentence(text.replace(key + '：', ''), delimiter)
            if '标本' in key:
                for k, _ in deepcopy(pack_info).items():
                    pack_info['标本：' + k] = pack_info.pop(k)

            ret[key].update(pack_info)

    return ret


def filter_string(text):
    for com in [
        re.compile(r'\s'),
        re.compile(r'\\xa0'),
        re.compile(r'\[\d]'),
        re.compile(r'’')
    ]:
        text = re.sub(com, '', text)

    return text
