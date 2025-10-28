# ve_handshake.py
import json, argparse, hashlib, time

p = argparse.ArgumentParser(description="PowerShell→Python JSON handshake test")
p.add_argument("--input", required=True, help="JSON string")
args = p.parse_args()

data = json.loads(args.input)
data["timestamp"] = time.time()
data["hash_self"] = hashlib.sha256(args.input.encode()).hexdigest()
print(json.dumps(data, indent=2, sort_keys=True))
