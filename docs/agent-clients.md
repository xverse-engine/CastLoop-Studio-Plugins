# 在外部 Agent 中继续创作

首批接入范围为 GPT 系列的 Codex、ChatGPT，以及 Claude 系列的 Claude、Claude Code。Studio 的「连接外部 Agent」和故事内「在 Agent 中继续」使用同一个交接弹窗。

Codex 与 Claude Code 的打开链接预填提示词，查看后手动发送。ChatGPT 与 Claude 的打开按钮将对应提示词复制到剪贴板，然后打开网页，在输入框粘贴并发送。也可以使用「复制提示词」。浏览器未能打开应用时，在已安装的客户端中粘贴即可。Claude Code 的链接需要本机已安装并注册 `claude-cli://` 协议处理器。

故事内的提示词携带明确的 storyId，首次只读取并核对作品。先保存 Studio 中的修改，外部编辑结束后重新打开故事核对结果。故事外进入对话后可稍后指定作品。

## 环境和授权

| 环境 | MCP 地址 | OAuth issuer |
| --- | --- | --- |
| 正式 | `https://studio.castloop.ai/mcp` | `https://auth.castloop.ai/oidc` |
| SIT | `https://castloop-sit.xverse.cn/mcp` | `https://sit-xnarrator-game-auth.xverse.cn/oidc` |

国内与海外正式 Studio 共用上表正式 MCP。SIT 使用测试账号和测试作品。本地、自定义后端使用交接提示词中的实际地址，云端客户端还需能访问该服务。

登录现有 Studio 账号，读取申请 `studio:read`，编辑同时申请 `studio:write`。需要长期连接时申请 `offline_access` 并验证刷新令牌。OAuth 请求的 `resource` 应为对应环境完整 MCP 地址。

截至 2026-11-12，正式环境公开发现声明支持 CIMD、PKCE S256 和公共客户端 token endpoint 的 `none` 认证方式，未公布 DCR 注册端点。Codex 继续使用已有预注册应用。其他客户端先按其支持的身份发现方式连接，若失败，由管理员为该客户端配置预注册应用，再按客户端实际回调及 token endpoint 认证方式完成授权。

## Codex

按[现有安装说明](../README.md)添加插件市场，安装 CastLoop Studio，登录授权。SIT 选择 CastLoop Studio SIT。Studio 的 Codex 按钮继续携带当前环境的插件 mention。

现有 `.mcp.json` 中的 OAuth 应用和本地回调属于这条接入路径，其他客户端应配置自己的实际注册信息。

## ChatGPT

1. 打开 ChatGPT 的插件管理，选择添加自定义 MCP 服务。账号或工作区需要提供相应自定义接入权限。
2. 填写当前环境 MCP 地址，选择 OAuth。根据管理员提供的配置选择 CIMD，或填写预注册应用信息。
3. 登录 Studio 并授予所需读写权限，安装并在会话中启用该插件。
4. 粘贴 Studio 复制的提示词，发送后先确认实际工具与目标故事。

预注册应用的回调 URL、应用类型及 token endpoint 认证方式以 ChatGPT 管理页面显示的信息为准。[ChatGPT 接入文档](https://developers.openai.com/api/docs/guides/custom-mcp-server)、[OAuth 文档](https://developers.openai.com/plugins/build/auth)

## Claude

1. 在 Claude 的 Connectors 中添加自定义远程连接器。
2. 填写当前环境 MCP 地址，根据服务器发现和管理员配置选择 Claude 身份或预注册 OAuth 应用。
3. 登录 Studio 并完成授权，在会话中启用连接器。
4. 粘贴 Studio 复制的提示词，发送后先读取目标作品。

网页和桌面的远程连接器通过 Anthropic 云端访问 MCP，需要服务及授权端点可从其网络访问。[Claude 连接器文档](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)

## Claude Code

在自己的终端添加正式 MCP 服务。SIT 应同时替换名称与地址。

```sh
claude mcp add --scope user --transport http castloop-studio https://studio.castloop.ai/mcp
```

在 Claude Code 中运行 `/mcp`，选择该服务并按提示登录 Studio。此配置会保存到自己的用户级 MCP 设置。若身份文件获取或自动注册失败，由管理员提供独立预注册应用的公开 Client ID 与已登记回调端口，使用以下模板配置。

```sh
claude mcp add --scope user --transport http --client-id YOUR_CLIENT_ID --callback-port YOUR_REGISTERED_PORT castloop-studio https://studio.castloop.ai/mcp
```

`YOUR_CLIENT_ID` 和 `YOUR_REGISTERED_PORT` 需要替换成管理员实际配置的值。公共 PKCE 客户端使用公开 Client ID。实际回调 URL 的主机、端口与路径须与 Logto 注册值一致，不同 Claude Code 版本的 localhost / 127.0.0.1 行为需要核对。

连接后使用 Studio 的「在 Claude Code 中打开」，或在 Claude Code 输入框粘贴交接提示词。`claude-cli://open?q=` 只预填内容，用户按 Enter 后发送。[Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)、[打开链接文档](https://code.claude.com/docs/en/deep-links)

## 验收状态

| 客户端 | 已有证据 | 待完成 |
| --- | --- | --- |
| Codex | 既有安装、授权及读改保存验收，四入口改造有前端回归 | 新版入口发布后复验 |
| ChatGPT | 交接入口与对应提示词、本地测试 | 真实注册、登录、读改保存、刷新及撤销 |
| Claude | 交接入口与对应提示词、本地测试 | 真实注册、登录、读改保存、刷新及撤销 |
| Claude Code | 官方链接和配置方式、本机 2.1.109 CLI 参数核对、本地测试 | 本机唤起、实际回调、登录、读改保存、刷新及撤销 |

每端使用专用测试作品，依次验证工具发现、读取、明确修改一个字段、读回和 Studio 显示，再验证只读令牌、无权作品、过期刷新与撤销。生成任务验证应保留 taskId / requestId，并分别检查接受、生成与保存状态。需要付费生成的验收应事先明确范围。只记录必要状态与错误码，报告中不包含访问令牌、刷新令牌或授权码。
