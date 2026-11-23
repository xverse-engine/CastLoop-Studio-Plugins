/**
 * Verify visible player text in the current state of a Chromium Playwright page.
 * The expected family comes from story input, not from the rendered CSS.
 */
export async function auditPlayerFonts(page, {
  root = '#game',
  family,
  weight = '500',
  renderedNames = [family],
  exceptions = []
} = {}) {
  if (!family) throw Error('An expected story font family is required');
  await page.evaluate(() => document.fonts.ready);
  const nodes = await page.evaluate(({ root, exceptions }) => {
    const player = document.querySelector(root);
    if (!player) throw Error('Player root not found: ' + root);
    const walker = document.createTreeWalker(player, NodeFilter.SHOW_TEXT);
    const found = new Map();

    function selector(element) {
      const parts = [];
      for (let node = element; node; node = node.parentElement) {
        const index = node.parentElement ? Array.from(node.parentElement.children).indexOf(node) + 1 : 1;
        parts.unshift(':nth-child(' + index + ')');
      }
      return parts.join(' > ');
    }

    while (walker.nextNode()) {
      const text = walker.currentNode;
      const element = text.parentElement;
      if (!text.textContent.trim() || !element ||
          element.closest('script, style, template, [hidden], [aria-hidden="true"]') ||
          exceptions.some(rule => element.closest(rule))) continue;
      const style = getComputedStyle(element);
      if (style.visibility !== 'visible') continue;
      const range = document.createRange();
      range.selectNodeContents(text);
      if (!Array.from(range.getClientRects()).some(rect => rect.width > 0 && rect.height > 0)) continue;
      const key = selector(element);
      found.set(key, {
        selector: key,
        text: (found.get(key)?.text || '') + text.textContent.trim(),
        family: style.fontFamily.split(',')[0].trim().replace(/^['"]|['"]$/g, ''),
        weight: style.fontWeight
      });
    }
    return [...found.values()];
  }, { root, exceptions });

  if (!nodes.length) throw Error('No rendered text found in ' + root + '; enter a visible player state first');
  const session = await page.context().newCDPSession(page);
  const issues = [];
  try {
    await session.send('DOM.enable');
    await session.send('CSS.enable');
    const { root: documentNode } = await session.send('DOM.getDocument');
    for (const node of nodes) {
      const { nodeId } = await session.send('DOM.querySelector', {
        nodeId: documentNode.nodeId,
        selector: node.selector
      });
      if (!nodeId) throw Error('Player state changed during font audit: ' + node.selector);
      const { fonts } = await session.send('CSS.getPlatformFontsForNode', { nodeId });
      const used = fonts.filter(font => font.glyphCount > 0);
      if (node.family !== family || node.weight !== String(weight) || !used.length ||
          used.some(font => !font.isCustomFont ||
            !renderedNames.includes(font.familyName) && !renderedNames.includes(font.postScriptName))) {
        issues.push({ ...node, used });
      }
    }
  } finally {
    await session.detach();
  }
  return { checked: nodes.length, issues };
}
