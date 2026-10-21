# AstrBot Sub2API 账号查询面板插件

这是上一版文本插件的增强版，增加了 **精美图片面板**。

## 新增功能

- `/s2 面板`
  - 生成一张精美总览图
  - 展示账号总数、正常/异常账号数、账号列表、全局状态、全局统计、模型预览
- `/s2 卡片 <ID/名称>`
  - 生成某个账号的精美卡片
  - 展示账号基本信息、额度/用量、模型列表

## 其它保留文本命令

- `/s2 测试`
- `/s2 账号 [关键词]`
- `/s2 详情 <ID/名称>`
- `/s2 用量 <ID/名称> [刷新]`
- `/s2 模型 <ID/名称>`
- `/s2 状态`
- `/s2 帮助`

## 安装

在 AstrBot 插件管理页面通过 GitHub 仓库地址安装：

`https://github.com/koichinoi/astrbot_plugin_sub2api_status`

也可以从仓库下载 ZIP 后上传，或克隆到 `data/plugins/astrbot_plugin_sub2api_status`。

## 配置

至少填写：

- `base_url`：例如 `http://127.0.0.1:9999`
- `admin_api_key`：Sub2API 管理员 API Key（推荐）

如果没有管理员 API Key，再使用：

- `admin_jwt`

## 依赖

本插件使用 AstrBot 自带的：

- `event.image_result()` 发送图片
- `self.html_render()` 使用 HTML + Jinja2 渲染图片

AstrBot 文档已明确支持通过 `html_render` 把自定义 HTML 模板渲染成图片，然后再 `yield event.image_result(url)` 发送。

## 安全说明

- 默认不输出敏感凭证
- 所有命令仅 AstrBot 管理员可用
- 插件查询的是 `/api/v1/admin/*` 管理接口，所以应使用管理员凭证

## 常用示例

```text
/s2 面板
/s2 面板 plus
/s2 卡片 1
/s2 卡片 koi
/s2 用量 1 刷新
```