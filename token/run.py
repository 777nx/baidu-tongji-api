# -*- coding: utf-8 -*-
# @Author   : Eurkon
# @Date     : 2022/3/28 15:21

import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from leancloud_rest import get_baidu_token, save_baidu_token  # noqa: E402


class UpdateAccessToken:
    def __init__(self):
        self.api_key = os.environ["APIKEY"]
        self.secret_key = os.environ["SECRETKEY"]
        self.app_id = os.environ["APPID"]
        self.app_key = os.environ["APPKEY"]

    def get_token(self):
        token_data = get_baidu_token(
            self.app_id,
            self.app_key,
            keys=('accessToken', 'refreshToken'),
        )
        self.object_id = token_data.get('objectId')
        self.access_token = token_data.get('accessToken')
        self.refresh_token = token_data.get('refreshToken')

    def update_token(self):
        url = (
            'https://openapi.baidu.com/oauth/2.0/token'
            '?grant_type=refresh_token'
            '&refresh_token=' + self.refresh_token
            + '&client_id=' + self.api_key
            + '&client_secret=' + self.secret_key
        )
        response = requests.get(url, timeout=30)
        result = response.json()
        if 'access_token' not in result or 'refresh_token' not in result:
            raise RuntimeError('刷新百度 token 失败: {}'.format(result))
        self.access_token = result['access_token']
        self.refresh_token = result['refresh_token']
        save_baidu_token(
            self.app_id,
            self.app_key,
            self.object_id,
            self.access_token,
            self.refresh_token,
        )


if __name__ == '__main__':
    u = UpdateAccessToken()
    u.get_token()
    u.update_token()
    print('Baidu token refreshed OK')
