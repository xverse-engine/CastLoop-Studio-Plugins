# Codex SIT DCR 迁移（2026-11-13）

## 范围

SIT 插件 0.1.19 删除 `.mcp.json` 中固定的 `oauth.clientId` 与 `callbackUrl`，保留 MCP 地址、HTTP 传输、四项 scope、插件名与市场来源。当前兼容清单使用 Codex 的自动客户端注册，不添加该格式未定义的 DCR 开关。Codex 优先使用显式配置的 Client ID；无固定 ID 时按 discovery 选择 CIMD 或 DCR。

SIT discovery 已声明 `client_id_metadata_document_supported: false`、`registration_endpoint: https://sit-xnarrator-game-auth.xverse.cn/oidc/mcp/register`，支持公共客户端 `none` 与 PKCE `S256`，因此新注册走 DCR。正式 discovery 尚无注册端点，正式插件 1.0.2 的固定 ID／回调保持原状。

同环境 Claude 插件按约定同步版本为 0.1.19，连接内容与 Skill 不变；ChatGPT 连接器和 Studio 前后端、Caster、MCP schema／执行、Logto 部署均不变。本批仅调整插件 OAuth 配置，无新增工具或收费能力。

## 用户流程与兼容

新用户仍从同一个市场安装 SIT 插件，登录自己的 Studio 账号授权，不需要填 Client ID、Secret 或回调端口。客户端管理注册结果、PKCE 和回调。

旧授权可能继续使用原客户端，升级插件不等于已完成 DCR 验收。需要验证时，通过客户端提供的断开／重新认证入口登录，再新建会话读取用户明确指定的测试故事；首次不修改或提交收费任务。不手改用户配置、凭据或缓存，不擅自撤销旧授权。旧预注册应用同时是 DCR 权限模板，不能删除。

配置回退可恢复上一版本 SIT 包及原固定公开客户端配置；不改变授权服务器或正式用户的连接。

## 验证边界

- 自动检查 SIT 无固定客户端／回调、scope 和环境隔离、正式配置不变，以及 Claude 同版本生成和 ZIP 内容。
- 2026-11-13 公网检查：SIT 原生公共客户端注册返回 201，新 Client ID、无 Secret、四项 scope 与 loopback 回调均符合请求；带 resource 与 PKCE S256 的授权请求返回 303 到登录页 `/sign-in`。检查共创建两个无用户授权的测试客户端，未获取令牌或访问作品。
- 公网 discovery 和 DCR 注册检查只证明对应阶段可用，不能替代 Codex 桌面真实登录、令牌刷新与工具读取。
- 真实 Codex 新注册 → 登录授权 → 新会话工具发现 → 明确 storyId 读取仍需客户端验收；不使用已有连接冒充新 DCR 链路成功。

官方依据：[Codex MCP 客户端注册](https://learn.chatgpt.com/docs/extend/mcp?surface=cli#oauth-client-registration)。
