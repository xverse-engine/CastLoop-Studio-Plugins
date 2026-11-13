# 在外部 Agent 中继续创作

Studio 交接入口按客户端分别提供提示词。故事内先保存修改；交接携带 storyId，连接成功后先读取并核对目标。打开链接和预填提示词不代表已连接或授权。

## 环境与当前范围

| 环境 | MCP 地址 | OAuth issuer |
| --- | --- | --- |
| 正式 | `https://studio.castloop.ai/mcp` | `https://auth.castloop.ai/oidc` |
| SIT | `https://castloop-sit.xverse.cn/mcp` | `https://sit-xnarrator-game-auth.xverse.cn/oidc` |

国内和海外正式 Studio 共用正式 MCP。SIT 使用测试账号与测试作品。各客户端配置和授权需分别验证，不能把 Codex 安装状态当作其他客户端已连接。

当前正式入口仅开放 Codex。本地前端已准备 SIT 的 Claude、Claude Code 独立页签，待部署和真实客户端验收；ChatGPT 的 SIT 直接填写 URL、登录授权和作品读取已由用户确认成功。SIT Logto 已实现并公布 DCR，无需授权 Pod 下载外部 CIMD 文件。正式环境的 DCR 尚未在本轮核验，不能套用 SIT 验收结论。

## Codex

按[现有安装说明](../README.md)安装对应环境插件并登录 Studio。既有固定公开 Client ID 与本地回调配置保持不变，不随本次切换 DCR。

## ChatGPT（SIT 已验证授权与读取）

在设置的连接器／插件中添加自定义 MCP，填写 SIT MCP 地址，选择 OAuth。客户端注册使用动态客户端注册（DCR），登录自己的 Studio 账号并授权，再在对话中启用。无需填写 Client ID、Secret 或端口。

此流程不要求导入 Git 插件包。编辑器的 ChatGPT 入口不在本次恢复范围。

## Claude 网页（独立流程，待真实客户端验收）

1. 在 Studio 的 Claude 页签点击打开，进入 `https://claude.ai/new?q=...`。提示词随链接传递，同时复制到剪贴板；若未预填则粘贴。
2. 未连接时，在 Claude 设置 → Connectors → Add custom connector 中填写当前环境的 MCP 地址。
3. OAuth 客户端选择 Register automatically，登录 Studio 并授权，不填 Client ID 或 Secret。
4. 在对话中启用该连接器，发送交接提示词，检查工具真实读取的 storyId 和内容。

不需要安装 Codex 插件或先配置 Claude Code。[官方自定义连接器说明](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)

## Claude Code 桌面（独立入口，待真实客户端验收）

Studio 的 Claude Code 页签使用 `claude://code/new?q=...` 打开 Claude 桌面应用的 Code 页签，并预填提示词。需要安装 Claude 桌面应用，并使用本地 Code 会话。应用未打开时，可复制提示词后手动打开 Code。

1. 在 Code 页签中点击输入框旁的 +，选择 Add connectors。如果菜单显示 Connectors，选择 Browse connectors。
2. 添加 Studio 自定义连接器，填写对应环境 MCP 地址，OAuth 客户端选择 Register automatically 并登录 Studio 授权。
3. 在 Code 会话中启用连接器，发送交接提示词，检查实际工具及目标 storyId 的读取结果。

两个入口分别提供打开与连接指引。Claude 自身会同步同账号的连接器，可直接使用已连接的 Studio。此流程在 App 中完成添加和授权，自动注册处理 Client ID 和回调参数。

[官方桌面深链](https://support.claude.com/en/articles/14729294-open-claude-desktop-with-a-link) · [Code 桌面连接器](https://code.claude.com/docs/en/desktop#connect-external-tools)

## 验收

每端从编辑器入口独立开始：检查目标客户端与预填提示词 → 添加本端连接 → 登录同意 → 工具发现 → 按交接 storyId 读取并核对。读取通过后，另行明确一个字段的修改范围，再验证写入、读回和 Studio 显示；付费生成须单独明确范围。刷新、撤销、无权作品和只读权限需各自记录，未完成不能写为全链路通过。报告不保存用户令牌、授权码或密码。
