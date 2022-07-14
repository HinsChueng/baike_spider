import functools
import traceback

from bs4 import BeautifulSoup
from requests import exceptions
from requests.api import request

from common.log import get_logger

logger = get_logger(__name__)

GET = 'GET'
POST = 'POST'
OPTIONS = 'OPTIONS'
HEAD = 'HEAD'
PUT = 'PUT'
PATCH = 'PATCH'
DELETE = 'DELETE'


def retry(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        i = 1
        while i <= 5:
            try:
                resp = func(*args, **kwargs)
                soup = BeautifulSoup(resp.text, features='lxml')
                if '验证' in soup.title.text:
                    logger.error(f'获取页面失败：{args}')
                    i += 1
                else:
                    return resp
            except Exception as e:
                logger.error(f'请求错误：{e}')
                logger.error(str(args))
                logger.error(str(kwargs))
                logger.error(traceback.format_exc())
                i += 1

            return

    return inner


@retry
def get_resp(method, url, data=None, headers=None, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10

    if method not in [GET, POST, OPTIONS, HEAD, PUT, PATCH, DELETE]:
        raise exceptions.InvalidSchema(f'请求方式错误，method={method}：\nurl={url}\ndata={data}')

    if method == GET:
        kwargs['params'] = data
    elif method == POST:
        kwargs['data'] = data
    resp = request(method, url=url, headers=headers, **kwargs)
    if resp.status_code != 200:
        raise exceptions.HTTPError(f'请求状态错误，status={resp.status_code}：\nurl={url}\nmethod={method}\ndata={data}')

    return resp
