#!/usr/bin/env python3
"""Isolated workspace v2 lifecycle (stdlib only; exactly one JSON line)."""
import argparse, contextlib, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, time, uuid
from pathlib import Path
TYPES={"feature","fix","hotfix"}; ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,100}$"); SLUG=re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
ASSET=Path(__file__).resolve().parents[1]/"assets"
INITIAL=("WORK-ITEM.json","CONTEXT.md","DECISION-BACKLOG.md","DECISION-FRONTIER.md","ROADMAP.md","ROUND-LOG.jsonl","state.json","PLAN-CONTEXT.md","CONSTITUTION-CHECK.md","AUDIT.md")
LEGACY=("CONTEXT.md","DECISION-BACKLOG.md","DECISION-FRONTIER.md","ROADMAP.md","ROUND-LOG.jsonl","state.json","PLAN-CONTEXT.md","AUDIT.md")
def out(x,code=0): print(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))); return code
def git(r,*args,input=None):
 p=subprocess.run(["git","-C",str(r),*args],text=True,capture_output=True,input=input); return p.stdout.strip() if p.returncode==0 else ""
def root(x):
 p=Path(x)
 if not p.is_dir() or p.is_symlink(): raise ValueError("root inválido")
 top=git(p,"rev-parse","--show-toplevel")
 if not top or Path(top).resolve()!=p.resolve(): raise ValueError("root deve ser git root")
 return p.resolve()
def sha(b): return hashlib.sha256(b).hexdigest()
def rb(p): return p.read_bytes()
def utf(p): return rb(p).decode("utf-8")
def atomic(p,b):
 p.parent.mkdir(parents=True,exist_ok=True); fd,t=tempfile.mkstemp(prefix=".grill-",dir=p.parent); os.write(fd,b); os.fsync(fd); os.close(fd); os.replace(t,p)
def constitution(r):
 p=r/".specify/memory/constitution.md"
 if not p.exists(): return {"state":"not-present","path":None,"sha256":None}
 b=rb(p); text=b.decode("utf-8")
 if not text.strip() or "{{" in text or "[PLACEHOLDER]" in text: raise ValueError("constitution inválida")
 return {"state":"present","path":".specify/memory/constitution.md","sha256":sha(b)}
def template(n):
 if n=="WORK-ITEM.json": q=ASSET/"WORK-ITEM.template.json"
 elif n=="state.json": q=ASSET/"state.template.json"
 else:
  stem,suf=n.rsplit('.',1); q=ASSET/(stem+".template."+suf)
 return rb(q) if q.is_file() else (b"" if n=="ROUND-LOG.jsonl" else (b"{}\n" if n.endswith(".json") else ("# "+n+"\n").encode()))
def metadata(r,a,wid):
 head=git(r,"rev-parse","HEAD") or "UNBORN"; ref=a.base_ref or "HEAD"; commit=git(r,"rev-parse",ref) or head
 if a.base_ref and not git(r,"rev-parse",ref): raise ValueError("base-ref inválida")
 wf=r/"WORKFLOW.md"; return {"schema":"grill-work-item/v2","work_id":wid,"type":a.type,"slug":a.slug,"branch":git(r,"branch","--show-current"),"HEAD":head,"base-ref":ref,"base-commit":commit,"constitution":constitution(r),"workflow":{"path":"WORKFLOW.md","sha256":sha(rb(wf)) if wf.is_file() else None},"scope":{"paths":[],"depends-on-work":[],"conflicts-with-adrs":[]}}
def init(a):
 r=root(a.root)
 if a.type not in TYPES or not SLUG.fullmatch(a.slug): raise ValueError("type/slug inválido")
 wid=a.work_id or f"{a.type}-{a.slug}-{uuid.uuid4().hex}"
 if not ID.fullmatch(wid): raise ValueError("work-id inválido")
 parent=r/".grill/work-items"; parent.mkdir(parents=True,exist_ok=True); d=parent/wid; lock=parent/("."+wid+".lock")
 try: os.mkdir(lock)
 except FileExistsError: return out({"verdict":"BLOCKED","code":"LOCK-CONTENTION","work_id":wid},2)
 try:
  m=metadata(r,a,wid)
  if d.exists():
   if d.is_symlink() or not (d/"WORK-ITEM.json").is_file(): return out({"verdict":"BLOCKED","code":"INTEGRITY-DIVERGENCE","work_id":wid},2)
   old=json.loads(utf(d/"WORK-ITEM.json")); keys=("work_id","type","slug","branch","HEAD","base-ref","base-commit","constitution","workflow")
   if any(old.get(k)!=m.get(k) for k in keys): return out({"verdict":"BLOCKED","code":"IDENTITY-DIVERGENCE","work_id":wid},2)
   return out({"status":"REUSED","work_id":wid,"path":str(d),"integrity":sha(rb(d/"WORK-ITEM.json"))})
  staging=Path(tempfile.mkdtemp(prefix="."+wid+"-",dir=parent))
  try:
   m["created_at_epoch"]=int(time.time()); (staging/"docs/adr").mkdir(parents=True); (staging/"handoffs").mkdir(parents=True); atomic(staging/"WORK-ITEM.json",(json.dumps(m,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode())
   for n in INITIAL[1:]: atomic(staging/n,template(n).replace(b"{{WORK_ID}}",wid.encode()))
   manifest={n:sha(rb(staging/n)) for n in INITIAL}; atomic(staging/"WORK-ITEM.json",(json.dumps({**m,"integrity_manifest":manifest},sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()); os.replace(staging,d)
  except Exception: shutil.rmtree(staging,ignore_errors=True); raise
  return out({"status":"CREATED","work_id":wid,"path":str(d),"integrity":sha(rb(d/"WORK-ITEM.json"))})
 finally: shutil.rmtree(lock,ignore_errors=True)
def clauses(text): return [(m.group(1).strip(),m.group(2).strip()) for m in re.finditer(r"(?m)^#{1,6}\s+(?:Principle|Section|Princípio|Seção)\s*[:.-]?\s*(.+)$",text,re.I)]
def constitution_check(r,d):
 c=r/".specify/memory/constitution.md"
 if not c.exists(): return None
 text=utf(c); expected=dict(clauses(text)); p=d/"CONSTITUTION-CHECK.md"
 if not p.is_file(): raise RuntimeError("CONSTITUTION-CHECK ausente")
 raw=utf(p); mh=re.search(r"(?im)^constitution[- _]hash\s*[:=]\s*([0-9a-f]{64})",raw)
 if not mh or mh.group(1)!=sha(rb(c)): raise RuntimeError("constitution hash stale")
 entries=[]
 for line in raw.splitlines():
  m=re.match(r"^\s*[-*]?\s*(?:clause|clause-id|heading)\s*[:=]\s*([^|]+)\|\s*status\s*[:=]\s*(\w+)\|\s*evidence\s*[:=]\s*(.+)$",line,re.I)
  if m: entries.append(tuple(x.strip() for x in m.groups()))
 if len(entries)!=len(expected) or len({x[0] for x in entries})!=len(entries): raise RuntimeError("clauses ausentes/duplicadas")
 for cid,status,ev in entries:
  if cid not in expected or status.upper() not in {"PASS","NOT-APPLICABLE"} or not ev.strip(): raise RuntimeError("clause inválida/pending/unmapped")
 return {"state":"present","sha256":sha(rb(c)),"clauses":len(entries)}
def audit(a):
 r=root(a.project_root or a.root); d=Path(a.artifact_root) if a.artifact_root else r/".grill/work-items"/a.work_id
 try:
  meta=json.loads(utf(d/"WORK-ITEM.json")); current=constitution(r); recorded=meta.get("constitution",{}).get("sha256")
  if current["state"]=="present" and recorded!=current["sha256"]: raise RuntimeError("constitution hash stale")
  cc=constitution_check(r,d)
 except RuntimeError as e:return out({"verdict":"BLOCKED-CONSTITUTION","code":"CONSTITUTION-CHECK","error":str(e)},3)
 except Exception:return out({"verdict":"NO-GO","code":"INVALID-WORK-ITEM"},1)
 missing=[n for n in INITIAL if not (d/n).is_file()]; findings=["MISSING:"+n for n in missing]
 if findings:return out({"verdict":"NO-GO","code":"ARTIFACT-INVALID","findings":findings},1)
 auditor=Path(__file__).with_name("audit_decisions.py"); p=subprocess.run([sys.executable,str(auditor),str(d),"--project-root",str(r),"--json"],text=True,capture_output=True)
 if p.returncode==2 and "unrecognized arguments" in p.stderr: p=subprocess.run([sys.executable,str(auditor),str(d),"--project-root",str(r)],text=True,capture_output=True)
 lines=p.stdout.splitlines(); receipt=json.loads(lines[-1]) if lines else {"verdict":"NO-GO"}
 return out({"verdict":"GO" if p.returncode==0 else receipt.get("verdict","NO-GO"),"code":"OK" if p.returncode==0 else receipt.get("code","AUDIT"),"work_id":meta.get("work_id"),"constitutional":cc,"audit":receipt},p.returncode if p.returncode in (0,1,2,3) else 1)
def reconcile(a):
 r=root(a.root); sources=[r]+[root(x) for x in a.source_root]; items=[]
 for sr in sources:
  d=sr/".grill/work-items"
  for x in sorted(d.iterdir()) if d.is_dir() else []:
   if x.is_dir() and (x/"WORK-ITEM.json").is_file(): items.append((json.loads(utf(x/"WORK-ITEM.json")),sha(rb(x/"WORK-ITEM.json"))))
 ids={}; conflicts=[]
 for m,f in items:
  w=m.get("work_id");
  if w in ids and ids[w]!=f: conflicts.append(w)
  ids[w]=f
 qualified=sorted(f"{w}/{w}" for w in ids)
 result={"verdict":"PREVIEW","code":"CONFLICTS" if conflicts else "OK","qualified_ids":qualified,"conflicts":sorted(set(conflicts)),"count":len(ids)}
 if a.apply:
  if git(r,"branch","--show-current")!=a.integration_branch or git(r,"status","--porcelain"): return out({**result,"verdict":"BLOCKED","code":"APPLY-REQUIRES-CLEAN-BRANCH"},2)
  if conflicts:return out({**result,"verdict":"NO-GO"},1)
  body=("# Global ROADMAP\n\n"+"\n".join("- "+q for q in qualified)+"\n").encode(); g=r/".grill/global"; atomic(g/"ROADMAP.md",body); atomic(g/"AUDIT.md",(json.dumps(result,sort_keys=True)+"\n").encode()); result["verdict"]="APPLIED"
 return out(result,0)
def migrate(a):
 r=root(a.root); blobs={}
 try:
  for n in LEGACY:
   p=r/n
   if p.exists(): blobs[n]=rb(p); blobs[n].decode("utf-8")
 except Exception as e:return out({"verdict":"NO-GO","code":"LEGACY-INVALID","error":str(e)},1)
 result={"verdict":"PREVIEW","code":"OK","legacy":sorted(blobs),"hashes":{n:sha(b) for n,b in blobs.items()}}
 if a.apply:
  wid=a.work_id or f"{a.type}-{a.slug}-migration"; d=r/".grill/work-items"/wid
  if d.exists():
   if all((d/n).is_file() and rb(d/n)==b for n,b in blobs.items()): result.update(verdict="REUSED",work_id=wid); return out(result)
   return out({**result,"verdict":"BLOCKED","code":"TARGET-DIVERGES"},2)
  q=argparse.Namespace(root=str(r),type=a.type,slug=a.slug,work_id=wid,base_ref=None)
  with contextlib.redirect_stdout(io.StringIO()): init(q)
  for n,b in blobs.items(): atomic(d/n,b)
  result.update(verdict="APPLIED",work_id=wid)
 return out(result)
def main():
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
 i=s.add_parser("init"); i.add_argument("root"); i.add_argument("--type",required=True); i.add_argument("--slug",required=True); i.add_argument("--work-id"); i.add_argument("--base-ref")
 q=s.add_parser("audit"); q.add_argument("root"); q.add_argument("--work-id"); q.add_argument("--artifact-root"); q.add_argument("--project-root")
 c=s.add_parser("reconcile"); c.add_argument("root"); c.add_argument("--source-root",action="append",default=[]); c.add_argument("--source-ref",action="append",default=[]); c.add_argument("--apply",action="store_true"); c.add_argument("--integration-branch")
 m=s.add_parser("migrate"); m.add_argument("root"); m.add_argument("--type",required=True); m.add_argument("--slug",required=True); m.add_argument("--work-id"); m.add_argument("--apply",action="store_true")
 a=p.parse_args()
 try:return {"init":init,"audit":audit,"reconcile":reconcile,"migrate":migrate}[a.cmd](a)
 except (ValueError,OSError,UnicodeError,json.JSONDecodeError) as e:return out({"verdict":"BLOCKED","code":"INVALID-INPUT","error":str(e)},2)
if __name__=="__main__": sys.exit(main())
