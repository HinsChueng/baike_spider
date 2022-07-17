import abc
import json
import re
import traceback

import jieba
from bs4 import BeautifulSoup

from animals import slice_text_by_animal_org
from common.file import write_to_file, dict_to_list, write_to_excel
from common.log import get_logger
from common.request import get_resp, GET
from common.slicer import slice_text, slice_text_by_h2, slice_habit_info, update
from config import ORIGIN_EXCEL_PATH, JSON_VERIFIED_PATH

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

        text = text.replace('第工', '第Ⅰ')
        text = text.replace('第l', '第1')
        return text

    def get_summary(self, tag):
        # 信息概览
        summary_tag = tag.find('div', class_='lemma-summary')
        if not summary_tag:
            return {}, {}

        text = self.filter_text(summary_tag)

        return {text: {}}, slice_habit_info(text)

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

    def get_main_body_dict(self, tag, keyword):
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
                    if not content:
                        continue

                    sliced_info = slice_text_by_h2(h2_name, content)
                    if not sliced_info:
                        sliced_info = slice_text_by_animal_org(keyword, content)
                    if not sliced_info:
                        sliced_info = slice_text(content)

                    if not h3_name:
                        origin[h2_name][content] = {}
                        data = update(sliced[h2_name], sliced_info)
                        sliced[h2_name].update(data)
                    else:
                        data = update(sliced[h2_name].get(h3_name, {}), sliced_info)

                        if h3_name in origin[h2_name]:
                            origin[h2_name][h3_name][content] = {}
                            sliced[h2_name][h3_name].update(data)
                        else:
                            origin[h2_name][h3_name] = {content: {}}
                            sliced[h2_name][h3_name] = data
            except Exception as e:
                print(e)
                logger.error(traceback.format_exc())
            finally:
                tag = getattr(tag, 'next_sibling', None)
                if not tag:
                    break

        return origin, sliced

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
        origin, sliced = self.get_main_body_dict(content_tag, keyword)

        sliced_result = {'summary': sliced_summary, 'main_body': sliced, 'table': table}
        write_to_file(f'{JSON_VERIFIED_PATH}/{keyword}.json', json.dumps(sliced_result, ensure_ascii=False))

        origin_result = {'summary': origin_summary, 'main_body': origin, 'table': table}
        header, data_list = dict_to_list(keyword, **origin_result)
        write_to_excel(f'{ORIGIN_EXCEL_PATH}/{keyword}.xlsx', header, data_list)

        return sliced_result
