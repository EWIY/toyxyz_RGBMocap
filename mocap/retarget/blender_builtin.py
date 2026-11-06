"""Build original contact proxies and armatures; never load a vendor character."""
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

from mocap.builtin_skeletons import definition
from .mapping import A, PARENTS, body_trajectory_root
from .file_paths import io_path, save_blend


def build(out, key):
    spec = definition(key)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    data = bpy.data.armatures.new('RGBMoCap_'+key)
    arm = bpy.data.objects.new('RGBMoCap_'+key, data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in spec['bones']:
        edit = data.edit_bones.new(bone['name'])
        edit.head = Vector(np.asarray(bone['head']) @ A.T)
        edit.tail = Vector(np.asarray(bone['tail']) @ A.T)
    for bone in spec['bones']:
        if bone['parent']:
            data.edit_bones[bone['name']].parent = data.edit_bones[bone['parent']]
    bpy.ops.object.mode_set(mode='OBJECT')
    names = spec['body_names']
    # Analytic box grids provide original sole/palm samples for the existing
    # contact solver. No vendor skin, material, texture or body geometry is used.
    vertices, faces, groups = [], [], []

    def box_grid(low, high, owner, steps):
        start = len(vertices)
        nx, ny, nz = steps
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    p = [low[j]+(high[j]-low[j])*value/(steps[j]-1)
                         for j, value in enumerate((ix, iy, iz))]
                    vertices.append((np.asarray(p) @ A.T).tolist())
                    groups.append(owner)
        def at(x, y, z):
            return start+(x*ny+y)*nz+z
        for y in (0, ny-1):
            for x in range(nx-1):
                for z in range(nz-1):
                    faces.append((at(x,y,z), at(x+1,y,z), at(x+1,y,z+1), at(x,y,z+1)))
        for x in (0, nx-1):
            for y in range(ny-1):
                for z in range(nz-1):
                    faces.append((at(x,y,z), at(x,y+1,z), at(x,y+1,z+1), at(x,y,z+1)))
        for z in (0, nz-1):
            for x in range(nx-1):
                for y in range(ny-1):
                    faces.append((at(x,y,z), at(x+1,y,z), at(x+1,y+1,z), at(x,y+1,z)))

    for side, sign in ((0, 1), (1, -1)):
        x = sign*.10
        box_grid((x-.045, 0, -.06), (x+.045, .065, .25), names[7+side], (4, 2, 6))
        x0, x1 = sorted((sign*.755, sign*.825))
        box_grid((x0, 1.43, -.03), (x1, 1.47, .03), names[20+side], (3, 2, 3))
    mesh = bpy.data.meshes.new('OriginalContactProxy')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    proxy = bpy.data.objects.new('OriginalContactProxy', mesh)
    bpy.context.collection.objects.link(proxy)
    proxy.parent = arm
    for name in sorted(set(groups)):
        proxy.vertex_groups.new(name=name).add([i for i,g in enumerate(groups) if g == name], 1., 'REPLACE')
    proxy.modifiers.new('Armature', 'ARMATURE').object = arm
    rest = np.asarray([next(b['head'] for b in spec['bones'] if b['name'] == name) for name in names])
    rig = dict(kind='mixamo', armature=arm.name, semantic={},
               trajectory_root=body_trajectory_root({b.name:b.parent.name if b.parent else None for b in data.bones}, names),
               bones=[dict(name=b.name,parent=b.parent.name if b.parent else None) for b in data.bones],
               meshes=[dict(name=proxy.name,vertices=len(vertices))],
               builtin=dict(key=key,version=spec['version'],vendor_asset=False), finger_mapping=spec['finger_mapping'])
    out = Path(out)
    Path(io_path(out)).mkdir(parents=True, exist_ok=True)
    Path(io_path(out/'mixamo-rig.json')).write_text(json.dumps(rig,indent=2),encoding='utf-8')
    np.savez(io_path(out/'mixamo-canonical.npz'),rest=rest,names=names,parents=PARENTS)
    from .blender_geometry import register
    register(out,'mixamo',rig,arm,names,rest)
    save_blend(out/'mixamo-rest.blend')
    metadata=dict(kind='mixamo',name='RGBMoCap '+key+' compatible template',
                  vertices=len(vertices),bones=len(data.bones),builtin=rig['builtin'])
    for name in ('import.json','complete.json'):
        Path(io_path(out/name)).write_text(json.dumps(metadata,indent=2),encoding='utf-8')
