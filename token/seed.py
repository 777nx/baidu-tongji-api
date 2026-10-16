# -*- coding: utf-8 -*-
"""首次把百度 token 写入 Upstash。

用法（本地或 GitHub Actions 临时跑一次）：
  set UPSTASH_REDIS_REST_URL=...
  set UPSTASH_REDIS_REST_TOKEN=...
  set BAIDU_ACCESS_TOKEN=...
  set BAIDU_REFRESH_TOKEN=...
  python token/seed.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.upstash_rest import save_baidu_token, get_baidu_token  # noqa: E402


def main():
    access = os.environ.get('BAIDU_ACCESS_TOKEN') or ''
    refresh = os.environ.get('BAIDU_REFRESH_TOKEN') or ''
    if not access or not refresh:
        raise RuntimeError('请设置环境变量 BAIDU_ACCESS_TOKEN 和 BAIDU_REFRESH_TOKEN')
    save_baidu_token(access, refresh)
    saved = get_baidu_token()
    print('seed OK')
    print('accessToken prefix:', saved['accessToken'][:20] + '...')
    print('refreshToken prefix:', saved['refreshToken'][:20] + '...')


if __name__ == '__main__':
    main()
