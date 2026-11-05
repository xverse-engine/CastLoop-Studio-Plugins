# Changelog

## 0.1.3 — 2026-11-05

- 将已验收的 SIT 插件迁入独立分发仓库，保留插件和市场 ID、版本、OAuth Client ID、回调及远程 MCP 地址。
- 使用 `.codex-plugin/plugin.json` 与 `.mcp.json`，避免混用清单导致只加载 Skills 而不发现 MCP。
- 包含角色读取与已有角色基础资料修改的使用指导，以及 CastLoop 图标。
- 已确认客户端发现两个工具；用户反馈 SIT 登录授权、角色读取、修改、读回及 Studio 保存核对通过。
- 正式环境插件暂未提供。Token 过期、拒绝授权等异常路径不据此视为已完整验收。
