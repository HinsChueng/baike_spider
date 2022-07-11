import json
import os
import re

from config import SLICED_EXCEL_PATH, HTML_PATH
from log import get_logger
from spider import BaiduHandler, WikiSpider, WikiHandler


def wiki():
    wiki_logger = get_logger('wiki')
    with open('未处理列表.txt') as f:
        kws = re.split(r'-\d\n', f.read())
        for kw in kws:
            html = WikiSpider().search_by_keyword(kw)
            data = WikiHandler().handle(html)
            if not data:
                wiki_logger.error(f'未找到：{kw}')

            fp = 'wiki'
            if not os.path.exists(fp):
                os.makedirs(fp)

            with open(f'{fp}/{kw}.html', 'w') as fw:
                fw.write(html)


baidu = BaiduHandler()

#
# fpath = 'files/分词后的数据-json-修正'
# for fname in os.listdir(fpath):
#     kw = fname.split('/')[-1].strip('.json')
#     with open(fpath + '/' + kw + '.json') as f:
#         baidu.write_to_excel(f'{SLICED_EXCEL_PATH}/{kw}.xlsx', **json.loads(f.read()))

text = '体躯强壮，光滑，头侧叶平截，眼较小，黑色，圆形。第1腹节下缘前部具长刚毛，第2、3腹节后腹角尖突，下缘具3～5个较大刺，第1～3腹节背后角具几个短毛。第4～6腹节背部各具两组短刺，第4节为3～5对，第5、6节为3～4对。尾节裂刻达叶长的2／3，叶末端钝圆，每侧有2刺，叶背面具1刺'
data = baidu.slice_text('', text)
print(json.dumps(data, ensure_ascii=False))


def update():
    root = '/Users/joeyon/PycharmProjects/tmp/2-分词后的数据-json'
    for file in os.listdir(root):
        name = file.replace('.json', '')
        with open(HTML_PATH + '/' + name + '.html') as f:
            html = f.read()
            baidu.handle(name, html)


update()
