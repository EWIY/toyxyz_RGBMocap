"""Regressions for valid copied tracking remaining visible in the GUI."""
import hashlib,json,os,shutil,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from mocap.fusion_pipeline import reuse_tracking
from mocap.single_actor import snapshot_key

class TrackingReuseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);self.src=root/'source';self.dst=root/'target'
  for p in (self.src,self.dst):
   p.mkdir();(p/'input.mp4').write_bytes(b'identical media')
   (p/'project.json').write_text(json.dumps(dict(frames=3)))
  np.savez(self.src/'tracking.npz',boxes=np.tile([1,2,12,20],(3,1)),observed=np.ones(3,bool))
  old=time.time()-120;os.utime(self.src/'input.mp4',(old-10,old-10));os.utime(self.src/'tracking.npz',(old,old))
  self.original=(self.src/'tracking.npz').read_bytes();self.stamp=(self.src/'tracking.npz').stat().st_mtime_ns

 def test_new_and_legacy_copies_have_valid_snapshot_without_changing_source(self):
  for old_copy in (False,True):
   with self.subTest(old_copy=old_copy):
    if old_copy:shutil.copy2(self.src/'tracking.npz',self.dst/'tracking.npz');self.assertIsNone(snapshot_key(self.dst))
    with patch('mocap.fusion_pipeline.candidates',return_value=iter([self.src])):
     self.assertTrue(reuse_tracking(self.dst))
    self.assertIsNotNone(snapshot_key(self.dst))
    self.assertEqual((self.dst/'tracking.npz').read_bytes(),self.original)
    self.assertEqual((self.src/'tracking.npz').read_bytes(),self.original)
    self.assertEqual((self.src/'tracking.npz').stat().st_mtime_ns,self.stamp)

 def test_stale_mismatched_media_or_observations_not_accepted(self):
  shutil.copy2(self.src/'tracking.npz',self.dst/'tracking.npz')
  for mismatch in ('media','observations'):
   with self.subTest(mismatch=mismatch):
    if mismatch=='media':(self.src/'input.mp4').write_bytes(b'different media')
    else:
     (self.src/'input.mp4').write_bytes(b'identical media')
     np.savez(self.src/'tracking.npz',boxes=np.tile([40,50,70,80],(3,1)),observed=np.ones(3,bool))
    with patch('mocap.fusion_pipeline.candidates',return_value=iter([self.src])):
     self.assertFalse(reuse_tracking(self.dst))
    self.assertIsNone(snapshot_key(self.dst))
    self.assertEqual((self.dst/'tracking.npz').read_bytes(),self.original)
