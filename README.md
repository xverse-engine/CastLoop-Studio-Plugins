# CastLoop Studio Plugins

Agent plugins and MCP connection configurations for CastLoop Studio.

本仓库用于维护和分发插件配置、Skills 与品牌资源。工具定义和业务执行由远程 CastLoop Studio Go MCP 服务提供；安装插件不要求下载或运行后端代码。

## 当前可用插件

| 插件 | 环境 | 版本 | 能力 |
| --- | --- | --- | --- |
| [CastLoop Studio SIT](plugins/castloop-studio-sit/README.md) | 测试环境 | 0.1.14 | 增加独立文本、图片、语音、音乐、视频生成指引；配套后端 3.31.0-preview.3，待真实生成验收，以实时 schema 为准 |

当前市场仅提供 SIT 测试插件，需要测试环境账号和目标作品的编辑权限。正式版尚未提供，不用于正式作品。

## 在 Codex 中安装

1. 打开插件目录，选择「添加 → 添加插件市场」。
2. 来源填写 `https://github.com/xverse-engine/CastLoop-Studio-Plugins.git`。Git 引用留空以使用默认分支；稀疏路径留空。
3. 在「CastLoop Studio 内部测试」市场中安装 CastLoop Studio SIT，按客户端提示登录授权。
4. 在新会话中选择该插件，指定 SIT 测试故事的名称或 ID，先读取角色。旧后端没有 `listStories` 时仍需提供 ID。

示例：

> 读取故事 <storyId> 的角色，先不要修改。

名称搜索需后端部署 `listStories`，同名作品需先确认具体目标，不会自动选择第一项。工具真正可调用、读取及修改保存成功，才代表连接与读写链路完成验收；技能开关或安装成功不代表已登录。

若曾添加后端仓库或本地目录作为同名市场来源，应通过客户端管理入口移除旧市场来源后再添加本仓库，避免同名市场冲突。无需手工修改个人 TOML 或插件缓存。

## Agent 自动验收

安装并授权后，可将 [SIT MCP 验收任务书](docs/mcp-sit-acceptance.md) 交给 Agent，指定专用测试故事执行。文档包含逐项调用、读回断言、可选收费测试、清理限制与报告模板；不要求手动逐条发测试指令。默认跳过付费生成，Studio 画面与跨账号权限仍单独验收。

## 更新与环境隔离

通过客户端支持的市场刷新、插件更新流程获取新版本，必要时重启并开启新会话。不保证每次提交后已打开的会话即时更新。

后续正式版使用 `plugins/castloop-studio/`，SIT 保留 `plugins/castloop-studio-sit/`；分别使用不同插件 ID、MCP 地址和 OAuth 应用，版本独立维护。当前不提供占位的正式版安装项。正式发布时默认市场只列正式版，SIT 另设测试市场入口。

## 仓库内容

- `.agents/plugins/marketplace.json`：当前测试市场清单，路径相对于仓库根目录。
- `plugins/castloop-studio-sit/`：已验收的 Codex 插件配置、角色操作 Skill 和图标。
- `CHANGELOG.md`：发布与迁移记录。

本仓库不包含后端业务实现、用户故事、用户凭据或服务端密钥。OAuth Client ID 是公开客户端标识，不是密钥。

## 许可

沿用仓库的 [MIT License](LICENSE)。安装插件不授予额外的 Studio 服务访问权限；实际访问仍受账号权限和适用服务条款约束。
