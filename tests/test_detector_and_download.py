"""Optional detector cache separation and the retained upstream callback fix."""
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mocap import detectors,models
from mocap.worker_progress import download_progress


class DetectorIdentityTests(unittest.TestCase):
    def test_detector_and_model_revision_have_distinct_cache_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            yolo=root/'yolo.pt';yolo.write_bytes(b'yolo fixture')
            humanart=root/'humanart.onnx';humanart.write_bytes(b'onnx fixture')
            entries={'yolo':SimpleNamespace(path=yolo),'humanart':SimpleNamespace(path=humanart)}
            with patch.object(models,'BY_KEY',entries),patch.dict(os.environ,{'RGB_MOCAP_DETECTOR':'yolov8'}):
                first=detectors.identity()
                os.environ['RGB_MOCAP_DETECTOR']='yolox'
                second=detectors.identity()
                self.assertNotEqual(first,second)
                humanart.write_bytes(b'replaced onnx fixture')
                self.assertNotEqual(second,detectors.identity())
                os.environ['RGB_MOCAP_DETECTOR']='invalid'
                with self.assertRaises(ValueError):detectors.identity()


class DownloadCallbackTests(unittest.TestCase):
    def test_recursive_metadata_download_accepts_explicit_progress(self):
        calls=[]
        outer=lambda *args,**kwargs:None
        explicit=lambda *args,**kwargs:None
        def original(key,progress=None):
            calls.append((key,progress))
            if key=='flowhmr':models.download('flow_metadata',progress=progress)
            return key
        with patch.object(models,'download',side_effect=original) as downloader:
            with download_progress(outer):
                self.assertEqual(models.download('flowhmr'),'flowhmr')
                self.assertEqual(models.download('flow_metadata',progress=explicit),'flow_metadata')
            self.assertIs(models.download,downloader)
        self.assertEqual(calls,[('flowhmr',outer),('flow_metadata',outer),('flow_metadata',explicit)])

    def test_downloader_is_restored_on_exception_and_nested_context(self):
        original=models.download
        first=lambda *args,**kwargs:None
        second=lambda *args,**kwargs:None
        with self.assertRaisesRegex(RuntimeError,'fixture failure'):
            with download_progress(first):
                wrapped=models.download
                with download_progress(second):
                    self.assertIsNot(models.download,wrapped)
                self.assertIs(models.download,wrapped)
                raise RuntimeError('fixture failure')
        self.assertIs(models.download,original)


if __name__=='__main__':unittest.main()
