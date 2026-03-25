// Lightweight DOM snapshot + diff helper.
// Usage:
//   const snap = window.__pwSnap = snapshotDom(window.__pwSnap);
//   console.log(JSON.stringify(snap, null, 2));

function snapshotDom(prev) {
  const MAX = 100; // cap for token efficiency
  const sel =
    'input, button, a, form, select, textarea, [role="button"], [role="link"], [role="textbox"], [contenteditable="true"]';

  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const style = window.getComputedStyle(el);
    return style && style.visibility !== "hidden" && style.display !== "none";
  };

  const pickText = (el) => {
    const t = (el.innerText || el.value || "").replace(/\s+/g, " ").trim();
    return t ? t.slice(0, 60) : null;
  };

  const pickAttr = (el, name) => el.getAttribute(name) || null;

  const mkSelector = (el) => {
    if (el.id) return `#${cssEscape(el.id)}`;
    const testId = pickAttr(el, "data-testid");
    if (testId) return `[data-testid="${cssEscape(testId)}"]`;
    const name = pickAttr(el, "name");
    if (name) return `${el.tagName.toLowerCase()}[name="${cssEscape(name)}"]`;
    const aria = pickAttr(el, "aria-label");
    if (aria) return `[aria-label="${cssEscape(aria)}"]`;
    const role = pickAttr(el, "role");
    const text = pickText(el);
    if (role && text) return `[role="${role}"]>>text="${text}"`;
    if (text) return `${el.tagName.toLowerCase()}>>text="${text}"`;
    return el.tagName.toLowerCase();
  };

  const cssEscape = (s) => s.replace(/["\\#.:]/g, (m) => "\\" + m);

  const items = [];
  const nodes = Array.from(document.querySelectorAll(sel))
    .filter(visible)
    .slice(0, MAX);

  for (const el of nodes) {
    items.push({
      t: el.tagName.toLowerCase(),
      ty: pickAttr(el, "type"),
      id: el.id || null,
      n: pickAttr(el, "name"),
      a: pickAttr(el, "aria-label"),
      r: pickAttr(el, "role"),
      d: pickAttr(el, "data-testid"),
      tx: pickText(el),
      h: el.href || null,
      s: mkSelector(el),
    });
  }

  // Minimal structure outline
  const outline = [];
  document.body &&
    Array.from(document.body.children)
      .slice(0, 12)
      .forEach((el) => {
        outline.push(el.tagName.toLowerCase());
      });

  const snap = { outline, items };

  if (!prev) return snap;

  // Diff: compare by selector+text
  const key = (x) => `${x.s}|${x.tx || ""}`;
  const prevMap = new Map(prev.items.map((x) => [key(x), x]));
  const curMap = new Map(items.map((x) => [key(x), x]));

  const added = [];
  const removed = [];
  for (const k of curMap.keys()) if (!prevMap.has(k)) added.push(curMap.get(k));
  for (const k of prevMap.keys())
    if (!curMap.has(k)) removed.push(prevMap.get(k));

  return { outline, items, diff: { added, removed } };
}
