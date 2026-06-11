# Public Release Safety Scan

Scan date: 2026-06-11

## Scope

This scan reviewed the Echo-Root-VE working tree for release-risk indicators before a v0.1.0 licensing packet.

Patterns checked included:

- API key / secret / token language
- private-key markers
- local absolute paths
- private habitat references
- personal names and pairing IDs
- Tailscale-style private network IPs
- compliance/certification overclaim language

## Findings

No live secret value was identified in the v0.1 receipt package.

Items requiring release-boundary handling:

- Older scripts contain local absolute paths such as `E:\...`.
- Optional/local integration scripts reference private Cipher habitat paths.
- `archive/` contains stale historical material, local paths, provider-routing examples, and test-only key names.
- Generated `ve_data/` records include demo pairing IDs and should not be treated as clean source artifacts.
- Some docs use "medical-grade-inspired" language. Current docs also state this is not FDA compliant, not certified, and not guaranteed.

## Actions Taken

- Added `RELEASE_MANIFEST.md` to define the minimal licensing packet.
- Added generated receipt ledgers to `.gitignore`.
- Updated reviewer demo docs to avoid machine-specific checkout paths.
- Extended `.github/ve_checks.py` to run unit tests and v0.1 receipt demo verify/replay.
- Documented release-boundary risks in `REPO_AUDIT.md`.

## Recommendation

Use the minimal packet in `RELEASE_MANIFEST.md` for licensing review. Do not publish the entire dirty working tree as a clean release until archived/historical files and local-integration scripts are separately reviewed.
