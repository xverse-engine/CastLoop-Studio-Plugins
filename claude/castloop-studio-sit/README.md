# CastLoop Studio SIT for Claude

插件版本 **0.1.24**，与同环境 Codex 插件共用版本号，仅连接测试环境：`https://castloop-sit.xverse.cn/mcp`。
支持 Claude 聊天（网页、桌面和手机）、Cowork 与 Claude Code。

## 安装与连接

从 Studio 打开 Claude 或 Claude Code，发送消息。客户端提供 **castloop-studio-sit** 时，确认安装并登录授权。已安装时直接使用插件内置的连接。工具加载后继续原任务。

Claude Code CLI 可按 Studio 交接消息中的安装说明完成配置。普通聊天需要账号可见的插件。团队管理员和维护者可参考[接入指南](https://github.com/xverse-engine/CastLoop-Studio-Plugins/blob/main/docs/agent-clients.md)。

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
