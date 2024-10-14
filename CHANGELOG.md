# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [Unreleased]

## [0.4.3] - 2024-08-29

### Fixed

- 修复 postgresql 下关系名过长的问题

## [0.4.2] - 2024-08-19

### Fixed

- 修复并发下的报错

## [0.4.1] - 2024-08-15

### Added

- 添加命令的帮助信息

## [0.4.0] - 2024-08-07

### Fixed

- 修复用户创建日期的时区问题

### Changed

- 事件响应器现在将阻断事件的传播
- 使用自带 typing 的 expiringdictx

## [0.3.0] - 2024-06-28

### Added

- 添加 py.typed 文件

### Removed

- 移除 Python 3.8 支持

## [0.2.0] - 2024-02-24

### Added

- 适配 Pydantic V2

## [0.1.2] - 2023-11-21

### Fixed

- 修复 sqlalchemy 的报错

## [0.1.1] - 2023-11-21

### Fixed

- 补上插件元数据缺失的项

## [0.1.0] - 2023-11-21

### Added

- 支持配置令牌前缀

### Fixed

- 修复并发时报错的问题

### Changed

- 需要通过 -l 参数修改用户名

## [0.0.5] - 2023-11-20

### Changed

- 降低遇到不支持平台的日志等级

## [0.0.4] - 2023-11-19

### Removed

- 移除 foreignkey 约束
- 移除不支持平台时的报错与提示

## [0.0.3] - 2023-10-22

### Added

- 升级 ORM 版本，降低 Python 版本限制

## [0.0.2] - 2023-10-07

### Added

- 支持修改用户名
- 添加 inspect 命令

### Changed

- 使用 nb orm

## [0.0.1] - 2023-09-19

### Added

- 可以使用的版本。

[Unreleased]: https://github.com/he0119/nonebot-plugin-user/compare/v0.4.3...HEAD
[0.4.3]: https://github.com/he0119/nonebot-plugin-user/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/he0119/nonebot-plugin-user/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/he0119/nonebot-plugin-user/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/he0119/nonebot-plugin-user/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/he0119/nonebot-plugin-user/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/he0119/nonebot-plugin-user/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/he0119/nonebot-plugin-user/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/he0119/nonebot-plugin-user/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/he0119/nonebot-plugin-user/compare/v0.0.5...v0.1.0
[0.0.5]: https://github.com/he0119/nonebot-plugin-user/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/he0119/nonebot-plugin-user/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/he0119/nonebot-plugin-user/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/he0119/nonebot-plugin-user/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/he0119/nonebot-plugin-user/releases/tag/v0.0.1
