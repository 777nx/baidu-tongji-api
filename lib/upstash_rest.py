# -*- coding: utf-8 -*-
"""Upstash Redis REST 封装：存储百度统计 accessToken / refreshToken。"""

import json
import os
import requests

TOKEN_KEY = 'baidu:token'


def _config():
    url = (os.environ.get('UPSTASH_REDIS_REST_URL') or '').rstrip('/')
    token = os.environ.get('UPSTASH_REDIS_REST_TOKEN') or ''
    if not url or not token:
        raise RuntimeError('缺少环境变量 UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN')
    return url, token


def _command(argv):
    url, token = _config()
    resp = requests.post(
        url,
        headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        },
        json=argv,
        timeout=15,
    )
    if resp.status_code >= 400:
        raise RuntimeError('Upstash 请求失败 HTTP {}: {}'.format(
            resp.status_code, resp.text[:500]))
    return resp.json().get('result')


def get_baidu_token():
    raw = _command(['GET', TOKEN_KEY])
    if raw is None:
        raise RuntimeError(
            'Upstash 中还没有 baidu:token，请先按 README 写入 accessToken/refreshToken')
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode('utf-8')
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get('accessToken') or not data.get('refreshToken'):
        raise RuntimeError('baidu:token 缺少 accessToken 或 refreshToken')
    return data


def save_baidu_token(access_token, refresh_token):
    payload = json.dumps({
        'accessToken': access_token,
        'refreshToken': refresh_token,
    }, ensure_ascii=False)
    return _command(['SET', TOKEN_KEY, payload])
