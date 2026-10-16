# -*- coding: utf-8 -*-
"""LeanCloud 国际版 REST 封装（供 GitHub Actions token 刷新使用）。"""

import os
import requests

CLASS_NAME = 'BaiduToken'


def _base_url(app_id):
    custom = os.environ.get('LEANCLOUD_API_SERVER') or os.environ.get('LC_API_SERVER')
    if custom:
        return custom.rstrip('/')
    return 'https://{}.api.lncldglobal.com'.format(app_id[:8].lower())


def _headers(app_id, app_key):
    return {
        'X-LC-Id': app_id,
        'X-LC-Key': app_key,
        'Content-Type': 'application/json',
    }


def get_baidu_token(app_id, app_key, keys=('accessToken',)):
    url = '{}/1.1/classes/{}'.format(_base_url(app_id), CLASS_NAME)
    params = {
        'limit': 1,
        'order': '-updatedAt',
        'keys': ','.join(keys),
    }
    resp = requests.get(url, headers=_headers(app_id, app_key), params=params, timeout=15)
    if resp.status_code >= 400:
        raise RuntimeError('LeanCloud 查询失败 HTTP {}: {} | url={}'.format(
            resp.status_code, resp.text[:500], url))
    results = resp.json().get('results') or []
    if not results:
        raise RuntimeError('BaiduToken 为空，请先在 LeanCloud 写入 accessToken/refreshToken')
    return results[0]


def save_baidu_token(app_id, app_key, object_id, access_token, refresh_token):
    url = '{}/1.1/classes/{}/{}'.format(_base_url(app_id), CLASS_NAME, object_id)
    payload = {
        'accessToken': access_token,
        'refreshToken': refresh_token,
    }
    resp = requests.put(url, headers=_headers(app_id, app_key), json=payload, timeout=15)
    if resp.status_code >= 400:
        raise RuntimeError('LeanCloud 写入失败 HTTP {}: {}'.format(
            resp.status_code, resp.text[:500]))
    return resp.json()
