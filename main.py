import time
import os

import pandas as pd

import config
import SpiderDB
import requests
import lxml.etree as etree
import functools
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


def parse(func):
    @functools.wraps(func)
    def inner(self):
        html_res = etree.HTML(self.html)
        result = html_res.xpath(func(self))
        return result

    return inner


class ParseHtml:
    def __init__(self, this_html):
        self.html = this_html

    @parse
    def get_src(self):
        """

        :return: 页面下所有a标签的href
        """
        return "//a/@href"

    @parse
    def get_title(self):
        """
        获取页面标题
        :return:
        """
        return "//head/title/text()"


class SpiderGetResponse:
    def __init__(self, url,  this_save_path):
        self.url = url
        self.headers = config.Headers
        self.proxy = config.Proxy
        self.this_save_path = this_save_path
        if not os.path.exists('数据'):
            os.mkdir('数据')

    def get_response(self, ):
        spider_db = SpiderDB.SpiderDB(save_path=self.this_save_path)
        row = spider_db.conn.execute(f"SELECT id FROM request_data WHERE url=?", (self.url,)).fetchone()
        if row is not None:
            # 如果已经存在，则返回对应的响应数据
            request_id = row[0]
            response_row = spider_db.conn.execute("SELECT content FROM response_data WHERE request_id=?",
                                                  (request_id,)).fetchone()
            if response_row is not None:
                # 如果存在响应数据，则返回响应数据
                content = response_row[0]
                spider_db.close()
                return content
        try:
            time.sleep(config.time_sleep)
            this_response = requests.get(self.url, headers=self.headers, proxies=self.proxy)
            this_response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f'{self.url}链接超时')
            spider_db.close()
        except requests.exceptions.RequestException as e:
            print(f'{self.url}请求异常')
            # 关闭数据库连接
            spider_db.close()
        else:

            # 将请求数据保存到request_data表格中，并获取自增id
            spider_db.insert_request_data(self.url, 'get', str(self.headers), str('params'), 'data')
            request_id = spider_db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            # 将响应数据保存到response_data表格中
            this_title = ParseHtml(this_response.text).get_title()
            if this_title:
                this_title = this_title[0]
            else:
                this_title = ''
            spider_db.insert_response_data(request_id, status_code=this_response.status_code,
                                           headers=str(this_response.headers),
                                           content=this_response.text, title=this_title, url=self.url)
            # 关闭数据库连接
            spider_db.close()
            return this_response.text


def get_url(this_url, this_host):
    req = SpiderGetResponse(url=this_url, this_save_path=os.path.join('数据', this_host+'.db')).get_response()
    if not req:
        return None
    if req == '':
        return None
    print(this_url)
    urls = ParseHtml(req).get_src()
    this_urls = list()
    for this_url_1 in urls:
        if len(this_url_1) == 0:
            continue
        if this_url_1[:10] == "javascript":  # javascript跳转
            continue
        elif this_url_1[0] == "/":  # 相对路径跳转
            this_url_1 = urljoin(this_url, this_url_1)  # 通过parse组装相对路径为绝对路径
        elif this_url_1[0:4] == "http":
            this_url_1 = urljoin(this_url, this_url)
        elif this_url_1[0] == ".":
            this_url_1 = urljoin(this_url, this_url_1)  # 通过parse组装相对路径为绝对路径
        elif this_url_1[0] != ".":  # 如果是没有层级的相对路径
            if this_url_1[-1] != "/":  # 如果不是“/”结尾
                if this_url_1[8:].rfind("/") != -1:  # 如果连接中包含“/”
                    this_url_1 = this_url[:this_url.rfind("/") + 1] + this_url_1  # 截取掉最后一个“/"之后字符串
                else:
                    this_url_1 = this_url + "/" + this_url_1
            else:
                this_url_1 = this_url + this_url_1
        if this_host not in this_url_1:
            continue
        this_urls.append(this_url_1)
    return set(this_urls)


class Spider:
    def __init__(self, protocol, host):
        self.url = protocol + host
        self.protocol = protocol
        self.host = host
        self.leval = config.Leval
        self.set_url = {self.url}

    def recursion_url(self):
        self.leval -= 1
        print("目前递归层级：" + str(self.leval))
        if self.leval < 0:
            return
        for value in self.set_url:
            http = self.protocol
            if http in value:
                return_set2 = get_url(value, self.host)
                if return_set2 is None:
                    continue
                self.set_url = self.set_url | return_set2  # 合并SET()集
        self.recursion_url()


if __name__ == '__main__':
    pool = ThreadPoolExecutor()
    data = pd.read_excel("域名.xlsx")
    for i, row in data.iterrows():
        host = row['域名']
        p = Spider(protocol='http://', host=host)
        pool.submit(p.recursion_url, )


