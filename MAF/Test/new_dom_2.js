// Lightweight, token-efficient snapshot + diff helper.
// Usage:
//   window.__pwSnap = snapshotDom(window.__pwSnap);
//   console.log(JSON.stringify(window.__pwSnap, null, 2)); // Human Debugging: 0 for llm, 2 for human.
//   window.__pwSnap; // Agent Tool

function snapshotDom(prev) {
  const MAX = 100;
  const INCLUDE_OUTLINE = false;

  const TEST_ID_ATTRS = [
    "data-state",
    "data-slot",
    "data-testid",
    "data-test-id",
    "data-test",
    "data-cy",
    "data-pw",
    "data-qa",
    "data-e2e",
    "data-automation-id",
  ];

  const INTERACTIVE_ROLES = new Set([
    "button",
    "link",
    "textbox",
    "combobox",
    "searchbox",
    "checkbox",
    "radio",
    "slider",
    "spinbutton",
    "switch",
    "menuitem",
    "menuitemcheckbox",
    "menuitemradio",
    "option",
    "tab",
    "treeitem",
    "img",
    "video",
    "audio",
  ]);

  const SELECTOR =
    'input, button, a, form, select, textarea, [role="button"], [role="link"], [role="textbox"], [role="combobox"], [role="searchbox"], [role="checkbox"], [role="radio"], [role="switch"], [role="menuitem"], [role="option"], [role="tab"], [contenteditable="true"]';

  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const s = window.getComputedStyle(el);
    return s && s.visibility !== "hidden" && s.display !== "none";
  };

  const pickText = (el) => {
    let t = (el.innerText || el.value || "").replace(/\s+/g, " ").trim();
    // Strip trailing count badges like "Request 77" or "Request77"
    if (t && /[A-Za-z]/.test(t) && /\d+$/.test(t)) {
      t = t.replace(/\s*\d+\s*$/, "").trim();
    }
    return t ? t.slice(0, 60) : null;
  };

  const getAttr = (el, name) => el.getAttribute(name) || null;

  const cssEscape = (s) => s.replace(/["\\#.:]/g, (m) => "\\" + m);

  const getStableAttr = (el) => {
    for (const attr of TEST_ID_ATTRS) {
      const v = el.getAttribute(attr);
      if (v) return { attr, value: v };
    }
    const id = el.getAttribute("id");
    if (id) return { attr: "id", value: id };
    return null;
  };

  const roleOf = (el) =>
    (el.getAttribute("role") || el.tagName.toLowerCase()).toLowerCase();

  const buildLocator = (el) => {
    const stable = getStableAttr(el);
    if (stable) return `[${stable.attr}="${cssEscape(stable.value)}"]`;

    const tag = el.tagName.toLowerCase();
    const nameAttr = getAttr(el, "name");
    if (tag === "input" && nameAttr)
      return `input[name="${cssEscape(nameAttr)}"]`;

    const role = el.getAttribute("role");
    const name = getAttr(el, "aria-label") || pickText(el) || "";
    if (role && name) return `role=${role}[name="${cssEscape(name)}"]`;
    if (role) return `role=${role}`;
    if (name) return `${el.tagName.toLowerCase()}>>text="${cssEscape(name)}"`;
    return tag;
  };

  const nodes = Array.from(document.querySelectorAll(SELECTOR))
    .filter(visible)
    .slice(0, MAX);

  const items = nodes.map((el) => {
    const tag = el.tagName.toLowerCase();
    const role = roleOf(el);
    const stable = getStableAttr(el);
    const item = {
      tag,
      selector: buildLocator(el),
      text: pickText(el),
      ref: stable ? stable.value : null,
      name: getAttr(el, "name"),
      ariaLabel: getAttr(el, "aria-label"),
      testId: getAttr(el, "data-testid"),
      id: el.id || null,
      href: el.href || null,
      role: role !== tag ? role : null,
    };
    Object.keys(item).forEach((k) => {
      if (item[k] == null || item[k] === "") delete item[k];
    });
    return item;
  });

  // Optional: filter to truly interactive roles if you want even fewer tokens
  const filtered = items.filter((x) => {
    const role = x.role || x.tag;
    return INTERACTIVE_ROLES.has(role) || x.tag === "input";
  });

  const outline = INCLUDE_OUTLINE
    ? Array.from(document.body?.children || [])
        .slice(0, 8)
        .map((el) => el.tagName.toLowerCase())
    : undefined;

  const snap = outline ? { outline, items: filtered } : { items: filtered };

  if (!prev) return snap;

  const key = (x) => `${x.selector}|${x.text || ""}`;
  const prevMap = new Map(prev.items.map((x) => [key(x), x]));
  const curMap = new Map(filtered.map((x) => [key(x), x]));

  const added = [];
  const removed = [];
  for (const k of curMap.keys()) if (!prevMap.has(k)) added.push(curMap.get(k));
  for (const k of prevMap.keys())
    if (!curMap.has(k)) removed.push(prevMap.get(k));

  return { outline, items: filtered, diff: { added, removed } };
}

window.__pwSnap = snapshotDom(window.__pwSnap);
// Debugging: 0 for llm, 2 for human.
// console.log(JSON.stringify(window.__pwSnap, null, 0));
// Agent Tooling: Return the snapshotDom
window.__pwSnap;
