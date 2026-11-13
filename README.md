# CastLoop Studio Plugins

Agent plugins and MCP connection configurations for CastLoop Studio.

Codex 使用现有插件；ChatGPT 使用远程 MCP 连接器；Claude 聊天、Cowork 和 Claude Code 共用本仓库的 Claude 插件市场。正式与 SIT 分成独立插件，地址由插件提供。Claude 插件已完成本地打包与清单校验，真实客户端 OAuth／工具读取需分别验收，安装成功不代表已连接。详见[客户端连接指南](docs/agent-clients.md)。

本仓库用于维护和分发插件配置、Skills 与品牌资源。工具定义和业务执行由远程 CastLoop Studio Go MCP 服务提供；安装插件不要求下载或运行后端代码。

## 更新与发版约定

正式插件中依赖新版 Studio 编辑器或后端能力的说明、配置和版本号，随配套 Studio 发版一起更新。功能开发阶段先更新 SIT 插件和验收文档，正式插件保留已上线的能力说明。与 Studio 版本无关的独立修正可单独更新正式插件。SIT 插件可按测试需要随时更新。

`scripts/sync-shared-plugin-files.py` 用于配套发版时将已验收的 SIT 共用内容同步到正式包；开发期间允许两者因部署进度不同而存在差异，`--check` 作为同步后的发布检查。

## 当前可用插件

| 插件 | 环境 | 版本 | 能力 |
| --- | --- | --- | --- |
| [CastLoop Studio](plugins/castloop-studio/README.md) | 正式环境 | 1.0.2 | 同步 Studio 3.34.0 独立生成结果入画布与补存指引；以已部署工具为准 |
| [CastLoop Studio SIT](plugins/castloop-studio-sit/README.md) | 测试环境 | 0.1.18 | 同步独立生成结果入画布与补存指引；以实时 schema 和部署回执为准 |

正式作品选择 **CastLoop Studio**；测试作品选择 **CastLoop Studio SIT**。两者连接不同环境，需要对应环境的账号和作品权限。

同一环境的 Codex 与 Claude 插件共用版本号：正式 **1.0.2**，SIT **0.1.18**。版本以 `plugins/<插件名>/.codex-plugin/plugin.json` 为来源，Claude 生成脚本自动同步清单、README 与 ZIP 文件名。以后同环境插件改动统一升版并重新生成，正式与 SIT 仍独立发版。ChatGPT 走连接器，无独立插件包版本。

## 在 Codex 中安装

1. 打开插件目录，选择「添加 → 添加插件市场」。
2. 来源填写 `https://github.com/xverse-engine/CastLoop-Studio-Plugins.git`。Git 引用留空以使用默认分支；稀疏路径留空。
3. 在「CastLoop Studio」市场中安装 **CastLoop Studio**，按客户端提示登录授权；测试环境安装名称带 SIT 的插件。
4. 在新会话中选择插件，即可说明创作需求；需要操作作品时再指定故事名称或 ID。也可以从 Studio 的「连接外部 Agent」入口打开 Codex。

示例：

> 读取故事 <storyId> 的角色，先不要修改。

名称搜索需后端部署 `listStories`，同名作品需先确认具体目标，不会自动选择第一项。工具真正可调用、读取及修改保存成功，才代表连接与读写链路完成验收；技能开关或安装成功不代表已登录。

若曾添加后端仓库或本地目录作为同名市场来源，应通过客户端管理入口移除旧市场来源后再添加本仓库，避免同名市场冲突。无需手工修改个人 TOML 或插件缓存。

## 在 Claude 中安装

1. 在 Claude 网页或桌面的 Plugins（旧界面为 Customize > Plugins）选择 Add > Add marketplace。
2. 填写 `xverse-engine/CastLoop-Studio-Plugins`，正式环境安装 `castloop-studio`，SIT 安装 `castloop-studio-sit`。
3. 打开插件的 Connectors 页签，添加／连接内置连接器，登录对应环境 Studio 账号授权；优先 OAuth 自动注册，无需手填 MCP 地址或 Client ID。组织管理员可能需要先添加或允许连接器。
4. 回到会话说明需求。插件 Skill 可用于网页、桌面与手机聊天、Cowork 和 Claude Code，各端加载其支持的组件。

Claude 桌面 Code 可点输入框左侧 **+ → Add plugins** 安装；若显示 Plugins，选 Browse plugins。安装后通过 Connectors 登录 Studio 授权，插件入口不可用时才用 + → Connectors 手动配置。

Claude Code CLI 可以独立安装：

```text
/plugin marketplace add xverse-engine/CastLoop-Studio-Plugins
/plugin install castloop-studio-sit@castloop-studio-development
```

正式环境将安装命令中的插件名换为 `castloop-studio`。在 `/mcp` 登录 Studio 授权。
账号安装可同步到支持该功能的 Claude Code 版本；API key／Gateway 登录不保证支持账号同步。CLI 安装不反向同步到账号。

Claude 插件位于 `claude/`，采用固定环境 URL 和 OAuth 自动注册，与 Codex 固定公开 Client ID／回调配置隔离。各环境从自己的现有创作 Skill 派生，不同步尚未正式部署的 SIT 能力。

```text
python scripts/build-claude-plugins.py
python scripts/build-claude-plugins.py --check
python -m unittest discover -s scripts/tests -p test_claude_plugins.py -v
```

测试 ZIP：追加 `--archive-dir <仓库外输出目录>`，每包只包含 Claude 清单、MCP、Skill、README 和 LICENSE。源文件生成、清单验证、OAuth 登录、实际故事读取分别验收。

## ChatGPT

继续按[连接指南](docs/agent-clients.md)添加远程 MCP 连接器，SIT 使用已验证的 DCR 流程。无需安装本仓库的 Claude 插件。

## Agent 自动验收

正式版可先执行 [PRD 核心冒烟测试](docs/mcp-prd-smoke-test.md)：使用新建测试故事检查连接、读写、剧情编辑、复制、JSON 往返及可选的少量付费生成；内含可直接交给 Agent 的提示词。

安装并授权后，可将 [SIT MCP 验收任务书](docs/mcp-sit-acceptance.md) 交给 Agent，指定专用测试故事执行。文档包含逐项调用、读回断言、可选收费测试、清理限制与报告模板；不要求手动逐条发测试指令。默认跳过付费生成，Studio 画面与跨账号权限仍单独验收。

## 更新与环境隔离

通过客户端支持的市场刷新、插件更新流程获取新版本，必要时重启并开启新会话。不保证每次提交后已打开的会话即时更新。

正式版使用 `plugins/castloop-studio/`，SIT 使用 `plugins/castloop-studio-sit/`；分别使用不同插件 ID、MCP 地址和 OAuth 应用，版本独立维护。保留现有市场 ID `castloop-studio-development`，只将展示名改为 CastLoop Studio，已有用户无需更换市场来源。正式插件在列表前方，SIT 保留供内部测试。

两包使用相同创作指引与图标。维护共享内容后运行 `python scripts/sync-shared-plugin-files.py`，校验用 `python scripts/sync-shared-plugin-files.py --check`；只有环境说明不同，OAuth 配置独立维护。Git 默认分支直接提供安装与更新，不要求创建 GitHub Release。

## 仓库内容

- `.agents/plugins/marketplace.json`：正式／测试插件市场清单，路径相对于仓库根目录。
- `.claude-plugin/marketplace.json`：Claude 聊天、Cowork、Claude Code 共用市场清单。
- `claude/castloop-studio/`、`claude/castloop-studio-sit/`：独立 Claude 包，每包包含 `.claude-plugin/plugin.json`、固定 URL 的 `.mcp.json` 和创作 Skill。
- 现有 Codex `.codex-plugin/` / `.mcp.json` 配置保持原状。
- `plugins/castloop-studio/`：正式环境插件配置、创作 Skill 和图标。
- `plugins/castloop-studio-sit/`：已验收的 Codex 插件配置、角色操作 Skill 和图标。
- `CHANGELOG.md`：发布与迁移记录。

本仓库不包含后端业务实现、用户故事、用户凭据或服务端密钥。OAuth Client ID 是公开客户端标识，不是密钥。

## 许可

沿用仓库的 [MIT License](LICENSE)。安装插件不授予额外的 Studio 服务访问权限；实际访问仍受账号权限和适用服务条款约束。
