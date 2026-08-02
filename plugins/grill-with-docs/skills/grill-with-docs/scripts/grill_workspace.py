#!/usr/bin/env python3
"""Core v2 work-item lifecycle. One JSON document is emitted per invocation."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, uuid
from pathlib import Path
TYPES={"feature","fix","hotfix"}; ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,100}$"); SLUG=re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
ASSET=Path(__file__).resolve().parents[1]/"assets"
FILES=("WORK-ITEM.json","CONTEXT.md","DECISION-BACKLOG.md","DECISION-FRONTIER.md","ROADMAP.md","ROUND-LOG.jsonl","state.json","PLAN-CONTEXT.md","CONSTITUTION-CHECK.md","AUDIT.md")
def emit(obj, code=0): print(json.dumps(obj,ensure_ascii=False,sort_keys=True)); return code
def git(r,*args):
 p=subprocess.run(["git","-C",str(r),*args],text=True,capture_output=True); return p.stdout.strip() if p.returncode==0 else ""
def project(p):
 p=Path(p)
 if not p.is_dir() or p.is_symlink(): raise ValueError("ROOT inválido")
 top=git(p,"rev-parse","--show-toplevel")
 if not top or Path(top).resolve()!=p.resolve(): raise ValueError("ROOT deve ser git root")
 return p.resolve()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_read(p): return p.read_bytes().decode("utf-8")
def atomic_bytes(p,b):
 p.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=".grill-tmp-",dir=p.parent); os.fchmod(fd,0o600)
 try:
  os.write(fd,b); os.fsync(fd); os.close(fd); os.replace(tmp,p)
 except Exception:
  try: os.close(fd)
  except OSError: pass
  try: os.unlink(tmp)
  except OSError: pass
  raise
def base_ref(r, requested):
 head=git(r,"rev-parse","HEAD")
 if requested:
  c=git(r,"rev-parse",requested)
  if not c: raise ValueError("base-ref inválida")
  return requested,c
 upstream=git(r,"rev-parse","--verify","@{upstream}")
 if upstream:
  mb=git(r,"merge-base","HEAD",upstream)
  if mb:return "merge-base("+upstream+")",mb
 return ("HEAD" if head else "UNBORN"),(head or "UNBORN")
def constitution_meta(r):
 p=r/".specify/memory/constitution.md"
 if not p.exists(): return {"state":"not-present","path":None,"sha256":None}
 try: b=p.read_bytes(); b.decode("utf-8")
 except (UnicodeError,OSError): raise ValueError("constitution ilegível")
 if not b.strip() or any(x in b.decode() for x in ("{{","[PLACEHOLDER]","YYYY-MM-DD")): raise ValueError("constitution inválida")
 return {"state":"present","path":".specify/memory/constitution.md","sha256":hashlib.sha256(b).hexdigest()}
def metadata(r,a,wid):
 head=git(r,"rev-parse","HEAD") or "UNBORN"; bref,bcommit=base_ref(r,a.base_ref)
 wf=r/"WORKFLOW.md"; wh=digest(wf) if wf.is_file() else None
 return {"schema":"grill-work-item/v2","work_id":wid,"type":a.type,"slug":a.slug,"branch":git(r,"branch","--show-current"),"HEAD":head,"base-ref":bref,"base-commit":bcommit,"constitution":constitution_meta(r),"workflow":{"path":"WORKFLOW.md","sha256":wh}}
def templates():
 vals={}
 for n in FILES:
  if n == "WORK-ITEM.json": src=ASSET/"WORK-ITEM.template.json"
  elif n == "state.json": src=ASSET/"state.template.json"
  else:
   stem,suffix=n.rsplit('.',1); src=ASSET/(stem+".template."+suffix)
  if src.is_file(): vals[n]=src.read_bytes()
 vals.setdefault("WORK-ITEM.json",b"{}\n"); vals.setdefault("state.json",b'{"status":"in-progress"}\n'); vals.setdefault("ROUND-LOG.jsonl",b"")
 for n in FILES: vals.setdefault(n,("# "+n.rsplit(".",1)[0]+"\n").encode())
 return vals
def acquire(lock):
 lock.parent.mkdir(parents=True,exist_ok=True)
 while True:
  try: os.mkdir(lock); return
  except FileExistsError:
   time.sleep(.02)
   if not lock.exists(): continue
   # stale lock is only removable when owner metadata is demonstrably dead
   try:
    owner=json.loads((lock/"owner").read_text()); os.kill(int(owner["pid"]),0)
   except ProcessLookupError: shutil.rmtree(lock,ignore_errors=True)
   except (OSError,ValueError,KeyError,json.JSONDecodeError): pass
def init(a):
 r=project(a.root)
 if a.type not in TYPES or not SLUG.fullmatch(a.slug): raise ValueError("type/slug inválido")
 wid=a.work_id or f"{a.type}-{a.slug}-{uuid.uuid4().hex}"
 if not ID.fullmatch(wid): raise ValueError("work-id inválido")
 parent=r/".grill/work-items"; d=parent/wid; lock=parent/("."+wid+".lock"); acquire(lock)
 try:
  meta=metadata(r,a,wid)
  if d.exists():
   if d.is_symlink() or not (d/"WORK-ITEM.json").is_file(): return emit({"verdict":"BLOCKED","code":"INTEGRITY-DIVERGENCE","work_id":wid},2)
   old=json.loads(safe_read(d/"WORK-ITEM.json"))
   immutable=("work_id","type","slug","branch","HEAD","base-ref","base-commit","constitution","workflow")
   if any(old.get(k)!=meta.get(k) for k in immutable): return emit({"verdict":"BLOCKED","code":"IDENTITY-DIVERGENCE","work_id":wid},2)
   return emit({"status":"REUSED","work_id":wid,"path":str(d),"integrity":digest(d/"WORK-ITEM.json")})
  staging=Path(tempfile.mkdtemp(prefix="."+wid+".",dir=parent))
  try:
   meta["created_at_epoch"]=int(time.time()); atomic_bytes(staging/"WORK-ITEM.json",(json.dumps(meta,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode())
   for n,b in templates().items():
    if n!="WORK-ITEM.json": atomic_bytes(staging/n,b.replace(b"{{WORK_ID}}",wid.encode()))
   (staging/"docs/adr").mkdir(parents=True); (staging/"handoffs").mkdir()
   os.rename(staging,d)
  except Exception: shutil.rmtree(staging,ignore_errors=True); raise
  return emit({"status":"CREATED","work_id":wid,"path":str(d),"integrity":digest(d/"WORK-ITEM.json")})
 finally: shutil.rmtree(lock,ignore_errors=True)
def audit(a):
 r=project(a.root); d=Path(a.artifact_root) if a.artifact_root else r/".grill/work-items"/a.work_id
 if not d.is_dir(): return emit({"verdict":"NO-GO","code":"WORK-ITEM-MISSING"},1)
 missing=[n for n in FILES if not (d/n).is_file()]; findings=[]
 try: meta=json.loads(safe_read(d/"WORK-ITEM.json")); safe_read(d/"CONTEXT.md")
 except Exception: return emit({"verdict":"NO-GO","code":"INVALID-WORK-ITEM"},1)
 if missing: findings.extend(["MISSING:"+x for x in missing])
 try:
  cm=constitution_meta(r)
  if cm["state"]=="present" and meta.get("constitution",{}).get("sha256")!=cm["sha256"]: findings.append("CONSTITUTION-HASH-STALE")
 except ValueError as e: return emit({"verdict":"BLOCKED-CONSTITUTION","code":"CONSTITUTION-INVALID","error":str(e)},3)
 # Delegate the governance contract auditor; it is read-only and its result is authoritative.
 auditor=Path(__file__).with_name("audit_decisions.py")
 target=d if a.artifact_root else r
 p=subprocess.run([sys.executable,str(auditor),str(target),"--project-root",str(r)],text=True,capture_output=True)
 try: receipt=json.loads(p.stdout.splitlines()[-1])
 except Exception: receipt={"verdict":"NO-GO","code":"AUDITOR-INVALID-OUTPUT"}
 if receipt.get("verdict") in {"NO-GO","BLOCKED"}: findings.append("AUDIT-DECISIONS:"+str(receipt.get("code",receipt.get("verdict"))))
 if findings:return emit({"verdict":"NO-GO","code":"ARTIFACT-INVALID","findings":sorted(findings),"work_id":meta.get("work_id")},1)
 return emit({"verdict":"GO","code":"OK","work_id":meta.get("work_id"),"audit":receipt},0)
def reconcile(a):
 r=project(a.root); roots=[r]+[project(x) for x in a.source_root]; items=[]
 for sr in roots:
  d=sr/".grill/work-items"
  if d.is_dir():
   for x in sorted(d.iterdir()):
    if x.is_dir() and (x/"WORK-ITEM.json").is_file(): items.append((sr,x,json.loads(safe_read(x/"WORK-ITEM.json"))))
 ids={}; conflicts=[]
 for sr,d,m in items:
  wid=m.get("work_id"); fp=digest(d/"WORK-ITEM.json")
  if wid in ids and ids[wid][1]!=fp: conflicts.append(wid)
  ids[wid]=(d,fp,m)
 result={"verdict":"PREVIEW","code":"CONFLICTS" if conflicts else "OK","qualified_ids":sorted(ids),"conflicts":sorted(set(conflicts)),"count":len(ids)}
 if a.apply:
  if git(r,"branch","--show-current")!=a.integration_branch or git(r,"status","--porcelain"): return emit({**result,"verdict":"BLOCKED","code":"APPLY_REQUIRES_CLEAN_INTEGRATION_BRANCH"},2)
  if conflicts:return emit({**result,"verdict":"NO-GO"},1)
  g=r/".grill/global"; body="# Global ROADMAP\n\n"+"".join(f"- {w} ({m['type']}): {m['slug']}\n" for w,(d,f,m) in sorted(ids.items()))
  atomic_bytes(g/"ROADMAP.md",body.encode()); atomic_bytes(g/"AUDIT.md",(json.dumps(result,sort_keys=True)+"\n").encode()); result["verdict"]="APPLIED"
 return emit(result,0 if result["verdict"] in {"PREVIEW","APPLIED"} else 1)
def migrate(a):
 r=project(a.root); names=("CONTEXT.md","DECISION-BACKLOG.md","DECISION-FRONTIER.md","ROADMAP.md","ROUND-LOG.jsonl","state.json","PLAN-CONTEXT.md","AUDIT.md")
 paths=[r/n for n in names if (r/n).exists()]; blobs={}
 try:
  for p in paths: blobs[p.name]=p.read_bytes(); p.read_bytes().decode("utf-8")
 except (UnicodeError,OSError) as e:return emit({"verdict":"NO-GO","code":"LEGACY-INVALID","error":str(e)},1)
 result={"verdict":"PREVIEW","code":"OK","legacy":sorted(blobs),"hashes":{n:hashlib.sha256(b).hexdigest() for n,b in blobs.items()}}
 if a.apply:
  wid=a.work_id or f"{a.type}-{a.slug}-migration"; d=r/".grill/work-items"/wid
  if d.exists(): return emit({**result,"verdict":"BLOCKED","code":"TARGET-EXISTS"},2)
  init(a); d=r/".grill/work-items"/wid
  try:
   for n,b in blobs.items(): atomic_bytes(d/n,b)
  except Exception: shutil.rmtree(d,ignore_errors=True); raise
  result.update(verdict="APPLIED",work_id=wid)
 return emit(result)
def main():
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
 i=s.add_parser("init"); i.add_argument("root"); i.add_argument("--type",required=True); i.add_argument("--slug",required=True); i.add_argument("--work-id"); i.add_argument("--base-ref")
 q=s.add_parser("audit"); q.add_argument("root"); q.add_argument("--work-id"); q.add_argument("--artifact-root"); q.add_argument("--project-root")
 c=s.add_parser("reconcile"); c.add_argument("root"); c.add_argument("--source-root",action="append",default=[]); c.add_argument("--source-ref",action="append",default=[]); c.add_argument("--apply",action="store_true"); c.add_argument("--integration-branch")
 m=s.add_parser("migrate"); m.add_argument("root"); m.add_argument("--type",required=True); m.add_argument("--slug",required=True); m.add_argument("--work-id"); m.add_argument("--apply",action="store_true")
 a=p.parse_args()
 try:return {"init":init,"audit":audit,"reconcile":reconcile,"migrate":migrate}[a.cmd](a)
 except (ValueError,OSError,UnicodeError,json.JSONDecodeError) as e:return emit({"verdict":"BLOCKED","code":"INVALID-INPUT","error":str(e)},2)
if __name__=="__main__":sys.exit(main())
