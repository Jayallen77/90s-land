async function start() {
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
  const { initializeSearch } = await import("./search.js?v=phase5-1");
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

if (document.querySelector('[data-timeline], [data-weekly], #this-week')) {
  const { initializeArchiveTimeline, initializeWeek } = await import('./archive.js?v=phase5-1');
  initializeArchiveTimeline();
  initializeWeek();
}

if (document.querySelector(".ed-main")) {
  const { initializeEditorial } = await import("./editorial.js?v=phase5-1");
  initializeEditorial();
}

if (document.querySelector('[data-hub]')) {
  const { initializeHubs } = await import('./hubs.js?v=phase5-1');
  initializeHubs();
}

}
start().catch(error => {
  document.documentElement.classList.replace("js", "no-js");
  console.error("Enhancements unavailable; showing the static archive.", error);
});
