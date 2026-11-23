import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const fixedTokens = new Map([
  ['--fixed-purchase-balance', '#1e22241a'],
  ['--fixed-purchase-surface', '#fffbe7'], ['--fixed-purchase-ink', '#323124'],
  ['--fixed-purchase-muted', '#32312499'], ['--fixed-purchase-action', '#fd6d4b'],
  ['--fixed-purchase-action-ink', '#3b0a00'], ['--fixed-purchase-focus', '#73301f'],
  ['--fixed-danger-ink', '#ffd8db'], ['--fixed-danger-border', '#ff7e91'],
]);

function isChromatic(hex) {
  const digits = hex.slice(1);
  const rgb = digits.length < 5 ? [...digits.slice(0, 3)] : digits.slice(0, 6).match(/../g);
  return new Set(rgb).size > 1;
}

function scan(css, file) {
  const source = css.replace(/\/\*[\s\S]*?\*\//g, '').replace(/url\([^)]*\)/gi, '');
  const issues = [];
  for (const [, property, raw] of source.matchAll(/(?:^|[;{])\s*([\w-]+)\s*:\s*([^;{}]+)/g)) {
    const value = raw.trim().toLowerCase();
    if (fixedTokens.get(property) === value) continue;
    const hex = value.match(/#(?:[\da-f]{8}|[\da-f]{6}|[\da-f]{4}|[\da-f]{3})(?![\w-])/gi) || [];
    const chromatic = hex.filter(isChromatic);
    const functions = [...value.matchAll(/\b(?:rgba?|hsla?|hwb|(?:ok)?lab|(?:ok)?lch|color)\(\s*([^()]*)/g)];
    const literal = functions.some(([, start]) => !/^from\s+(?:var|currentcolor)\b/.test(start));
    const named = /(?:^|[\s,(])(?:purple|violet|rebeccapurple|indigo|magenta|fuchsia|cyan|aqua|teal|blue|navy|red|green|yellow|orange|pink|lime|gold|brown|coral|tomato|turquoise|lavender)(?=$|[\s,)])/i;
    if (chromatic.length || literal || named.test(value)) issues.push(file + ': ' + property + ': ' + raw.trim());
  }
  return issues;
}

export async function auditThemeColors(project) {
  const issues = [];
  async function visit(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        if (!['vendor', 'inputs', 'node_modules', '.git'].includes(entry.name)) await visit(file);
      } else if (/\.(css|html)$/i.test(entry.name)) {
        const source = await readFile(file, 'utf8');
        const relative = path.relative(project, file);
        if (entry.name.endsWith('.css')) issues.push(...scan(source, relative));
        else {
          for (const [, css] of source.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) issues.push(...scan(css, relative));
          for (const [, quote, css] of source.matchAll(/\bstyle\s*=\s*(["'])([\s\S]*?)\1/gi)) issues.push(...scan(css, relative));
        }
      }
    }
  }
  await visit(project);
  return issues;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const project = process.argv[2];
  if (!project) throw Error('Usage: node audit-theme-colors.mjs <project-directory>');
  const issues = await auditThemeColors(path.resolve(project));
  if (issues.length) throw Error('Fixed theme colors found:\n' + issues.join('\n'));
  console.log('CSS and HTML inline theme color audit passed.');
}
