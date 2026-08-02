#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
PLUGIN=Path(__file__).parents[1]; SCRIPT=PLUGIN/'skills/grill-with-docs/scripts/grill_workspace.py'
def run(*a,cwd=None): return subprocess.run([sys.executable,str(SCRIPT),*a],cwd=cwd,text=True,capture_output=True)
class Workspace(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.r=Path(self.t.name); subprocess.run(['git','init','-q'],cwd=self.r,check=True); subprocess.run(['git','config','user.email','x@y'],cwd=self.r); subprocess.run(['git','config','user.name','x'],cwd=self.r); (self.r/'WORKFLOW.md').write_text('global')
 def tearDown(self): self.t.cleanup()
 def test_init_isolated_and_idempotent(self):
  a=run('init',str(self.r),'--type','feature','--slug','same'); b=run('init',str(self.r),'--type','fix','--slug','same'); self.assertEqual(a.returncode,0); self.assertEqual(b.returncode,0); self.assertNotEqual(json.loads(a.stdout)['work_id'],json.loads(b.stdout)['work_id']); self.assertEqual(run('init',str(self.r),'--type','feature','--slug','same','--work-id',json.loads(a.stdout)['work_id']).returncode,0); self.assertEqual((self.r/'WORKFLOW.md').read_text(),'global')
 def test_type_collision_and_constitution(self):
  x=run('init',str(self.r),'--type','bad','--slug','x'); self.assertNotEqual(x.returncode,0); x=run('init',str(self.r),'--type','feature','--slug','x','--work-id','fixed'); self.assertEqual(x.returncode,0); y=run('init',str(self.r),'--type','feature','--slug','y','--work-id','fixed'); self.assertNotEqual(y.returncode,0); z=run('audit',str(self.r),'--work-id','fixed'); self.assertEqual(json.loads(z.stdout)['verdict'],'BLOCKED-CONSTITUTION')
if __name__=='__main__': unittest.main()
