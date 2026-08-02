#!/usr/bin/env python3
"""Independent contract matrix for workspace v2."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
PLUGIN=Path(__file__).parents[1]; SCRIPT=PLUGIN/'skills/grill-with-docs/scripts/grill_workspace.py'
def run(*args,cwd=None): return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],cwd=cwd,text=True,capture_output=True)
def obj(p):
 assert len(p.stdout.splitlines())==1,p.stdout; return json.loads(p.stdout)
class WorkspaceContract(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.r=Path(self.t.name); subprocess.run(['git','init','-q'],cwd=self.r,check=True); subprocess.run(['git','config','user.email','x@y'],cwd=self.r); subprocess.run(['git','config','user.name','x'],cwd=self.r); (self.r/'WORKFLOW.md').write_text('global',encoding='utf8')
 def tearDown(self): self.t.cleanup()
 def test_init_identity_manifest_and_isolation(self):
  a=obj(run('init',self.r,'--type','feature','--slug','same')); b=obj(run('init',self.r,'--type','fix','--slug','same')); self.assertNotEqual(a['work_id'],b['work_id'])
  d=Path(a['path']); m=json.loads((d/'WORK-ITEM.json').read_text()); self.assertEqual(set(m['integrity_manifest']),{'WORK-ITEM.json','CONTEXT.md','DECISION-BACKLOG.md','DECISION-FRONTIER.md','ROADMAP.md','ROUND-LOG.jsonl','state.json','PLAN-CONTEXT.md','CONSTITUTION-CHECK.md','AUDIT.md'}); self.assertEqual((self.r/'WORKFLOW.md').read_text(),'global')
  self.assertEqual(obj(run('init',self.r,'--type','feature','--slug','same','--work-id',a['work_id']))['status'],'REUSED')
  self.assertNotEqual(run('init',self.r,'--type','bad','--slug','x').returncode,0); self.assertNotEqual(run('init',self.r,'--type','feature','--slug','../x').returncode,0)
 def test_constitution_absent_present_and_stale(self):
  a=obj(run('init',self.r,'--type','feature','--slug','c','--work-id','c1')); self.assertEqual(obj(run('audit',self.r,'--work-id','c1'))['constitutional'],None)
  c=self.r/'.specify/memory/constitution.md'; c.parent.mkdir(parents=True); c.write_text('# Principle: Safety\n',encoding='utf8'); z=run('audit',self.r,'--work-id','c1'); self.assertEqual(z.returncode,3); self.assertEqual(obj(z)['verdict'],'BLOCKED-CONSTITUTION')
 def test_reconcile_preview_repeat_and_apply_guards(self):
  obj(run('init',self.r,'--type','feature','--slug','r','--work-id','w1')); x=obj(run('reconcile',self.r)); self.assertEqual(x['verdict'],'PREVIEW'); self.assertEqual(x,obj(run('reconcile',self.r)))
  self.assertEqual(obj(run('reconcile',self.r,'--apply','--integration-branch','wrong'))['verdict'],'BLOCKED')
 def test_migrate_utf8_preview_apply_reuse(self):
  (self.r/'CONTEXT.md').write_text('conteúdo integral\n',encoding='utf8'); p=obj(run('migrate',self.r,'--type','feature','--slug','mig','--work-id','m1')); self.assertEqual(p['verdict'],'PREVIEW'); a=obj(run('migrate',self.r,'--type','feature','--slug','mig','--work-id','m1','--apply')); self.assertEqual(a['verdict'],'APPLIED'); self.assertEqual((self.r/'.grill/work-items/m1/CONTEXT.md').read_text(), 'conteúdo integral\n'); self.assertEqual(obj(run('migrate',self.r,'--type','feature','--slug','mig','--work-id','m1','--apply'))['verdict'],'REUSED')
if __name__=='__main__': unittest.main()
