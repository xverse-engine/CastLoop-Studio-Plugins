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
ENVIRONMENTS = {
    'castloop-studio': ('https://studio.castloop.ai/mcp', 'PRD', '正式'),
    'castloop-studio-sit': ('https://castloop-sit.xverse.cn/mcp', 'SIT', '测试'),
}
GUIDE = 'https://github.com/xverse-engine/CastLoop-Studio-Plugins/blob/main/docs/agent-clients.md'
ONBOARDING = '''## First connection and handoff

Check the CastLoop Studio MCP tools actually available in the current session.
Installing this plugin or seeing this skill is not proof that tools are connected.
Use only this plugin's environment; never substitute a production connection for SIT or vice versa.

Reuse this plugin's bundled connector. If disconnected, offer the client's
Connect or Authenticate action and let the user sign in. Never ask for credentials;
never invent an OAuth URL. If already installed, avoid adding a duplicate.
In local Claude Code, follow the matching Studio installation guide from the
handoff when setup is missing. In chat, offer the available native plugin action.
If the account cannot access the plugin, report that limitation.
Recheck available tools after authorization and resume the original request.
If the client requires a reload or fresh session, explain that single next step.

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
        version = codex['version']
        prefix = Path('claude') / name
        files[prefix / '.claude-plugin/plugin.json'] = json_bytes({
            'name': name,
            'version': version, 'description': codex['description'],
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
        game = Path('skills/castloop-mini-game-ui')
        paths = [Path('SKILL.md'), Path('author-guide.md')]
        paths.extend(path.relative_to(root / game) for path in sorted((root / game).rglob('*'))
                     if path.is_file() and path != root / game / 'SKILL.md'
                     and path.suffix in {'.md', '.ts', '.json', '.mjs', '.py'})
        for relative in paths:
            files[prefix / game / relative] = (source / game / relative).read_bytes()
        files[prefix / 'LICENSE'] = (root / 'LICENSE').read_bytes()
        files[prefix / 'README.md'] = f'''# CastLoop Studio {'SIT' if environment == 'SIT' else 'PRD'} for Claude

插件版本 **{version}**，与同环境 Codex 插件共用版本号，仅连接{chinese_environment}环境：`{url}`。
支持 Claude 聊天（网页、桌面和手机）、Cowork 与 Claude Code。

## 安装与连接

从 Studio 打开 Claude 或 Claude Code，发送消息。客户端提供 **{name}** 时，确认安装并登录授权。已安装时直接使用插件内置的连接。工具加载后继续原任务。

Claude Code CLI 可按 Studio 交接消息中的安装说明完成配置。普通聊天需要账号可见的插件。团队管理员和维护者可参考[接入指南]({GUIDE})。

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
    targets = []
    for name in ENVIRONMENTS:
        manifest = json.loads(files[Path('claude') / name / '.claude-plugin/plugin.json'])
        targets.append(output / f"{name}-claude-{manifest['version']}.zip")
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
