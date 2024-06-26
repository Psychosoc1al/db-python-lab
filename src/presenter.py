import re
from datetime import date

from PyQt6.QtCore import QObject, QEvent, Qt
from PyQt6.QtWidgets import QPushButton

from src.model import Model
from src.view import View


class Presenter:
    _model: Model
    _view: View
    _current_db_id: int
    _activated_list_item: str
    _last_query_result: tuple[list[str], list[list[str | int | date]]]

    def __init__(self, model, view) -> None:
        self._model = model
        self._view = view

        self._setup_gui_connections()
        self._view.parameters_dialog.submitted.connect(
            self._handle_parameters_on_submit
        )

        self._view.selected_rows_changed.connect(self._delete_table_rows)
        self._view.add_row_button.clicked.connect(self._handle_add_row_button_click)
        self._view.cell_edited.connect(self._handle_cell_edited)

    def _setup_gui_connections(self) -> None:
        self._set_toolbar_actions()
        self._view.execute_query_button.clicked.connect(self._handle_query_button_click)

        shortcut_filter = ShortcutFilter(self._view.execute_query_button, self)
        self._view.installEventFilter(shortcut_filter)

        self._view.list_widget.itemActivated.connect(self._handle_list_item_activated)

    def _set_toolbar_actions(self) -> None:
        for widget in self._view.tools.children():
            if isinstance(widget, QPushButton):
                widget.clicked.connect(lambda _, w=widget: set_actions(w))

        def set_actions(button: QPushButton) -> None:
            self._view.clear_all()
            self._current_db_id = int(button.text()[-1])
            self._model.create_connection(self._current_db_id)

            self._view.query_input.setEnabled(True)
            self._view.execute_query_button.setEnabled(True)

            try:
                _, msysobjects_data = self._model.execute_query(
                    self._current_db_id, "SELECT * FROM MSysObjects"
                )
                self._view.set_list_data([row[11] for row in msysobjects_data])
                self._set_inactive_list_items()
            except Exception as exception:
                self.show_error(exception)

    def _handle_query_button_click(self) -> None:
        query = self._view.query_input.toPlainText()
        try:
            headers, data = self._model.execute_query(self._current_db_id, query)
            if headers:
                self._view.set_table_data(headers, data, len(data), len(headers))
            else:
                self._handle_list_item_activated()
        except Exception as exception:
            self.show_error(exception)

    def _handle_list_item_activated(self) -> None:
        self._activated_list_item = self._view.list_widget.currentItem().text()
        try:
            headers, data = self._model.execute_query(
                self._current_db_id, f"SELECT * FROM [{self._activated_list_item}]"
            )
            if data and self._activated_list_item in (
                "Вид спорта",
                "Спортсмен",
                "Соревнование",
                "Команда",
                "Стадион",
                "Результат",
            ):
                data.append([""] * len(headers))
            self._last_query_result = (headers, data)

            self._view.set_table_data(headers, data, len(data), len(headers))
            self._view.table_data_label.setText(f"{self._activated_list_item} data")
        except Exception as exception:
            if "07002" in str(exception):
                params_amount_search = re.search(r" (\d)\. \(", str(exception))
                params_amount = int(params_amount_search.group(1))

                self._view.show_parameters_dialog(params_amount)
            elif "HY000" in str(exception):
                query = f"""
                SELECT MSysQueries.Name1
                FROM MSysObjects INNER JOIN MSysQueries ON MSysObjects.Id = MSysQueries.ObjectId
                WHERE (((MSysObjects.Name) = '{self._activated_list_item}') AND 
                ((MSysQueries.Attribute) IN (1, 5)) AND ((MSysQueries.Name1) IS NOT NULL))
                """

                try:
                    self._model.execute_query(
                        self._current_db_id, f"EXEC [{self._activated_list_item}]"
                    )

                    _, data = self._model.execute_query(self._current_db_id, query)
                    table_name = data[0][0]

                    headers, data = self._model.execute_query(
                        self._current_db_id, f"SELECT * FROM [{table_name}]"
                    )
                    self._view.set_table_data(headers, data, len(data), len(headers))
                    self._view.table_data_label.setText(f"{table_name} data")
                except Exception as exception:
                    self.show_error(exception)
            else:
                self.show_error(exception)

    def show_error(self, exception: Exception) -> None:
        self._view.show_error_message(str(exception))

    def _set_inactive_list_items(self):
        _, data = self._model.execute_query(
            self._current_db_id, "SELECT * FROM MSysObjects"
        )
        items = [
            self._view.list_widget.item(index)
            for index in range(self._view.list_widget.count() - 1)
        ]
        for index, item in enumerate(items):
            item_type = int(data[index][-1])
            item_flag = int(data[index][4])
            if not (
                item_type in (1, 5)
                and item_flag
                in (-2147483648, -2147352566, 0, 3, 10, 32, 48, 64, 262154)
            ):
                item.setFlags(~Qt.ItemFlag.ItemIsEnabled)

    def _handle_parameters_on_submit(self, params_str: str) -> None:
        try:
            params = params_str.split("\v")
            query_params_string = "?"
            if len(params) != 1:
                query_params_string += ", ?" * (len(params) - 1)

            headers, data = self._model.execute_query(
                self._current_db_id,
                f"EXEC [{self._activated_list_item}] {query_params_string}",
                params,
            )
            self._view.set_table_data(headers, data, len(data), len(headers))
            self._view.table_data_label.setText(f"{self._activated_list_item} data")
        except Exception as exception:
            self.show_error(exception)
            self._view.clear_all(False)

    def _delete_table_rows(self, rows: str) -> None:
        try:
            rows_list = [int(row) for row in rows.split(",")]
            for row in rows_list:
                first_column, second_column = self._last_query_result[0][:2]
                values = self._last_query_result[1][row][:2]

                first_value = (
                    f"#{values[0]}#" if isinstance(values[0], date) else values[0]
                )
                second_value = (
                    f"'{values[1]}'" if isinstance(values[1], str) else values[1]
                )

                self._model.execute_query(
                    self._current_db_id,
                    f"""
                DELETE FROM [{self._activated_list_item}]
                WHERE (([{first_column}] = {first_value}) AND ([{second_column}] = {second_value}))
                """,
                )

            self._handle_list_item_activated()
        except Exception as exception:
            self.show_error(exception)

    def _handle_add_row_button_click(self, _) -> None:
        try:
            table_widget = self._view.table_widget
            values = [
                table_widget.item(table_widget.rowCount() - 1, column).text()
                for column in range(table_widget.columnCount())
            ]
            values_str = ", ".join([f"'{value}'" for value in values])

            self._model.execute_query(
                self._current_db_id,
                f"""
                INSERT INTO [{self._activated_list_item}]
                VALUES ({values_str})
                """,
            )

            self._handle_list_item_activated()
        except Exception as exception:
            self.show_error(exception)

    def _handle_cell_edited(self, row: int, column: int) -> None:
        try:
            first_column, second_column = self._last_query_result[0][:2]
            values = self._last_query_result[1][row][:2]

            first_condition_value = (
                f"#{values[0]}#" if isinstance(values[0], date) else values[0]
            )
            second_condition_value = (
                f"'{values[1]}'" if isinstance(values[1], str) else values[1]
            )

            value = self._view.table_widget.item(row, column).text()

            self._model.execute_query(
                self._current_db_id,
                f"""
                    UPDATE [{self._activated_list_item}]
                    SET [{self._last_query_result[0][column]}] = '{value}'
                    WHERE (([{first_column}] = {first_condition_value}) 
                    AND ([{second_column}] = {second_condition_value}))
                    """,
            )

            self._handle_list_item_activated()
        except Exception as exception:
            self._handle_list_item_activated()
            self.show_error(exception)


class ShortcutFilter(QObject):
    def __init__(self, button: QPushButton, presenter: "Presenter") -> None:
        super().__init__(button)

        self._button = button
        self._presenter = presenter

    def eventFilter(self, _: QObject, event) -> bool:
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            try:
                self._button.click()
                return True
            except Exception as exception:
                self._presenter.show_error(exception)
        return False
