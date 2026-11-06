"""YOLOX-X person detection trained on HumanArt (COCO-person + art data).

The default YOLOv8x detector is trained on COCO photographs and often misses
stylised or armored humanoids.  This optional detector reuses the ONNX model
published for RTMPose (`yolox_x_8xb8-300e_humanart`) and follows the YOLOX
decoder used by OpenMMLab's ONNX SDK. The pinned ONNX Runtime uses CUDA when
available and falls back to CPU. Weights are acquired separately in Model Manager.
"""

import os
from pathlib import Path

import cv2
import numpy as np

from .paths import ROOT

MODEL_PATH = ROOT / "models" / "yolox" / "yolox_x_humanart.onnx"


def _nms(boxes: np.ndarray, scores: np.ndarray, threshold: float) -> list[int]:
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size:
        i = order[0]
        keep.append(int(i))
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-9)
        order = order[np.where(iou <= threshold)[0] + 1]
    return keep


class HumanArtDetector:
    def __init__(self, model_path: Path | str | None = None, input_size: int = 640,
                 score_thr: float = 0.3, nms_thr: float = 0.45):
        path = Path(model_path or MODEL_PATH)
        if not path.is_file():
            raise RuntimeError(
                "YOLOX HumanArt detector is missing: " + str(path) +
                "\nOpen Model Manager and import the supported HumanArt ONNX, or select the default YOLOv8x detector.")
        self._dll_directories = []
        try:
            import torch
            lib = Path(torch.__file__).resolve().parent / "lib"
            if lib.is_dir() and hasattr(os, "add_dll_directory"):
                self._dll_directories.append(os.add_dll_directory(str(lib)))
        except Exception:
            pass
        import onnxruntime as ort
        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.intra_op_num_threads = 4
        providers = []
        if "CUDAExecutionProvider" in ort.get_available_providers():
            providers.append(("CUDAExecutionProvider", {"device_id": 0, "cudnn_conv_algo_search": "HEURISTIC"}))
        providers.append("CPUExecutionProvider")
        try:
            self.session = ort.InferenceSession(str(path), sess_options=options, providers=providers)
            if "CUDAExecutionProvider" not in self.session.get_providers():
                self.session = ort.InferenceSession(str(path), sess_options=options, providers=["CPUExecutionProvider"])
        except Exception:
            self.session = ort.InferenceSession(str(path), sess_options=options, providers=["CPUExecutionProvider"])
        self.providers = self.session.get_providers()
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size
        self.score_thr = score_thr
        self.nms_thr = nms_thr
        self._grids = None

    def _grid(self):
        if self._grids is None:
            grids, strides = [], []
            for stride in (8, 16, 32):
                size = self.input_size // stride
                xv, yv = np.meshgrid(np.arange(size), np.arange(size))
                grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
                grids.append(grid)
                strides.append(np.full((*grid.shape[:2], 1), stride))
            self._grids = (np.concatenate(grids, 1), np.concatenate(strides, 1))
        return self._grids

    def detect(self, image_bgr: np.ndarray, score_thr: float | None = None) -> tuple[np.ndarray, np.ndarray]:
        height, width = image_bgr.shape[:2]
        size = self.input_size
        ratio = min(size / height, size / width)
        resized = cv2.resize(image_bgr, (int(width * ratio), int(height * ratio)), interpolation=cv2.INTER_LINEAR)
        padded = np.full((size, size, 3), 114, dtype=np.uint8)
        padded[:resized.shape[0], :resized.shape[1]] = resized
        blob = padded.transpose(2, 0, 1)[None].astype(np.float32)
        output = self.session.run(None, {self.input_name: blob})[0]
        threshold = self.score_thr if score_thr is None else score_thr
        if output.shape[-1] == 5:
            boxes = output[0, :, :4] / ratio
            scores = output[0, :, 4]
            mask = scores > threshold
            return boxes[mask].astype(np.float32), scores[mask].astype(np.float32)
        grids, strides = self._grid()
        predictions = output.copy()
        predictions[..., :2] = (predictions[..., :2] + grids) * strides
        predictions[..., 2:4] = np.exp(predictions[..., 2:4]) * strides
        pred = predictions[0]
        cx, cy, bw, bh = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
        boxes = np.stack([(cx - bw / 2) / ratio, (cy - bh / 2) / ratio,
                          (cx + bw / 2) / ratio, (cy + bh / 2) / ratio], axis=1)
        scores = pred[:, 4] * pred[:, 5]
        mask = scores > threshold
        boxes, scores = boxes[mask], scores[mask]
        if not len(boxes):
            return np.zeros((0, 4), np.float32), np.zeros((0,), np.float32)
        keep = _nms(boxes, scores, self.nms_thr)
        return boxes[keep].astype(np.float32), scores[keep].astype(np.float32)
