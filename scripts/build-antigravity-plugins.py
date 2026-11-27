"""Build environment-isolated Antigravity native plugin packages.

Run after changing the corresponding environment's creation skill. --check
detects drift; --archive-dir exports only the generated public package files.
This does not install plugins, publish them, or authorize an account.
"""
import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = {
    'castloop-studio': ('https://studio.castloop.ai/mcp', 'PRD', '正式'),
    'castloop-studio-sit': ('https://castloop-sit.xverse.cn/mcp', 'SIT', '测试'),
}
GUIDE = 'https://github.com/xverse-engine/CastLoop-Studio-Plugins/blob/main/docs/agent-clients.md'
ONBOARDING = '''## First connection and handoff

Check the CastLoop Studio MCP tools actually available in the current session.
Installing this plugin or seeing this skill is not proof that tools are connected.
Use only this plugin's environment; never substitute a production connection for SIT or vice versa.

If tools are unavailable, stop. Ask the user to verify the plugin is enabled in
Antigravity Customizations (or check Additional Options (...) > MCP Servers) and
complete the browser OAuth sign-in flow when prompted. Prefer automatic OAuth
registration; do not ask users to enter a Client ID, secret, callback port,
password or token. Never invent an OAuth URL.

If the user completes sign-in and tools are still absent, ask them to start a
new turn or reload MCP servers in Antigravity before concluding authentication
failed.

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
    files = {}
    for name, (url, environment, chinese_environment) in ENVIRONMENTS.items():
        source = root / 'plugins' / name
        codex = json.loads((source / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        mcp = json.loads((source / '.mcp.json').read_text(encoding='utf-8'))
        if codex['name'] != name or mcp['mcpServers'][name]['url'] != url:
            raise ValueError('Source identity or MCP environment mismatch: ' + name)
        version = codex['version']
        display_name = codex.get('interface', {}).get('displayName', name)
        prompts = list(codex.get('interface', {}).get('defaultPrompt', []))[:3]
        prefix = Path('antigravity') / name
        files[prefix / 'plugin.json'] = json_bytes({
            'name': name,
            'displayName': display_name,
            'version': version,
            'description': codex['description'],
            'author': {'name': 'CastLoop'},
            'repository': 'https://github.com/xverse-engine/CastLoop-Studio-Plugins',
            'logo': 'assets/icon.png',
            'suggestedPrompts': prompts,
        })
        files[prefix / 'mcp_config.json'] = json_bytes({
            'mcpServers': {
                name: {'url': url},
            },
        })
        files[prefix / 'assets/icon.png'] = (source / 'assets/icon.png').read_bytes()
        skill = (source / 'skills/studio-creation/SKILL.md').read_text(encoding='utf-8')
        skill = skill.replace(
            'description: ',
            'description: Use when connecting or continuing a CastLoop Studio task in Antigravity. ',
            1,
        )
        frontmatter_end = skill.index('\n---', 3) + len('\n---')
        heading_end = skill.index('\n\n', frontmatter_end + 2)
        skill = skill[:heading_end + 2] + ONBOARDING + skill[heading_end + 2:]
        files[prefix / 'skills/studio-creation/SKILL.md'] = skill.encode('utf-8')
        game = Path('skills/castloop-mini-game-ui')
        game_source = source / game
        if game_source.is_dir():
            for path in sorted(game_source.rglob('*')):
                if path.is_file() and path.suffix in {'.md', '.ts', '.json', '.mjs', '.py'}:
                    relative = path.relative_to(game_source)
                    files[prefix / game / relative] = path.read_bytes()
        files[prefix / 'LICENSE'] = (root / 'LICENSE').read_bytes()
        files[prefix / 'README.md'] = f'''# {display_name} for Antigravity

插件版本 **{version}**，与同环境 Codex／Claude 插件共用版本号，仅连接{chinese_environment}环境：`{url}`。

## 安装与连接

### 方式一：安装原生 Antigravity 插件（推荐）

将本目录（`antigravity/{name}`）复制到全局插件目录 `~/.gemini/config/plugins/{name}/`（或通过 `agy plugin install` 安装本仓库对应目录）。

安装后插件会自动加载内置的 Streamable HTTP MCP 服务与创作 Skill：
1. 打开 Antigravity，在 **Additional Options (...) → MCP Servers** 中确认 `{name}` 已列出。
2. 首次连接时按提示在浏览器中登录对应环境的 Studio 账号并同意授权（自动走 OAuth 注册，无需手填 Client ID、Secret 或回调端口）。
3. 授权完成后在对话中即可直接调用 Studio 工具。

### 方式二：仅配置远程 MCP

如果只需工具而不安装完整插件，可在 `~/.gemini/config/mcp_config.json` 中添加：

```json
{{
  "mcpServers": {{
    "{name}": {{
      "url": "{url}"
    }}
  }}
}}
```

## 使用

说明创作需求，按需提供故事名称或 ID。首次交接只读，不主动列作品或选择最近故事，不修改或提交收费任务。只读取线上已保存内容，浏览器未保存的修改不算已同步。

更多说明见[连接指南]({GUIDE})。
'''.encode('utf-8')
    return files


def write_archives(files, output):
    targets = []
    for name in ENVIRONMENTS:
        manifest = json.loads(files[Path('antigravity') / name / 'plugin.json'])
        targets.append(output / f"{name}-antigravity-{manifest['version']}.zip")
    for target in targets:
        if target.exists():
            raise FileExistsError('Archive already exists: ' + str(target))
    output.mkdir(parents=True, exist_ok=True)
    for name, target in zip(ENVIRONMENTS, targets):
        prefix = Path('antigravity') / name
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
            if not path.is_file():
                raise SystemExit('Antigravity package missing: ' + relative.as_posix())
            if relative.suffix == '.png':
                if path.read_bytes() != content:
                    raise SystemExit('Antigravity package differs: ' + relative.as_posix())
            elif path.read_text(encoding='utf-8') != content.decode('utf-8').replace('\r\n', '\n'):
                raise SystemExit('Antigravity package differs: ' + relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if args.archive_dir:
        for path in write_archives(files, destination):
            print(path)
    print(
        'Antigravity packages match'
        if args.check
        else 'Antigravity packages generated; real-client OAuth verification still required'
    )


if __name__ == '__main__':
    main()
