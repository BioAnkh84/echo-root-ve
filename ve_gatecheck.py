# ve_gatecheck.py
import random, json

GATE_RULE = "PROCEED iff rho>=0.70 and gamma>=0.70 and delta<=0.30; ABORT if delta>0.40 or gamma<0.65; else PAUSE"

def gate(rho, gamma, delta):
    if rho >= 0.70 and gamma >= 0.70 and delta <= 0.30:
        return "PROCEED"
    elif delta > 0.40 or gamma < 0.65:
        return "ABORT"
    else:
        return "PAUSE"

def main(n=5, seed=None):
    if seed is not None:
        random.seed(seed)
    sample = [{
        "rho": round(random.uniform(0.5, 1.0), 2),
        "gamma": round(random.uniform(0.5, 1.0), 2),
        "delta": round(random.uniform(0.0, 0.5), 2)
    } for _ in range(n)]
    for s in sample:
        s["decision"] = gate(**s)
    print(json.dumps({
        "gate_rule": GATE_RULE,
        "n": n,
        "rows": sample
    }, indent=2))

if __name__ == "__main__":
    main()
