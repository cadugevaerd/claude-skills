#!/usr/bin/env python3
"""Workspace v2 core: deterministic, read-only previews and atomic writes."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, uuid
from pathlib import Path
TYPES={"feature","fix","hotfix"}; ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,100}$"); SLUG=re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
BASE=Path(__file__).resolve().parents[1]/"assets"
FILES=("WORK-ITEM.json","CONTEXT.md","DECISION-BACKLOG.md","DECISION-FRONTIER.md","ROADMAP.md","ROUND-LOG.jsonl","state.json","PLAN-CONTEXT.md","CONSTITUTION-CHECK.md","AUDIT.md")
LEGACY=FILES[1:]
def emit(x,code=0): print(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))); return code
def git(r,*args,input=None):
 p=subprocess.run(["git","-C",str(r),*args],text=True,capture_output=True,input=input); return p.stdout.strip() if p.returncode==0 else ""
def sha(b): return hashlib.sha256(b).hexdigest()
def root(x):
 p=Path(x).resolve()
 if not p.is_dir() or p.is_symlink() or Path(git(p,"rev-parse","--show-toplevel")).resolve()!=p: raise ValueError("root inválido")
 return p
def read(p):
 if p.is_symlink(): raise ValueError("symlink rejeitado")
 b=p.read_bytes(); b.decode("utf-8"); return b
def atomic(p,b):
 if p.exists() and p.is_symlink(): raise ValueError("symlink target rejeitado")
 p.parent.mkdir(parents=True,exist_ok=True); fd,t=tempfile.mkstemp(prefix=".grill-tmp-",dir=p.parent); ok=False
 try:
  with os.fdopen(fd,"wb") as f: f.write(b); f.flush(); os.fsync(f.fileno())
  os.replace(t,p); ok=True
 finally:
  if not ok: shutil.rmtree(t,ignore_errors=True)
def constitution(r):
 p=r/".specify/memory/constitution.md"
 if not p.exists(): return {"state":"not-present","path":None,"sha256":None}
 b=read(p); text=b.decode();
 if not text.strip() or "{{" in text or "[PLACEHOLDER]" in text: raise ValueError("constitution inválida")
 return {"state":"present","path":".specify/memory/constitution.md","sha256":sha(b)}
def headings(text):
 out=[]
 for line in text.splitlines():
  m=re.match(r"^(##|###)\s+(.+?)\s*$",line)
  if m and m.group(2).strip() not in {"Overview","Visão geral","Contents","Índice"}: out.append((m.group(2),re.sub(r"[^a-z0-9]+","-",m.group(2).lower()).strip("-")))
 return out
def check_const(r,d):
 c=r/".specify/memory/constitution.md"
 if not c.exists(): return None
 cb=read(c); expected=headings(cb.decode()); p=d/"CONSTITUTION-CHECK.md"
 if not p.is_file(): raise RuntimeError("CONSTITUTION-CHECK ausente")
 raw=read(p).decode(); m=re.search(r"```json\s*\n(.*?)\n```",raw,re.S|re.I)
 if not m: raise RuntimeError("formato managed fenced JSON inválido")
 try: data=json.loads(m.group(1))
 except Exception as e: raise RuntimeError("JSON inválido") from e
 if data.get("constitution_sha256")!=sha(cb): raise RuntimeError("constitution hash stale")
 clauses=data.get("clauses")
 if not isinstance(clauses,list) or len(clauses)!=len(expected): raise RuntimeError("cobertura inválida")
 ids=[x.get("id") for x in clauses if isinstance(x,dict)]
 wanted=[f"CLAUSE-{n+1:04d}-{slug.upper()}" for n,(_,slug) in enumerate(expected)]
 if ids!=wanted or len(set(ids))!=len(ids): raise RuntimeError("cláusulas ausentes/duplicadas")
 for x in clauses:
  if x.get("status") not in {"PASS","NOT-APPLICABLE"} or not str(x.get("evidence","")).strip() or not str(x.get("justification","")).strip(): raise RuntimeError("clause inválida")
 return {"state":"present","sha256":sha(cb),"clauses":len(clauses)}
def tmpl(n,wid):
 q=BASE/(n.replace(".",".template.",1) if n not in {"WORK-ITEM.json","state.json"} else n.replace(".json",".template.json"))
 b=q.read_bytes() if q.is_file() else (b"" if n.endswith("jsonl") else (b"{}\n" if n.endswith("json") else ("# "+n+"\n").encode()))
 return b.replace(b"{{WORK_ID}}",wid.encode())
def identity(r,a,wid):
 head=git(r,"rev-parse","HEAD") or "UNBORN"; ref=a.base_ref or "HEAD"; commit=git(r,"rev-parse",ref)
 if not commit: commit="UNBORN"
 wf=r/"WORKFLOW.md"; return {"schema":"grill-work-item/v2","work_id":wid,"type":a.type,"slug":a.slug,"branch":git(r,"branch","--show-current"),"HEAD":head,"base-ref":ref,"base-commit":commit,"constitution":constitution(r),"workflow":{"path":"WORKFLOW.md","sha256":sha(read(wf)) if wf.is_file() else None},"scope":{"paths":[],"depends-on-work":[],"conflicts-with-adrs":[]}}
def init(a):
 r=root(a.root)
 if a.type not in TYPES or not SLUG.fullmatch(a.slug): raise ValueError("type/slug inválido")
 wid=a.work_id or f"{a.type}-{a.slug}-{uuid.uuid4().hex}"
 if not ID.fullmatch(wid): raise ValueError("work-id inválido")
 par=r/".grill/work-items"; par.mkdir(parents=True,exist_ok=True); d=par/wid; lock=par/("."+wid+".lock")
 try: os.mkdir(lock)
 except FileExistsError: return emit({"verdict":"BLOCKED","code":"LOCK-CONTENTION","work_id":wid},2)
 try:
  m=identity(r,a,wid); imm={k:m[k] for k in ("schema","work_id","type","slug","branch","HEAD","base-ref","base-commit","constitution","workflow")}; m["immutable"]={"data":imm,"sha256":sha(json.dumps(imm,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())}; m["initial_artifacts"]={}
  if d.exists():
   old=json.loads(read(d/"WORK-ITEM.json"));
   if old.get("immutable")!=m["immutable"]: return emit({"verdict":"BLOCKED","code":"IDENTITY-DIVERGENCE","work_id":wid},2)
   return emit({"status":"REUSED","work_id":wid,"path":str(d)})
  st=Path(tempfile.mkdtemp(prefix=".staging-",dir=par))
  try:
   for n in FILES[1:]: atomic(st/n,tmpl(n,wid))
   m["initial_artifacts"]={n:sha(read(st/n)) for n in FILES[1:]}; m["integrity_manifest"]={"WORK-ITEM.json":None,**m["initial_artifacts"]}; atomic(st/"WORK-ITEM.json",(json.dumps(m,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()); (st/"docs/adr").mkdir(parents=True); (st/"handoffs").mkdir(); os.replace(st,d)
  except Exception: shutil.rmtree(st,ignore_errors=True); raise
  return emit({"status":"CREATED","work_id":wid,"path":str(d)})
 finally: shutil.rmtree(lock,ignore_errors=True)
def audit(a):
 r=root(a.project_root or a.root); d=Path(a.artifact_root) if a.artifact_root else r/".grill/work-items"/a.work_id
 try:
  m=json.loads(read(d/"WORK-ITEM.json")); cur=constitution(r); rec=m.get("constitution",{}).get("sha256")
  if cur["state"]=="present" and rec!=cur["sha256"]: raise RuntimeError("constitution hash stale")
  cc=check_const(r,d)
 except RuntimeError as e:return emit({"verdict":"BLOCKED-CONSTITUTION","code":"CONSTITUTION-CHECK","error":str(e)},3)
 except Exception:return emit({"verdict":"NO-GO","code":"INVALID-WORK-ITEM"},1)
 if any(not (d/n).is_file() for n in FILES): return emit({"verdict":"NO-GO","code":"ARTIFACT-INVALID"},1)
 auditor=Path(__file__).with_name("audit_decisions.py"); p=subprocess.run([sys.executable,str(auditor),str(d),"--project-root",str(r),"--json"],text=True,capture_output=True); recp=json.loads(p.stdout.splitlines()[-1]) if p.stdout.splitlines() else {}
 return emit({"verdict":"GO" if p.returncode==0 else recp.get("verdict","NO-GO"),"code":"OK" if p.returncode==0 else recp.get("code","AUDIT"),"work_id":m.get("work_id"),"constitutional":cc,"audit":recp},p.returncode if p.returncode in (0,1,2,3) else 1)
def bundle_from_dir(d):
 files={}
 for p in sorted(d.rglob("*")) if d.is_dir() else []:
  if p.is_file() and not p.is_symlink(): files[str(p.relative_to(d))]=read(p)
 return sha(b"".join(k.encode()+b"\0"+v+b"\0" for k,v in files.items())),files
def reconcile(a):
 r=root(a.root); sources=[(r,None)]+[(root(x),None) for x in a.source_root]; items=[]
 for sr,ref in sources:
  d=sr/".grill/work-items"
  if d.is_dir():
   for x in sorted(d.iterdir()):
    if x.is_dir() and (x/"WORK-ITEM.json").is_file(): items.append((json.loads(read(x/"WORK-ITEM.json")),bundle_from_dir(x)[0]))
 for ref in a.source_ref:
  for line in git(r,"ls-tree","-r","--name-only",ref,".grill/work-items").splitlines():
   if line.endswith("/WORK-ITEM.json"):
    wid=line.split("/")[2]; files={}
    for f in git(r,"ls-tree","-r","--name-only",ref,f".grill/work-items/{wid}").splitlines(): files[f.split(f".grill/work-items/{wid}/",1)[1]]=subprocess.run(["git","-C",str(r),"show",f"{ref}:{f}"],capture_output=True).stdout
    items.append((json.loads(files["WORK-ITEM.json"]),sha(b"".join(k.encode()+b"\0"+v+b"\0" for k,v in sorted(files.items())))))
 ids={}; conflicts=[]
 for m,f in items:
  w=m.get("work_id");
  if w in ids and ids[w]!=f: conflicts.append(w)
  ids[w]=f
 qualified=[]
 for w in sorted(ids):
  found=set()
  for mm,ff in items:
   if mm.get("work_id")==w: found.update(re.findall(r"ADR-\d+",json.dumps(mm,ensure_ascii=False)))
  qualified.extend(f"{w}/{adr}" for adr in sorted(found))
 qualified=qualified or sorted(ids)
 result={"verdict":"PREVIEW","code":"CONFLICTS" if conflicts else "OK","qualified_ids":qualified,"conflicts":sorted(set(conflicts)),"count":len(ids)}
 if a.apply:
  if git(r,"branch","--show-current")!=a.integration_branch or git(r,"status","--porcelain"): return emit({**result,"verdict":"BLOCKED","code":"APPLY-REQUIRES-CLEAN-BRANCH"},2)
  if conflicts:return emit({**result,"verdict":"NO-GO"},1)
  body=("# Global ROADMAP\n\n"+"\n".join("- "+q for q in qualified)+"\n").encode(); atomic(r/".grill/global/ROADMAP.md",body); atomic(r/".grill/global/AUDIT.md",json.dumps(result,sort_keys=True).encode()+b"\n"); result["verdict"]="APPLIED"
 return emit(result)
def migrate(a):
 r=root(a.root); paths=[]
 for base in ("CONTEXT.md","DECISION-BACKLOG.md","DECISION-FRONTIER.md","ROADMAP.md","ROUND-LOG.jsonl","state.json","PLAN-CONTEXT.md","AUDIT.md","docs/adr","adrs","handoffs"):
  p=r/base
  if p.is_symlink(): return emit({"verdict":"BLOCKED","code":"SYMLINK"},2)
  if p.is_file(): paths.append((base,read(p)))
  elif p.is_dir():
   for q in sorted(p.rglob("*")):
    if q.is_symlink(): return emit({"verdict":"BLOCKED","code":"SYMLINK"},2)
    if q.is_file(): paths.append((str(q.relative_to(r)),read(q)))
 result={"verdict":"PREVIEW","code":"OK","files":sorted(k for k,_ in paths),"hashes":{k:sha(v) for k,v in paths}}
 if a.apply:
  wid=a.work_id or f"{a.type}-{a.slug}-migration"; d=r/".grill/work-items"/wid
  if d.exists():
   old={str(q.relative_to(d)):read(q) for q in d.rglob("*") if q.is_file()}; new=dict(paths)
   same=all(old.get(k)==v for k,v in new.items())
   return emit({**result,"verdict":"REUSED" if same else "BLOCKED","code":"OK" if same else "TARGET-DIVERGES","work_id":wid},0 if same else 2)
  (r/".grill").mkdir(exist_ok=True); st=Path(tempfile.mkdtemp(prefix=".migration-",dir=r/".grill"));
  try:
   for k,v in paths: atomic(st/k,v)
   (st/"docs/adr").mkdir(parents=True,exist_ok=True); (st/"handoffs").mkdir(exist_ok=True); d.parent.mkdir(parents=True,exist_ok=True); os.replace(st,d)
  except Exception: shutil.rmtree(st,ignore_errors=True); raise
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
if __name__=="__main__": sys.exit(main())
