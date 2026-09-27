<main id="main-content">
  <section class="guestbook window">
    <div class="window-bar"><span>GUESTBOOK_SANDBOX.HTML</span><span class="window-buttons" aria-hidden="true">♡ ×</span></div>
    <div class="page-pad">
      <nav class="breadcrumbs"><a href="/">Museum Desk</a> / Guestbook Sandbox</nav>
      <p class="eyebrow">Interactive recreation · nothing leaves this page</p>
      <h1>Preview a guestbook entry.</h1>
      <p class="sandbox-notice" id="guestbookNotice"><strong>This is a sandbox.</strong> Your entry is not sent, stored, published, or shared. Refreshing the page removes the preview.</p>
      <form id="guestbookForm" data-guestbook-form aria-describedby="guestbookNotice">
        <label>Your handle <input name="name" maxlength="24" placeholder="xX_sk8r_1997_Xx" required></label>
        <label>Your message <textarea name="message" maxlength="140" placeholder="this site rules!!!" required></textarea></label>
        <button class="button primary" type="submit">Preview my entry — not saved</button>
      </form>
      <div class="guestbook-entries guestbook-preview" data-guestbook-preview hidden aria-label="Guestbook entry preview"></div>
    </div>
  </section>
  </main>
