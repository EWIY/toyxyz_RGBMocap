"""Cache identity for the selected person detector; no inference imports."""
import hashlib
import importlib.metadata
import os
from pathlib import Path


def identity():
    from .models import BY_KEY
    from .result_artifacts import file_stat
    key=os.environ.get('RGB_MOCAP_DETECTOR','yolov8')
    if key not in {'yolov8','yolox'}:
        raise ValueError('Unsupported person detector: '+key)
    model=BY_KEY['humanart' if key=='yolox' else 'yolo'].path
    result=dict(detector=key,model=file_stat(model) if model.is_file() else None)
    if key=='yolox':
        result['adapter']=hashlib.sha256(Path(__file__).with_name('yolox_humanart.py').read_bytes()).hexdigest()
        try:result['runtime']=importlib.metadata.version('onnxruntime-gpu')
        except importlib.metadata.PackageNotFoundError:result['runtime']='not-installed'
    return result
