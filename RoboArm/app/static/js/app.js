// RoboArm Phase I — UI controls (language / font / size)
(function () {
  "use strict";

  function applyFontVars(family, size) {
    const root = document.documentElement;
    if (family) root.style.setProperty("--app-font-family", family);
    if (size) root.style.setProperty("--app-font-size", size + "px");
    updateStage(family, size);
  }

  function updateStage(family, size) {
    const sizeEl = document.querySelector(".font-stage__size");
    const familyEl = document.querySelector(".font-stage__family");
    if (size && sizeEl) sizeEl.textContent = size + "px";
    if (family && familyEl) {
      const display = family.replace(/^"|"$/g, "").split(",")[0].trim();
      familyEl.textContent = display;
    }
  }

  function submitForm() {
    const form = document.getElementById("pref-form");
    if (form) form.submit();
  }

  const langSel = document.getElementById("lang-select");
  if (langSel) langSel.addEventListener("change", submitForm);

  const sizeInput = document.getElementById("font-size-input");
  if (sizeInput) {
    sizeInput.addEventListener("input", function () {
      const v = parseInt(sizeInput.value, 10);
      if (!isNaN(v) && v >= 10 && v <= 28) applyFontVars(null, v);
    });
    sizeInput.addEventListener("change", submitForm);
  }

  const fontSel = document.getElementById("font-family-select");
  if (fontSel) {
    fontSel.addEventListener("change", function () {
      const opt = fontSel.options[fontSel.selectedIndex];
      const cssValue = opt.getAttribute("data-css") || opt.value;
      applyFontVars(cssValue, null);
      submitForm();
    });
  }
})();
