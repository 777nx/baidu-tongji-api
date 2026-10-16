# -*- coding: utf-8 -*-
# @Author    : Eurkon
# @Date      : 2021/6/5 10:19

import os
import json
import traceback
import requests
from urllib import parse
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler

from leancloud_rest import get_baidu_token


def get_data(params):
    """重定向请求百度统计，解决跨域问题"""
    if 'access_token' not in params or not params.get('access_token'):
        app_id = os.environ.get('APPID')
        app_key = os.environ.get('APPKEY')
        if not app_id or not app_key:
            raise RuntimeError('缺少环境变量 APPID / APPKEY')
        token_data = get_baidu_token(app_id, app_key, keys=('accessToken',))
        access_token = token_data.get('accessToken')
        if not access_token:
            raise RuntimeError('LeanCloud BaiduToken.accessToken 为空')
        params['access_token'] = access_token

    url = 'https://openapi.baidu.com/rest/2.0/tongji/report/getData'
    req = requests.post(url=url, data=params, timeout=30)
    return req.json()


class handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        try:
            params = dict(parse.parse_qsl(urlparse(self.path).query))
            data = get_data(params)
            self._json(200, data)
        except Exception as exc:
            self._json(500, {
                'error': str(exc),
                'traceback': traceback.format_exc(),
            })
