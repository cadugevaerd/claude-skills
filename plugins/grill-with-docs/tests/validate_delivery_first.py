#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

CORE=Path(__file__).resolve().parents[1]/"skills/grill-with-docs/scripts/grill_workspace.py"

def main():
    with tempfile.TemporaryDirectory(prefix="grill-delivery-") as d:
        root=Path(d)
        subprocess.run(["git","init","-q"],cwd=root,check=True)
        (root/".grill/work-items/h1").mkdir(parents=True)
        (root/".grill/work-items/h1/WORK-ITEM.json").write_text(json.dumps({"immutable":{"schema":"grill-work-item/v2","work_id":"h1","type":"hotfix","slug":"x"},"immutable_sha256":"bad","scope":{"paths":[]}}))
        r=subprocess.run([sys.executable,str(CORE),"hotfix-go",str(root),"--work-id","h1","--scope","src/api.py","--evidence","repro","--test-command","true","--rollback","revert"],text=True,capture_output=True)
        assert r.returncode==2 and "IMMUTABLE-TAMPERED" in r.stdout, r.stdout
    print("delivery-first deterministic checks: ok")
if __name__=="__main__": main()
