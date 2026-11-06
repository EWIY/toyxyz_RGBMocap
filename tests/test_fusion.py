"""CPU regression tests for optional fusion; no checkpoints or video required.

Run with the app's shared Python: python -m unittest discover -s tests -p test_fusion.py
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scipy.spatial.transform import Rotation

from mocap.fusion import blend_rotations, options, PARENTS, REGIONS, input_identity, current
from mocap.fusion_pipeline import matching, same_tracking, sources, load_sources
from mocap.motion_tools import MOTION_TOOLS
from mocap.storage import atomic_json


def world(local):
    result=[]
    for j,p in enumerate(PARENTS):
        result.append(local[:,j] if p<0 else result[p]@local[:,j])
    return np.stack(result,1)


class BlendTests(unittest.TestCase):
    def setUp(self):
        self.flow=Rotation.random(7*52,random_state=1).as_matrix().reshape(7,52,3,3)
        self.gv=Rotation.random(7*22,random_state=2).as_matrix().reshape(7,22,3,3)

    def test_zero_and_empty_are_exact_passthrough(self):
        for settings in ({'weight':0},{'regions':[]}):
            np.testing.assert_array_equal(blend_rotations(self.flow,self.gv,settings),self.flow)

    def test_unselected_local_motion_exact_at_all_weights(self):
        for region in REGIONS:
            protected=[j for j in range(52) if j not in REGIONS[region]]
            for weight in (.01,.5,1.):
                result=blend_rotations(self.flow,self.gv,dict(regions=[region],weight=weight))
                np.testing.assert_array_equal(result[:,protected],self.flow[:,protected])
                np.testing.assert_allclose(result.swapaxes(-1,-2)@result,np.broadcast_to(np.eye(3),result.shape),atol=1e-12)

    def test_full_guidance_matches_aligned_global_orientations(self):
        fused=world(blend_rotations(self.flow,self.gv))
        yaw=lambda r:np.arctan2(r[0,2],r[2,2])
        align=Rotation.from_euler('y',yaw(self.flow[0,0])-yaw(self.gv[0,0])).as_matrix()
        goal=align@world(self.gv)
        selected=[j for bones in REGIONS.values() for j in bones]
        np.testing.assert_allclose(fused[:,selected],goal[:,selected],atol=1e-12)

    def test_half_weight_shortest_arc_and_turn_timing(self):
        flow=np.broadcast_to(np.eye(3),(5,52,3,3)).copy()
        gv=np.broadcast_to(np.eye(3),(5,22,3,3)).copy()
        turns=np.array([0,20,70,130,170])
        flow[:,0]=Rotation.from_euler('y',turns,degrees=True).as_matrix()
        gv[:,0]=flow[:,0]
        gv[:,15]=Rotation.from_euler('x',[0,60,120,-120,-60],degrees=True).as_matrix()
        result=blend_rotations(flow,gv,dict(weight=.5,regions=['head']))
        np.testing.assert_array_equal(result[:,0],flow[:,0])
        np.testing.assert_allclose(result[:,15],Rotation.from_euler('x',[0,30,60,-60,-30],degrees=True).as_matrix(),atol=1e-12)

    def test_malformed_input_rejected(self):
        for value in (-.1,1.1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):options(dict(weight=value))
        with self.assertRaises(ValueError):options(dict(regions=['root']))
        with self.assertRaises(ValueError):blend_rotations(self.flow,self.gv[:-1])
        bad=self.gv.copy();bad[0,0,0,0]=np.nan
        with self.assertRaises(ValueError):blend_rotations(self.flow,bad)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.state=dict(source_sha256='video-a',start=0,end=1,frames=30,fps=30,width=640,height=480,
                        pipeline={'model':'fusion','result':'corrected_initial'},camera='static')
        self.project=self.make('fusion','fusion')
        self.flow=self.make('flowhmr','flowhmr')
        self.gv=self.make('gvhmr','gvhmr')

    def make(self,name,model):
        p=self.base/name;p.mkdir(parents=True)
        state=copy.deepcopy(self.state);state['pipeline']['model']=model
        atomic_json(p/'project.json',state)
        (p/'input.mp4').write_bytes(b'fixture-video')
        np.savez(p/'tracking.npz',boxes=np.zeros((30,4)),K=np.eye(3))
        return p

    def candidates(self,project,model):
        return iter([self.flow if model=='flowhmr' else self.gv])

    def test_existing_sources_do_not_launch_workers(self):
        calls=[]
        with patch('mocap.fusion_pipeline.candidates',self.candidates),patch('mocap.motion_tools.result_is_current',return_value=True):
            selected=sources(self.project,lambda *a,**k:None,lambda *a:calls.append(a))
            self.assertEqual(set(selected),{'flowhmr','gvhmr'})
            self.assertFalse(calls)
            atomic_json(self.project/'project.json',{**self.state,'fusion_options':dict(weight=.3,regions=['head'])})
            self.assertEqual(load_sources(self.project,lambda *a,**k:None,lambda *a:calls.append(a)),selected)
            self.assertFalse(calls)

    def test_only_missing_engine_runs_in_order(self):
        calls=[]
        ready=set([self.flow])
        def run(stage,project,kind,emit):
            calls.append(stage)
            ready.add(project)
        with patch('mocap.fusion_pipeline.candidates',self.candidates),patch('mocap.motion_tools.result_is_current',side_effect=lambda p,k:p in ready):
            sources(self.project,lambda *a,**k:None,run)
        self.assertEqual(calls,['gvhmr'])

    def test_failed_dependency_does_not_publish_sources(self):
        def fail(*args):raise RuntimeError('cancelled')
        with patch('mocap.fusion_pipeline.candidates',self.candidates),patch('mocap.motion_tools.result_is_current',return_value=False):
            with self.assertRaisesRegex(RuntimeError,'cancelled'):sources(self.project,lambda *a,**k:None,fail)
        self.assertFalse((self.project/'fusion_sources.json').exists())

    def test_wrong_timing_person_and_video_rejected(self):
        baseline={**self.state,'person_id':1,'person_frames':[0,30],'person_fingerprint':'detector-generation'}
        for key,value in [('source_sha256','b'),('fps',24),('frames',29),('start',.1),('person_id',2),('person_fingerprint','other')]:
            self.assertFalse(matching(baseline,{**baseline,key:value}),key)
        self.assertTrue(matching(baseline,baseline))
        np.savez(self.gv/'tracking.npz',boxes=np.ones((30,4)),K=np.eye(3))
        self.assertFalse(same_tracking(self.flow,self.gv))

    def test_stages_and_runtime_are_opt_in(self):
        from mocap.runtime_registry import profile_for
        self.assertEqual(MOTION_TOOLS['fusion'].stages(correction=True),['track','fusion_sources','fusion_blend'])
        self.assertEqual(MOTION_TOOLS['flowhmr'].stages(correction=True),['track','flow_camera','flow_features','flowhmr','correct','flow_export'])
        self.assertEqual(profile_for('fusion_native'),'flow')
        self.assertEqual(profile_for('fusion_sources'),'shared')
        self.assertEqual(profile_for('gvhmr'),'shared')
        self.assertEqual(profile_for('correct',['--project',str(self.project)]),'shared')

    def receipt(self):
        from mocap.result_artifacts import file_stat
        from mocap.correction_settings import correction_options
        from mocap.fusion import VERSION
        refs={m:str(p) for m,p in (('flowhmr',self.flow),('gvhmr',self.gv))}
        for p in (self.project,self.flow,self.gv):(p/'hmr4d_results.pt').write_bytes(b'prediction')
        atomic_json(self.project/'fusion_sources.json',dict(identity=input_identity(self.project),sources=refs))
        record=dict(version=VERSION,options=options(),identity=input_identity(self.project),
            correction=correction_options(),output=file_stat(self.project/'hmr4d_results.pt'),
            sources=[dict(model=m,project=str(p),stat=file_stat(p/'hmr4d_results.pt'),identity=input_identity(p))
                     for m,p in (('flowhmr',self.flow),('gvhmr',self.gv))])
        atomic_json(self.project/'initial_fusion.json',record)

    def test_receipt_invalidates_on_weight_input_source_and_pending(self):
        self.receipt()
        with patch('mocap.motion_tools.result_is_current',return_value=True):
            self.assertTrue(current(self.project,'initial'))
            atomic_json(self.project/'project.json',{**self.state,'fusion_options':{'weight':.5}})
            self.assertFalse(current(self.project,'initial'))
            atomic_json(self.project/'project.json',self.state)
            self.assertTrue(current(self.project,'initial'))
            (self.project/'fusion_pending.json').write_text('{}')
            self.assertFalse(current(self.project,'initial'))
            (self.project/'fusion_pending.json').unlink()
            (self.gv/'hmr4d_results.pt').write_bytes(b'replaced-prediction')
            self.assertFalse(current(self.project,'initial'))

    def test_changed_tracking_and_actor_cannot_keep_old_fusion(self):
        self.receipt()
        with patch('mocap.motion_tools.result_is_current',return_value=True):
            np.savez(self.flow/'tracking.npz',boxes=np.ones((30,4)),K=np.eye(3))
            self.assertFalse(current(self.project,'initial'))
        self.receipt()
        with patch('mocap.motion_tools.result_is_current',return_value=True):
            state=json.loads((self.gv/'project.json').read_text());state['person_id']=5
            atomic_json(self.gv/'project.json',state)
            self.assertFalse(current(self.project,'initial'))

    def test_recursive_fusion_source_rejected(self):
        self.receipt()
        state=json.loads((self.gv/'project.json').read_text());state['pipeline']['model']='fusion'
        atomic_json(self.gv/'project.json',state)
        self.assertFalse(current(self.project,'initial'))


if __name__=='__main__':unittest.main()
