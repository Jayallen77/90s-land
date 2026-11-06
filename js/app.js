async function start() {
 document.documentElement.classList.replace("no-js", "js");

const [{ initializeNavigation }, { initializePassport }, { initializeSurprise }] =
  await Promise.all([
    import("./navigation.js?v=connected-20261106"),
    import("./passport.js?v=connected-20261106"),
    import("./surprise.js?v=connected-20261106"),
  ]);

initializeNavigation();
initializePassport();
initializeSurprise();

if(document.querySelector('[data-reading-tool]')){
 const {initializeReadingTools}=await import('./reading-tools.js?v=connected-20261106');
 initializeReadingTools();
}

if(document.querySelector('[data-web-exhibit]')){
 const {initializeExhibits}=await import('./exhibits.js');
 initializeExhibits();
}


if (document.querySelector("[data-tour-id], [data-homepage-builder]")) {
  const { initializeHomepageBuilder, initializeTour } = await import("./tour.js?v=connected-20261106");
  initializeTour();
  initializeHomepageBuilder();
}

if (document.querySelector("#siteSearchInput")) {
  const { initializeSearch } = await import("./search.js?v=connected-20261106");
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
  const { initializeArchiveTimeline, initializeWeek } = await import('./archive.js?v=connected-20261106');
  initializeArchiveTimeline();
  initializeWeek();
}

if (document.querySelector(".ed-main")) {
  const { initializeEditorial } = await import("./editorial.js?v=connected-20261106");
  initializeEditorial();
}

if (document.querySelector('[data-hub]')) {
  const { initializeHubs } = await import('./hubs.js?v=connected-20261106');
  initializeHubs();
}

}
start().catch(error => {
  document.documentElement.classList.replace("js", "no-js");
  console.error("Enhancements unavailable; showing the static archive.", error);
});
