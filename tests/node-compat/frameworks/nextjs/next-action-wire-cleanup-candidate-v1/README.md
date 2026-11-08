# Current captured action transport Source

This unexecuted Source fork binds the corrected cleanup native browser's actual POST 7 (`05cd3b4d…`, `/actionPosts/0`). Its exact 391-byte form is `cc609fbe…`, with action ID `4018730ebe8dc9bc100be933e21dabdfa132c639ab`. `request.json` retains the observed header map/body, including the captured multipart boundary. Nothing is regenerated from an action manifest or opaque Flight data.

The capture core and independent HTTP/gzip model are byte-identical to held `d2d38c28…`. The only wire-client code difference is its expected body SHA literal, from old `ad790726…` to this actual body. All raw-prefix-before-validation, HTTP framing/end, single gzip member/normal finish/CRC/ISIZE, bounded decoded output and cleanup ordering assertions remain unchanged. Flight bytes stay opaque; no React parser, browser, functional Next acceptance or cause claim is added.

The existing diagnostic explicitly supplies Host, Origin, Referer, Accept-Encoding:gzip, Connection:keep-alive and Content-Length:391; only the leased loopback origin/host/referer are substituted as before. The captured Playwright header map is not claimed to be a complete raw browser header block. Limits remain 20 seconds, 2 MiB wire, 2 MiB encoded body and 4 MiB decoded body; no retry or additional request is introduced.

The two new owners share this single physical client/core/model. Their original output prefixes are retained, with future fresh Root runIds. New owner Source-index binding is pending this family's ordered seal. All new action/result slots are NULL. No new Node/JavaScript parser, producer, API, HTTP or guest invocation has occurred, and no native code was compiled. Earlier transport passes and cache/browser failures remain unchanged.

B made these finite bindings; C authored the reviewed common/owner ancestors and independently peers the fork. Source checks are Python byte/JSON comparisons only. Root owns later protocol/grants/actions.
