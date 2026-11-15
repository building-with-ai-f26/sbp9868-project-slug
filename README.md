# CyberEye

> **One-line pitch:** An AI-assisted message analyzer that helps people recognize phishing warning signs and verify suspicious requests before clicking.

- **Builder:** `@sbp9868`
- **Pod:** [Pod Name / Number]
- **Product Page & Living PRD:** https://building-with-ai-f26.github.io/sbp9868-project-slug/
- **App:** runs locally through Week 4; add a cloud URL in Build 5.

## Start here: Build 1

**Due Monday, November 9 at noon, New York time.** No class November 3; keep building that week.

1. Join the [class organization](https://github.com/building-with-ai-f26), then use this template to create a **public** repo named `<netid>-<project-slug>`. Ask Christian or Hew if the organization is missing from the owner list.
2. Set up Git and one coding agent during the week of October 27. Follow the [Icerynk setup guide](https://www.icerynk.com/c/fa26-tech-gb-2160-dm2-f2/content/pre-class-setup-github-openrouter-your-coding-agent).
3. Publish [`docs/index.html`](./docs/index.html): **Settings → Pages → Deploy from a branch → main → /docs → Save**. When deployment finishes, open `https://building-with-ai-f26.github.io/<your-repo-name>/`.
4. Fill in PRD v1: a reachable user, their painful before/after workflow, one core workflow, and three non-goals.
5. Build a rough local prototype. Add a screenshot or GIF and an honest Build 1 log to the Product Page, including progress, learning, problems, costs, and hours.
6. Push meaningful commits on **at least two separate days each week outside class**, including the November 3 break.
7. Submit your **Product Page URL and repository URL in Icerynk**. Come ready to demo the prototype in two minutes on November 10.

Create your PostHog account in Week 1. Install it on the Product Page and local app in **Build 2**, then verify events. The Product Page is public from Build 1; the app can stay local through Week 4.

## Repository map

| File / folder | Purpose |
| --- | --- |
| [`docs/index.html`](./docs/index.html) | Required public pitch, living PRD, and weekly build log. Update with actual work and evidence. |
| [`Intent.md`](./Intent.md), [`Plan.md`](./Plan.md), [`journal/`](./journal/) | Optional drafting aids. No duplicate submission is required. |
| [`AGENTS.md`](./AGENTS.md) | Local run commands, project context, and agent rules. Build 2 onward. |
| [`tests/`](./tests/) | Verification guidance. Build 4 offers Track A domain evals **or** Track B user replays. |
| [`SPONSOR_MEMO.md`](./SPONSOR_MEMO.md) | One-page recommendation backed by actual usage, full costs, and risks. Due December 14 at noon. |

[Icerynk](https://www.icerynk.com/c/fa26-tech-gb-2160-dm2-f2/content) holds the assignment instructions and submissions.

## Local setup (Build 2: AI backend)

Requires Python 3.9+ and an OpenRouter API key. No third-party Python packages are required.

1. Clone this repo or open your existing clone in Terminal.
2. Run `cp .env.example .env` in the project folder.
3. Open `.env` and replace the placeholder `OPENROUTER_API_KEY` with your real key. Never commit `.env`.
4. Run `python3 server.py`.
5. Open http://127.0.0.1:8000/prototype.html and click **Analyze message**.
6. Run tests: `python3 -m unittest discover -s tests -v`. GitHub Actions also checks them.

The GitHub Pages site is a static preview: live AI analysis works **only on localhost**. Keep the local Terminal running during pod testing. No suspicious links are opened.

The backend returns risk indicators, uncertainty, suggested independent verification and token/cost usage when supplied by OpenRouter. PostHog has been added to the Product Page and prototype for pageviews, button interaction events and replay, but actual event delivery must be verified by visiting the pages.

Never paste API keys, credentials, or private messages into repository files, screenshots, or analytics.
