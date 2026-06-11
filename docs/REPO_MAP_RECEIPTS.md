# Repo Map Receipts

`repo_map.py` gives humans and AI the same compact orientation view before deeper search.

It is intentionally not a replacement for `rg`, tests, schema checks, or file inspection. It answers:

```text
What shape is this repo right now?
Which folders are source surfaces?
Which noisy folders were excluded?
What hash identifies this map?
```

## Command

```powershell
py -3.11 .\repo_map.py --depth 3
py -3.11 .\repo_map.py --depth 3 --json
```

To write a generated snapshot for later comparison:

```powershell
py -3.11 .\repo_map.py --depth 3 --write-snapshot .\receipts\repo_map_latest.json --json
```

To compare against a previous snapshot:

```powershell
py -3.11 .\repo_map.py --depth 3 --delta-from .\receipts\repo_map_latest.json
```

## Default Excludes

- `.git`
- `.venv`
- `__pycache__`
- `.ve_logs`
- `.ve_snapshots`
- `archive`
- `ve_data`

## Doctrine

Repo map means orientation, not proof.

```text
Map exists != files are healthy.
File present != file is fresh.
Folder empty != missing documentation.
Hash identifies the map, not the truth of every claim.
Delta identifies structure changes, not semantic content changes.
```

## Delta Receipt Boundary

`repo_map_delta` reports only:

- added paths
- removed paths
- file/folder kind changes
- size changes

It does not claim a same-size file is unchanged, and it does not claim that a size change is semantically meaningful. Use content hashes or file inspection when that stronger claim is needed.

Use the map first, then use targeted search and receipts:

```text
repo map
  -> targeted rg
  -> file inspection
  -> tests
  -> receipt/replay
```
