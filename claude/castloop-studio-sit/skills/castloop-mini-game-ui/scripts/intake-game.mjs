import { mkdir, readFile, realpath, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';

const [projectDir, gameId, ui, rules] = process.argv.slice(2);
if (!projectDir || !ui || !rules || !/^[a-z][a-z0-9-]*$/.test(gameId || '')) {
  throw Error('Usage: node intake-game.mjs <project> <game-id> <UI file or HTTPS URL> <rules file or HTTPS URL>');
}

const project = await realpath(projectDir);
const config = JSON.parse(await readFile(path.join(project, 'project.json'), 'utf8'));
if (!Array.isArray(config.gameplay)) throw Error('Invalid project.json gameplay');
const inputs = path.join(project, 'games', gameId, 'inputs');
const pending = [];
const sources = {};

for (const [role, source] of [['ui', ui], ['rules', rules]]) {
  if (/^https:\/\//i.test(source)) {
    sources[role] = { url: new URL(source).href };
    continue;
  }
  const file = await realpath(source);
  if (!(await stat(file)).isFile()) throw Error('Expected a file: ' + source);
  const relative = role + '/' + path.basename(file);
  sources[role] = { file: relative };
  pending.push([relative, await readFile(file)]);
}
pending.push(['sources.json', Buffer.from(JSON.stringify(sources, null, 2) + '\n')]);

async function existingMatches(file, bytes) {
  try {
    if (!(await readFile(file)).equals(bytes)) throw Error('Input already exists with different content: ' + file);
    return true;
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
}

for (const [relative, bytes] of pending) await existingMatches(path.join(inputs, relative), bytes);
for (const [relative, bytes] of pending) {
  const target = path.join(inputs, relative);
  await mkdir(path.dirname(target), { recursive: true });
  try {
    await writeFile(target, bytes, { flag: 'wx' });
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    await existingMatches(target, bytes);
  }
}

console.log(JSON.stringify({
  gameId,
  registered: config.gameplay.some(game => game.id === gameId),
  inputs,
  sources
}, null, 2));
