#!/usr/bin/env python3
"""Core v2 isolated work-item workspace CLI (stdlib, deterministic/read-only gates)."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
TYPES={'feature','fix','hotfix'}; ID=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{1,100}$'); SLUG=re.compile(r'^[a-z0-9][a-z0-9-]{0,80}$')
FILES=['WORK-ITEM.json','CONTEXT.md','DECISION-BACKLOG.md','DECISION-FRONTIER.md','ROADMAP.md','ROUND-LOG.jsonl','state.json','PLAN-CONTEXT.md','CONSTITUTION-CHECK.md','AUDIT.md']
def out(x, code=0): print(json.dumps(x,ensure_ascii=False,sort_keys=True)); return code
def root(p):
 p=Path(p)
 if not p.exists() or not p.is_dir() or p.is_symlink(): raise ValueError('ROOT inválido')
 r=subprocess.run(['git','-C',str(p),'rev-parse','--show-toplevel'],text=True,capture_output=True)
 if r.returncode: raise ValueError('ROOT não é git root')
 real=Path(r.stdout.strip()).resolve()
 if real!=p.resolve(): raise ValueError('ROOT deve ser git root real')
 return real
def git(r,*a): return subprocess.run(['git','-C',str(r),*a],text=True,capture_output=True).stdout.strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,data):
 p.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix='.tmp-',dir=p.parent); os.write(fd,data.encode()); os.fsync(fd); os.close(fd); os.replace(tmp,p)
def init(a):
 r=root(a.root); slug=a.slug
 if a.type not in TYPES or not SLUG.fullmatch(slug): raise ValueError('type/slug inválido')
 head=git(r,'rev-parse','HEAD') or 'UNCOMMITTED'; base=git(r,'merge-base','HEAD','HEAD') or head
 wid=a.work_id or f'{a.type}-{slug}-{hashlib.sha256((head+slug+str(time.time_ns())).encode()).hexdigest()[:16]}'
 if not ID.fullmatch(wid): raise ValueError('work-id inválido')
 d=r/'.grill'/'work-items'/wid; lock=d.parent/(wid+'.lock')
 d.parent.mkdir(parents=True,exist_ok=True)
 try: lock.mkdir()
 except FileExistsError: pass
 try:
  meta={'schema':'grill-work-item/v2','work_id':wid,'type':a.type,'slug':slug,'branch':git(r,'branch','--show-current'),'head':head,'base':base,'created_at_epoch':int(time.time())}
  if d.exists():
   old=json.loads((d/'WORK-ITEM.json').read_text(encoding='utf-8'))
   if any(old.get(k)!=meta.get(k) for k in ('work_id','type','slug')): raise ValueError('work-id conflitante')
   return out({'status':'REUSED','work_id':wid,'path':str(d),'sha256':sha(d/'WORK-ITEM.json')})
  d.mkdir()
  atomic(d/'WORK-ITEM.json',json.dumps(meta,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
  vals={'CONTEXT.md':'# Context\n','DECISION-BACKLOG.md':'# Decision backlog\n','DECISION-FRONTIER.md':'# Decision frontier\n','ROADMAP.md':'# Roadmap\n','ROUND-LOG.jsonl':'','PLAN-CONTEXT.md':'# Plan context\n','CONSTITUTION-CHECK.md':'# Constitution check\nstatus: NOT-PRESENT\n','AUDIT.md':'# Audit\nstatus: initialized\n','state.json':json.dumps({'work_id':wid,'status':'in-progress'},indent=2)+'\n'}
  for n,v in vals.items(): atomic(d/n,v)
  (d/'docs'/'adr').mkdir(parents=True); (d/'handoffs').mkdir()
  return out({'status':'CREATED','work_id':wid,'path':str(d),'sha256':sha(d/'WORK-ITEM.json')})
 finally:
  try: lock.rmdir()
  except OSError: pass
def audit(a):
 r=root(a.root); d=r/'.grill'/'work-items'/a.work_id
 if not d.is_dir(): return out({'verdict':'BLOCKED','code':'WORK-ITEM-MISSING'})
 findings=[]
 try: meta=json.loads((d/'WORK-ITEM.json').read_text(encoding='utf-8'))
 except (OSError,UnicodeError,json.JSONDecodeError): return out({'verdict':'BLOCKED','code':'INVALID-WORK-ITEM'})
 for n in FILES:
  if not (d/n).is_file(): findings.append('MISSING:'+n)
 c=r/'.specify/memory/constitution.md'
 if not c.exists(): return out({'verdict':'BLOCKED-CONSTITUTION','code':'CONSTITUTION-NOT-PRESENT','findings':findings})
 try: text=c.read_text(encoding='utf-8')
 except UnicodeError: return out({'verdict':'BLOCKED-CONSTITUTION','code':'CONSTITUTION-UNREADABLE'})
 if not text.strip() or '{{' in text or '[PLACEHOLDER]' in text: return out({'verdict':'BLOCKED-CONSTITUTION','code':'CONSTITUTION-PLACEHOLDER'})
 expected=json.loads((d/'WORK-ITEM.json').read_text())
 cc=(d/'CONSTITUTION-CHECK.md').read_text(encoding='utf-8')
 if any(x in cc for x in ('PENDING','UNMAPPED','VIOLATION','BLOCKED')): return out({'verdict':'BLOCKED-CONSTITUTION','code':'CONSTITUTION-CHECK-INCOMPLETE','findings':findings})
 verdict='GO' if not findings else 'NO-GO'; return out({'verdict':verdict,'code':'OK' if verdict=='GO' else 'ARTIFACT-MISSING','findings':findings,'work_id':a.work_id})
def reconcile(a):
 r=root(a.root); items=[]
 for d in sorted((r/'.grill/work-items').glob('*')) if (r/'.grill/work-items').is_dir() else []:
  if d.is_dir() and (d/'WORK-ITEM.json').is_file():
   try: items.append(json.loads((d/'WORK-ITEM.json').read_text(encoding='utf-8')))
   except Exception: return out({'verdict':'BLOCKED','code':'INVALID-WORK-ITEM'})
 ids={}; conflicts=[]
 for x in items:
  if x['work_id'] in ids and ids[x['work_id']]!=x: conflicts.append(x['work_id'])
  ids[x['work_id']]=x
 if conflicts: return out({'verdict':'BLOCKED','code':'DUPLICATE-WORK-ID','work_ids':sorted(set(conflicts))})
 result={'verdict':'PREVIEW','code':'OK','work_ids':sorted(ids),'count':len(ids)}
 if a.apply:
  branch=git(r,'branch','--show-current'); dirty=git(r,'status','--porcelain')
  if branch!=a.integration_branch or dirty: return out({'verdict':'BLOCKED','code':'APPLY_REQUIRES_CLEAN_INTEGRATION_BRANCH'})
  g=r/'.grill/global'; g.mkdir(parents=True,exist_ok=True)
  body='# Global ROADMAP (projection)\\n\\n'+''.join(f"- {x['work_id']} ({x['type']}): {x['slug']}\\n" for x in sorted(items,key=lambda z:z['work_id']))
  atomic(g/'ROADMAP.md',body); atomic(g/'AUDIT.md',json.dumps(result,sort_keys=True)+'\\n'); result['verdict']='APPLIED'
 return out(result)
def migrate(a):
 r=root(a.root); legacy=[x for x in ('CONTEXT.md','ROADMAP.md','state.json') if (r/x).exists()]; result={'verdict':'PREVIEW','code':'OK','legacy':legacy}
 if a.apply:
  wid=a.work_id or f'{a.type}-{a.slug}-migration'; x=argparse.Namespace(root=str(r),type=a.type,slug=a.slug,work_id=wid); init(x); d=r/'.grill/work-items'/wid;
  for n in legacy:
   target=d/n
   if not target.exists(): atomic(target,(r/n).read_bytes().decode('utf-8'))
  result['verdict']='APPLIED'; result['work_id']=d.name
 return out(result)
def main():
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True); i=s.add_parser('init'); i.add_argument('root'); i.add_argument('--type',required=True); i.add_argument('--slug',required=True); i.add_argument('--work-id'); q=s.add_parser('audit'); q.add_argument('root'); q.add_argument('--work-id',required=True); c=s.add_parser('reconcile'); c.add_argument('root'); c.add_argument('--apply',action='store_true'); c.add_argument('--integration-branch'); m=s.add_parser('migrate'); m.add_argument('root'); m.add_argument('--type',required=True); m.add_argument('--slug',required=True); m.add_argument('--work-id'); m.add_argument('--apply',action='store_true'); a=p.parse_args()
 try: return {'init':init,'audit':audit,'reconcile':reconcile,'migrate':migrate}[a.cmd](a)
 except (ValueError,OSError,UnicodeError) as e: return out({'verdict':'BLOCKED','code':'INVALID-INPUT','error':str(e)},2)
if __name__=='__main__': sys.exit(main())
