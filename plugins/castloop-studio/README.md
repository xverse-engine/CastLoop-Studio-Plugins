# CastLoop Studio

本目录提供 Codex 插件。Claude 聊天、Cowork 与 Claude Code 使用独立的 [Claude 正式包](../../claude/castloop-studio/README.md)；ChatGPT 通过连接器接入。安装与授权见[客户端指南](../../docs/agent-clients.md)。下方 Client ID 仅用于现有 Codex 接入。

Codex 正式环境插件，版本 **1.0.2**，同步 Studio 3.34.0 使用指引。支持独立生成结果自动保存到故事画布，并在保存失败时复用成功产物补存。上述行为及精确资产修改、历史图片采用、音色查询均以连接后实时工具定义和服务端部署为准。

用对话编辑故事、角色、地点、道具、世界观和大纲，生成图片、文本、语音、音乐和视频，查询任务及保存结果。支持作品查找、新建、复制和项目 JSON 导入导出；具体参数以连接后的工具定义为准。生成可能收费，不提供发布能力。

## 安装

按[仓库安装说明](../../README.md)添加 Git 市场，选择 **CastLoop Studio**，登录并授权。SIT 是独立测试插件，不连接正式作品。

可以先说「介绍你能怎样帮我创作」，之后再指定故事名称或 ID；也可以从 Studio 故事内的「工具 → 在 Codex 中继续」打开。先保存浏览器里的修改，读取并确认目标后再编辑；作品同名时应确认具体 ID。

## 连接配置

- MCP：`https://studio.castloop.ai/mcp`
- Logto issuer：`https://auth.castloop.ai/oidc`
- 公开 OAuth Client ID：`zl6mpa97xs5zdjt3by7pr`
- 本地回调：`http://127.0.0.1/callback`
- 权限：`openid`、`studio:read`、`studio:write`、`offline_access`

采用与 SIT 已验收插件相同的公共 Native 客户端、授权码及 PKCE 配置，不携带 Client Secret。账号授权和作品权限均在服务端校验。插件不包含服务器代码、用户故事或密钥。

## 验证连接

在新对话中先检查实际可用工具，再读取一个正式测试故事；明确授权修改一个字段后读回，并在 Studio 核对。登录首次成功后，在访问令牌到期后再次调用，核对 Logto 的 Refresh Token 交换成功。工具列表可见不等于实际读写成功；超时先查询结果，不盲目重复生成。

正式服务独立部署。服务端需要 `MCP_ENABLED=true`、`MCP_PUBLIC_URL=https://studio.castloop.ai/mcp`，并将 `/mcp` 及 `/.well-known/oauth-protected-resource/mcp` 转发到 Go 服务。保留原 Studio 的 `LOGTO_API_RESOURCE`；MCP 使用自己的资源标识。HK Logto 的固定客户端兼容变量为 `MCP_OFFLINE_ACCESS_CONSENT_CLIENT_IDS=zl6mpa97xs5zdjt3by7pr`，并在该应用授予正式 MCP 资源的读写权限。
