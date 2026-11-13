"""Build environment-isolated Claude packages without changing Codex files.

Run after changing the corresponding environment's creation skill. --check
detects drift; --archive-dir exports only the generated public package files.
This does not install plugins, publish them, or authorize an account.
"""
import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.1'
ENVIRONMENTS = {
    'castloop-studio': ('https://studio.castloop.ai/mcp', 'PRD', '正式'),
    'castloop-studio-sit': ('https://castloop-sit.xverse.cn/mcp', 'SIT', '测试'),
}
GUIDE = 'https://github.com/xverse-engine/CastLoop-Studio-Plugins/blob/main/docs/agent-clients.md'
ONBOARDING = '''## First connection and handoff

Check the CastLoop Studio MCP tools actually available in the current session.
Installing this plugin or seeing this skill is not proof that tools are connected.
Use only this plugin's environment; never substitute a production connection for SIT or vice versa.

If tools are unavailable, stop. In Claude chat or Cowork, open this plugin's
Connectors tab, add/connect its bundled connector, then sign in to Studio and
authorize it. Prefer automatic OAuth registration; do not ask users to enter a
Client ID, secret, callback port, password or token. An organization Owner may
need to add/allow the connector first. For Desktop Code installation, direct
users to + > Add plugins beside the prompt box (or Plugins > Browse plugins).
Use + > Connectors to connect and authorize Studio. Give /plugin installation
commands and /mcp authorization instructions to CLI users, not as the only
desktop workflow. Never invent an OAuth URL. Follow the connection guide in
the README for fallback custom connectors or CLI instructions.

If the user replies "Connected", check available tools again. If still absent,
ask them to reload plugins/start a new session, or return to Studio and reopen
the appropriate Claude/Claude Code handoff. Do not claim authentication failed
merely because an existing session has not loaded the tools.

Do not proactively list stories, ask the user to choose one, or pick the most
recent story. Without a user request or explicit story ID, briefly explain how
you can help create and wait. With an explicit story ID, first read and verify
that saved story using readStorySections; never guess another target.

Do not modify stories or submit paid tasks during onboarding. Later edits or
paid generation require an explicit user request under the rules below. Read
saved online content only; unsaved browser content is not synchronized.

'''


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def generated_files(root=ROOT):
    files, entries = {}, []
    for name, (url, environment, chinese_environment) in ENVIRONMENTS.items():
        source = root / 'plugins' / name
        codex = json.loads((source / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        mcp = json.loads((source / '.mcp.json').read_text(encoding='utf-8'))
        if codex['name'] != name or mcp['mcpServers'][name]['url'] != url:
            raise ValueError('Source identity or MCP environment mismatch: ' + name)
        prefix = Path('claude') / name
        files[prefix / '.claude-plugin/plugin.json'] = json_bytes({
            'name': name,
            'version': VERSION, 'description': codex['description'],
            'author': {'name': 'CastLoop'}, 'license': 'MIT',
            'repository': 'https://github.com/xverse-engine/CastLoop-Studio-Plugins',
        })
        # All Claude surfaces see the same fixed URL. No Codex public client or
        # local callback settings: the actual Claude host registers via DCR.
        files[prefix / '.mcp.json'] = json_bytes({'mcpServers': {name: {'type': 'http', 'url': url}}})
        skill = (source / 'skills/studio-creation/SKILL.md').read_text(encoding='utf-8')
        skill = skill.replace('description: ', 'description: Use when connecting or continuing a CastLoop Studio task in Claude. ', 1)
        frontmatter_end = skill.index('\n---', 3) + len('\n---')
        heading_end = skill.index('\n\n', frontmatter_end + 2)
        skill = skill[:heading_end + 2] + ONBOARDING + skill[heading_end + 2:]
        files[prefix / 'skills/studio-creation/SKILL.md'] = skill.encode('utf-8')
        files[prefix / 'LICENSE'] = (root / 'LICENSE').read_bytes()
        files[prefix / 'README.md'] = f'''# CastLoop Studio {'SIT' if environment == 'SIT' else 'PRD'} for Claude

Claude 插件版本 **{VERSION}**，仅连接{chinese_environment}环境：`{url}`。
支持 Claude 聊天（网页、桌面和手机）、Cowork 与 Claude Code。

## 安装与连接

在 Claude 网页或桌面的 Plugins（旧界面 Customize > Plugins）中，选择
Add > Add marketplace，填写 `xverse-engine/CastLoop-Studio-Plugins`，安装 **{name}**。
打开插件的 Connectors 页签，添加／连接内置连接器，登录对应环境 Studio 账号授权。
优先自动注册 OAuth，无需手填 MCP 地址、Client ID 或回调端口。
Team／Enterprise 可能需要管理员先添加或允许连接器。

Claude 桌面 Code：点输入框左侧 **+ → Add plugins** 安装；若显示 Plugins，选
Browse plugins。添加上述仓库市场并安装 **{name}**，再通过 Connectors 登录
Studio 授权。插件不可用时才用 **+ → Connectors** 添加当前环境 MCP 地址。
桌面本地／SSH 会话支持插件浏览器，云端／WSL 会话的限制以客户端为准。

Claude Code CLI 也可独立安装：

```text
/plugin marketplace add xverse-engine/CastLoop-Studio-Plugins
/plugin install {name}@castloop-studio-development
```

CLI 使用 `/mcp` 完成登录授权。账号插件同步需要支持该功能的 Claude Code
版本和 Claude 账号登录；API key／Gateway 登录不保证支持账号同步。
CLI 安装不反向同步到 Claude 账号。安装后开启新会话或按客户端支持使用 `/reload-plugins`。

## 使用

说明创作需求，按需提供故事名称或 ID。首次交接只读，不主动列作品或选择最近故事，
不修改或提交收费任务。后续明确要求修改／生成时按 Skill 和实际工具能力执行。
只读取线上保存内容，浏览器未保存的修改不算已同步。

The plugin bundles creation instructions and one fixed remote MCP connection for
the {environment} environment. Installation does not grant access to Studio. Connect and
authorize your own Studio account before requesting tools. Account permissions,
available tools and any generation charges are enforced by the remote service.
Package validation does not verify OAuth login or a successful story read.

安装、授权与连接器／CLI 备选方式见[连接指南]({GUIDE})。
正式和 SIT 的 OAuth、工具发现与作品读取分别验收，不跨环境替代。
'''.encode('utf-8')
        entries.append({'name': name, 'source': './' + prefix.as_posix(), 'description': codex['description']})
    files[Path('.claude-plugin/marketplace.json')] = json_bytes({
        'name': 'castloop-studio-development', 'owner': {'name': 'CastLoop'},
        'metadata': {'description': 'CastLoop Studio plugins for Claude chat, Cowork and Claude Code'},
        'plugins': entries,
    })
    return files


def write_archives(files, output):
    targets = [output / f'{name}-claude-{VERSION}.zip' for name in ENVIRONMENTS]
    for target in targets:
        if target.exists():
            raise FileExistsError('Archive already exists: ' + str(target))
    output.mkdir(parents=True, exist_ok=True)
    for name, target in zip(ENVIRONMENTS, targets):
        prefix = Path('claude') / name
        with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path, content in files.items():
                if path.parts[:len(prefix.parts)] != prefix.parts:
                    continue
                info = zipfile.ZipInfo(path.relative_to(prefix).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, content)
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--archive-dir', type=Path)
    args = parser.parse_args()
    files = generated_files()
    if args.archive_dir:
        destination = args.archive_dir.resolve()
        if destination == ROOT or ROOT in destination.parents:
            parser.error('Archives must be outside the public repository')
    for relative, content in files.items():
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content.decode('utf-8').replace('\r\n', '\n'):
                raise SystemExit('Claude package differs: ' + relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if args.archive_dir:
        for path in write_archives(files, destination):
            print(path)
    print('Claude packages match' if args.check else 'Claude packages generated; real-client OAuth verification still required')


if __name__ == '__main__':
    main()
