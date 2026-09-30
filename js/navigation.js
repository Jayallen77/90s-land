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

function initializeDirectory() {
  const toggle = document.querySelector(".menu-toggle");
  const directory = document.querySelector("#museumDirectory");
  if (!toggle || !directory) return;

  toggle.addEventListener("click", () => {
    openDialog(directory, toggle);
    toggle.setAttribute("aria-expanded", "true");
    directory.querySelector("a")?.focus();
  });

  directory.addEventListener("close", () => {
    toggle.setAttribute("aria-expanded", "false");
  });
  directory.addEventListener("click", event => {
    if (event.target.closest("a, [data-directory-passport]")) {
      // Switching dialogs must return focus to the visible menu control.
      if (event.target.closest('[data-directory-passport]')) {
        dialogTriggers.delete(directory);
        directory.close();
      } else closeDialog(directory);
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
  initializeDialogs();
  initializeDirectory();
}
