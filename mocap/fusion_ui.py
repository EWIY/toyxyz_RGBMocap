"""Small optional model page; no inference imports in the desktop."""
from .i18n import t as _tr
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QCheckBox
from PySide6.QtCore import Qt
from .fusion import options, REGIONS


def add_page(window):
    page = QWidget()
    page.setProperty('motion_tool', 'fusion')
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignTop)
    label = QLabel(_tr('GVHMR guidance weight'))
    label.setWordWrap(True)
    layout.addWidget(label)
    window.fusion_weight = QDoubleSpinBox()
    window.fusion_weight.setRange(0, 100)
    window.fusion_weight.setDecimals(0)
    window.fusion_weight.setSingleStep(5)
    window.fusion_weight.setSuffix(' %')
    window.fusion_weight.setValue(100)
    layout.addWidget(window.fusion_weight)
    layout.addWidget(QLabel(_tr('Guided bones')))
    window.fusion_regions = {}
    for key, text in (('torso', 'Torso (3 spine joints)'),
                      ('neck', 'Neck'), ('head', 'Head')):
        box = QCheckBox(text)
        box.setChecked(True)
        window.fusion_regions[key] = box
        layout.addWidget(box)
    note = QLabel(_tr('0% keeps FlowHMR; 100% follows GVHMR on selected bones. Root motion, legs and local arm motion stay with FlowHMR. '
                   'Reconstruct 3D computes missing captures and saves a separate fusion result. Weight and region edits reuse the captures.'))
    note.setWordWrap(True)
    note.setObjectName('muted')
    layout.addWidget(note)
    window.model_pages.addWidget(page)
    window.fusion_weight.valueChanged.connect(lambda: changed(window))
    for box in window.fusion_regions.values():
        box.toggled.connect(lambda: changed(window))


def selected(window):
    return options(dict(weight=window.fusion_weight.value()/100,
                        regions=[r for r in REGIONS if window.fusion_regions[r].isChecked()]))


def restore(window, value):
    value = options(value)
    for control, setting in [(window.fusion_weight, value['weight']*100),
                             *[(window.fusion_regions[r], r in value['regions']) for r in REGIONS]]:
        previous = control.blockSignals(True)
        if isinstance(control, QDoubleSpinBox):
            control.setValue(setting)
        else:
            control.setChecked(setting)
        control.blockSignals(previous)


def changed(window):
    if getattr(window, 'busy', False) or window.model_choice.currentData() != 'fusion':
        return
    from .storage import atomic_json
    from .people_store import root_for
    import json
    if window.project is not None:
        root = root_for(window.project)
        path = root/'project.json'
        state = json.loads(path.read_text(encoding='utf-8'))
        state['fusion_options'] = selected(window)
        atomic_json(path, state)
    window.status.setText(_tr('Fusion settings changed. Reconstruct 3D to update; cached captures will be reused.'))
    window.update_readiness()
