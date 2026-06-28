# License Readiness Checklist

Target: v0.1.0 License-ready MVP

- [x] Product definition: runtime governance layer for agentic AI.
- [x] Installable local demo with no external dependency required.
- [x] Test suite command documented.
- [x] Sample receipts available through demo command.
- [x] Architecture docs created.
- [x] Security policy present.
- [x] Commercial license placeholder created.
- [x] Known limitations documented.
- [x] Minimal release manifest created.
- [x] Public release safety scan documented.
- [x] CI PR check includes tests and receipt demo verify/replay.
- [x] Repo-map receipt added for shared human/AI orientation.
- [x] Repo-map delta receipt added for structure-change orientation.
- [x] Bounded self-proposal mechanics documented, tested, and receipt-backed.
- [x] Autonomy charter documents explicit cannot-do boundaries.
- [x] Scheduled health check path documented as evidence-only automation.
- [x] Spatial governance adapter documented as envelope review only, not robotics control.
- [x] External AI authority boundary documented as advisory evidence by default.
- [x] VSA Tuning Round 1 checklist keeps baseline deviation separate from emotion, diagnosis, identity, or authority claims.
- [x] Versioned release tag instructions listed below.
- [ ] Final public/commercial license model reviewed.
- [ ] Support/SLA placeholder converted to actual commercial terms.
- [ ] External legal/compliance language reviewed before licensing outreach.
- [ ] Older archive and local-integration files reviewed before broad public source publication.

## Release Tag Instructions

```powershell
git status
py -3.11 -m unittest discover -s Tests
git tag -a v0.1.0 -m "Echo-Root-VE v0.1.0 license-ready MVP"
git push origin v0.1.0
```

Only tag after tests pass and the release owner approves the final license language.
