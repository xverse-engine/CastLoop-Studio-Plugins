# 在外部 Agent 中继续创作

编辑器按客户端提供独立的打开按钮和提示词。故事内先保存修改；交接携带 storyId，连接成功后先读取并核对目标。打开链接、安装插件和看到 Skill 不代表工具已连接。

## 环境与验收状态

| 环境 | MCP 地址 | 插件名 |
| --- | --- | --- |
| PRD（国内与海外共用） | `https://studio.castloop.ai/mcp` | `castloop-studio` |
| SIT（测试账号） | `https://castloop-sit.xverse.cn/mcp` | `castloop-studio-sit` |

Codex 已按固定公开 Client ID 流程验证。ChatGPT SIT 的 DCR 登录授权与作品读取已由用户确认。Claude 插件完成源文件、ZIP 与本地清单检查；Claude 聊天、Cowork、Code 的真实 OAuth／工具读取仍需逐端验收。2026-11-13 公开 discovery 检查：SIT 已公布 `/oidc/mcp/register`，PRD 未公布 registration_endpoint，仍声明支持 CIMD。PRD 需要配套更新 Logto 自动注册配置或另行验证 CIMD／预注册路径，不能套用 SIT 结论。正式前端入口仍仅开放 Codex；SIT 按 GPT／Claude 分组提供各自两个打开按钮。

## Codex

按[现有安装说明](../README.md#在-codex-中安装)安装对应环境插件并登录 Studio。既有 Client ID 与本地回调配置保持原状。

## ChatGPT

在设置的连接器／插件中添加自定义 MCP，填写对应环境 MCP 地址，选择 OAuth。SIT 客户端注册使用动态客户端注册（DCR），登录自己的 Studio 账号并授权，再在对话中启用。无需填写 Client ID、Secret 或端口。此流程不要求安装 Git 插件。

## Claude 聊天与 Cowork：优先安装插件

1. 在网页或桌面的 Plugins（旧界面 Customize > Plugins）选择 Add > Add marketplace。
2. 填写 `xverse-engine/CastLoop-Studio-Plugins`，安装表中对应环境插件。仓库功能分支未合入默认分支前，先使用本地构建的 ZIP 验收，不能假定默认分支已有新文件。
3. 打开插件的 **Connectors** 页签，添加／连接内置 Studio 连接器。优先 Register automatically，登录对应环境 Studio 账号授权。插件提供地址，无需自行填 Client ID 或 Secret。Team／Enterprise 可能需要 Owner 先添加或允许连接器。
4. 开启会话并使用插件 Skill。账号插件也可用于手机聊天，安装管理可先在网页／桌面完成。Cowork 新建任务后加载插件。
5. 从编辑器点击「在 Claude 中打开」，链接 `https://claude.ai/new?q=...` 预填交接提示词；没有预填时粘贴。检查当前会话实际工具，再说明需求或读取明确 storyId。

安装不会替用户授权。连接器显示 Connected、会话发现工具、成功读取目标作品是三项独立检查。

## Claude Code：同一插件，独立安装也可

### 桌面应用 Code 页签

1. 在本地或 SSH Code 会话的输入框左侧点击 **+ → Add plugins**。
2. 若菜单显示 Plugins，则选 **Plugins → Browse plugins**；Manage plugins 用于启停或卸载。
3. 在插件浏览器添加 `xverse-engine/CastLoop-Studio-Plugins` 市场，安装当前环境的 `castloop-studio-sit` 或 `castloop-studio`。
4. 通过 **Connectors** 完成 Studio 登录授权；OAuth 优先自动注册。插件入口不可用时，才用 **+ → Connectors** 手动添加当前环境地址。
5. 安装或授权后新建会话，再检查实际工具；必要时回编辑器重新点击对应入口。

这是桌面安装流程，无需先使用终端 `/plugin` 命令。插件浏览器不适用于云端会话，WSL 会话限制以官方说明和实际客户端为准。

### CLI 与账号同步

账号安装的插件可单向同步到同账号登录的 Claude Code，官方要求 v2.1.273 或以上；旧版本请先更新。API key／Gateway／云提供商登录不保证支持账号同步。若需要独立本机安装：

```text
/plugin marketplace add xverse-engine/CastLoop-Studio-Plugins
/plugin install castloop-studio-sit@castloop-studio-development
```

正式环境换为 `castloop-studio@castloop-studio-development`。安装后在 `/mcp` 找到插件提供的 Studio 服务并完成登录授权。开启新会话，或在支持的版本中用 `/reload-plugins` 重新加载。CLI 安装不会反向同步到 Claude 账号。

编辑器「在 Claude Code 中打开」通过 `claude://code/new?q=...` 进入桌面 Code 页签并预填提示词，需要桌面应用和本地 Code 会话。若应用未打开，手动进入 Code 页签并粘贴提示词。手机／网页聊天使用 Claude 聊天入口。

首次交接仅读取线上保存内容，不主动列作品、选择最近故事、修改故事或提交收费任务。后续明确要求修改／生成后按 Skill、实际工具和账号权限执行。

## 无法安装或连接时

- **插件入口不可用**：按客户端支持添加自定义连接器。桌面输入框内左侧 `+` → Connectors / Add connectors；也可在 Plugins／旧版 Customize 中管理连接器。填入表中当前环境 MCP URL，选择 OAuth 自动注册并登录 Studio。
- **Code CLI 备用**：运行下面命令后，在 `/mcp` 完成授权。SIT 示例：

  ```text
  claude mcp add --transport http --scope user castloop-studio-sit https://castloop-sit.xverse.cn/mcp
  ```

  同一客户端优先只保留一种 Studio 安装方式，避免插件和手动配置出现两份同环境工具。
- **自动注册失败**：由管理员检查该环境的 OAuth discovery、注册端点和允许的回调。客户端支持时可由管理员提供为该 Claude 客户端预注册的公开 Client ID；不能直接照搬 Codex 回调，也不应让普通用户创建应用。不要把 Secret、密码或 Token 发到对话中。
- **回复“已连接”后仍无工具**：重新检查实际工具，启动新会话／重载插件；也可回编辑器重新点击对应 Claude／Claude Code 入口。不要仅凭旧会话无工具就认定登录失败，不编造授权 URL。
- **账号或组织限制**：由 Owner 检查插件、连接器与来源权限。Gateway 登录环境以实际支持为准，不承诺账号插件同步。

## 维护与测试

Claude 源包位于 `claude/`，与 Codex 配置隔离。正式与 SIT 各自从对应环境 Skill 派生，保留已部署能力边界。

```text
python scripts/build-claude-plugins.py
python scripts/build-claude-plugins.py --check
python scripts/build-claude-plugins.py --check --archive-dir <仓库外输出目录>
claude plugin validate claude/castloop-studio-sit
claude plugin validate claude/castloop-studio
claude plugin validate .
```

ZIP 可在 Plugins > Add > Upload plugin 上传本账号私测。源文件改变后重新生成，Claude 包单独升版；不要为了 Claude 改变现有 Codex OAuth 配置。生成脚本不会安装、登录或发布插件。

每端验收：安装 → 连接器授权／Code `/mcp` → 新会话工具发现 → 读取指定测试 storyId 并核对。默认不做修改或收费生成；需要时另行明确范围，再验证写入与读回。SIT 与 PRD 分开记录，报告不包含密码、令牌或授权码。

官方参考：[桌面 Code 安装插件](https://code.claude.com/docs/en/desktop#install-plugins) · [插件平台支持](https://claude.com/docs/plugins/platform-support) · [插件安装与连接器](https://claude.com/docs/plugins/overview) · [插件结构和逐端测试](https://claude.com/docs/plugins/build) · [账号插件同步](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) · [桌面深链](https://support.claude.com/en/articles/14729294-open-claude-desktop-with-a-link)
