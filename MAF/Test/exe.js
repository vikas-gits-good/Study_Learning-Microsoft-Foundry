() => {
  const selectors =
    'input, button, a, form, select, textarea, [role="button"], [role="link"]';
  const elements = [...document.querySelectorAll(selectors)]
    .filter((el) => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    })
    .slice(0, 80)
    .map((el) => ({
      tag: el.tagName.toLowerCase(),
      type: el.getAttribute("type") || null,
      id: el.id || null,
      name: el.getAttribute("name") || null,
      placeholder: el.getAttribute("placeholder") || null,
      ariaLabel: el.getAttribute("aria-label") || null,
      testId: el.getAttribute("data-testid") || null,
      text: (el.innerText || el.value || "").slice(0, 80) || null,
      href: el.href || null,
    }));
  return elements.reduce((acc, el) => {
    Object.keys(el).forEach((key) => {
      if (!acc[key]) acc[key] = [];
      acc[key].push(el[key]);
    });
    return acc;
  }, {});
};
