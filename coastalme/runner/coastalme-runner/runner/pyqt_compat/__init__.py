try:
    from PyQt6.QtCore import Qt, QProcess
    from PyQt6.QtWidgets import (QHeaderView, QStyle, QMessageBox, QAbstractItemView, QDialogButtonBox, QLineEdit,
                                 QSizePolicy)
    from PyQt6.QtGui import QPalette, QKeySequence
    is_qt6 = True
except ImportError:
    from PyQt5.QtCore import Qt, QProcess
    from PyQt5.QtWidgets import (QHeaderView, QStyle, QMessageBox, QAbstractItemView, QDialogButtonBox, QLineEdit,
                                 QSizePolicy)
    from PyQt5.QtGui import QPalette, QKeySequence
    is_qt6 = False


if is_qt6:
    # colours
    QT_RED = Qt.GlobalColor.red
    QT_BLUE = Qt.GlobalColor.blue
    QT_GREEN = Qt.GlobalColor.green
    QT_BLACK = Qt.GlobalColor.black
    QT_WHITE = Qt.GlobalColor.white
    QT_DARK_GREEN = Qt.GlobalColor.darkGreen
    QT_TRANSPARENT = Qt.GlobalColor.transparent
    QT_MAGENTA = Qt.GlobalColor.magenta

    # orientation
    QT_HORIZONTAL = Qt.Orientation.Horizontal
    QT_VERTICAL = Qt.Orientation.Vertical

    # alignment
    QT_ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
    QT_ALIGN_RIGHT = Qt.AlignmentFlag.AlignRight

    # text format
    QT_RICH_TEXT = Qt.TextFormat.RichText

    # window type
    QT_WINDOW_TYPE = Qt.WindowType.Window
    QT_DIALOG_TYPE = Qt.WindowType.Dialog

    # window hint
    QT_WINDOW_CONTEXT_HELP_BUTTON_HINT = Qt.WindowType.WindowContextHelpButtonHint

    # check state
    QT_CHECKED = Qt.CheckState.Checked
    QT_UNCHECKED = Qt.CheckState.Unchecked
    QT_PARTIALLY_CHECKED = Qt.CheckState.PartiallyChecked

    # item data roles
    QT_ITEM_DATA_FOREGROUND_ROLE = Qt.ItemDataRole.ForegroundRole
    QT_ITEM_DATA_DISPLAY_ROLE = Qt.ItemDataRole.DisplayRole

    # item flags
    QT_ITEM_FLAG_NO_ITEM_FLAGS = Qt.ItemFlag.NoItemFlags
    QT_ITEM_FLAG_ITEM_IS_SELECTABLE = Qt.ItemFlag.ItemIsSelectable
    QT_ITEM_FLAG_ITEM_IS_EDITABLE = Qt.ItemFlag.ItemIsEditable
    QT_ITEM_FLAG_ITEM_IS_DRAG_ENABLED = Qt.ItemFlag.ItemIsDragEnabled
    QT_ITEM_FLAG_ITEM_IS_DROP_ENABLED = Qt.ItemFlag.ItemIsDropEnabled
    QT_ITEM_FLAG_ITEM_IS_USER_CHECKABLE = Qt.ItemFlag.ItemIsUserCheckable
    QT_ITEM_FLAG_ITEM_IS_ENABLED = Qt.ItemFlag.ItemIsEnabled
    QT_ITEM_FLAG_ITEM_IS_AUTO_TRISTATE = Qt.ItemFlag.ItemIsAutoTristate
    QT_ITEM_FLAG_ITEM_NEVER_HAS_CHILDREN = Qt.ItemFlag.ItemNeverHasChildren
    QT_ITEM_FLAG_ITEM_IS_USER_TRISTATE = Qt.ItemFlag.ItemIsUserTristate

    # focus policy
    QT_NO_FOCUS = Qt.FocusPolicy.NoFocus
    QT_TAB_FOCUS = Qt.FocusPolicy.TabFocus
    QT_CLICK_FOCUS = Qt.FocusPolicy.ClickFocus
    QT_STRONG_FOCUS = Qt.FocusPolicy.StrongFocus
    QT_WHEEL_FOCUS = Qt.FocusPolicy.WheelFocus

    # keys
    QT_KEY_RETURN = Qt.Key.Key_Return
    QT_KEY_ESCAPE = Qt.Key.Key_Escape
    QT_KEY_C = Qt.Key.Key_C
    QT_KEY_V = Qt.Key.Key_V
    QT_KEY_F = Qt.Key.Key_F
    QT_KEY_F3 = Qt.Key.Key_F3

    # keyboard modifiers
    QT_KEY_NO_MODIFIER = Qt.KeyboardModifier.NoModifier
    QT_KEY_MODIFIER_SHIFT = Qt.KeyboardModifier.ShiftModifier
    QT_KEY_MODIFIER_CONTROL = Qt.KeyboardModifier.ControlModifier
    QT_KEY_MODIFIER_ALT = Qt.KeyboardModifier.AltModifier

    # qkeysequence
    QT_KEY_SEQUENCE_COPY = QKeySequence.StandardKey.Copy
    QT_KEY_SEQUENCE_PASTE = QKeySequence.StandardKey.Paste
    QT_KEY_SEQUENCE_CUT = QKeySequence.StandardKey.Cut

    # qheaderview
    QT_HEADER_VIEW_RESIZE_TO_CONTENT = QHeaderView.ResizeMode.ResizeToContents
    QT_HEADER_VIEW_STRETCH = QHeaderView.ResizeMode.Stretch

    # qabstractitemview
    QT_ABSTRACT_ITEM_VIEW_SELECT_ROWS = QAbstractItemView.SelectionBehavior.SelectRows

    # qstyle
    QT_STYLE_SP_DIR_OPEN_ICON = QStyle.StandardPixmap.SP_DirOpenIcon

    # qpalette
    QT_PALETTE_WINDOW_TEXT = QPalette.ColorRole.WindowText
    QT_PALETTE_WINDOW = QPalette.ColorRole.Window
    QT_PALETTE_NORMAL = QPalette.ColorGroup.Normal
    QT_PALETTE_BASE = QPalette.ColorRole.Base

    # qmessagebox
    QT_MESSAGE_BOX_YES = QMessageBox.StandardButton.Yes
    QT_MESSAGE_BOX_OK = QMessageBox.StandardButton.Ok
    QT_MESSAGE_BOX_INFORMATION = QMessageBox.Icon.Information

    # qdialogbuttonbox
    QT_BUTTON_BOX_OK = QDialogButtonBox.StandardButton.Ok
    QT_BUTTON_BOX_CANCEL = QDialogButtonBox.StandardButton.Cancel

    # qlineedit
    QT_LINE_EDIT_LEADING_POSITION = QLineEdit.ActionPosition.LeadingPosition
    QT_LINE_EDIT_TRAILING_POSITION = QLineEdit.ActionPosition.TrailingPosition

    # qsizepolicy
    QT_SIZE_POLICY_IGNORED = QSizePolicy.Policy.Ignored

    # qprocess
    QT_PROCESS_CRASH_EXIT = QProcess.ExitStatus.CrashExit
else:
    # colours
    QT_RED = Qt.red
    QT_BLUE = Qt.blue
    QT_GREEN = Qt.green
    QT_BLACK = Qt.black
    QT_WHITE = Qt.white
    QT_DARK_GREEN = Qt.darkGreen
    QT_TRANSPARENT = Qt.transparent
    QT_MAGENTA = Qt.magenta

    # orientation
    QT_HORIZONTAL = Qt.Horizontal
    QT_VERTICAL = Qt.Vertical

    # alignment
    QT_ALIGN_LEFT = Qt.AlignLeft
    QT_ALIGN_RIGHT = Qt.AlignRight

    # text format
    QT_RICH_TEXT = Qt.RichText

    # window type
    QT_WINDOW_TYPE = Qt.Window
    QT_DIALOG_TYPE = Qt.Dialog

    # window hint
    QT_WINDOW_CONTEXT_HELP_BUTTON_HINT = Qt.WindowContextHelpButtonHint

    # check state
    QT_CHECKED = Qt.Checked
    QT_UNCHECKED = Qt.Unchecked
    QT_PARTIALLY_CHECKED = Qt.PartiallyChecked

    # item data roles
    QT_ITEM_DATA_FOREGROUND_ROLE = Qt.ForegroundRole
    QT_ITEM_DATA_DISPLAY_ROLE = Qt.DisplayRole

    # item flags
    QT_ITEM_FLAG_NO_ITEM_FLAGS = Qt.NoItemFlags
    QT_ITEM_FLAG_ITEM_IS_SELECTABLE = Qt.ItemIsSelectable
    QT_ITEM_FLAG_ITEM_IS_EDITABLE = Qt.ItemIsEditable
    QT_ITEM_FLAG_ITEM_IS_DRAG_ENABLED = Qt.ItemIsDragEnabled
    QT_ITEM_FLAG_ITEM_IS_DROP_ENABLED = Qt.ItemIsDropEnabled
    QT_ITEM_FLAG_ITEM_IS_USER_CHECKABLE = Qt.ItemIsUserCheckable
    QT_ITEM_FLAG_ITEM_IS_ENABLED = Qt.ItemIsEnabled
    QT_ITEM_FLAG_ITEM_IS_AUTO_TRISTATE = Qt.ItemIsAutoTristate
    QT_ITEM_FLAG_ITEM_NEVER_HAS_CHILDREN = Qt.ItemNeverHasChildren
    QT_ITEM_FLAG_ITEM_IS_USER_TRISTATE = Qt.ItemIsUserTristate

    # focus policy
    QT_NO_FOCUS = Qt.NoFocus
    QT_TAB_FOCUS = Qt.TabFocus
    QT_CLICK_FOCUS = Qt.ClickFocus
    QT_STRONG_FOCUS = Qt.StrongFocus
    QT_WHEEL_FOCUS = Qt.WheelFocus

    # keys
    QT_KEY_RETURN = Qt.Key_Return
    QT_KEY_ESCAPE = Qt.Key_Escape
    QT_KEY_C = Qt.Key_C
    QT_KEY_V = Qt.Key_V
    QT_KEY_F = Qt.Key_F
    QT_KEY_F3 = Qt.Key_F3

    # keyboard modifiers
    QT_KEY_NO_MODIFIER = Qt.NoModifier
    QT_KEY_MODIFIER_SHIFT = Qt.ShiftModifier
    QT_KEY_MODIFIER_CONTROL = Qt.ControlModifier
    QT_KEY_MODIFIER_ALT = Qt.AltModifier

    # qkeysequence
    QT_KEY_SEQUENCE_COPY = QKeySequence.Copy
    QT_KEY_SEQUENCE_PASTE = QKeySequence.Paste
    QT_KEY_SEQUENCE_CUT = QKeySequence.Cut

    # qheaderview
    QT_HEADER_VIEW_RESIZE_TO_CONTENT = QHeaderView.ResizeToContents
    QT_HEADER_VIEW_STRETCH = QHeaderView.Stretch

    # qabstractitemview
    QT_ABSTRACT_ITEM_VIEW_SELECT_ROWS = QAbstractItemView.SelectRows

    # qstyle
    QT_STYLE_SP_DIR_OPEN_ICON = QStyle.SP_DirOpenIcon

    # qpalette
    QT_PALETTE_WINDOW_TEXT = QPalette.WindowText
    QT_PALETTE_WINDOW = QPalette.Window
    QT_PALETTE_NORMAL = QPalette.Normal
    QT_PALETTE_BASE = QPalette.Base

    # qmessagebox
    QT_MESSAGE_BOX_YES = QMessageBox.Yes
    QT_MESSAGE_BOX_OK = QMessageBox.Ok
    QT_MESSAGE_BOX_INFORMATION = QMessageBox.Information

    # qdialogbuttonbox
    QT_BUTTON_BOX_OK = QDialogButtonBox.Ok
    QT_BUTTON_BOX_CANCEL = QDialogButtonBox.Cancel

    # qlineedit
    QT_LINE_EDIT_LEADING_POSITION = QLineEdit.ActionPosition.LeadingPosition
    QT_LINE_EDIT_TRAILING_POSITION = QLineEdit.ActionPosition.TrailingPosition

    # qsizepolicy
    QT_SIZE_POLICY_IGNORED = QSizePolicy.Ignored

    # qprocess
    QT_PROCESS_CRASH_EXIT = QProcess.CrashExit
