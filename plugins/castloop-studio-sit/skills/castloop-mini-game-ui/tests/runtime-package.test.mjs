import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, readFile, mkdir, rm, readdir, symlink } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { auditRuntime } from '../scripts/audit-runtime.mjs';
import { assembleRuntime } from '../scripts/assemble-runtime.mjs';

const webp = Buffer.from('UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA', 'base64');
const gameDirectory = output => path.join(output, 'mini-games', 'test-game', '1.0.0');

async function fixture(fn) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'castloop-package-test-'));
  try {
    const src = path.join(root, 'source'); await mkdir(src);
    const config = { specVersion: '1.1.0', protocolVersion: '1.1', gameId: 'test-game', gameVersion: '1.0.0',
      entry: 'index.html', runtime: { mode: 'production', hostAdapter: 'platform' }, hostBridge: 'host.mjs',
      capabilities: ['save', 'unlock', 'result', 'exit'], saveSchemaVersion: 1, resultCodes: ['success', 'failure'],
      commerce: { authority: 'platform', offers: [{ offerId: 'hint-01', grantKey: 'hint-01', kind: 'unlock', scope: 'run', methods: ['diamonds', 'membership', 'rewarded_ad'] }] },
      runtimeFiles: ['cover.webp', 'index.html', 'host.mjs', 'release.json'], releaseEvidence: 'release.json' };
    await writeFile(path.join(src, 'cover.webp'), webp);
    await writeFile(path.join(src, 'index.html'), '<script type="module" src="host.mjs"></script>');
    await writeFile(path.join(src, 'host.mjs'), 'export const protocolVersion = "1.1";');
    await writeFile(path.join(src, 'release.json'), JSON.stringify({ gameId: 'test-game', gameVersion: '1.0.0', protocolVersion: '1.1', status: 'passed', targets: ['web'], checks: ['host-roundtrip','lifecycle','result','save','unlock'].map(name=>({name,status:'passed'})) }));
    const save = () => writeFile(path.join(src, 'game-package.json'), JSON.stringify(config));
    await save(); await fn({ root, src, config, save });
  } finally {
    const relative = path.relative(os.tmpdir(), root);
    if (relative.startsWith('..') || path.isAbsolute(relative) || !path.basename(root).startsWith('castloop-package-test-')) throw Error('unsafe test cleanup');
    await rm(root, { recursive: true, force: true });
  }
}

test('copies only declared runtime files and hashes the exact output reproducibly', () => fixture(async ({root,src}) => {
  await writeFile(path.join(src, '.env'), 'secret=never-ship');
  const first = await assembleRuntime(src, path.join(root, 'one'));
  const second = await assembleRuntime(src, path.join(root, 'two'));
  assert.equal(first.bundleHash, second.bundleHash);
  assert.deepEqual((await readdir(gameDirectory(path.join(root, 'one')))).sort(), ['cover.webp','game-package.json','generation-manifest.json','host.mjs','index.html','release.json']);
  assert.equal(first.files['host.mjs'].sha256.length, 64);
  assert.equal(JSON.parse(await readFile(path.join(gameDirectory(path.join(root,'one')),'game-package.json'),'utf8')).gameId, 'test-game');
  await writeFile(path.join(src,'host.mjs'),'export const changed = true;');
  const changed = await assembleRuntime(src, path.join(root, 'three'));
  assert.notEqual(changed.bundleHash, first.bundleHash);
}));
test('rejects production mock adapters and mock code markers', () => fixture(async ({src,config,save}) => {
  config.runtime.hostAdapter = 'mock'; await save(); await assert.rejects(auditRuntime(src), /production.*platform/);
  config.runtime.hostAdapter = 'platform'; await save();
  await writeFile(path.join(src,'host.mjs'),'const MOCK_CONFIG = {};');
  await assert.rejects(auditRuntime(src), /Mock/);
}));
test('preview permits explicit mock and remains labelled preview', () => fixture(async ({src,config,save}) => {
  config.runtime = { mode: 'preview', hostAdapter: 'mock' }; delete config.releaseEvidence;
  config.runtimeFiles = ['cover.webp','index.html','host.mjs']; await save();
  assert.equal((await auditRuntime(src)).config.runtime.mode,'preview');
}));
test('1.2 interaction integration package is auditable but is never production certification', () => fixture(async ({src,config,save}) => {
  config.specVersion='1.2.0';config.runtime={mode:'integration',hostAdapter:'platform'};
  config.commerce.offers[0].scope='interaction';delete config.releaseEvidence;
  config.runtimeFiles=['cover.webp','index.html','host.mjs'];await save();
  assert.equal((await auditRuntime(src)).config.runtime.mode,'integration');
  config.commerce.offers[0].scope='run';await save();await assert.rejects(auditRuntime(src),/scope/);
  config.commerce.offers[0].scope='interaction';config.runtime.mode='production';await save();await assert.rejects(auditRuntime(src),/evidence/);
}));
test('requires server-owned commerce, unique offers and an unlock capability', () => fixture(async ({src,config,save}) => {
  config.commerce.authority='client'; await save(); await assert.rejects(auditRuntime(src), /authority/);
  config.commerce.authority='platform'; config.commerce.offers.push({...config.commerce.offers[0]}); await save(); await assert.rejects(auditRuntime(src), /offerId/);
  config.commerce.offers.pop(); config.capabilities=['save','result','exit']; await save(); await assert.rejects(auditRuntime(src), /unlock/);
}));
test('rejects runtime traversal, missing resources and private files', () => fixture(async ({src,config,save}) => {
  config.runtimeFiles.push('../outside.js'); await save(); await assert.rejects(auditRuntime(src), /relative/);
  config.runtimeFiles.pop(); config.runtimeFiles.push('absent.webp'); await save(); await assert.rejects(auditRuntime(src), /ENOENT/);
  config.runtimeFiles.pop(); config.runtimeFiles.push('.env'); await save(); await assert.rejects(auditRuntime(src), /private/);
}));
test('rejects symlink resources without following them', () => fixture(async ({root,src,config,save}) => {
  await mkdir(path.join(root,'outside')); await symlink(path.join(root,'outside'),path.join(src,'linked'),'junction');
  config.runtimeFiles.push('linked/leak.js'); await save(); await assert.rejects(auditRuntime(src), /symlink/);
}));
test('requires matching passed release evidence and rejects stale/failing evidence', () => fixture(async ({src}) => {
  await writeFile(path.join(src,'release.json'), JSON.stringify({status:'passed',gameVersion:'old'}));
  await assert.rejects(auditRuntime(src), /evidence/);
}));
test('rejects runtime prices and incomplete release checks', () => fixture(async ({src,config,save}) => {
  config.commerce.offers[0].price=10; await save(); await assert.rejects(auditRuntime(src), /prices/);
  delete config.commerce.offers[0].price; await save();
  const evidence=JSON.parse(await readFile(path.join(src,'release.json'),'utf8'));
  evidence.checks=evidence.checks.filter(c=>c.name!=='unlock');
  await writeFile(path.join(src,'release.json'),JSON.stringify(evidence));
  await assert.rejects(auditRuntime(src), /required release/);
}));
test('refuses existing nonempty output and either ancestor relation', () => fixture(async ({src,root}) => {
  await assert.rejects(assembleRuntime(src, path.join(src,'output')), /overlap/);
  await assert.rejects(assembleRuntime(src, root), /overlap/);
  const output=path.join(root,'output'); await mkdir(gameDirectory(output),{recursive:true}); await writeFile(path.join(gameDirectory(output),'keep.txt'),'keep');
  await assert.rejects(assembleRuntime(src,output), /empty/);
  assert.equal(await readFile(path.join(gameDirectory(output),'keep.txt'),'utf8'),'keep');
}));

test('rejects non-WebP runtime images including vector images', () => fixture(async ({src,config,save}) => {
  for (const extension of ['png','jpg','jpeg','svg','gif','avif','bmp','ico','apng','tif','tiff']) {
    const name=`image.${extension}`;
    await writeFile(path.join(src,name),'not a WebP image');
    config.runtimeFiles.push(name); await save();
    await assert.rejects(auditRuntime(src), /WebP/, extension);
    config.runtimeFiles.pop();
  }
}));

test('accepts actual WebP images and rejects a PNG renamed as WebP', () => fixture(async ({src,root,config,save}) => {
  config.runtimeFiles.push('scene.webp'); await save();
  await writeFile(path.join(src,'scene.webp'),webp);
  const manifest=await assembleRuntime(src,path.join(root,'assets'));
  assert.deepEqual(await readFile(path.join(gameDirectory(path.join(root,'assets')),'scene.webp')),webp);
  assert.equal(manifest.files['scene.webp'].size,webp.length);
  await writeFile(path.join(src,'scene.webp'),Buffer.from('89504e470d0a1a0a','hex'));
  await assert.rejects(auditRuntime(src), /WebP/);
}));

test('rejects embedded non-WebP image data instead of bypassing the image rule', () => fixture(async ({src}) => {
  await writeFile(path.join(src,'index.html'),'<img src="data:image/png;base64,iVBORw0KGgo=">');
  await assert.rejects(auditRuntime(src), /WebP/);
}));

test('keeps games and versions independent inside the same story assets directory', () => fixture(async ({src,root,config,save}) => {
  const assets=path.join(root,'story-assets');
  await mkdir(assets); await writeFile(path.join(assets,'story-cover.webp'),webp);
  await assembleRuntime(src,assets);
  config.gameId='another-game';
  const evidence=JSON.parse(await readFile(path.join(src,'release.json'),'utf8'));
  evidence.gameId=config.gameId; await writeFile(path.join(src,'release.json'),JSON.stringify(evidence));
  await save(); await assembleRuntime(src,assets);
  config.gameVersion='1.0.1'; evidence.gameVersion=config.gameVersion;
  await writeFile(path.join(src,'release.json'),JSON.stringify(evidence));
  await save(); const result=await assembleRuntime(src,assets);
  assert.equal(result.assetDirectory,'mini-games/another-game/1.0.1');
  assert.deepEqual((await readdir(path.join(assets,'mini-games'))).sort(),['another-game','test-game']);
  assert.deepEqual((await readdir(path.join(assets,'mini-games','another-game'))).sort(),['1.0.0','1.0.1']);
  assert.equal(JSON.parse(await readFile(path.join(gameDirectory(assets),'game-package.json'),'utf8')).gameId,'test-game');
  assert.deepEqual(await readFile(path.join(assets,'story-cover.webp')),webp);
}));

test('requires a declared library cover', () => fixture(async ({config,save,src}) => {
  config.runtimeFiles = config.runtimeFiles.filter(name => name !== 'cover.webp'); await save();
  await assert.rejects(auditRuntime(src), /cover.webp/);
}));
