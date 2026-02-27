# Progress

Hotfixes:
- 2026-02-26: Restored agent.critic.evaluate entrypoint and import stability.
- 2026-02-26: Query schema fix for OpenAI response_format.

Milestones (Playbooks):

- [x] P1: playbook engine
- [x] P2: research playbook
- [x] P3: data scraping playbook
- [x] P4: supplier playbook
- [x] P5: automation playbook

Milestones (Research v2):

- [x] R2-M1: query engine
- [x] R2-M2: multi-query search + diversity enforcement
- [x] R2-M3: credibility scoring
- [x] R2-M4: structured extraction v2
- [x] R2-M5: synthesis engine
- [x] R2-M6: coverage critic upgrade
- [x] R2-M7: report generator v2

Milestones (Research core integration):

- [x] R3-M1: research service layer
- [x] R3-M2: supplier playbook integration
- [x] R3-M3: data scraping integration
- [x] R3-M4: automation integration
- [x] R3-M5: intelligence cache
- [x] R3-M6: CLI commands
- [x] R3-M7: playbook decision upgrade

Milestones (R3.1 Stabilization):

- [x] R3.1-M1: google extraction engine
- [x] R3.1-M2: discover_sources rewrite
- [x] R3.1-M3: controller selector integration
- [x] R3.1-M4: verification tests

Milestones (R3.2 Google hardening):

- [x] R3.2-M1: google extraction hardening
- [x] R3.2-M2: failsafe discovery pipeline
- [x] R3.2-M3: ranking improvements
- [x] R3.2-M4: discovery benchmarks + CLI hook
- [x] R3.2-M5: docs updates

Milestones (UX release):

- [x] UX-M1: terminal presence banner + prompt + log categories
- [x] UX-M2: first run wizard
- [x] UX-M3: README human setup guide
- [x] UX-M4: smoke test + human testing doc
- [x] UX-M5: fix blockers found

Milestones (R3.3 Bugfix):

- [x] R3.3: OpenAI schema root fix + smoke test updates

Milestones (R3.4 Discovery reliability):

- [x] R3.4-M1: provider abstraction + DDG fallback
- [x] R3.4-M2: discover_sources provider chain + debug artifacts
- [x] R3.4-M3: ranking improvements
- [x] R3.4-M4: discovery benchmarks + CLI hook

Self-test fixes (2026-02-27):
- [x] Windows py313 deps: greenlet/playwright compatibility
- [x] Discovery fallback heuristics + provider hardening
- [x] Benchmark stability mode (fast discovery)
