# CastLoop Studio SIT

Codex 插件版本 **0.1.8**（配套后端 **3.30.1-preview.1**，需部署后验收），仅连接 CastLoop Studio 测试环境。

## 能力

| 工具 | 用途 |
| --- | --- |
| `listStories` | 列出可操作的故事，或按名称片段搜索；支持分页，同名作品分别返回。需后端部署该工具 |
| `readStoryCharacters` | 读取已保存故事的角色，支持分页及指定角色 |
| `composeCharacter` | 统一新建/修改角色：资料生成、音色/TTS 设置和阶段状态批量操作；需实时 schema 支持 |
| `add/removeCharacterPhase/State` | 四个角色阶段/状态独立增删入口，不生图 |
| `readStorySections` / `readStoryGraph` / `readStoryNodes` | 读取故事、资产和剧情 |
| `patchStoryOutline` | 修改大纲，不直接修改剧情节点 |
| `composeStoryFlow`（本批后端起完整支持下列范围） | 精确节点新增/修改/删除、选项文本与普通跳转、对话组件及分支台词编辑；不支持 AI 子图生成 |
| `composeLocation` / `composeItem` / `composeWorldSetting` | 创建/修改资产文字资料与世界观，不生图 |

故事读改仍使用明确的 storyId 和作品编辑权限；可先通过 listStories 将名称解析为 ID，重名时由用户确认。旧后端未提供列表时仍手动指定 ID，未开放新参数时保留基础修改范围。上述新增能力需后端部署，不能仅凭插件版本判断可用。默认 Narrator 受保护；读取线上已保存的可编辑草稿，不包含浏览器未保存内容。不提供生图、语音合成或发布能力。

## 连接配置

- MCP：`https://castloop-sit.xverse.cn/mcp`
- 公开 OAuth Client ID：`y30cn0zl9be20aeog6kh6`
- 本地回调：`http://127.0.0.1/callback`
- 申请权限：`openid`、`studio:read`、`studio:write`、`offline_access`
- 采用预注册公共客户端的授权码与 PKCE 流程，不携带 Client Secret 或用户凭据。

本插件使用 `.codex-plugin/plugin.json` 引用 `.mcp.json` 和 Skills。工具列表来自远程 MCP 服务，不在插件内复制。不要将插件包地址作为 MCP 服务地址。

## 安装与登录

按[仓库安装说明](../../README.md)添加 Git 市场并安装。在客户端的 MCP 管理入口完成登录授权；已有手动配置的同环境连接可由用户禁用，避免重复。

当前包没有托管 App 绑定，不保证出现 Figma 式「已连接账号」区域。插件安装成功不代表 OAuth 成功；新会话应发现实际可调用的 `readStoryCharacters`、`composeCharacter`。若授权 URL 的 client_id 仍是 chatgpt.com 身份文件 URL，说明预注册配置未生效，应停止该次授权并检查加载配置。

本地回调只用于当前已验收的 Codex 本地连接。后续若接官方目录或托管连接，须另行核对 OAuth 应用与准确回调，不自动套用本地回调。

## 验收记录

2026-11-05：客户端已发现两个工具；用户反馈 SIT 登录授权、角色读取、修改、读回及 Studio 保存核对测试通过。该结论不替代拒绝授权、无权作品、Token 过期与刷新等异常路径的单独验收。

只读示例：

> 读取故事 <storyId> 的角色，先不要修改。

修改时明确角色和需要调整的字段。成功后读回核对，再打开 Studio 检查保存结果。请求结果不确定时先读取，不盲目重复写入。

## 更新

更新插件配置、Skills 或资源时提升插件版本，并通过客户端支持的更新流程重新加载。Go MCP 服务独立部署；未实现的工具不能仅通过更新 Skill 声明为可用。
