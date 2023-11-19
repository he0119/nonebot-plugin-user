<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# NoneBot Plugin User

_✨ NoneBot 用户插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-user/main/LICENSE">
    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-user.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-user">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-user.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
  <a href="https://codecov.io/gh/he0119/nonebot-plugin-user">
    <img src="https://codecov.io/gh/he0119/nonebot-plugin-user/branch/main/graph/badge.svg?token=jd5ufc1alv"/>
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=7zQUpiGp">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-730374631-orange?style=flat-square" alt="QQ Chat Group">
  </a>
</p>

## 简介

## 使用方式

加载插件后发送 `/user` 或 `/bind`。

## 插件适配

先在插件代码最前面声明依赖

```python
from nonebot import require
require("nonebot_plugin_user")
```

获取用户信息

```python
from nonebot_plugin_user import User

@matcher.handle()
async def _(user: User):
    print(user.id)
```

获取用户会话信息

```python
from nonebot_plugin_user import UserSession

@matcher.handle()
async def _(session: UserSession):
    print(session.user_id)
```

## 配置项

配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。

## 计划

- [ ] 支持权限

## 鸣谢

- [Koishi](https://github.com/koishijs/koishi): 本项目直接参考
- [nonebot-plugin-session](https://github.com/noneplugin/nonebot-plugin-session): 获取用户信息
