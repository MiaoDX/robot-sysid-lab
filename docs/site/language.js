// Paired static pages share anchors, media, and one remembered language choice.
(() => {
  const current = document.documentElement.lang === "zh-CN" ? "zh-CN" : "en";
  const links = [...document.querySelectorAll(".language-switch a")];
  const peer = links.find((a) => a.hreflang !== current);
  const url = new URL(location.href);
  const get = (storage, key) => { try { return window[storage].getItem(key); } catch { return null; } };
  const put = (storage, key, value) => { try { window[storage].setItem(key, value); } catch {} };
  const requested = url.searchParams.get("lang");
  const valid = (lang) => lang === "en" || lang === "zh-CN";
  const isEntry = /\/course\/index(?:\.zh-CN)?\.html$/.test(url.pathname);
  const preferred = requested || (isEntry && get("localStorage", "sysid-language"));
  if (valid(preferred) && preferred !== current && peer) {
    const target = new URL(peer.href);
    target.search = url.search;
    target.searchParams.set("lang", preferred);
    target.hash = url.hash;
    location.replace(target);
    return;
  }
  put("localStorage", "sysid-language", current);

  for (const link of links) {
    const target = new URL(link.href);
    target.search = url.search;
    target.searchParams.set("lang", link.hreflang);
    target.hash = url.hash;
    link.href = target;
    link.addEventListener("click", (event) => {
      if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      target.hash = location.hash;
      link.href = target;
      put("localStorage", "sysid-language", link.hreflang);
      const headings = [...document.querySelectorAll("main [id]")];
      const visible = headings.filter((el) => el.getBoundingClientRect().top <= 140).at(-1);
      const position = {path: target.pathname, id: visible?.id, offset: visible?.getBoundingClientRect().top, y: scrollY};
      put("sessionStorage", "sysid-reading-position", JSON.stringify(position));
    });
  }

  // Explicit language on navigation also makes a copied URL unambiguous.
  for (const link of document.querySelectorAll("a[href]")) {
    if (link.closest(".language-switch") || link.getAttribute("href").startsWith("#")) continue;
    const target = new URL(link.href);
    if (target.origin === location.origin && target.pathname.endsWith(".html")) {
      target.searchParams.set("lang", link.hreflang || current);
      link.href = target;
    }
  }

  const restore = () => {
    let position;
    try { position = JSON.parse(get("sessionStorage", "sysid-reading-position")); } catch { return; }
    if (!position || position.path !== location.pathname) return;
    try { sessionStorage.removeItem("sysid-reading-position"); } catch {}
    const el = position.id && document.getElementById(position.id);
    const top = el ? scrollY + el.getBoundingClientRect().top - position.offset : position.y;
    scrollTo({top, behavior: "instant"});
  };
  if (document.readyState === "complete") restore();
  else addEventListener("load", restore, {once: true});
})();
