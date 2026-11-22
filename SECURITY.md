# CyberEye security review · Build 3

**Beginner lane. AI app with no database.** The Python service sends submitted text to OpenRouter. Screenshots are processed in the browser. CyberEye has no accounts, database, server-side uploads, or storage buckets. Database isolation, backup and bucket tests do not apply.

| Check | Evidence and status |
| --- | --- |
| Credentials | Reviewed current tracked text files including frontend assets and the SVG. The example environment file contained a recognizable placeholder. Removed its key-like prefix. No credential value was identified in this review. The live scan found none of the six assigned prefixes in the product page, app page, OCR loader, Tesseract bundle, or PostHog bootstrap. |
| Analysis limits | Previously every accepted request could reach OpenRouter. Now the server allows five analysis attempts per visitor over ten minutes and 24 total per process in the same window. Local handler test sends 30 requests with an empty JSON object: five validation errors followed by 25 HTTP 429 responses, with no provider calls. The [production test](https://github.com/building-with-ai-f26/sbp9868-project-slug/actions/runs/45075418946) sent the same 30 requests. Requests 1–5 returned 400, requests 6–30 returned 429, and the final response specified Retry-After 600 seconds. [Screenshot](docs/images/CyberEye-live-429.png). |
| Limiter scope | Single instance. Uses the peer address locally and the CDN visitor address on Render, with peer fallback. Verify identification on the deployed service. Shared networks can share a quota and restarts reset counters. |
| Input and output | Existing tests cover message length, instruction separation, malformed provider output and upstream errors. Browser code renders model text as text nodes. The app does not fetch links from submissions. |
| Analytics | Input masking was configured. Generated findings could repeat message content in replay. Blocked the findings panel and OCR status in replay and excluded them from autocapture. PostHog recorded OCR and analysis events and a replay for the synthetic production session. Visual inspection of masking is pending. |
| Dependencies | Python backend uses the standard library. Browser loads Tesseract.js 7.0.0 and PostHog externally. Added npm audit for the OCR package and dependency tree in Actions. Local registry lookup was blocked. [GitHub Actions run 45074286918](https://github.com/building-with-ai-f26/sbp9868-project-slug/actions/runs/45074286918) passed the OCR audit at the high-severity threshold, backend tests, and JavaScript syntax check. The externally served PostHog script is outside npm audit coverage. |
| Spending | Blueprint selects the free model router. Owner must confirm the actual monthly provider cap. |
| Production safeguards | AGENTS.md requires owner approval for destructive operations, credentials, permissions and spend. |

## Production verification

On November 22, 2026, the [Render app](https://cybereye-sbp9868.onrender.com) returned an AI assessment for a synthetic payment-verification message. In a 390 × 844 browser viewport, OCR extracted “MEET AT NOON” from a synthetic screenshot and the app returned a second assessment. Both displayed an inference cost of $0.000000. The test used browser phone emulation. A classmate’s physical-phone check, visual replay masking review, and confirmation of the provider’s monthly hard cap remain open.

The limiter test used empty JSON to exercise validation and throttling without using model credits. The linked screenshot is a browser capture of the live-test report generated from the recorded HTTP responses.
