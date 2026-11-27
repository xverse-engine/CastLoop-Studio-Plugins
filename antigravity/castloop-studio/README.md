# CastLoop Studio for Antigravity

插件版本 **1.1.0**，与同环境 Codex／Claude 插件共用版本号，仅连接正式环境：`https://studio.castloop.ai/mcp`。

## 安装与连接

### 方式一：安装原生 Antigravity 插件（推荐）

将本目录（`antigravity/castloop-studio`）复制到全局插件目录 `~/.gemini/config/plugins/castloop-studio/`（或通过 `agy plugin install` 安装本仓库对应目录）。

安装后插件会自动加载内置的 Streamable HTTP MCP 服务与创作 Skill：
1. 打开 Antigravity，在 **Additional Options (...) → MCP Servers** 中确认 `castloop-studio` 已列出。
2. 首次连接时按提示在浏览器中登录对应环境的 Studio 账号并同意授权（自动走 OAuth 注册，无需手填 Client ID、Secret 或回调端口）。
3. 授权完成后在对话中即可直接调用 Studio 工具。

### 方式二：仅配置远程 MCP

如果只需工具而不安装完整插件，可在 `~/.gemini/config/mcp_config.json` 中添加：

```json
{
  "mcpServers": {
    "castloop-studio": {
      "url": "https://studio.castloop.ai/mcp"
    }
  }
}
```

## 使用

说明创作需求，按需提供故事名称或 ID。首次交接只读，不主动列作品或选择最近故事，不修改或提交收费任务。只读取线上已保存内容，浏览器未保存的修改不算已同步。

更多说明见[连接指南](https://github.com/xverse-engine/CastLoop-Studio-Plugins/blob/main/docs/agent-clients.md)。
