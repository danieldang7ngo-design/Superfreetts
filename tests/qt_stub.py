"""A tiny, dependency-free Qt stand-in for UI smoke tests.

The real suite mocks ``aqt`` with :mod:`unittest.mock`, which is fine for pure
logic but useless for widgets: every call returns another ``MagicMock``, so a
combo box never has items, a checkbox never reports a state, and the first
``if widget.currentIndex() > 1`` comparison raises ``TypeError``.

This module provides just enough of the Qt widget API to build the add-on's
dialogs for real: widgets keep text/checked/enabled state, layouts keep their
children, combo boxes keep their item list and emit ``currentIndexChanged`` the
way Qt does (only when the index actually changes), and timers fire
synchronously so debounce paths are exercised.

Install it with ``install(monkeypatch)``; it swaps ``aqt.qt`` for the fake
namespace for the duration of the test.
"""

from __future__ import annotations

import inspect
import sys
import types


_SEPARATOR = "\u2500\u2500\u2500"


# --------------------------------------------------------------------------- #
# primitives
# --------------------------------------------------------------------------- #


class _Namespace:
    """Recursive attribute bag used for Qt's nested enums (``Qt.AlignTop``)."""

    def __init__(self, name="<ns>"):
        self._name = name

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        return _Namespace(f"{self._name}.{item}")

    def __call__(self, *args, **kwargs):
        return _Namespace(self._name)

    def __int__(self):
        return 0

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, _Namespace) and other._name == self._name

    def __hash__(self):
        return hash(self._name)

    def __repr__(self):
        return f"<{self._name}>"


def _call_slot(slot, args, kwargs):
    """Call ``slot`` the way PyQt does: pass only as many args as it accepts."""
    try:
        signature = inspect.signature(slot)
    except (TypeError, ValueError):
        slot(*args, **kwargs)
        return
    parameters = list(signature.parameters.values())
    if any(p.kind == p.VAR_POSITIONAL for p in parameters):
        slot(*args, **kwargs)
        return
    positional = [
        p for p in parameters if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    if len(positional) < len(args):
        args = args[: len(positional)]
    slot(*args, **kwargs)


class Signal:
    def __init__(self, name="signal"):
        self._name = name
        self._slots = []

    def connect(self, slot, *args, **kwargs):
        self._slots.append(slot)

    def disconnect(self, slot=None):
        if slot is None:
            self._slots.clear()
        elif slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        for slot in list(self._slots):
            _call_slot(slot, args, kwargs)

    def __len__(self):
        return len(self._slots)


class _Meta(type):
    """Lets ``SomeWidget.InsertPolicy.NoInsert`` work without declaring enums."""

    def __getattr__(cls, name):
        if name.startswith("__"):
            raise AttributeError(name)
        value = _Namespace(f"{cls.__name__}.{name}")
        setattr(cls, name, value)
        return value


class _Style:
    def unpolish(self, *_args, **_kwargs):
        return None

    def polish(self, *_args, **_kwargs):
        return None


class Font(metaclass=_Meta):
    def __init__(self, *args, **kwargs):
        self._point_size = 9
        self._pixel_size = 12
        self._bold = False
        self._italic = False
        self._weight = None
        self._family = ""

    def setPointSize(self, value):
        self._point_size = value

    def pointSize(self):
        return self._point_size

    def setPixelSize(self, value):
        self._pixel_size = value

    def pixelSize(self):
        return self._pixel_size

    def setBold(self, value):
        self._bold = bool(value)

    def bold(self):
        return self._bold

    def setItalic(self, value):
        self._italic = bool(value)

    def italic(self):
        return self._italic

    def setWeight(self, value):
        self._weight = value

    def weight(self):
        return self._weight

    def setFamily(self, value):
        self._family = value

    def setUnderline(self, value):
        return None


class LayoutItem:
    def __init__(self, widget=None, layout=None):
        self._widget = widget
        self._layout = layout

    def widget(self):
        return self._widget

    def layout(self):
        return self._layout


class Layout(metaclass=_Meta):
    def __init__(self, parent=None):
        self._items = []
        self._parent = None
        self.spacing = 0
        self.margins = (0, 0, 0, 0)
        if parent is not None:
            parent.setLayout(self)

    # -- structure
    def addWidget(self, widget, *args, **kwargs):
        self._items.append(LayoutItem(widget=widget))
        if widget is not None:
            widget._owner_layout = self

    def addLayout(self, layout, *args, **kwargs):
        self._items.append(LayoutItem(layout=layout))

    def addStretch(self, *args, **kwargs):
        self._items.append(LayoutItem())

    def addSpacing(self, *args, **kwargs):
        self._items.append(LayoutItem())

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        return self.itemAt(index)

    def widgets(self):
        return [item.widget() for item in self._items if item.widget() is not None]

    def removeWidget(self, widget):
        self._items = [item for item in self._items if item.widget() is not widget]

    # -- styling no-ops
    def setContentsMargins(self, *args):
        self.margins = args

    def setSpacing(self, value):
        self.spacing = value

    def setColumnStretch(self, *args):
        return None

    def setRowStretch(self, *args):
        return None

    def setColumnMinimumWidth(self, *args):
        return None

    def setAlignment(self, *args):
        return None

    def setSizeConstraint(self, *args):
        return None

    def insertWidget(self, index, widget):
        self._items.insert(index, LayoutItem(widget=widget))

    def __getattr__(self, name):
        if name.startswith("set") or name.startswith("add"):
            def _noop(*args, **kwargs):
                return None

            return _noop
        raise AttributeError(name)


class Widget(metaclass=_Meta):
    """Base stand-in for ``QWidget`` and friends."""

    def __init__(self, *args, **kwargs):
        text = args[0] if args and isinstance(args[0], str) else ""
        self._text = text
        self._visible = True
        self._enabled = True
        self._checked = False
        self._object_name = ""
        self._properties = {}
        self._style_sheet = ""
        self._tooltip = ""
        self._layout = None
        self._parent = None
        self._font = Font()
        self._minimum = (0, 0)
        self._maximum = (16777215, 16777215)
        self._size = (0, 0)
        self._calls = []
        self.clicked = Signal("clicked")
        self.pressed = Signal("pressed")
        self.released = Signal("released")
        self.toggled = Signal("toggled")
        self.stateChanged = Signal("stateChanged")

    # -- generic recording fallback for forgotten setters
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name.startswith(("set", "add", "insert", "ensure", "install", "apply")):
            def _noop(*args, **kwargs):
                self._calls.append(name)
                return None

            return _noop
        raise AttributeError(name)

    # -- text
    def text(self):
        return self._text

    def setText(self, value):
        self._text = "" if value is None else str(value)

    def setObjectName(self, value):
        self._object_name = value

    def objectName(self):
        return self._object_name

    def setProperty(self, key, value):
        self._properties[key] = value

    def property(self, key):
        return self._properties.get(key)

    def setStyleSheet(self, value):
        self._style_sheet = value

    def styleSheet(self):
        return self._style_sheet

    def setToolTip(self, value):
        self._tooltip = value

    def toolTip(self):
        return self._tooltip

    def style(self):
        return _Style()

    def font(self):
        return self._font

    def setFont(self, font):
        self._font = font

    # -- state
    def setVisible(self, value):
        self._visible = bool(value)

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def isVisible(self):
        return self._visible

    def isVisibleTo(self, _parent=None):
        return self._visible

    def setEnabled(self, value):
        self._enabled = bool(value)

    def setDisabled(self, value):
        self._enabled = not bool(value)

    def isEnabled(self):
        return self._enabled

    def setCheckable(self, value):
        self._checkable = bool(value)

    def isCheckable(self):
        return getattr(self, "_checkable", False)

    def setChecked(self, value):
        value = bool(value)
        if value == self._checked:
            return
        self._checked = value
        self.stateChanged.emit(2 if value else 0)
        self.toggled.emit(value)

    def isChecked(self):
        return self._checked

    def setTristate(self, *_args):
        return None

    # -- geometry
    def setMinimumWidth(self, value):
        self._minimum = (value, self._minimum[1])

    def setMinimumHeight(self, value):
        self._minimum = (self._minimum[0], value)

    def setMaximumWidth(self, value):
        self._maximum = (value, self._maximum[1])

    def setMaximumHeight(self, value):
        self._maximum = (self._maximum[0], value)

    def minimumWidth(self):
        return self._minimum[0]

    def minimumHeight(self):
        return self._minimum[1]

    def setFixedWidth(self, value):
        self.setMinimumWidth(value)
        self.setMaximumWidth(value)

    def setFixedHeight(self, value):
        self.setMinimumHeight(value)
        self.setMaximumHeight(value)

    def setMinimumSize(self, width, height):
        self._minimum = (width, height)

    def resize(self, width, height):
        self._size = (width, height)

    def size(self):
        return _Namespace("QSize")

    def width(self):
        return self._size[0]

    def height(self):
        return self._size[1]

    def rect(self):
        return _Namespace("QRect")

    def setSizePolicy(self, *args):
        return None

    def sizePolicy(self):
        return _Namespace("QSizePolicy")

    def setCursor(self, *_args):
        return None

    def setContentsMargins(self, *args):
        return None

    def setLayout(self, layout):
        self._layout = layout
        if layout is not None:
            layout._parent = self

    def layout(self):
        return self._layout

    def setParent(self, parent):
        self._parent = parent
        if parent is None:
            owner = getattr(self, "_owner_layout", None)
            if owner is not None:
                owner.removeWidget(self)
                self._owner_layout = None

    def parent(self):
        return self._parent

    def setWindowTitle(self, value):
        self._text = value

    def windowTitle(self):
        return self._text

    def setUpdatesEnabled(self, *_args):
        return None

    def update(self):
        return None

    def repaint(self):
        return None

    def children(self):
        return []

    def findChildren(self, *_args):
        return []

    def setFocusPolicy(self, *_args):
        return None

    def setAttribute(self, *_args):
        return None

    def close(self):
        self._visible = False


class Label(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkActivated = Signal("linkActivated")

    def setTextFormat(self, *_args):
        return None

    def setPixmap(self, *_args):
        return None

    def setScaledContents(self, *_args):
        return None

    def setOpenExternalLinks(self, *_args):
        return None

    def setAlignment(self, *_args):
        return None

    def setWordWrap(self, value):
        self._word_wrap = bool(value)

    def wordWrap(self):
        return getattr(self, "_word_wrap", False)

    def setMargin(self, value):
        self._margin = value

    def setIndent(self, value):
        self._indent = value

    def setTextInteractionFlags(self, *_args):
        return None


class PushButton(Widget):
    pass


class ToolButton(Widget):
    def setArrowType(self, value):
        self._arrow_type = value

    def arrowType(self):
        return getattr(self, "_arrow_type", None)

    def setToolButtonStyle(self, *_args):
        return None

    def setAutoRaise(self, *_args):
        return None

    def setFlat(self, value):
        self._flat = bool(value)

    def setIcon(self, *_args):
        return None

    def setIconSize(self, *_args):
        return None

    def setText(self, value):
        self._text = value


class CheckBox(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RadioButton(Widget):
    """Radio buttons are exclusive inside their button group, like Qt's."""

    _group = None

    def setChecked(self, value):
        if value and self._group is not None:
            for other in self._group._buttons:
                if other is not self and other._checked:
                    other._checked = False
                    other.toggled.emit(False)
        super().setChecked(value)


class LineEdit(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged = Signal("textChanged")
        self.editingFinished = Signal("editingFinished")
        self.returnPressed = Signal("returnPressed")

    def setText(self, value):
        value = "" if value is None else str(value)
        changed = value != self._text
        self._text = value
        if changed:
            self.textChanged.emit(value)

    def text(self):
        return self._text

    def setPlaceholderText(self, value):
        self._placeholder = value

    def placeholderText(self):
        return getattr(self, "_placeholder", "")

    def setEchoMode(self, *_args):
        return None

    def setReadOnly(self, value):
        self._read_only = bool(value)

    def setClearButtonEnabled(self, *_args):
        return None

    def lineEdit(self):
        return self

    def setValidator(self, *_args):
        return None


class PlainTextEdit(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged = Signal("textChanged")

    def setPlainText(self, value):
        self._text = "" if value is None else str(value)
        self.textChanged.emit()

    def toPlainText(self):
        return self._text

    def setTabChangesFocus(self, *_args):
        return None


class SpinBox(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valueChanged = Signal("valueChanged")
        self._value = 0
        self._range = (0, 99)

    def setRange(self, minimum, maximum):
        self._range = (minimum, maximum)

    def minimum(self):
        return self._range[0]

    def maximum(self):
        return self._range[1]

    def setValue(self, value):
        if isinstance(self._value, int):
            value = int(value)
        if value == self._value:
            return
        self._value = value
        self.valueChanged.emit(value)

    def value(self):
        return self._value

    def setSingleStep(self, *_args):
        return None

    def setSuffix(self, *_args):
        return None

    def setDecimals(self, *_args):
        return None


class DoubleSpinBox(SpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0.0
        self._range = (0.0, 1.0)

    def setValue(self, value):
        value = float(value)
        if value == self._value:
            return
        self._value = value
        self.valueChanged.emit(value)


class Completer:
    def setFilterMode(self, *_args):
        return None

    def setCaseSensitivity(self, *_args):
        return None

    def setCompletionMode(self, *_args):
        return None


class ComboBox(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items = []
        self._index = -1
        self._editable = False
        self.currentIndexChanged = Signal("currentIndexChanged")
        self.currentTextChanged = Signal("currentTextChanged")
        self.activated = Signal("activated")
        self.editTextChanged = Signal("editTextChanged")

    # -- population
    def addItem(self, text, _data=None):
        self._items.append(str(text))
        if self._index < 0:
            self._set_index(0)

    def addItems(self, items):
        for item in items:
            self._items.append(str(item))
        if self._index < 0 and self._items:
            self._set_index(0)

    def insertItem(self, index, text):
        self._items.insert(index, str(text))

    def insertSeparator(self, index):
        # Qt inserts a real (unselectable) row, so item indexes shift by one.
        self._items.insert(index, _SEPARATOR)

    def clear(self):
        self._items = []
        self._set_index(-1)

    def count(self):
        return len(self._items)

    def itemText(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return ""

    def items(self):
        return list(self._items)

    # -- selection
    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        self._set_index(index)

    def _set_index(self, index):
        old_index, old_text = self._index, self.currentText()
        self._index = index
        if old_index != index:
            self.currentIndexChanged.emit(index)
        new_text = self.currentText()
        if new_text != old_text:
            self.currentTextChanged.emit(new_text)

    def currentText(self):
        if 0 <= self._index < len(self._items):
            return self._items[self._index]
        return self._text if self._editable else ""

    def setCurrentText(self, text):
        text = "" if text is None else str(text)
        found = self.findText(text)
        if found >= 0:
            self._set_index(found)
            return
        old_text = self.currentText()
        self._text = text
        if text != old_text:
            self.currentTextChanged.emit(text)

    def findText(self, text):
        try:
            return self._items.index(text)
        except ValueError:
            return -1

    def setEditable(self, value):
        self._editable = bool(value)

    def isEditable(self):
        return self._editable

    def setInsertPolicy(self, *_args):
        return None

    def setMaxVisibleItems(self, *_args):
        return None

    def completer(self):
        return Completer()

    def view(self):
        return Widget()

    def lineEdit(self):
        return LineEdit()

    def setCurrentIndexSilently(self, index):
        self._index = index


class ButtonGroup(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buttons = []

    def addButton(self, button):
        self._buttons.append(button)
        button._group = self

    def buttons(self):
        return list(self._buttons)

    def checkedButton(self):
        for button in self._buttons:
            if button.isChecked():
                return button
        return None

    def checkedId(self):
        return -1


class StackedWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pages = []
        self._index = -1
        self.currentChanged = Signal("currentChanged")

    def addWidget(self, widget):
        self._pages.append(widget)
        if self._index < 0:
            self._index = 0
        return len(self._pages) - 1

    def count(self):
        return len(self._pages)

    def setCurrentIndex(self, index):
        self._index = index
        self.currentChanged.emit(index)

    def currentIndex(self):
        return self._index

    def currentWidget(self):
        if 0 <= self._index < len(self._pages):
            return self._pages[self._index]
        return None

    def setCurrentWidget(self, widget):
        self._index = self._pages.index(widget)


class ScrollArea(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._widget = None

    def setWidget(self, widget):
        self._widget = widget

    def widget(self):
        return self._widget

    def setWidgetResizable(self, value):
        self._resizable = bool(value)

    def setFrameShape(self, *_args):
        return None

    def setHorizontalScrollBarPolicy(self, *_args):
        return None

    def setVerticalScrollBarPolicy(self, *_args):
        return None

    def ensureWidgetVisible(self, *_args):
        return None

    def setAlignment(self, *_args):
        return None


class GroupBox(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setTitle(self, value):
        self._text = value

    def title(self):
        return self._text


class Frame(Widget):
    pass


class Dialog(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.finished = Signal("finished")
        self.accepted = Signal("accepted")
        self.rejected = Signal("rejected")
        self._accepted = False

    def exec(self):
        return 0

    def exec_(self):
        return 0

    def open(self):
        return None

    def accept(self):
        self._accepted = True
        self.accepted.emit()
        self.finished.emit(1)

    def reject(self):
        self._accepted = False
        self.rejected.emit()
        self.finished.emit(0)

    def setModal(self, *_args):
        return None

    def setWindowFlag(self, *_args):
        return None

    def setWindowFlags(self, *_args):
        return None


class Timer(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.timeout = Signal("timeout")
        self._active = False
        self._single_shot = False

    def setSingleShot(self, value):
        self._single_shot = bool(value)

    def isSingleShot(self):
        return self._single_shot

    def setInterval(self, value):
        self._interval = value

    def start(self, *_args):
        self._active = True
        self.timeout.emit()

    def stop(self):
        self._active = False

    def isActive(self):
        return self._active

    @staticmethod
    def singleShot(_msec, callback):
        callback()


class KeySequence(metaclass=_Meta):
    def __init__(self, value=None):
        self._value = value or ""

    def toString(self, *_args):
        return self._value

    def isEmpty(self):
        return not self._value


class KeySequenceEdit(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keySequenceChanged = Signal("keySequenceChanged")
        self._sequence = KeySequence()

    def setKeySequence(self, sequence):
        self._sequence = sequence

    def keySequence(self):
        return self._sequence

    def clear(self):
        self._sequence = KeySequence()
        self.keySequenceChanged.emit(self._sequence)


class Pixmap(metaclass=_Meta):
    def __init__(self, *_args, **_kwargs):
        pass

    def width(self):
        return 0

    def height(self):
        return 0

    def isNull(self):
        return False


class Icon(metaclass=_Meta):
    def __init__(self, *_args, **_kwargs):
        pass


class Painter(metaclass=_Meta):
    RenderHint = _Namespace("QPainter.RenderHint")

    def __init__(self, *_args, **_kwargs):
        pass

    def setRenderHint(self, *_args):
        return None

    def drawPixmap(self, *_args):
        return None


class Application(metaclass=_Meta):
    def __init__(self, *_args, **_kwargs):
        pass

    @staticmethod
    def instance():
        return None


class FileDialog(metaclass=_Meta):
    @staticmethod
    def getOpenFileName(*_args, **_kwargs):
        return ("", "")

    @staticmethod
    def getExistingDirectory(*_args, **_kwargs):
        return ""

    @staticmethod
    def getSaveFileName(*_args, **_kwargs):
        return ("", "")


class MessageBox(metaclass=_Meta):
    @staticmethod
    def information(*_args, **_kwargs):
        return 0

    @staticmethod
    def warning(*_args, **_kwargs):
        return 0

    @staticmethod
    def critical(*_args, **_kwargs):
        return 0

    @staticmethod
    def question(*_args, **_kwargs):
        return 0

    def setText(self, *_args):
        return None

    def exec(self):
        return 0


class Action(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.triggered = Signal("triggered")
        self.setShortcut = lambda *_a, **_k: None


class Menu(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aboutToShow = Signal("aboutToShow")

    def addAction(self, *_args):
        return Action()

    def addMenu(self, *_args):
        return Menu()

    def exec(self, *_args):
        return None


class AbstractItemModel(metaclass=_Meta):
    """Stand-in for QAbstractTableModel/QAbstractListModel."""

    def __init__(self, *args, **kwargs):
        self.layoutChanged = Signal("layoutChanged")
        self.dataChanged = Signal("dataChanged")
        self.modelReset = Signal("modelReset")

    def beginResetModel(self):
        return None

    def endResetModel(self):
        return None

    def createIndex(self, row, column):
        return _Namespace("QModelIndex")

    def rowCount(self, _parent=None):
        return 0

    def columnCount(self, _parent=None):
        return 0

    def index(self, row, column, _parent=None):
        return _Namespace("QModelIndex")


class QObject(metaclass=_Meta):
    def __init__(self, *_args, **_kwargs):
        self._object_name = ""

    def setObjectName(self, value):
        self._object_name = value

    def objectName(self):
        return self._object_name


class TabWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tabs = []
        self._index = -1
        self.currentChanged = Signal("currentChanged")

    def addTab(self, widget, label):
        self._tabs.append((widget, label))
        if self._index < 0:
            self._index = 0
        return len(self._tabs) - 1

    def insertTab(self, index, widget, label):
        self._tabs.insert(index, (widget, label))
        return index

    def count(self):
        return len(self._tabs)

    def tabText(self, index):
        return self._tabs[index][1]

    def setTabText(self, index, label):
        widget, _ = self._tabs[index]
        self._tabs[index] = (widget, label)

    def widget(self, index):
        return self._tabs[index][0]

    def setCurrentIndex(self, index):
        self._index = index
        self.currentChanged.emit(index)

    def currentIndex(self):
        return self._index

    def setTabEnabled(self, *_args):
        return None

    def removeTab(self, index):
        self._tabs.pop(index)


class SelectionModel:
    def __init__(self, indexes=None):
        self._indexes = list(indexes or [])

    def selectedRows(self, *_args):
        return []

    def selectedIndexes(self):
        return list(self._indexes)

    def selectedItems(self):
        return []

    def hasSelection(self):
        return False

    def clearSelection(self):
        return None


class GenericTable(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rows = 0
        self._columns = 0

    def setRowCount(self, value):
        self._rows = value

    def rowCount(self):
        return self._rows

    def setColumnCount(self, value):
        self._columns = value

    def columnCount(self):
        return self._columns

    def setHorizontalHeaderLabels(self, *_args):
        return None

    def setCellWidget(self, *_args):
        return None

    def setItem(self, *_args):
        return None

    def horizontalHeader(self):
        return Widget()

    def verticalHeader(self):
        return Widget()

    def setSelectionBehavior(self, *_args):
        return None

    def setEditTriggers(self, *_args):
        return None

    def setAlternatingRowColors(self, *_args):
        return None

    def selectionModel(self):
        return SelectionModel(getattr(self, "_selection_indexes", []))

    def model(self):
        return getattr(self, "_model", None)

    def setModel(self, model):
        self._model = model


class TableItem(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setFlags(self, *_args):
        return None


# --------------------------------------------------------------------------- #
# namespace assembly
# --------------------------------------------------------------------------- #

_EXPLICIT = {
    "QWidget": Widget,
    "QDialog": Dialog,
    "QLabel": Label,
    "QPushButton": PushButton,
    "QToolButton": ToolButton,
    "QCheckBox": CheckBox,
    "QRadioButton": RadioButton,
    "QLineEdit": LineEdit,
    "QPlainTextEdit": PlainTextEdit,
    "QTextEdit": PlainTextEdit,
    "QSpinBox": SpinBox,
    "QDoubleSpinBox": DoubleSpinBox,
    "QComboBox": ComboBox,
    "QButtonGroup": ButtonGroup,
    "QStackedWidget": StackedWidget,
    "QScrollArea": ScrollArea,
    "QGroupBox": GroupBox,
    "QFrame": Frame,
    "QVBoxLayout": Layout,
    "QHBoxLayout": Layout,
    "QGridLayout": Layout,
    "QFormLayout": Layout,
    "QTimer": Timer,
    "QKeySequence": KeySequence,
    "QKeySequenceEdit": KeySequenceEdit,
    "QPixmap": Pixmap,
    "QIcon": Icon,
    "QPainter": Painter,
    "QFont": Font,
    "QApplication": Application,
    "QFileDialog": FileDialog,
    "QMessageBox": MessageBox,
    "QAction": Action,
    "QMenu": Menu,
    "QObject": QObject,
    "QTableWidget": GenericTable,
    "QTableView": GenericTable,
    "QTreeWidget": GenericTable,
    "QListWidget": GenericTable,
    "QTabWidget": TabWidget,
    "QTableWidgetItem": TableItem,
    "QListWidgetItem": TableItem,
    "QTreeWidgetItem": TableItem,
    "QAbstractTableModel": AbstractItemModel,
    "QAbstractListModel": AbstractItemModel,
    # friendly aliases (useful in assertions: qt.LineEdit, qt.CheckBox, ...)
    "Widget": Widget,
    "Dialog": Dialog,
    "Label": Label,
    "PushButton": PushButton,
    "ToolButton": ToolButton,
    "CheckBox": CheckBox,
    "RadioButton": RadioButton,
    "LineEdit": LineEdit,
    "PlainTextEdit": PlainTextEdit,
    "SpinBox": SpinBox,
    "DoubleSpinBox": DoubleSpinBox,
    "ComboBox": ComboBox,
    "ButtonGroup": ButtonGroup,
    "StackedWidget": StackedWidget,
    "ScrollArea": ScrollArea,
    "GroupBox": GroupBox,
    "Frame": Frame,
    "Layout": Layout,
    "Timer": Timer,
    "KeySequenceEdit": KeySequenceEdit,
    "TabWidget": TabWidget,
    "SelectionModel": SelectionModel,
}


class QtNamespace(types.ModuleType):
    def __init__(self):
        super().__init__("aqt.qt")
        self.Qt = _Namespace("Qt")
        for name in (
            "QSizePolicy",
            "QEvent",
            "QVariant",
            "QHeaderView",
            "QAbstractItemView",
            "QDialogButtonBox",
            "QSize",
            "QRect",
            "QPoint",
            "QRectF",
            "QPointF",
            "QStyle",
            "QPalette",
        ):
            setattr(self, name, _Meta(name, (), {}))
        for name, klass in _EXPLICIT.items():
            setattr(self, name, klass)

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        # Unknown Qt class: synthesise a widget stub so modules that touch it
        # keep working (the test asserts on behaviour, not on that widget).
        klass = _Meta(name, (Widget,), {})
        setattr(self, name, klass)
        return klass


def build():
    """Return a fresh fake ``aqt.qt`` module namespace."""
    return QtNamespace()


def _aqt_modules():
    """Every ``aqt`` module object the add-on modules may hold a reference to.

    ``tests/mock_anki.mock_all()`` recreates ``sys.modules['aqt']``, and modules
    that did ``import aqt.qt`` keep the module object that existed at import
    time, so patching only ``sys.modules['aqt']`` misses them once the suite has
    reloaded the mocks.
    """
    found = set()
    current = sys.modules.get("aqt")
    if isinstance(current, types.ModuleType):
        found.add(current)
    for module in list(sys.modules.values()):
        holder = getattr(module, "aqt", None)
        if isinstance(holder, types.ModuleType) and hasattr(holder, "qt"):
            found.add(holder)
    return found


def install(monkeypatch):
    """Swap ``aqt.qt`` for the fake namespace; returns the namespace."""
    namespace = build()
    for aqt_module in _aqt_modules():
        monkeypatch.setattr(aqt_module, "qt", namespace, raising=False)

    # ``gui_utils.NonAliasedImage`` was declared as a QWidget subclass when the
    # module was imported (against the MagicMock Qt), so its methods would not
    # come from the fake widget.  Rebind it to the fake base class.
    try:
        from superfreetts_addon import gui_utils

        monkeypatch.setattr(gui_utils, "NonAliasedImage", namespace.QWidget, raising=False)
    except Exception:  # pragma: no cover - gui_utils always importable here
        pass
    return namespace


def is_installed():
    import aqt

    return isinstance(aqt.qt, QtNamespace)


def _self_check():  # pragma: no cover - manual helper
    combo = ComboBox()
    seen = []
    combo.currentIndexChanged.connect(lambda index: seen.append(index))
    combo.addItems(["a", "b"])
    combo.setCurrentIndex(1)
    assert combo.currentText() == "b"
    assert seen == [0, 1], seen
    assert sys.version_info >= (3, 8)
    print("qt_stub ok")


if __name__ == "__main__":  # pragma: no cover
    _self_check()
