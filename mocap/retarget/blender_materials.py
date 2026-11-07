"""Optional declarative FBX material bindings; no bone or mesh changes."""
import hashlib,json
from pathlib import Path
import bpy

def apply_sidecar(filename):
    path=filename.with_suffix('.materials.json')
    if not path.is_file():return None
    if path.stat().st_size>65536:raise ValueError('Material sidecar is too large.')
    spec=json.loads(path.read_text(encoding='utf-8'))
    if spec['source_sha256']!=hashlib.sha256(filename.read_bytes()).hexdigest():
        raise ValueError('Material sidecar does not match this FBX.')
    materials=spec['materials']
    if not isinstance(materials,dict) or len(materials)>64:raise ValueError('Invalid material bindings.')
    for name,row in materials.items():
        material=bpy.data.materials.get(name)
        if material is None:raise ValueError('Material not present in FBX: '+name)
        color=row.get('color',[1.,1.,1.,1.])
        if len(color)!=4 or not all(isinstance(v,(float,int)) and 0<=v<=1 for v in color):
            raise ValueError('Invalid material colour.')
        material.use_nodes=True;material.diffuse_color=color
        nodes=material.node_tree.nodes;links=material.node_tree.links
        bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        bs.inputs['Base Color'].default_value=color
        for semantic,input_name in (('base_color','Base Color'),('normal','Normal')):
            texture=row.get(semantic)
            if texture is None:continue
            file=(filename.parent/texture['file']).resolve()
            if not file.is_relative_to(filename.parent.resolve()) or not file.is_file():
                raise ValueError('Material texture must be beside the FBX or in a child folder.')
            if hashlib.sha256(file.read_bytes()).hexdigest()!=texture['sha256']:
                raise ValueError('Material texture hash mismatch.')
            image=bpy.data.images.load(str(file),check_existing=True)
            node=nodes.new('ShaderNodeTexImage');node.image=image
            if semantic=='normal':
                image.colorspace_settings.name='Non-Color'
                normal=nodes.new('ShaderNodeNormalMap')
                links.new(node.outputs['Color'],normal.inputs['Color'])
                links.new(normal.outputs['Normal'],bs.inputs[input_name])
            else:links.new(node.outputs['Color'],bs.inputs[input_name])
    return dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),materials=list(materials))
