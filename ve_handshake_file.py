import json, argparse, hashlib, time, sys
p = argparse.ArgumentParser()
p.add_argument("--file", required=True)
args = p.parse_args()
raw = open(args.file, "r", encoding="utf-8-sig").read()
print("RAW_PAYLOAD:", raw)
data = json.loads(raw)
data["timestamp"] = time.time()
data["hash_self"] = hashlib.sha256(raw.encode()).hexdigest()
print(json.dumps(data, indent=2, sort_keys=True))


