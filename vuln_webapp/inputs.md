Full URLs / path variants — normal path, trailing slash vs none, encoded chars, path traversal segments.
- Example: /products/123, /products/123/, /%2e%2e/%2e%2e/etc/passwd

Query strings & params — empty/missing, repeated params, huge values, special chars.
- Example: ?q=&q=admin&id=1&id=2&search=A...A(50k)

Form bodies — normal form-encoded, multipart with file, mismatched content-type.
- Example: application/x-www-form-urlencoded vs multipart/form-data

Headers — Host, Origin, Referer, User-Agent, cookies, custom headers, duplicated headers.
- Example: Origin: https://evil.com, Cookie: session=...

Cookies & session tokens — truncated, expired, tampered, very long, special chars.

Uploaded files — different extensions, renamed types, nested archives, huge files, corrupted headers.

WebSocket frames — text and binary frames, fragmented frames, large frames.

Client-side inputs — postMessage payloads, localStorage values, hidden inputs.
