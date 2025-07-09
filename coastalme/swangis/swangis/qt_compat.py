try:
    from PyQt6.QtCore import Qt
    is_qt6 = True
except ImportError:
    from PyQt5.QtCore import Qt
    is_qt6 = False


if is_qt6:
    # brush style
    QT_STYLE_NO_BRUSH = Qt.BrushStyle.NoBrush

    # item data role
    QT_ITEM_DATA_USER_ROLE = Qt.ItemDataRole.UserRole

    # alignment
    QT_ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
    QT_ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter

    # dock widget area
    QT_DOCK_WIDGET_AREA_LEFT = Qt.DockWidgetArea.LeftDockWidgetArea
    QT_DOCK_WIDGET_AREA_RIGHT = Qt.DockWidgetArea.RightDockWidgetArea
else:
    # brush style
    QT_STYLE_NO_BRUSH = Qt.NoBrush

    # item data role
    QT_ITEM_DATA_USER_ROLE = Qt.UserRole

    # alignment
    QT_ALIGN_LEFT = Qt.AlignLeft
    QT_ALIGN_CENTER = Qt.AlignCenter

    # dock widget area
    QT_DOCK_WIDGET_AREA_LEFT = Qt.LeftDockWidgetArea
    QT_DOCK_WIDGET_AREA_RIGHT = Qt.RightDockWidgetArea
