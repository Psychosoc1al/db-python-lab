import qdarktheme
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QListWidget, QWidget, QApplication,
                             QTableWidget, QTableWidgetItem, QHBoxLayout, QSplitter, QVBoxLayout, QLabel, QTextEdit,
                             QPushButton, QMessageBox, QAbstractItemView)

from qtacrylic_lib import WindowEffect


class View(QMainWindow):
    def __init__(self) -> None:
        super().__init__(parent=None)

        self.setWindowTitle('Database worker')

        self._create_toolbar()
        self._create_and_set_widgets()
        self._set_size_and_position()

        self._windowFX = WindowEffect()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._windowFX.setAcrylicEffect(int(self.winId()))
        qdarktheme.setup_theme(custom_colors={'primary': '#d79df1'})

        self.show()

    def _create_toolbar(self) -> None:
        self.tools = QToolBar(self)
        label = QLabel('Choose database: ', self)
        label.setStyleSheet('font-weight: bold;')
        self.tools.addWidget(label)
        self.tools.addSeparator()

        for i in range(4, 7):
            action_button = QPushButton(f'Database №{i}', self)
            action_button.setCheckable(True)
            action_button.clicked.connect(lambda _, btn=action_button: _set_buttons_untoggling(btn.text()))
            self.tools.addWidget(action_button)

        def _set_buttons_untoggling(button_text: str) -> None:
            for widget in self.tools.children():
                if isinstance(widget, QPushButton) and widget.text() != button_text:
                    self.db_inner_label.setText(button_text + ' inner data')
                    widget.setChecked(False)

        self.addToolBar(self.tools)

    def _create_and_set_widgets(self) -> None:
        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_splitter.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        main_splitter.setHandleWidth(3)
        self.setCentralWidget(main_splitter)

        left_widget = self._create_left_side_widgets()
        main_splitter.addWidget(left_widget)

        right_widget = self._create_right_side_widgets()
        main_splitter.addWidget(right_widget)

        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

    def _create_left_side_widgets(self) -> QWidget:
        left_widget = QWidget(self.centralWidget())
        left_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.db_inner_label = QLabel('Database inner data', left_widget)
        self.db_inner_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.db_inner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.db_inner_label)

        self.list_widget = ListWidget()
        left_layout.addWidget(self.list_widget)

        return left_widget

    def _create_right_side_widgets(self) -> QSplitter:
        self._right_splitter = QSplitter(Qt.Orientation.Vertical)
        self._right_splitter.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._right_splitter.setHandleWidth(3)

        right_upper_widget = self._create_right_upper_widgets(self._right_splitter)
        self._right_splitter.addWidget(right_upper_widget)

        right_lower_widget = self._create_right_lower_widgets(self._right_splitter)
        self._right_splitter.addWidget(right_lower_widget)

        self._right_splitter.setStretchFactor(0, 1)
        self._right_splitter.splitterMoved.connect(self._adjust_query_input_size)

        return self._right_splitter

    def _create_right_upper_widgets(self, parent: QWidget) -> QWidget:
        right_upper_widget = QWidget(parent)
        right_upper_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        right_upper_layout = QVBoxLayout(right_upper_widget)
        right_upper_layout.setContentsMargins(0, 0, 0, 5)

        self.table_data_label = QLabel('Database selected table data', right_upper_widget)
        self.table_data_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        right_upper_layout.addWidget(self.table_data_label)

        self._table_widget = TableWidget()
        right_upper_layout.addWidget(self._table_widget)

        return right_upper_widget

    def _create_right_lower_widgets(self, parent: QWidget) -> QWidget:
        right_lower_widget = QWidget(parent)
        right_lower_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        right_lower_layout = QVBoxLayout(right_lower_widget)
        right_lower_layout.setContentsMargins(0, 0, 0, 0)

        query_label = QLabel('Database query', right_lower_widget)
        query_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        right_lower_layout.addWidget(query_label)

        self.query_input = QTextEdit(right_lower_widget)
        self.query_input.setPlaceholderText('Enter your query here')
        self.query_input.setStyleSheet('background: transparent; font-size: 14px;')
        self.query_input.setMinimumHeight(50)
        self.query_input.setMaximumHeight(50)
        self.query_input.setEnabled(False)
        right_lower_layout.addWidget(self.query_input)

        button_layout = QHBoxLayout(right_lower_widget)
        button_layout.setContentsMargins(0, 0, 70, 5)
        right_lower_layout.addLayout(button_layout)

        self.execute_query_button = QPushButton('Execute query', right_lower_widget)
        self.execute_query_button.setStyleSheet('font-size: 14px;')
        self.execute_query_button.setFixedWidth(150)
        self.execute_query_button.setEnabled(False)
        button_layout.insertWidget(0, self.execute_query_button, alignment=Qt.AlignmentFlag.AlignRight)

        return right_lower_widget

    def _adjust_query_input_size(self) -> None:
        self.query_input.setMaximumHeight(5000)
        self._right_splitter.splitterMoved.disconnect(self._adjust_query_input_size)

    def _set_size_and_position(self) -> None:
        window_width, window_height = 1300, 730
        self.resize(window_width, window_height)

        screen = QApplication.primaryScreen()
        screen_size = screen.size()

        x = (screen_size.width() - window_width) // 2
        y = (screen_size.height() - window_height) // 2
        self.move(x, y)

    def set_table_data(self, headers: list[str], data: list[list[str, ...]], row_count: int, column_count: int) -> None:
        self._table_widget.clear_and_hide_table()
        self._table_widget.set_table_data(headers, data, row_count, column_count)

    def set_list_data(self, data: list[str]) -> None:
        self.list_widget.clear_list()
        self.list_widget.set_list_data(data)

    def show_error_message(self, message: str) -> None:
        QMessageBox.critical(self, 'An error occurred', message)


class TableWidget(QTableWidget):
    _headers: list[str]
    _data: list[list[str, ...]]
    _row_count: int
    _column_count: int

    def __init__(self):
        super().__init__()

        self.setStyleSheet('background: transparent; font-size: 16px;')
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def set_table_data(self, headers: list[str], data: list[list[str, ...]], row_count: int, column_count: int) -> None:
        self._headers = headers
        self._data = data
        self._row_count = row_count
        self._column_count = column_count

        self._fill_table_data()
        self._fit_table_sizes()

    def _fill_table_data(self) -> None:
        self.setColumnCount(self._column_count)
        self.setRowCount(self._row_count)
        self.setHorizontalHeaderLabels(self._headers)

        for i in range(self._row_count):
            for j in range(self._column_count):
                table_item = QTableWidgetItem(self._data[i][j])
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(i, j, table_item)

    def _fit_table_sizes(self) -> None:
        for j in range(self._column_count):
            self.resizeColumnToContents(j)
            self.setColumnWidth(j, self.columnWidth(j) + 10)

        for i in range(self._row_count):
            self.resizeRowToContents(i)
            self.setRowHeight(i, self.rowHeight(i) - 4)

    def clear_and_hide_table(self):
        self.setColumnCount(0)
        self.setRowCount(0)
        self.clear()


class ListWidget(QListWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('background: transparent; font-size: 16px;')

    def clear_list(self):
        self.clear()

    def set_list_data(self, data: list[str]) -> None:
        for elem in data:
            self.addItem(elem)
