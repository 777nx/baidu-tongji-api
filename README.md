# baidu-tongji-api

用 Python 代理百度统计 API，解决浏览器跨域；部署在 Vercel。  
Token 存储已从 LeanCloud 迁移到 **Upstash Redis**。

## 教程原文

https://blog.eurkon.com/post/61763977.html

## 环境变量

| 变量 | 用在哪里 | 说明 |
| --- | --- | --- |
| `UPSTASH_REDIS_REST_URL` | Vercel + GitHub Actions | Upstash REST URL |
| `UPSTASH_REDIS_REST_TOKEN` | Vercel + GitHub Actions | Upstash REST Token |
| `APIKEY` | 仅 GitHub Actions | 百度统计 API Key |
| `SECRETKEY` | 仅 GitHub Actions | 百度统计 Secret Key |

Redis 中固定 key：`baidu:token`，值为 JSON：

```json
{"accessToken":"...","refreshToken":"..."}
```

## 重新获取百度 token（过期时）

1. 浏览器打开（替换 CLIENT_ID）：

```text
http://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri=oob&scope=basic&display=popup
```

2. 用拿到的 code 换 token（替换 CODE / CLIENT_ID / CLIENT_SECRET）：

```text
http://openapi.baidu.com/oauth/2.0/token?grant_type=authorization_code&code={CODE}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri=oob
```

3. 把返回的 `access_token` / `refresh_token` 写入 Upstash（控制台 Data Browser，或运行 `python token/seed.py`）。

## 前端调用示例

```text
https://你的域名/api?site_id=站点ID&method=overview/getDistrictRpt&start_date=20220601&end_date=20261016&metrics=pv_count
```
