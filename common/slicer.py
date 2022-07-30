import re
from copy import deepcopy

import jieba

ROMAN_NUMS = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ'
NUMS = ''.join([str(i) for i in range(0, 10)])
CONN_CHARS = '其几和及与至、-—－的之各除外'


def update(data, update_data):
    for k, v in update_data.items():
        if k in data:
            data[k].update(v)
        else:
            data[k] = v
    return data


def sentence_to_kv(words):
    i = 1

    while i < len(words) - 1:
        next_word = words[i]

        if words[i - 1].endswith('长') and re.search(r'(\d)', next_word):
            break

        if next_word in ROMAN_NUMS + NUMS + CONN_CHARS:
            i += 2
        else:
            break

    key = ''.join([w for w in words[:i]])
    value = ''.join([w for w in words[i:]]).lstrip('：:')

    tmp = re.match(r'(.*?)(\d[个枚对])', key)
    if tmp:
        key = tmp[1]
        value = tmp[2] + value

    return key, value


def pack_single_sentence(text, delimiter='：'):
    item = text.lstrip('在')

    count_com = re.compile(r'[共有具].*?个(.*?)[，,]')
    data = count_com.search(text)
    if data:
        key = data[1]
        value = text
    elif '雌雄异体' in text:
        key = '性别特征'
        value = text
    else:
        words = list(jieba.cut(item))
        key, value = sentence_to_kv(words)

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

        elif '分布' in item and '：' not in item:
            ret[f'分布范围：{item.lstrip("分布")}'] = dict()

        elif item.startswith('淡水'):
            ret[f'水质条件：{item}'] = dict()

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
            update(ret, slice_habit_info(text))
            break

    return ret


def slice_text(text):
    ret = dict()
    com = re.compile(r'(.{2,10})：.*')
    match_info = com.match(text)
    if not match_info:
        for sentence in text.split('。'):
            pack_info = pack_sentence(sentence)
            update(ret, pack_info)
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

            ret[key] = update(ret[key], pack_info)

    return ret


def get_k_end(start, words):
    m = start + 1
    while m < len(words) and words[m] in '、-—－':
        m += 2
    return m


def get_k_v(a, b, words, organ_list):
    if words[a] in organ_list:
        c = get_k_end(a, words)
        k = "".join(words[a: c])
        v = "".join(words[c:b])
    else:
        v = ''.join(words[a:b])
        k = '形态'
        if re.search(r'([黄褐红黑色])', v):
            k = '颜色'
        elif v.endswith('形'):
            k = '形状'

        count_com = re.compile(r'[共有具].*?个(.*?)[，,]')
        data = count_com.search(v)
        if data:
            k = data[0]

    v = v.lstrip('的').rstrip(',，；;。.')
    return k, v


def org_match(word, org_list):
    for org in org_list:
        info = re.match(org, word)
        if info:
            return True

    return False


def slice_organ(organ_text, organ_list):
    data = dict()

    if not organ_text:
        return data

    jieba.suggest_freq(organ_list, True)
    for w in organ_list:
        jieba.add_word(w)

    organ_text = organ_text.replace('． ', '.')
    words = list(jieba.cut(organ_text))

    i, j = 1, 0

    while i < len(words):
        if org_match(words[i], organ_list) and words[i - 1] in ',，;；、。':
            if i != 0:
                k, v = get_k_v(j, i, words, organ_list)
                data['：'.join([k, v])] = {}
            j = i

        i += 1

    k, v = get_k_v(j, i, words, organ_list)
    data['：'.join([k, v])] = {}

    return data


def slice_organs(organ_text, organ_list):
    ret = dict()

    for item in re.split(r'[;；]', organ_text):
        ret.update(slice_organ(item, organ_list))

    return ret
