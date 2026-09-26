// Render math from authored Markdown without a remote CDN or Python server.
(() => {
  if (!window.katex) return;
  const walker = document.createTreeWalker(document.querySelector("main"), NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) if (!walker.currentNode.parentElement.closest("pre,code,script,style")) nodes.push(walker.currentNode);
  const pattern = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g;
  for (const node of nodes) {
    const matches = [...node.textContent.matchAll(pattern)];
    if (!matches.length) continue;
    const fragment = document.createDocumentFragment();
    let index = 0;
    for (const match of matches) {
      fragment.append(node.textContent.slice(index, match.index));
      const element = document.createElement("span");
      katex.render(match[1] || match[2], element, {displayMode: !!match[1], throwOnError: false, trust: false});
      fragment.append(element);
      index = match.index + match[0].length;
    }
    fragment.append(node.textContent.slice(index));
    node.replaceWith(fragment);
  }
})();
