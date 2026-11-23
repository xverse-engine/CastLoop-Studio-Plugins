import { readFile, realpath, lstat } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const identifier = /^[a-z][a-z0-9-]{0,63}$/;
const version = /^\d+\.\d+\.\d+$/;
const capabilities = new Set(['save','unlock','result','exit']);
const methods = new Set(['diamonds','membership','rewarded_ad','free']);
const imageExtensions = new Set(['.png','.jpg','.jpeg','.svg','.gif','.avif','.bmp','.ico','.apng','.tif','.tiff','.heic','.heif','.jxl']);
const extensions = new Set(['.html','.css','.mjs','.js','.json','.webp','.woff','.woff2','.ttf','.otf','.mp3','.wav','.ogg','.mp4','.webm','.txt']);
function requireCondition(value, message) { if (!value) throw Error(message); }
function isWebP(bytes) {
  return bytes.length >= 20 && bytes.toString('ascii',0,4) === 'RIFF'
    && bytes.toString('ascii',8,12) === 'WEBP'
    && ['VP8 ','VP8L','VP8X'].includes(bytes.toString('ascii',12,16))
    && bytes.readUInt32LE(4) === bytes.length - 8
    && bytes.readUInt32LE(16) <= bytes.length - 20;
}
function uniqueStrings(values, label, predicate = () => true) {
  requireCondition(Array.isArray(values) && values.every(v => typeof v === 'string' && predicate(v)) && new Set(values).size === values.length, 'Invalid or duplicate '+label);
}
function safeRelative(value) {
  requireCondition(typeof value === 'string' && value && !path.isAbsolute(value)
    && !/[\\:%?#\x00-\x1f]/.test(value)
    && value.split('/').every(part => part && part !== '.' && part !== '..' && !/[. ]$/.test(part)), 'Expected safe project-relative path: '+value);
  return value;
}
async function readRuntimeFile(root, name) {
  safeRelative(name);
  for (const part of name.split('/')) {
    requireCondition(!part.startsWith('.') && !['inputs','node_modules','sources','tests'].includes(part.toLowerCase()), 'Refusing private runtime file: '+name);
  }
  const extension = path.extname(name).toLowerCase();
  requireCondition(!imageExtensions.has(extension), 'Runtime images must use WebP: '+name);
  requireCondition(extensions.has(extension), 'Unsupported runtime file: '+name);
  let current = root;
  for (const part of name.split('/')) {
    current = path.join(current, part);
    requireCondition(!(await lstat(current)).isSymbolicLink(), 'Refusing symlink runtime file: '+name);
  }
  requireCondition((await lstat(current)).isFile(), 'Runtime dependency is not a file: '+name);
  const bytes = await readFile(current);
  if (extension === '.webp') requireCondition(isWebP(bytes), 'Invalid WebP image bytes: '+name);
  if (['.html','.css','.js','.mjs','.json'].includes(extension)) {
    const embeddedTypes = [...bytes.toString('utf8').matchAll(/data:image\/([a-z0-9.+-]+)/gi)];
    requireCondition(embeddedTypes.every(match => match[1].toLowerCase() === 'webp'), 'Embedded runtime images must use WebP: '+name);
  }
  return bytes;
}

/** Static packaging preflight, not runtime certification or a security sandbox. */
export async function auditRuntime(directory) {
  const root = await realpath(directory);
  const manifestBytes = await readRuntimeFile(root,'game-package.json');
  const config = JSON.parse(manifestBytes.toString('utf8'));
  requireCondition(['1.1.0','1.2.0'].includes(config.specVersion) && config.protocolVersion === '1.1', 'Unsupported package/protocol version');
  requireCondition(identifier.test(config.gameId) && version.test(config.gameVersion), 'Invalid game identity/version');
  requireCondition(['preview','integration','production'].includes(config.runtime?.mode), 'Invalid runtime mode');
  requireCondition(config.runtime?.mode !== 'preview' ? config.runtime.hostAdapter === 'platform' : config.runtime.hostAdapter === 'mock', 'production requires platform adapter; preview requires mock');
  uniqueStrings(config.capabilities,'capabilities',v => capabilities.has(v));
  requireCondition(config.capabilities.includes('result') && config.capabilities.includes('exit'), 'result and exit capabilities required');
  requireCondition(Number.isInteger(config.saveSchemaVersion) && config.saveSchemaVersion > 0, 'Invalid saveSchemaVersion');
  uniqueStrings(config.resultCodes,'resultCodes',v => identifier.test(v));
  requireCondition(config.resultCodes.length > 0, 'At least one resultCode required');
  requireCondition(config.commerce?.authority === 'platform', 'commerce authority must be platform');
  requireCondition(Array.isArray(config.commerce.offers), 'Missing offers declaration');
  const offerIds = new Set();
  for (const offer of config.commerce.offers) {
    requireCondition(identifier.test(offer.offerId) && !offerIds.has(offer.offerId), 'Invalid or duplicate offerId');
    offerIds.add(offer.offerId);
    requireCondition(identifier.test(offer.grantKey), 'Invalid grantKey');
    requireCondition(['unlock','consumable'].includes(offer.kind) && (config.specVersion==='1.2.0' ? offer.scope==='interaction' : ['run','story','account','membership'].includes(offer.scope)), 'Invalid offer kind/scope');
    uniqueStrings(offer.methods,'offer methods',v => methods.has(v));
    requireCondition(offer.methods.length > 0, 'Offer needs a method');
    requireCondition(Object.keys(offer).every(k => ['offerId','grantKey','kind','scope','methods'].includes(k)), 'Offer prices/eligibility belong to platform policy, not runtime declaration');
  }
  requireCondition(!offerIds.size || config.capabilities.includes('unlock'), 'Offers require unlock capability');
  uniqueStrings(config.runtimeFiles,'runtimeFiles');
  requireCondition(new Set(config.runtimeFiles.map(f => f.toLowerCase())).size === config.runtimeFiles.length,'Case-colliding runtime files');
  requireCondition(config.runtimeFiles.includes(config.entry) && /\.html$/.test(config.entry), 'entry HTML must be declared');
  requireCondition(config.runtimeFiles.includes(config.hostBridge) && /\.(m?js)$/.test(config.hostBridge), 'hostBridge JS must be declared');
  const files = new Map([['game-package.json',manifestBytes]]);
  for (const name of config.runtimeFiles) {
    requireCondition(!['game-package.json','generation-manifest.json'].includes(name.toLowerCase()),'Reserved generated filename: '+name);
    const bytes = await readRuntimeFile(root,name);
    if (config.runtime.mode !== 'preview' && /\.(m?js|html)$/.test(name)) {
      requireCondition(!/MOCK_CONFIG|createMockHost|simulated purchase|mock-host/i.test(bytes.toString('utf8')), 'Mock marker in production code: '+name);
    }
    files.set(name,bytes);
  }
  if (config.runtime.mode === 'production') {
    requireCondition(typeof config.releaseEvidence === 'string' && files.has(config.releaseEvidence), 'production release evidence must be declared');
    const evidence = JSON.parse(files.get(config.releaseEvidence).toString('utf8'));
    requireCondition(evidence.gameId === config.gameId && evidence.gameVersion === config.gameVersion && evidence.protocolVersion === config.protocolVersion && evidence.status === 'passed', 'Invalid or stale release evidence identity/status');
    uniqueStrings(evidence.targets,'evidence targets',v => ['web','ios','android'].includes(v));
    requireCondition(evidence.targets.length > 0 && Array.isArray(evidence.checks) && evidence.checks.length > 0
      && evidence.checks.every(c => typeof c.name === 'string' && c.name.trim() && c.status === 'passed'), 'Missing/failed release evidence checks');
    uniqueStrings(evidence.checks.map(c => c.name),'evidence checks');
    const requiredChecks=['host-roundtrip','lifecycle','result'];
    if(config.capabilities.includes('save')) requiredChecks.push('save');
    if(offerIds.size) requiredChecks.push('unlock');
    requireCondition(requiredChecks.every(name => evidence.checks.some(c => c.name === name)), 'Missing required release evidence checks: '+requiredChecks.join(','));
  }
  return {root,config,files};
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    if (process.argv.length !== 3) throw Error('Usage: node audit-runtime.mjs <project-directory>');
    const result = await auditRuntime(process.argv[2]);
    console.log(JSON.stringify({passed:true,mode:result.config.runtime.mode,files:result.files.size,scope:'static-preflight-only'}));
  } catch (error) { console.error(error.message); process.exitCode=1; }
}
