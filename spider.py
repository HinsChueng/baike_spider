import abc
import json
import re
import traceback
from copy import deepcopy

import jieba
import pandas
from bs4 import BeautifulSoup
from jieba import posseg

from config import ORIGIN_EXCEL_PATH, JSON_VERIFIED_PATH
from log import get_logger
from request import get_resp, GET

logger = get_logger(__name__)
jieba.load_userdict('dictionary.txt')

# 百度百科域名
BAIDU_BAIKE_DOMAIN = 'https://baike.baidu.com'
# 维基百科域名
WIKI_BAIKE_DOMAIN = 'https://zh.wikipedia.org'

headers = dict()
headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,' \
                    'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)' \
                        ' Chrome/103.0.5060.66 Safari/537.36 Edg/103.0.1264.44'


class Spider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def search_by_keyword(self, keyword):
        pass


class BaiduSpider(Spider):
    def search_by_keyword(self, keyword):
        url = f'{BAIDU_BAIKE_DOMAIN}/item/{keyword}'
        resp = get_resp(GET, url, headers=headers)
        html = getattr(resp, 'text', '')
        soup = BeautifulSoup(html, features='lxml')
        select_tag = soup.find('div', class_='lemmaWgt-subLemmaListTitle')
        if not select_tag:
            return html
        else:
            tag = soup.find('div', class_='para')
            url = f"{BAIDU_BAIKE_DOMAIN}{tag.a['href']}"
            resp = get_resp(GET, url, headers=headers)
            return getattr(resp, 'text', '')


class WikiSpider(Spider):
    def search_by_keyword(self, keyword):
        url = f'{WIKI_BAIKE_DOMAIN}/w/index.php?search={keyword}'
        resp = get_resp(GET, url, headers=headers)
        return getattr(resp, 'text', '')


class WikiHandler:
    @staticmethod
    def handle(html):
        soup = BeautifulSoup(html, features='lxml')
        no_result = soup.find('p', class_='mw-search-nonefound')
        if no_result:
            return False
        return True


class BaiduHandler:
    def get_summary(self, tag):
        # 信息概览
        summary_tag = tag.find('div', class_='lemma-summary')
        if summary_tag:
            text = self.filter_text(summary_tag)
            return {text: {}}, self.pack_sentence(text)

        return {}, {}

    @staticmethod
    def get_table(tag):
        ret = dict()
        table_tag = tag.select('table[log-set-param="table_view"]')
        if not table_tag:
            return ret

        for tr in table_tag[0].contents:
            content = tr.text
            remain_names = ['参考', '文献', '模式', '产地', '国内', '分布', '国外', '分布', '资料', '来源']

            for name in remain_names:
                if name in content:
                    ret[content] = {}

        return ret

    @staticmethod
    def get_title_name(tag, level):
        h = tag.find('h' + str(level))
        h_name = h.text
        child = getattr(h, 'span', None)
        if child:
            h_name = h.text.lstrip(child.text)

        return h_name

    @staticmethod
    def filter_text(tag):
        text = ''
        for t in tag.children:
            attrs = getattr(t, 'attrs', {})
            cls_list = attrs.get('class', [])
            if 'lemma-album' in cls_list:
                continue
            text += t.text

        for com in [
            re.compile(r'\s'),
            re.compile(r'\\xa0'),
            re.compile(r'\[\d-?\d?]'),
            re.compile(r'\(图\d{1,5}[a-z]?\)')
        ]:
            text = re.sub(com, '', text)

        return text

    @staticmethod
    def pack_sentence(paragraph, delimiter='：'):
        ret = dict()
        roman_nums = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ']
        nums = ''.join([str(i) for i in range(0, 10)])

        for item in re.split(r'[;；。]', paragraph):
            words = list(posseg.cut(item))
            i = 1
            while i < len(words) - 1:
                next_word = words[i].word
                if next_word in roman_nums or next_word in ['和', '、', '及', '与'] or next_word in nums:
                    i += 2
                else:
                    break

            key = ''.join([w.word for w in words[:i]])
            value = ''.join([w.word for w in words[i:]])

            if not key and not value:
                continue

            ret[delimiter.join([key, value])] = dict()

        return ret

    def slice_text(self, h2_name, text):
        if h2_name in ['原始文献', '模式产地', '国内分布', '国外分布', '资料来源', '地理分布', '参考文献']:
            return {f'{h2_name[2:]}：{v}': {} for v in re.split('[；。;]', text)[:-1]}

        elif h2_name == '分布范围':
            if '国内分布' in text or '国外分布' in text:
                return {text: {}}
            else:
                return {'分布：' + text: {}}

        ret = dict()
        com = re.compile(r'(.{2,10})：.*')
        match_info = com.match(text)
        if not match_info:
            for sentence in text.split('。'):
                pack_info = self.pack_sentence(sentence)
                ret.update(pack_info)
        else:
            words = re.split(r'[；;。]', text)

            if len(words) < 3:
                ret[text] = {}
            else:
                key = match_info[1]
                ret[key] = dict()
                delimiter = '' if '标本' in key else '：'
                pack_info = self.pack_sentence(text.lstrip(key + '：'), delimiter)
                if '标本' in key:
                    for k, _ in deepcopy(pack_info).items():
                        pack_info['标本：' + k] = pack_info.pop(k)

                ret[key].update(pack_info)

        return ret

    @staticmethod
    def filter(text):
        for com in [
            re.compile(r'\s'),
            re.compile(r'\\xa0'),
            re.compile(r'\[\d]'),
            re.compile(r'’')
        ]:
            text = re.sub(com, '', text)
        return text

    def get_main_body_dict(self, tag):
        origin, sliced = dict(), dict()
        h2_name, h3_name = '', ''

        # class如果有多个，只能根据第一个来查找
        tag = tag.find('div', class_='para-title')

        while True:
            try:
                tag_attrs = getattr(tag, 'attrs', {})
                tag_cls_list = tag_attrs.get('class', [])
                if not tag_cls_list:
                    continue

                tag_name = ' '.join(tag_cls_list)

                if tag_name.startswith('para-title level-2'):
                    h2_name = self.get_title_name(tag, 2)
                    origin[h2_name] = {}
                    sliced[h2_name] = {}

                elif tag_name.startswith('para-title level-3'):
                    h3_name = self.get_title_name(tag, 3)
                    origin[h2_name][h3_name] = {}
                    sliced[h2_name][h3_name] = {}

                elif tag_name == 'para':
                    content = self.filter_text(tag)
                    sliced_info = self.slice_text(h2_name, content)
                    if not content:
                        continue

                    if not h3_name:
                        origin[h2_name][content] = {}
                        sliced[h2_name].update(sliced_info)
                    else:
                        if h3_name in origin[h2_name]:
                            origin[h2_name][h3_name][content] = {}
                            sliced[h2_name][h3_name].update(sliced_info)
                        else:
                            origin[h2_name][h3_name] = {content: {}}
                            sliced[h2_name][h3_name] = sliced_info
            except Exception as e:
                print(e)
                logger.error(traceback.format_exc())
            finally:
                tag = getattr(tag, 'next_sibling', None)
                if not tag:
                    break

        return origin, sliced

    @staticmethod
    def dict_to_list(keyword, **kwargs):
        write_list = []
        header = ['中文名称']
        row_count = 0

        for _, data in kwargs.items():
            for h2, h2_data in data.items():
                row_count = 1 if row_count <= 1 else row_count
                if not h2_data:
                    write_list.append([keyword, h2])
                else:
                    for h3, h3_data in h2_data.items():
                        row_count = 2 if row_count <= 2 else row_count
                        if not h3_data:
                            write_list.append([keyword, h2, h3])
                        else:
                            for content, _ in h3_data.items():
                                row_count = 3 if row_count <= 3 else row_count
                                write_list.append([keyword, h2, h3, content])

        header.extend(['' for _ in range(row_count)])

        return header, write_list

    @staticmethod
    def write_to_excel(file_path, header, data_list):
        with pandas.ExcelWriter(file_path, mode='w+') as writer:
            df = pandas.DataFrame(data_list)
            df.to_excel(writer, index=False, header=header)
            logger.info(f'写入成功：{file_path}')

    @staticmethod
    def write_to_file(file_path, data: str):
        with open(file_path, 'w') as f:
            f.write(data)
            logger.info(f'写入成功：{file_path}')

    def handle(self, keyword, html):
        soup = BeautifulSoup(html, features='lxml')
        no_result = soup.find('div', class_='errorBox')
        if no_result:
            return {}

        content_tag = soup.find('div', class_='content')

        # 概述
        origin_summary, sliced_summary = self.get_summary(content_tag)
        # 表格
        table = self.get_table(content_tag)
        # 详细信息
        origin, sliced = self.get_main_body_dict(content_tag)

        sliced_result = {'summary': sliced_summary, 'main_body': sliced, 'table': table}
        self.write_to_file(f'{JSON_VERIFIED_PATH}/{keyword}.json', json.dumps(sliced_result, ensure_ascii=False))

        origin_result = {'summary': origin_summary, 'main_body': origin, 'table': table}
        header, data_list = self.dict_to_list(keyword, **origin_result)
        self.write_to_excel(f'{ORIGIN_EXCEL_PATH}/{keyword}.xlsx', header, data_list)

        return sliced_result
