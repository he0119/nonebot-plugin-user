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
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
  <a href="https://codecov.io/gh/he0119/nonebot-plugin-user">
    <img src="https://codecov.io/gh/he0119/nonebot-plugin-user/branch/main/graph/badge.svg?token=jd5ufc1alv" alt="codecov"/>
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=7zQUpiGp">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-730374631-orange?style=flat-square" alt="QQ Chat Group">
  </a>
</p>

## 简介

## 使用方式

加载插件后发送 `/user` 或 `/bind`。

### 查看用户信息

通过 user 命令可查看用户信息:

```text
平台名：qq
平台 ID：10000
用户名：uy/sun
创建日期：2023-11-02 04:52:42
```

### 绑定用户

通过 bind 命令可将不同用户的数据绑定:

```text
命令 bind 可用于在多个平台间绑定用户数据。绑定过程中，原始平台的用户数据将完全保留，而目标平台的用户数据将被原始平台的数据所覆盖。
请确认当前平台是你的目标平台，并在 5 分钟内使用你的账号在原始平台内向机器人发送以下文本：
/bind nonebot/123456
绑定完成后，你可以随时使用「bind -r」来解除绑定状态。
```

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
    await matcher.finish(user.id)
```

获取用户会话信息

```python
from nonebot_plugin_user import UserSession


@matcher.handle()
async def _(session: UserSession):
  await matcher.finish(session.platform_user.id)
```

## 配置项

配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。

### user_token_prefix

- 类型: `str`
- 默认: `nonebot/`
- 说明: 生成令牌的前缀

## 计划

- [ ] 支持权限

## 鸣谢

- [Koishi](https://github.com/koishijs/koishi): 本项目直接参考
- [nonebot-plugin-session](https://github.com/noneplugin/nonebot-plugin-session): 获取用户信息
- [nonebot-plugin-uninfo](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo): 通用的会话信息插件
