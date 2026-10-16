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

TOKEN_KEY = 'baidu:token'


def _fetch_access_token():
    url = (os.environ.get('UPSTASH_REDIS_REST_URL') or '').rstrip('/')
    token = os.environ.get('UPSTASH_REDIS_REST_TOKEN') or ''
    if not url or not token:
        raise RuntimeError('缺少环境变量 UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN')

    resp = requests.post(
        url,
        headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        },
        json=['GET', TOKEN_KEY],
        timeout=15,
    )
    if resp.status_code >= 400:
        raise RuntimeError('Upstash 查询失败 HTTP {}: {}'.format(
            resp.status_code, resp.text[:500]))

    raw = resp.json().get('result')
    if raw is None:
        raise RuntimeError('Upstash 中还没有 baidu:token，请先写入 accessToken/refreshToken')
    data = json.loads(raw) if isinstance(raw, str) else raw
    access_token = (data or {}).get('accessToken')
    if not access_token:
        raise RuntimeError('baidu:token.accessToken 为空')
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
