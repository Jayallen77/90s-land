const dialogTriggers = new WeakMap();

function restoreDialogFocus(dialog) {
  const target = dialogTriggers.get(dialog);
  dialogTriggers.delete(dialog);
  if (target?.isConnected) {
    target.focus();
    window.setTimeout(() => {
      if (target.isConnected) target.focus();
    }, 0);
  }
}

function closeMobileMenu(toggle, nav, restoreFocus = false) {
  toggle.setAttribute("aria-expanded", "false");
  nav.classList.remove("is-open");
  document.body.classList.remove("menu-open");
  if (restoreFocus) toggle.focus();
}

function initializeMobileMenu() {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector("#siteNav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const willOpen = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(willOpen));
    nav.classList.toggle("is-open", willOpen);
    document.body.classList.toggle("menu-open", willOpen);
    if (willOpen) nav.querySelector("a")?.focus();
  });

  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMobileMenu(toggle, nav);
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      toggle.getAttribute("aria-expanded") === "true" &&
      !document.querySelector("dialog[open]")
    ) {
      closeMobileMenu(toggle, nav, true);
    }
  });
}

export function openDialog(dialog, trigger = document.activeElement) {
  if (!dialog) return;
  if (trigger) dialogTriggers.set(dialog, trigger);
  if (!dialog.open) dialog.showModal();
}

export function closeDialog(dialog) {
  if (!dialog?.open) return;
  dialog.close();
  restoreDialogFocus(dialog);
}

function initializeDialogs() {
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("close", () => restoreDialogFocus(dialog));
    dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      const target =
        dialogTriggers.get(dialog) ||
        (dialog.id.startsWith("passport")
          ? document.querySelector("[data-passport-trigger]")
          : document.querySelector("[data-surprise-trigger]"));
      dialogTriggers.delete(dialog);
      dialog.close();
      if (target?.isConnected) {
        target.focus();
        window.setTimeout(() => target.focus(), 0);
      }
    });
  });
  document.addEventListener("click", (event) => {
    const close = event.target.closest("[data-dialog-close]");
    if (close) {
      closeDialog(document.getElementById(close.dataset.dialogClose));
      return;
    }

    if (event.target instanceof HTMLDialogElement) {
      const bounds = event.target.getBoundingClientRect();
      const inside =
        event.clientX >= bounds.left &&
        event.clientX <= bounds.right &&
        event.clientY >= bounds.top &&
        event.clientY <= bounds.bottom;
      if (!inside) closeDialog(event.target);
    }
  });
}

export function initializeNavigation() {
  initializeMobileMenu();
  initializeDialogs();
}
