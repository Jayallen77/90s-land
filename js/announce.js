export function announce(message) {
  const region = document.querySelector("#museumStatus");
  if (!region) return;
  region.textContent = "";
  window.requestAnimationFrame(() => {
    region.textContent = message;
  });
}
