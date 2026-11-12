"""Source-motion export options; existing character exports remain separate."""
from .i18n import t as _tr
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QComboBox,QCheckBox,QLabel,QDialogButtonBox,QDoubleSpinBox,QLayout

class SourceExportDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle(_tr('Export'));self.setMinimumWidth(660)
        self.model=parent.model_choice.currentData() if parent is not None and hasattr(parent,'model_choice') else None
        layout=QVBoxLayout(self);layout.setSizeConstraint(QLayout.SetMinimumSize);layout.setContentsMargins(18,18,18,18);layout.setSpacing(12)
        form=QFormLayout();form.setVerticalSpacing(12);layout.addLayout(form)
        self.format=QComboBox();self.format.addItem(_tr('FBX (.fbx)'), 'fbx');self.format.addItem(_tr('BVH (.bvh)'), 'bvh');self.format.addItem(_tr('Blender project + video (.blend)'), 'blend')
        form.addRow(_tr('Format'), self.format)
        self.profile=QComboBox();self.profile.addItem(_tr('Generic / Blender'), 'generic')
        if self.model != 'gemx':
            self.profile.addItem(_tr('3ds Max Biped'), 'biped')
        self.profile.setToolTip(_tr('Generic / Blender keeps anatomical names and original rotation orders. 3ds Max Biped uses Character Studio names and uniform ZXY rotations. Both keep metre units and Y up.'))
        self.profile_label=QLabel(_tr('BVH profile'));form.addRow(self.profile_label,self.profile)
        self.fbx_compatibility=QCheckBox('FBX Compatibility (Maya)')
        self.fbx_compatibility.setToolTip('Use the included Blender runtime to write an FBX for Maya and Blender.')
        layout.addWidget(self.fbx_compatibility)
        self.whole_scene=QCheckBox(_tr('MAMMA whole scene: body meshes and all cameras'));layout.addWidget(self.whole_scene)
        self.whole_scene.setToolTip(_tr('Export checked people, exact animated surfaces, reference skeletons and every calibrated camera/video. Keeps the original timeline. Mesh caches can be large.'))
        self.tpose=QCheckBox(_tr('Add T-pose before motion'));self.tpose.setChecked(False)
        self.tpose.setToolTip(_tr('Insert a T-pose at the first motion frame root position. Original frames shift by one; their poses and timing intervals stay unchanged.'))
        layout.addWidget(self.tpose)
        self.place_at_origin=QCheckBox(_tr('Place at origin'));layout.addWidget(self.place_at_origin)
        self.place_at_origin.setToolTip(_tr("Center each person's first exported frame on world X/Z. Height and travel are preserved. People are centered independently; their relative placement changes."))
        self.symmetric_rest=QCheckBox(_tr('Symmetrical rest pose'));layout.addWidget(self.symmetric_rest)
        self.symmetric_rest.setToolTip(_tr('Use mirrored left/right rest bones with averaged paired lengths and a straight vertical spine. Animation rotations and timing are retained; changed proportions can move hands and feet. Exported files only.'))
        self.animate_camera=QCheckBox(_tr('Export saved camera tracking'));self.animate_camera.setChecked(True);layout.addWidget(self.animate_camera)
        self.background_refine=QCheckBox(_tr('Refine Camera Rotation'));layout.addWidget(self.background_refine)
        from .camera_ui import BACKGROUND_HELP
        self.background_refine.setToolTip(_tr(BACKGROUND_HELP))
        if parent is not None and hasattr(parent,'camera_tools'):self.background_refine.setChecked(parent.camera_tools.background_options().get(self.model,False))
        self.translation_scale=QDoubleSpinBox();self.translation_scale.setRange(0,100);self.translation_scale.setDecimals(3);self.translation_scale.setValue(1);self.translation_scale.setSingleStep(.1)
        if parent is not None and hasattr(parent,'camera_tools'):self.translation_scale.setValue(parent.camera_tools.scale.value())
        self.translation_scale.setToolTip(_tr('Approximate saved camera movement. 0 fixes the camera center; 1 uses the estimate. This does not change the source animation.'))
        self.scale_label=QLabel(_tr('Camera movement scale'));form.addRow(self.scale_label,self.translation_scale)
        self.note=QLabel();self.note.setWordWrap(True);layout.addWidget(self.note)
        layout.addStretch(1)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(_tr('Continue...'));buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        for signal in (self.format.currentIndexChanged,self.whole_scene.toggled,self.animate_camera.toggled):signal.connect(self.update_format)
        self.update_format()
    def update_format(self):
        fmt=self.format.currentData();blend=fmt=='blend';whole=blend and self.model=='mamma' and self.whole_scene.isChecked()
        self.profile_label.setVisible(fmt=='bvh');self.profile.setVisible(fmt=='bvh')
        self.fbx_compatibility.setVisible(fmt=='fbx')
        self.whole_scene.setVisible(blend and self.model=='mamma');self.tpose.setEnabled(not whole);self.tpose.setVisible(not whole)
        for control in (self.place_at_origin,self.symmetric_rest):control.setVisible(not blend);control.setEnabled(not blend)
        self.animate_camera.setVisible(blend and not whole)
        camera=blend and not whole and self.model in ('flowhmr','exmr')
        self.background_refine.setVisible(camera);self.background_refine.setEnabled(self.animate_camera.isChecked())
        self.scale_label.setVisible(camera);self.translation_scale.setVisible(camera);self.translation_scale.setEnabled(self.animate_camera.isChecked())
        if self.model == 'gemx':
            self.symmetric_rest.hide()
            self.symmetric_rest.setEnabled(False)
            if blend:
                self.tpose.hide()
                self.animate_camera.hide()
            self.note.setText(
                'Exports the native SOMA skeleton, exact animated surface and synchronized video in a new Blender bundle folder. Keep the files together.'
                if blend else
                'Exports the selected SOMA Native77 skeleton and motion at 30 fps. BVH uses metres and Y up. Add T-pose inserts one frame using the native rest pose.'
            )
            self.layout().activate()
            self.adjustSize()
            return
        text=('Creates a new folder containing the .blend, videos and mesh caches. Keep the folder together. Bodies are baked PC2 surfaces; skeletons are separate editable references. No T-pose is inserted.' if whole else
              'Creates a new folder containing the .blend and synchronized video. Keep both together. The video is a camera-view background, not a render background. Saved camera movement is approximate.' if blend else
              'Exports the selected source skeleton. BVH uses metres and Y up. The T-pose is an extra animation frame; it does not replace the character bind pose.')
        self.note.setText(_tr(text))
        self.layout().activate();self.adjustSize()
    def options(self):
        if self.model == 'gemx' and self.format.currentData() == 'blend':
            return dict(format='blend', animate_camera=False)
        fmt=self.format.currentData();whole=fmt=='blend' and self.model=='mamma' and self.whole_scene.isChecked()
        value=dict(format='blend_scene' if whole else fmt,bvh_profile=self.profile.currentData() if fmt=='bvh' else 'generic',prepend_tpose=self.tpose.isChecked() and not whole)
        if fmt=='fbx':value['fbx_compatibility']=self.fbx_compatibility.isChecked()
        value.update(place_at_origin=self.place_at_origin.isChecked() and fmt in ('fbx','bvh'),symmetric_rest=self.model != 'gemx' and self.symmetric_rest.isChecked() and fmt in ('fbx','bvh'))
        if fmt=='blend':value.update(animate_camera=self.animate_camera.isChecked(),background_refine=self.background_refine.isChecked() and self.animate_camera.isChecked() and self.model in ('flowhmr','exmr'),camera_translation_scale=self.translation_scale.value())
        return value
