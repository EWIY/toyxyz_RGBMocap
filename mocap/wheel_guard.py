"""Keep the mouse wheel from editing spin boxes and drop-downs on hover.

Qt lets spin boxes and closed drop-downs consume wheel-notches, so scrolling a
long sidebar can silently change the model, floor height or pelvis offset. This
application-wide filter forwards the notch to the enclosing scroll area instead:

- closed QComboBox: never changes by wheel, click it to open the popup (inside
  the popup the wheel still scrolls the item list);
- QAbstractSpinBox: only changes while it has focus (click it first).
"""

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractScrollArea, QAbstractSpinBox, QComboBox


class WheelGuard(QObject):
    def _forward_to_scroll_area(self, widget, event) -> bool:
        area = widget.parentWidget()
        while area is not None and not isinstance(area, QAbstractScrollArea):
            area = area.parentWidget()
        if area is None:
            return False
        delta = event.angleDelta().y() or event.angleDelta().x()
        if delta:
            bar = area.verticalScrollBar()
            bar.setValue(bar.value() - int(delta * 0.5))
        return True

    def eventFilter(self, obj, event):
        if event.type() != QEvent.Wheel:
            return False
        if isinstance(obj, QComboBox):
            view = obj.view()
            if view is not None and view.isVisible():
                return False
            self._forward_to_scroll_area(obj, event)
            return True
        if isinstance(obj, QAbstractSpinBox) and not obj.hasFocus():
            self._forward_to_scroll_area(obj, event)
            return True
        return False


def install(app):
    guard = WheelGuard(app)
    app.installEventFilter(guard)
    app._wheel_guard = guard
    return guard
