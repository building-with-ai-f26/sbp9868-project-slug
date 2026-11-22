# CyberEye security review · Build 3

**Beginner lane. AI app with no database.** The Python service sends submitted text to OpenRouter. Screenshots are processed in the browser. CyberEye has no accounts, database, server-side uploads, or storage buckets. Database isolation, backup and bucket tests do not apply.

| Check | Evidence and status |
| --- | --- |
| Credentials | Reviewed current tracked text files including frontend assets and the SVG. The example environment file contained a recognizable placeholder. Removed its key-like prefix. No credential value was identified in this review. Production asset inspection is pending. |
| Analysis limits | Previously every accepted request could reach OpenRouter. Now the server allows five analysis attempts per visitor over ten minutes and 24 total per process in the same window. Local handler test sends 30 requests with an empty JSON object: five validation errors followed by 25 HTTP 429 responses, with no provider calls. Live evidence is pending. |
| Limiter scope | Single instance. Uses the peer address locally and the CDN visitor address on Render, with peer fallback. Verify identification on the deployed service. Shared networks can share a quota and restarts reset counters. |
| Input and output | Existing tests cover message length, instruction separation, malformed provider output and upstream errors. Browser code renders model text as text nodes. The app does not fetch links from submissions. |
| Analytics | Input masking was configured. Generated findings could repeat message content in replay. Blocked the findings panel and OCR status in replay and excluded them from autocapture. Verify using synthetic data on the production hostname. |
| Dependencies | Python backend uses the standard library. Browser loads Tesseract.js 7.0.0 and PostHog externally. Added npm audit for the OCR package and dependency tree in Actions. Local registry lookup was blocked. [GitHub Actions run 45074286918](https://github.com/building-with-ai-f26/sbp9868-project-slug/actions/runs/45074286918) passed the OCR audit at the high-severity threshold, backend tests, and JavaScript syntax check. The externally served PostHog script is outside npm audit coverage. |
| Spending | Blueprint selects the free model router. Owner must confirm the actual monthly provider cap. |
| Production safeguards | AGENTS.md requires owner approval for destructive operations, credentials, permissions and spend. |

## Evidence still required
Record the deployed URL and revision, mobile paste and OCR results, provider budget verification, production asset scan, PostHog event and masked replay, and a screenshot of the live 429. Use synthetic data. No live verification has been recorded.
