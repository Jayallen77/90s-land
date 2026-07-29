document.documentElement.classList.replace("no-js", "js");

const [{ initializeNavigation }, { initializePassport }, { initializeSurprise }] =
  await Promise.all([
    import("./navigation.js"),
    import("./passport.js"),
    import("./surprise.js"),
  ]);

initializeNavigation();
initializePassport();
initializeSurprise();

if (document.querySelector("[data-tour-id], [data-homepage-builder]")) {
  const { initializeHomepageBuilder, initializeTour } = await import("./tour.js");
  initializeTour();
  initializeHomepageBuilder();
}

if (document.querySelector("#siteSearchInput")) {
  const { initializeSearch } = await import("./search.js");
  initializeSearch();
}

if (document.querySelector("#resourceGrid")) {
  const { initializeResources } = await import("./resources.js");
  initializeResources();
}

if (document.querySelector("[data-guestbook-form]")) {
  const { initializeGuestbook } = await import("./guestbook.js");
  initializeGuestbook();
}
