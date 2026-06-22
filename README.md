![New1Direction](banner.svg)

**Self-taught engineer — AI agent infrastructure, Rust systems, and security.**

I build tooling that makes autonomous AI agents **verifiable, recoverable, and safe to run** — from a tamper-evident execution ledger, to ephemeral secret handling, to a coding agent that keeps its receipts.

## Flagship projects

- **[korg](https://github.com/New1Direction/korg)** — a causally-ordered, rewindable event-ledger for autonomous agents. Every step an agent takes is recorded in a hash-chained, tamper-evident ledger anyone can independently verify. Rust · zero-trust · no blockchain.
- **[ningen-shikkaku](https://github.com/New1Direction/ningen-shikkaku)** — burn-after-reading secrets for AI agents. Keys live in `mlock`'d, non-swappable RAM, are served over MCP, and are wiped after N reads or the instant your session dies. A hardened Rust daemon (seccomp allowlist, no core dumps, non-elidable memory wipe) shipped with a fully-documented threat model.
- **[korgex](https://github.com/New1Direction/korgex)** — a verifiable AI coding agent that works with any model and keeps a checkable record of every change it makes. Python · published on PyPI.

## Selected work

- **[thumper](https://github.com/New1Direction/thumper)** — the local execution and self-recovery substrate beneath korgex: runs code fast and repairs its own errors.
- **[webmcp-anything](https://github.com/New1Direction/webmcp-anything)** ([wmcp.sh](https://wmcp.sh)) — turn any website into agent-callable MCP tools with one line of config.
- **[RepoLens](https://github.com/New1Direction/RepoLens)** — click any repository and get a straight answer on whether to use it.
- **[coherence-auditor](https://github.com/New1Direction/coherence-auditor)** — detects an LLM contradicting its own stated probabilities and prices the inconsistency as a guaranteed-loss bet.
- **[pi-platform](https://github.com/New1Direction/pi-platform)** — a deterministic semantic execution kernel with a governance-first architecture.

<sub>Each project's full documentation lives in its README.</sub>

---

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/New1Direction/New1Direction/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/New1Direction/New1Direction/output/github-contribution-grid-snake.svg">
  <img alt="New1Direction contribution graph" src="https://raw.githubusercontent.com/New1Direction/New1Direction/output/github-contribution-grid-snake.svg">
</picture>
