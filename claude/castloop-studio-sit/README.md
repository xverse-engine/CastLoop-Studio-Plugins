# CastLoop Studio SIT for Claude

Claude 插件版本 **0.1.1**，仅连接测试环境：`https://castloop-sit.xverse.cn/mcp`。
支持 Claude 聊天（网页、桌面和手机）、Cowork 与 Claude Code。

## 安装与连接

在 Claude 网页或桌面的 Plugins（旧界面 Customize > Plugins）中，选择
Add > Add marketplace，填写 `xverse-engine/CastLoop-Studio-Plugins`，安装 **castloop-studio-sit**。
打开插件的 Connectors 页签，添加／连接内置连接器，登录对应环境 Studio 账号授权。
优先自动注册 OAuth，无需手填 MCP 地址、Client ID 或回调端口。
Team／Enterprise 可能需要管理员先添加或允许连接器。

Claude 桌面 Code：点输入框左侧 **+ → Add plugins** 安装；若显示 Plugins，选
Browse plugins。添加上述仓库市场并安装 **castloop-studio-sit**，再通过 Connectors 登录
Studio 授权。插件不可用时才用 **+ → Connectors** 添加当前环境 MCP 地址。
桌面本地／SSH 会话支持插件浏览器，云端／WSL 会话的限制以客户端为准。

Claude Code CLI 也可独立安装：

```text
/plugin marketplace add xverse-engine/CastLoop-Studio-Plugins
/plugin install castloop-studio-sit@castloop-studio-development
```

CLI 使用 `/mcp` 完成登录授权。账号插件同步需要支持该功能的 Claude Code
版本和 Claude 账号登录；API key／Gateway 登录不保证支持账号同步。
CLI 安装不反向同步到 Claude 账号。安装后开启新会话或按客户端支持使用 `/reload-plugins`。

## 使用

说明创作需求，按需提供故事名称或 ID。首次交接只读，不主动列作品或选择最近故事，
不修改或提交收费任务。后续明确要求修改／生成时按 Skill 和实际工具能力执行。
只读取线上保存内容，浏览器未保存的修改不算已同步。

The plugin bundles creation instructions and one fixed remote MCP connection for
the SIT environment. Installation does not grant access to Studio. Connect and
authorize your own Studio account before requesting tools. Account permissions,
available tools and any generation charges are enforced by the remote service.
Package validation does not verify OAuth login or a successful story read.

安装、授权与连接器／CLI 备选方式见[连接指南](https://github.com/xverse-engine/CastLoop-Studio-Plugins/blob/main/docs/agent-clients.md)。
正式和 SIT 的 OAuth、工具发现与作品读取分别验收，不跨环境替代。
