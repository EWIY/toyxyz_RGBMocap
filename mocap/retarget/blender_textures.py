"""Original-size material textures and per-corner UVs, independent of motion."""
import hashlib
import json
import shutil
import uuid
from pathlib import Path

import bpy
import numpy as np

from .file_paths import io_path

CACHE = 'preview-textures-v1'


def preview_material(material):
    color = list(material.diffuse_color) if material else [.65, .65, .65, 1.]
    if not material or not material.use_nodes:
        return None, color, None
    nodes = material.node_tree.nodes
    shader = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    if shader is not None:
        base = shader.inputs['Base Color']
        color = list(base.default_value)
        if base.is_linked:
            texture = base.links[0].from_node
            if texture.type == 'TEX_IMAGE' and texture.image:
                return shader, color, texture.image
    for node in nodes:
        if node.type == 'TEX_IMAGE' and node.image and 'shade' not in node.name.lower():
            if not any(link.to_node.type == 'NORMAL_MAP' for link in node.outputs['Color'].links):
                return shader, color, node.image
    return shader, color, None


def _normal_map(shader, uv):
    if shader is None or uv is None or not shader.inputs['Normal'].is_linked:
        return None, 0.
    node = shader.inputs['Normal'].links[0].from_node
    if node.type != 'NORMAL_MAP' or node.space != 'TANGENT' or node.uv_map not in ('', uv.name):
        return None, 0.
    color, strength = node.inputs['Color'], node.inputs['Strength']
    if not color.is_linked or strength.is_linked or strength.default_value <= 0:
        return None, 0.
    texture = color.links[0].from_node
    if texture.type != 'TEX_IMAGE' or texture.inputs['Vector'].is_linked:
        return None, 0.
    return texture.image, float(strength.default_value)


def _cache_image(image, folder, images, sizes):
    if image is None or not all(image.size):
        return None
    if image.name in images:
        return images[image.name]
    w, h = image.size
    size = w * h * 4
    if size > 256 * 1024**2 or size + sum(w * h * 4 for w, h in sizes.values()) > 512 * 1024**2:
        raise ValueError('Original character textures exceed the 256 MB/image or 512 MB/character preview limit.')
    key = 'image' + str(len(images))
    pixels = np.empty(size, np.float32)
    image.pixels.foreach_get(pixels)
    np.clip(pixels, 0, 1, out=pixels)
    pixels *= 255
    np.save(folder / (key + '.npy'), pixels.reshape(h, w, 4).astype(np.uint8))
    images[image.name] = key
    sizes[key] = [w, h]
    return key


def extract(out):
    out = Path(io_path(out))
    if (out / CACHE / 'manifest.json').is_file():
        return
    temp = out / ('.textures-' + uuid.uuid4().hex)
    temp.mkdir()
    try:
        images, sizes, batches, corners, faces = {}, {}, [], [], []
        offset = 0
        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH':
                continue
            mesh = obj.data
            mesh.calc_loop_triangles()
            uv = mesh.uv_layers.active
            faces.extend([[offset + i for i in t.vertices] for t in mesh.loop_triangles])
            for mi in sorted({t.material_index for t in mesh.loop_triangles}):
                mat = mesh.materials[mi] if mi < len(mesh.materials) else None
                shader, color, texture = preview_material(mat)
                normal, strength = _normal_map(shader, uv)
                key = _cache_image(texture, temp, images, sizes) if uv else None
                normal_key = _cache_image(normal, temp, images, sizes)
                start = len(corners)
                for tri in mesh.loop_triangles:
                    if tri.material_index == mi:
                        for li in tri.loops:
                            corners.append([offset + mesh.loops[li].vertex_index, *(uv.data[li].uv if uv else (0, 0))])
                batch = dict(start=start, count=len(corners)-start, image=key, color=color)
                if normal_key is not None:
                    batch.update(normal=normal_key, normal_strength=strength)
                batches.append(batch)
            offset += len(mesh.vertices)
        faces = np.asarray(faces, np.uint32)
        with np.load(out / 'preview.npz', allow_pickle=False) as asset:
            if len(asset['vertices']) != offset or not np.array_equal(asset['faces'], faces):
                raise ValueError('Stored character geometry differs from the texture source. Reimport the character.')
        np.save(temp / 'corners.npy', np.asarray(corners, np.float32))
        metadata = dict(version=1, vertices=offset, faces_sha256=hashlib.sha256(faces.tobytes()).hexdigest(),
                        batches=batches, images=sizes)
        (temp / 'manifest.json').write_text(json.dumps(metadata), encoding='utf8')
        temp.rename(out / CACHE)
    finally:
        # Only this invocation's temporary directory, never a user asset.
        if temp.exists():
            shutil.rmtree(temp)
