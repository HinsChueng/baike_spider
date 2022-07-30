import functools
import json
import os.path
import random
import time
import traceback

import pandas
from bs4 import BeautifulSoup

from common.file import write_to_file, write_to_excel
from config import HTML_PATH, WAIT_TIME, SOURCE_FILE_PATH
from spider import BaiduSpider, BaiduHandler
from common.log import get_logger

baidu_spider = BaiduSpider()
baidu_handler = BaiduHandler()

logger = get_logger(__name__)
error_logger = get_logger(__name__ + '_error')

# 从文件读取并处理成功
FILE_SUC = 0
# 从http读取并处理成功
HTTP_SUC = 1
# http错误
HTTP_WRONG = 2
# 解析发生异常
HANDlE_FAILED = 3
# 百度验证机器人，网页异常
HTML_WRONG = 4
# 百度百科没有结果
BAIKE_NO_RESULT = 5


def handle_one(keyword):
    html_path = f'{HTML_PATH}/{keyword}.html'
    if os.path.isfile(html_path):
        with open(html_path, 'r') as f:
            html = f.read()
            handle_result = FILE_SUC
    else:
        html = baidu_spider.search_by_keyword(keyword)
        if not html:
            logger.error(f'向百度百科发起请求时发生http错误： {keyword}\n')
            return HTTP_WRONG

        write_to_file(html_path, html)
        handle_result = HTTP_SUC

    soup = BeautifulSoup(html, features='lxml')
    if '验证' in soup.title.text:
        error_logger.error(f'从百科获取数据时遇到了反爬：{keyword}')
        error_logger.error(f'删除html：{html_path}')
        os.remove(html_path)

        return HTML_WRONG

    try:
        handle_info = baidu_handler.handle(keyword, html)
        if not handle_info:
            error_logger.error(f'百度百科没有相关结果：{keyword}')
            return BAIKE_NO_RESULT

    except Exception as e:
        error_logger.error(f'解析html时发生错误：{keyword}')
        error_logger.error(traceback.format_exc())
        print(e)
        return HANDlE_FAILED

    return handle_result


def after_handle(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        logger.info(f'全部处理完成！共处理 {len(args)}个，其中 :')
        logger.info(f'{len(result[HTTP_SUC])} 个通过【http请求】获取并【成功】解析数据')
        logger.info(f'{len(result[FILE_SUC])} 个通过【本地文件】获取并【成功】解析数据')
        logger.info(f'{len(result[HTML_WRONG])} 个从百科获取数据时遇到了反爬，【失败】')
        logger.info(f'{len(result[HANDlE_FAILED])} 个解析html【失败】')
        logger.info(f'{len(result[HTTP_WRONG])} 个向百度百科发起请求时发生http错误，【失败】')
        logger.info(f'{len(result[BAIKE_NO_RESULT])} 个百度百科【没有相关结果】')

        write_to_excel('未处理名录.xlsx', ['中文名称'], result[BAIKE_NO_RESULT])

        with open('处理结果合计.json', 'w') as f:
            f.write(json.dumps(result, ensure_ascii=False))

        return result

    return inner


@after_handle
def handle_many(keywords):
    result = {k: [] for k in [HTTP_SUC, FILE_SUC, HTML_WRONG, HANDlE_FAILED, HTTP_WRONG, BAIKE_NO_RESULT]}

    for i, kw in enumerate(keywords, start=1):
        logger.info(f'开始处理第{i}个： {kw}')
        flag = handle_one(kw)

        if flag == HTTP_SUC:
            wait_time = random.randint(*WAIT_TIME)
            logger.info(f'等待：{wait_time}s')
            time.sleep(wait_time)

        result[flag].append(kw)
        logger.info(f'第{i}个处理完成： {kw}\n')

    return result


def run():
    keywords = list()
    data = pandas.read_excel(SOURCE_FILE_PATH, sheet_name=0, usecols=[1], header=None)

    for i, item in enumerate(data.values):
        name = item[0].replace('[虫责]', '')
        keywords.append(name)

    handle_many(keywords)


if __name__ == '__main__':
    run()
