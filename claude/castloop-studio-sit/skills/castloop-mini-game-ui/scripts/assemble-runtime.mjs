import { mkdir, realpath, readdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { auditRuntime } from './audit-runtime.mjs';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function contains(root, candidate) {
  const relative = path.relative(root,candidate);
  return !relative || (!relative.startsWith('..'+path.sep) && relative !== '..' && !path.isAbsolute(relative));
}
async function resolvedDestination(value) {
  try { return await realpath(value); } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    const parent=path.dirname(value);
    if (parent===value) throw error;
    return path.join(await resolvedDestination(parent),path.basename(value));
  }
}

export async function assembleRuntime(project, storyAssetsDirectory) {
  const {root,config,files} = await auditRuntime(project);
  const assetsRoot = await resolvedDestination(path.resolve(storyAssetsDirectory));
  const assetDirectory = `mini-games/${config.gameId}/${config.gameVersion}`;
  const destination = path.join(assetsRoot,...assetDirectory.split('/'));
  if (contains(root,assetsRoot) || contains(assetsRoot,root)) throw Error('Source/output overlap is not allowed');
  if (await resolvedDestination(destination) !== destination) throw Error('Refusing symlink game output directory');
  await mkdir(destination,{recursive:true});
  if ((await readdir(destination)).length) throw Error('Use an empty output directory');
  const entries = {};
  for (const name of [...files.keys()].sort()) {
    const bytes=files.get(name);
    await mkdir(path.dirname(path.join(destination,name)),{recursive:true});
    await writeFile(path.join(destination,name),bytes,{flag:'wx'});
    entries[name]={sha256:hash(bytes),size:bytes.length};
  }
  const manifest={specVersion:config.specVersion,protocolVersion:config.protocolVersion,gameId:config.gameId,gameVersion:config.gameVersion,assetDirectory,
    mode:config.runtime.mode,files:entries,bundleHash:hash(JSON.stringify(entries)),verification:'static-preflight-only'};
  await writeFile(path.join(destination,'generation-manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
  return manifest;
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    if (process.argv.length !== 4) throw Error('Usage: node assemble-runtime.mjs <project-directory> <story-assets-directory>');
    const result=await assembleRuntime(process.argv[2],process.argv[3]);
    console.log(JSON.stringify({gameId:result.gameId,assetDirectory:result.assetDirectory,mode:result.mode,files:Object.keys(result.files).length,bundleHash:result.bundleHash}));
  } catch (error) { console.error(error.message); process.exitCode=1; }
}
