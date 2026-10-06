<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/hero-dark-still.svg" />
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/hero-light-still.svg" />
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/hero-dark.svg" />
  <img alt="IronMurphy, AI agent and full-stack engineer. An edge dislocation glides through a crystal lattice one atom row at a time: small steps every day." src="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/hero-light.svg" />
</picture>

<p align="center">
  <a href="https://github.com/sclfcz/commerceagent"><img alt="Featured: CommerceAgent" src="https://img.shields.io/badge/Featured-CommerceAgent-C8783E?style=flat-square&logo=electron&logoColor=white" /></a>
  <a href="https://github.com/sclfcz/health-miniprogram"><img alt="Featured: 康养日记" src="https://img.shields.io/badge/Featured-%E5%BA%B7%E5%85%BB%E6%97%A5%E8%AE%B0%20%C2%B7%20WeChat%20Mini%20Program-07C160?style=flat-square&logo=wechat&logoColor=white" /></a>
  <!-- header-stats:start --><a href="#open-source-contributions"><img alt="Upstream merged PRs: 15" src="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/header-merged.svg" /></a><!-- header-stats:end -->
</p>

I studied materials, where metals don't break all at once: they give way one row of atoms at a time. I build software the same way, in small verified steps.

- Building [CommerceAgent](https://github.com/sclfcz/commerceagent), a self-hosted Claude Code workbench reachable from the browser and seven messaging channels.
- Building [康养日记](https://github.com/sclfcz/health-miniprogram), a WeChat Mini Program that keeps elderly patients on their medication schedule and tells their family when they fall off it.
- Exploring agent systems, MCP apps, developer tooling, and self-hosted software. Open to thoughtful collaboration on useful open-source projects.

## Built by me

Projects I started and maintain myself, the work I would want you to read first.

### [CommerceAgent](https://github.com/sclfcz/commerceagent), 面向电商场景的智能运营工作台

<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/commerceagent-dark-still.svg" />
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/commerceagent-light-still.svg" />
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/commerceagent-dark.svg" />
  <img alt="Messages from the browser, Feishu, Telegram, QQ, DingTalk, WeChat, Discord and WhatsApp all reach one CommerceAgent, which runs each task on the host or in a Docker sandbox." src="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/commerceagent-light.svg" />
</picture>

A self-hosted, multi-user, agent-first Claude Code workbench: one agent, workspace, and automation set, reachable from the browser and seven messaging channels.

- Wraps the Claude Agent SDK for TypeScript into a long-running service shared across Feishu, Telegram, QQ, DingTalk, WeChat, Discord, and WhatsApp.
- Tasks execute on the host or inside Docker sandboxes, with an explicit ACL matrix and CI on every push.
- Desktop builds bundle the backend, the web UI, and a Node runtime into a single Electron app, so installing it needs neither Node nor a database.

<img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat-square&logo=typescript&logoColor=white" /> <img alt="Electron" src="https://img.shields.io/badge/Electron-desktop-47848F?style=flat-square&logo=electron&logoColor=white" /> <img alt="License" src="https://img.shields.io/badge/License-MIT-0F766E?style=flat-square" />

### [康养日记](https://github.com/sclfcz/health-miniprogram), medication care for elderly patients

<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/health-dark-still.svg" />
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/health-light-still.svg" />
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/health-dark.svg" />
  <img alt="Nine scheduled doses over three days. Missed doses are recorded automatically, and the third miss in a row notifies the family." src="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/health-light.svg" />
</picture>

Scheduled reminders, automatic missed-dose records, and a family alert after three missed doses in a row.

- Two scheduled cloud functions carry the whole reminder pipeline, a 5-minute reminder pass and a 10-minute missed-dose pass. Each is idempotent through its own log collection, so a retry never double-notifies a family.
- The "three missed doses in a row" streak is computed over a **total order** (business time, then `create_time`, then `_id`), so the verdict cannot flip with the database's return order.
- Timezone-safe by construction: the cloud runs on UTC and the client derives "today" in Asia/Shanghai, so the task list and the reminders cannot disagree by a day.
- Every query is owner-scoped and paged past the platform caps (100 documents per cloud query, 20 per client query); the naive version quietly read other patients' plans and truncated at 100 records.
- Ships a dependency-free suite: `node tests/regression.test.js` runs 11 invariants across three timezones, and each one goes red if the corresponding fix is reverted.

<img alt="WeChat Mini Program" src="https://img.shields.io/badge/WeChat%20Mini%20Program-07C160?style=flat-square&logo=wechat&logoColor=white" /> <img alt="CloudBase" src="https://img.shields.io/badge/CloudBase-006EFF?style=flat-square&logo=tencentcloud&logoColor=white" /> <img alt="tests" src="https://img.shields.io/badge/regression%20tests-no%20dependencies-339933?style=flat-square&logo=nodedotjs&logoColor=white" />

## Open-source contributions

Projects with 1,000+ stars that have merged my pull requests upstream, refreshed automatically. Individual pull requests are not listed here.

<!-- merged-prs:start -->
<p align="center">
  <img src="https://raw.githubusercontent.com/sclfcz/sclfcz/main/assets/stats.svg" alt="15 merged PRs in 7 projects, 251.7k upstream stars" />
</p>

| Project | ★ | Merged |
| :-- | --: | --: |
| [`bytedance/deer-flow`](https://github.com/bytedance/deer-flow) | 83.4k | 3 |
| [`crewAIInc/crewAI`](https://github.com/crewAIInc/crewAI) | 59.4k | 1 |
| [`agno-agi/agno`](https://github.com/agno-agi/agno) | 42.6k | 1 |
| [`PrefectHQ/fastmcp`](https://github.com/PrefectHQ/fastmcp) | 28.0k | 1 |
| [`deepset-ai/haystack`](https://github.com/deepset-ai/haystack) | 26.7k | 1 |
| [`TencentCloud/Octop`](https://github.com/TencentCloud/Octop) | 7.1k | 7 |
| [`VRSEN/agency-swarm`](https://github.com/VRSEN/agency-swarm) | 4.6k | 1 |

<sub>Plus 1 more merge below the 1,000-star floor: `llm-d/llm-d-inference-sim`.</sub>

<sub>Merges only, counted per project above the 1,000-star floor. Checked automatically by [.github/workflows/refresh.yml](.github/workflows/refresh.yml); last change 2026-10-06 09:23 UTC.</sub>
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
    <img alt="My contribution graph, eaten by a snake" src="https://raw.githubusercontent.com/sclfcz/sclfcz/output/snake-light.svg" />
  </picture>
</p>

<sub>Generated daily from my contribution graph by [.github/workflows/snake.yml](.github/workflows/snake.yml). Artwork above is built by [design/build.py](design/build.py).</sub>

---

If one of my projects is useful to you, a star or issue is always appreciated.
