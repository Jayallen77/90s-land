# Inactive production header recommendations

These examples are documentation only. They were not applied to Cloudflare,
Nginx, the VPS, or production. Re-test the final production asset host and
third-party requirements before enabling the CSP.

## Recommended policy

- HTML: `Cache-Control: public, max-age=0, must-revalidate`
- Versioned CSS, JavaScript, fonts, and media:
  `Cache-Control: public, max-age=31536000, immutable`
- Other static assets: `Cache-Control: public, max-age=86400`
- `Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src
  'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:;
  font-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self';
  upgrade-insecure-requests`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Content-Type-Options: nosniff`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()`
- `X-Frame-Options: DENY` as a legacy companion to `frame-ancestors`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` only after
  every included subdomain is HTTPS-ready
- Serve `/404.html` for unknown routes while retaining the HTTP 404 status.

## Nginx sketch

```nginx
error_page 404 /404.html;

location = /404.html {
  internal;
}

location ~* \.html$ {
  add_header Cache-Control "public, max-age=0, must-revalidate";
}

location ~* \.(?:css|js|woff2?|ttf|png|jpe?g|gif|webp|avif|svg|ico)$ {
  add_header Cache-Control "public, max-age=31536000, immutable";
}

add_header Content-Security-Policy "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; font-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; upgrade-insecure-requests" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;
add_header X-Frame-Options "DENY" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Cloudflare notes

Create equivalent Transform Rules or Response Header Modification Rules and
Cache Rules. Exclude HTML from immutable caching, keep the custom 404 status,
and stage CSP in report-only mode before enforcement.
