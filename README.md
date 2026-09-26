<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/banner-dark.svg" />
  <img alt="IronMurphy — AI Agent / Full-stack Engineer" src="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/banner-light.svg" />
</picture>

<p align="center">
  <a href="https://github.com/sclfcz/commerceagent"><img alt="Featured: CommerceAgent" src="https://img.shields.io/badge/Featured-CommerceAgent-F97316?style=flat-square&logo=electron&logoColor=white" /></a>
  <a href="https://github.com/sclfcz/health-miniprogram"><img alt="Featured: 康养日记" src="https://img.shields.io/badge/Featured-%E5%BA%B7%E5%85%BB%E6%97%A5%E8%AE%B0%20%C2%B7%20WeChat%20Mini%20Program-07C160?style=flat-square&logo=wechat&logoColor=white" /></a>
  <a href="#open-source-contributions"><img alt="Upstream merged PRs" src="https://img.shields.io/badge/Upstream%20merged%20PRs-11-8250DF?style=flat-square&logo=git&logoColor=white" /></a>
</p>

- Building [CommerceAgent](https://github.com/sclfcz/commerceagent), a self-hosted Claude Code workbench reachable from the browser and seven messaging channels.
- Building [康养日记](https://github.com/sclfcz/health-miniprogram), a WeChat Mini Program that keeps elderly patients on their medication schedule and tells their family when they fall off it.
- Exploring agent systems, MCP apps, developer tooling, and self-hosted software. Open to thoughtful collaboration on useful open-source projects.

## Built by me

Projects I started and maintain myself — the work I would want you to read first.

### 🛒 [`CommerceAgent`](https://github.com/sclfcz/commerceagent) · 面向电商场景的智能运营工作台

> A self-hosted, multi-user, agent-first Claude Code workbench: one agent, workspace, and automation set, reachable from the browser and seven messaging channels.

<img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat-square&logo=typescript&logoColor=white" /> <img alt="Electron" src="https://img.shields.io/badge/Electron-desktop-47848F?style=flat-square&logo=electron&logoColor=white" /> <img alt="License" src="https://img.shields.io/badge/License-MIT-0F766E?style=flat-square" />

- Wraps the Claude Agent SDK for TypeScript into a long-running service shared across Feishu, Telegram, QQ, DingTalk, WeChat, Discord, and WhatsApp.
- Tasks execute on the host or inside Docker sandboxes, with an explicit ACL matrix and CI on every push.
- Desktop builds bundle the backend, the web UI, and a Node runtime into a single Electron app, so installing it needs neither Node nor a database.

### 🏥 康养日记 · [`health-miniprogram`](https://github.com/sclfcz/health-miniprogram)

> Medication care for elderly patients and their families: scheduled reminders, automatic missed-dose records, and a family alert after three missed doses in a row.

<img alt="WeChat Mini Program" src="https://img.shields.io/badge/WeChat%20Mini%20Program-07C160?style=flat-square&logo=wechat&logoColor=white" /> <img alt="CloudBase" src="https://img.shields.io/badge/CloudBase-006EFF?style=flat-square&logo=tencentcloud&logoColor=white" /> <img alt="tests" src="https://img.shields.io/badge/regression%20tests-no%20dependencies-339933?style=flat-square&logo=nodedotjs&logoColor=white" />

- Two scheduled cloud functions carry the whole reminder pipeline — a 5-minute reminder pass and a 10-minute missed-dose pass — each idempotent through its own log collection, so a retry never double-notifies a family.
- The "three missed doses in a row" streak is computed over a **total order** (business time → `create_time` → `_id`), so the verdict cannot flip with the database's return order.
- Timezone-safe by construction: the cloud runs on UTC and the client derives "today" in Asia/Shanghai, so the task list and the reminders cannot disagree by a day.
- Every query is owner-scoped and paged past the platform caps (100 documents per cloud query, 20 per client query); the naive version quietly read other patients' plans and truncated at 100 records.
- Ships a dependency-free suite: `node tests/regression.test.js` runs 11 invariants across three timezones, and each one goes red if the corresponding fix is reverted.

## Open-source contributions

Projects with 1,000+ stars that have merged my pull requests upstream, refreshed automatically. Individual pull requests are not listed here.

<!-- merged-prs:start -->
<p align="center">
  <img src="https://img.shields.io/badge/Merged%20PRs-11-8250DF?style=for-the-badge&logo=git&logoColor=white" alt="11 merged prs" />
  <img src="https://img.shields.io/badge/Projects-5-0969DA?style=for-the-badge&logo=box&logoColor=white" alt="5 projects" />
  <img src="https://img.shields.io/badge/Upstream%20stars-194.1k-BF8700?style=for-the-badge&logo=github&logoColor=white" alt="194.1k upstream stars" />
</p>

| Project | ★ | Merged |
| :-- | --: | --: |
| [`bytedance/deer-flow`](https://github.com/bytedance/deer-flow) | 83.0k | 1 |
| [`crewAIInc/crewAI`](https://github.com/crewAIInc/crewAI) | 59.1k | 1 |
| [`agno-agi/agno`](https://github.com/agno-agi/agno) | 42.4k | 1 |
| [`TencentCloud/Octop`](https://github.com/TencentCloud/Octop) | 5.1k | 7 |
| [`VRSEN/agency-swarm`](https://github.com/VRSEN/agency-swarm) | 4.6k | 1 |

<sub>Merges only, counted per project above the 1,000-star floor. Checked automatically by [.github/workflows/refresh.yml](.github/workflows/refresh.yml); last change 2026-09-26 18:02 UTC.</sub>
<!-- merged-prs:end -->

## Tech

<p align="center">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" />
  <img alt="Electron" src="https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white" />
  <img alt="MCP" src="https://img.shields.io/badge/MCP-6E56CF?style=flat-square" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" />
  <img alt="WeChat Mini Program" src="https://img.shields.io/badge/Mini%20Program-07C160?style=flat-square&logo=wechat&logoColor=white" />
</p>

## Contributions

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/output/snake-dark.svg" />
    <img alt="my contribution graph, eaten by a snake" src="https://raw.githubusercontent.com/sclfcz/sclfcz/output/snake-light.svg" />
  </picture>
</p>

<sub>🐍 Generated daily from my contribution graph by [.github/workflows/snake.yml](.github/workflows/snake.yml).</sub>

---

If one of my projects is useful to you, a star or issue is always appreciated.
