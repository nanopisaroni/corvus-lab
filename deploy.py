#!/usr/bin/env python3
"""Deploy corvus-lab (static: index.html, dashboard.html, metrics.js, vercel.json) via REST API + curl."""
import json, os, subprocess, sys, time

PROJECT_NAME = "corvus-lab"
ALIAS = "corvus-lab.vercel.app"
ROOT = os.path.expanduser("~/projects/corvus-lab")
FILES = ["index.html", "dashboard.html", "metrics.js", "metrics_history.json", "vercel.json"]

def token():
    for line in open(os.path.expanduser("~/.hermes/.env")):
        if line.startswith("VERCEL_TOKEN="):
            return line.strip().split("=", 1)[1]
    return os.environ.get("VERCEL_TOKEN")

def curl(args):
    out = subprocess.run(["curl", "-s", "--max-time", "120"] + args,
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"raw": out[:300]}

def main():
    t = token()
    if not t:
        sys.exit("no VERCEL_TOKEN")

    # project exists -> GET id
    g = curl([f"https://api.vercel.com/v9/projects/{PROJECT_NAME}",
              "-H", f"Authorization: Bearer {t}"])
    pid = g.get("id")
    print("project:", pid)
    if not pid:
        sys.exit("project not found: " + json.dumps(g)[:200])

    files = []
    for f in FILES:
        with open(os.path.join(ROOT, f), "r", encoding="utf-8") as fh:
            files.append({"file": f, "data": fh.read()})
    body = {"name": PROJECT_NAME, "files": files,
            "projectSettings": {"framework": None}, "target": "production"}
    tmp = "/tmp/vercel_body_cl.json"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(body, fh)
    d = curl(["-X", "POST", "https://api.vercel.com/v13/deployments",
              "-H", f"Authorization: Bearer {t}", "-H", "Content-Type: application/json",
              "-d", "@" + tmp])
    dep = d.get("id")
    if not dep:
        print("deploy error:", d)
        sys.exit(1)
    print("deployment:", dep, d.get("url"))

    state = None
    for i in range(15):
        time.sleep(10)
        st = curl([f"https://api.vercel.com/v13/deployments/{dep}",
                   "-H", f"Authorization: Bearer {t}"])
        state = st.get("readyState")
        print(f"[{i}] {state}")
        if state == "READY":
            break
        if state == "ERROR":
            print("ERR:", st.get("errorMessage") or st.get("errorCode"))
            sys.exit(1)
    if state != "READY":
        sys.exit("deployment not ready")

    if ALIAS:
        a = curl(["-X", "POST", f"https://api.vercel.com/v2/deployments/{dep}/aliases",
                  "-H", f"Authorization: Bearer {t}", "-H", "Content-Type: application/json",
                  "-d", json.dumps({"alias": ALIAS})])
        print("alias:", a.get("alias") or a)

if __name__ == "__main__":
    main()
