# -*- coding: utf-8 -*-
# @Author    : Eurkon
# @Date      : 2021/6/5 10:19
#
# 注意：此文件必须自包含，不要 from 同目录其他 py（Vercel 会把 api/*.py 都当成函数入口）。

import os
import json
import traceback
import requests
from urllib import parse
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler


def _leancloud_base(app_id):
    custom = os.environ.get('LEANCLOUD_API_SERVER') or os.environ.get('LC_API_SERVER')
    if custom:
        return custom.rstrip('/')
    return 'https://{}.api.lncldglobal.com'.format(app_id[:8].lower())


def _fetch_access_token():
    app_id = os.environ.get('APPID')
    app_key = os.environ.get('APPKEY')
    if not app_id or not app_key:
        raise RuntimeError('缺少环境变量 APPID / APPKEY')

    url = '{}/1.1/classes/BaiduToken'.format(_leancloud_base(app_id))
    headers = {
        'X-LC-Id': app_id,
        'X-LC-Key': app_key,
        'Content-Type': 'application/json',
    }
    params = {
        'limit': 1,
        'order': '-updatedAt',
        'keys': 'accessToken',
    }
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if resp.status_code >= 400:
        raise RuntimeError('LeanCloud 查询失败 HTTP {}: {} | url={}'.format(
            resp.status_code, resp.text[:500], url))
    results = resp.json().get('results') or []
    if not results:
        raise RuntimeError('BaiduToken 为空，请先在 LeanCloud 写入 accessToken/refreshToken')
    access_token = results[0].get('accessToken')
    if not access_token:
        raise RuntimeError('LeanCloud BaiduToken.accessToken 为空')
    return access_token


def get_data(params):
    if 'access_token' not in params or not params.get('access_token'):
        params['access_token'] = _fetch_access_token()

    url = 'https://openapi.baidu.com/rest/2.0/tongji/report/getData'
    req = requests.post(url=url, data=params, timeout=30)
    return req.json()


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

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
