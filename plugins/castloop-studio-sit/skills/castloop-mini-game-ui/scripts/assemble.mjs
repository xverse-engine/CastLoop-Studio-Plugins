import { access, cp, mkdir, readFile, readdir, realpath, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { auditThemeColors } from './audit-theme-colors.mjs';

const [projectDir, outputDir, artFlag] = process.argv.slice(2);
if (artFlag && artFlag !== "--require-art") throw Error("Unknown option: " + artFlag);
if (!projectDir || !outputDir) throw Error('Usage: node assemble.mjs <project-directory> <empty-output-directory> [--require-art]');
const project = await realpath(projectDir);
const output = path.resolve(outputDir);

function inside(root, relative) {
  const target = path.resolve(root, relative);
  const offset = path.relative(root, target);
  if (!offset || offset === '..' || offset.startsWith('..' + path.sep) || path.isAbsolute(offset)) {
    throw Error('Expected a project-relative path: ' + relative);
  }
  return target;
}

const readJson = async name => JSON.parse(await readFile(inside(project, name), 'utf8'));
const config = await readJson('project.json');
const theme = await readJson(config.theme);
const story = await readJson(config.story);
const slices = await readJson(config.slices);
const asset = name => 'assets/' + name;
const files = new Set([...config.required, config.registry, config.story, config.theme, config.slices, asset(story.referenceImage)]);
const engines = {};
const artFiles = new Map();
const games = new Set();
const themes = new Set();
const identifier = /^[a-z][a-z0-9-]*$/;
if (config.specVersion !== '1.0.0' || !identifier.test(config.id) || story.id !== config.id) throw Error('Invalid project identity or specification version');
if (!config.gameplay.length || !theme.themes.length) throw Error('At least one game and one theme are required');

for (const game of config.gameplay) {
  if (!identifier.test(game.id) || games.has(game.id)) throw Error('Invalid or duplicate game ID: ' + game.id);
  games.add(game.id);
  files.add(game.engine);
  files.add(game.view);
  engines[game.id] = createHash('sha256').update(await readFile(inside(project, game.engine))).digest('hex');
}
const palette = {green:'#B3FF87',cyan:'#97FFFF',blue:'#6EB6FF',purple:'#C2AEFF',pink:'#FFA8EF',yellow:'#FFE565',orange:'#FFA473',red:'#FF8181'};
const fonts = {modern:'Lexend',classic:'Newsreader',future:'Tektur'};
const allowed = new Set(['id','label','palette','fontStyle','displayFont','panel','surface','radius','motion','source','scene']);
for (const variant of theme.themes) {
  if (!identifier.test(variant.id) || themes.has(variant.id)) throw Error('Invalid or duplicate theme ID: ' + variant.id);
  if (Object.keys(variant).some(key => !allowed.has(key))) throw Error('Unknown theme field: ' + variant.id);
  if (!Object.hasOwn(palette, variant.palette) || theme.palettes.find(p => p.id === variant.palette)?.main !== palette[variant.palette] ||
      !Object.hasOwn(fonts, variant.fontStyle) || fonts[variant.fontStyle] !== variant.displayFont) throw Error('Theme palette or font outside catalog');
  themes.add(variant.id);
  if (!slices[variant.id] || slices[variant.id].pieces.length !== 9) throw Error('Expected nine slices: ' + variant.id);
  if (artFlag === '--require-art') {
    const { sourceCorner: [cw, ch], sourceSize: [w, h], pieces } = slices[variant.id];
    if (![cw, ch, w, h].every(Number.isInteger) || cw <= 0 || ch <= 0 || w <= 2*cw || h <= 2*ch) {
      throw Error('Invalid nine-slice geometry: ' + variant.id);
    }
    const xs = [0, cw, w-cw, w], ys = [0, ch, h-ch, h];
    const cells = new Set();
    for (const { row, col, box } of pieces) {
      const cell = row + ':' + col;
      if (![0, 1, 2].includes(row) || ![0, 1, 2].includes(col) || cells.has(cell) ||
          JSON.stringify(box) !== JSON.stringify([xs[col], ys[row], xs[col+1], ys[row+1]])) {
        throw Error('Expected nine contiguous, aligned slices: ' + variant.id + ' ' + cell);
      }
      cells.add(cell);
    }
  }
  artFiles.set(asset(variant.scene), "scene");
  artFiles.set(asset(variant.panel), "panel");
  files.add(asset(variant.scene));
  files.add(asset(variant.panel));
  for (const piece of slices[variant.id].pieces) {
    files.add(asset(piece.file));
    artFiles.set(asset(piece.file), "panel");
  }
  for (const game of config.gameplay) for (const sprite of game.sprites) {
    const file = asset(variant.id + '-' + (story.itemAliases[sprite] || sprite) + '.png');
    files.add(file);
    artFiles.set(file, 'item');
  }
}
if (artFlag === '--require-art') {
  const colorIssues = await auditThemeColors(project);
  if (colorIssues.length) throw Error('Fixed theme colors found:\n' + colorIssues.join('\n'));
  const art = await readJson('art-manifest.json');
  if (art.storyId !== story.id || !Array.isArray(art.assets)) throw Error('Invalid story art manifest');
  const covered = new Set();
  for (const entry of art.assets) {
    if (typeof entry.source !== 'string' || !entry.source || typeof entry.prompt !== 'string' ||
        !entry.prompt.trim() || !Array.isArray(entry.files) || !entry.files.length) {
      throw Error('Art entries require a source image, prompt and runtime files');
    }
    files.add(entry.source);
    for (const file of entry.files) {
      if (artFiles.get(file) !== entry.role || covered.has(file)) throw Error('Unexpected or duplicate art mapping: ' + file);
      covered.add(file);
    }
  }
  for (const file of artFiles.keys()) {
    if (!covered.has(file)) throw Error('Missing generated art mapping: ' + file);
    const bytes = await readFile(inside(project, file));
    const raster = bytes.subarray(0, 8).equals(Buffer.from('89504e470d0a1a0a', 'hex')) ||
      (bytes.toString('ascii', 0, 4) === 'RIFF' && bytes.toString('ascii', 8, 12) === 'WEBP') ||
      bytes.subarray(0, 3).equals(Buffer.from('ffd8ff', 'hex'));
    if (!raster) throw Error('Expected PNG, WebP or JPEG artwork: ' + file);
  }
  files.add('art-manifest.json');
}
for (const name of files) {
  const file = await realpath(inside(project, name));
  inside(project, file);
  await access(file);
}
await mkdir(output, {recursive:true});
const actualOutput = await realpath(output);
if (actualOutput === project || actualOutput.startsWith(project + path.sep)) throw Error('Output must be outside the source project');
if ((await readdir(actualOutput)).length) throw Error('Use an empty output directory');
await cp(project, actualOutput, {
  recursive: true,
  filter(source) {
    const [folder, game, entry] = path.relative(project, source).split(path.sep);
    return !(folder === 'games' && game && entry === 'inputs');
  }
});
const manifest = {specVersion:config.specVersion, project:config.id, gameplay:[...games], themes:[...themes], engineHashes:engines, requiredFiles:files.size};
await writeFile(path.join(actualOutput, 'generation-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify(manifest));
