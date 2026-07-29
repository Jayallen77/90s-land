import { announce } from "./announce.js";

export function initializeGuestbook() {
  const form = document.querySelector("[data-guestbook-form]");
  const preview = document.querySelector("[data-guestbook-preview]");
  if (!form || !preview) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const values = new FormData(form);
    const name = String(values.get("name") || "").trim() || "Anonymous visitor";
    const message =
      String(values.get("message") || "").trim() ||
      "Stopped by the museum desk.";
    preview.replaceChildren();
    const heading = document.createElement("strong");
    heading.textContent = `${name} previewed:`;
    const copy = document.createElement("p");
    copy.textContent = message;
    preview.append(heading, copy);
    preview.hidden = false;
    announce("Guestbook preview updated. Nothing was saved or sent.");
  });
}
