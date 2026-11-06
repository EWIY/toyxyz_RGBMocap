"""Presentation-only worker entry; inference/cache identities stay unchanged."""
import json,runpy,sys
from contextlib import contextmanager,nullcontext

for stream in (sys.stdout,sys.stderr):
    if hasattr(stream,'reconfigure'):
        stream.reconfigure(encoding='utf-8',errors='backslashreplace')


def emit(kind,**value):
    print('@@MOCAP@@'+json.dumps(dict(type=kind,**value)),flush=True)


@contextmanager
def download_progress(callback):
    """Preserve the downloader signature, including recursive metadata calls."""
    from . import models
    original=models.download
    def wrapped(key,progress=None):
        return original(key,progress=callback if progress is None else progress)
    try:
        models.download=wrapped
        yield
    finally:models.download=original


def main():
    stage=sys.argv[1] if len(sys.argv)>1 else ''
    if stage=='prepare' and '--motion-tool' in sys.argv and sys.argv[sys.argv.index('--motion-tool')+1]=='fusion':
        from . import worker
        original=worker.emit
        def prepared(kind,**value):
            if kind=='prepared':
                import os
                from pathlib import Path
                from .storage import atomic_json
                from .fusion import options
                path=Path(value['project'])/'project.json'
                state=json.loads(path.read_text(encoding='utf-8'))
                state['fusion_options']=options(json.loads(os.environ.get('RGB_MOCAP_FUSION_OPTIONS','{}')))
                atomic_json(path,state)
                value['manifest']['fusion_options']=state['fusion_options']
            original(kind,**value)
        worker.emit=prepared
        try:return worker.main()
        finally:worker.emit=original
    if stage=='fusion_native':
        from .fusion_native import main as fusion_main
        return fusion_main(sys.argv[1:],emit)
    if stage in ('fusion_sources','fusion_blend'):
        from .fusion_pipeline import main as fusion_main
        return fusion_main(sys.argv[1:],emit)
    if stage in ('track','correct','rig','mesh','export') and '--project' in sys.argv:
        from pathlib import Path
        project=Path(sys.argv[sys.argv.index('--project')+1])
        state=json.loads((project/'project.json').read_text(encoding='utf-8'))
        if state.get('pipeline',{}).get('model')=='fusion':
            if stage=='track':
                from .fusion_pipeline import reuse_tracking
                if reuse_tracking(project):
                    emit('complete',stage='track',output=str(project/'tracking.npz'),cached=True)
                    return 0
            else:
                from .fusion_pipeline import main as fusion_main
                return fusion_main(sys.argv[1:],emit)
    if stage in ('save_blend','save_blend_scene'):
        from .blend_export_worker import main as save_main
        return save_main(emit)
    if stage=='camera_background':
        from .camera_background_worker import main as camera_main
        return camera_main()
    if stage=='camera_reference':
        from .camera_reference import main as camera_main
        return camera_main()
    if stage=='copy_bvh':
        from .source_export_worker import main as save_main
        return save_main(emit)
    if stage=='flow_mamma_gravity':
        from .mamma_gravity_worker import main as gravity_main
        return gravity_main()
    if stage=='pear_camera_preview':
        from .pear.camera_preview import main as camera_main
        return camera_main()
    if stage=='flow_pear_align':
        from .pear.align_worker import main as align_main
        return align_main()
    if stage=='pear_live':
        from .pear.worker import main as live_main
        return live_main()
    if stage in ('prompthmr_prepare','prompthmr_publish'):
        from .compute_policy import configure_worker_cpu
        configure_worker_cpu(stage)
        from .prompthmr_pipeline import main as phmr_main
        return phmr_main(sys.argv[1:])
    if stage in ('flow_batch','exmr_batch','gvhmr_batch'):
        from .batch_worker import main as batch_main
        from .progress_events import tqdm_events
        with tqdm_events(emit):return batch_main(sys.argv[1:],emit)
    if stage in ('mamma_prepare','mamma_publish'):
        from .compute_policy import configure_worker_cpu
        configure_worker_cpu(stage)
        from .mamma_pipeline import main as mamma_main
        return mamma_main(sys.argv[1:])
    if stage=='character':
        from .retarget.worker import main as character_main
        return character_main(sys.argv[2:])
    if stage=='save_project':
        from .project_save import main as save_main
        sys.argv.pop(1)
        return save_main(emit)
    if stage.startswith('exmr') or stage=='download':
        from .progress_events import tqdm_events
        with tqdm_events(emit), (download_progress(emit) if stage=='download' else nullcontext()):
            runpy.run_module('mocap.worker',run_name='__main__')
    else:runpy.run_module('mocap.worker',run_name='__main__')


if __name__=='__main__':raise SystemExit(main())
