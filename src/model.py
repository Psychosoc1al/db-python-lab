from pyodbc import connect


class Model:
    _connection_string = (
        'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=D:\Study\DB\7-python\databases\#.accdb;'
    )

    def __init__(self) -> None:
        self._connections = {}
        self._cursors = {}

    def __enter__(self) -> 'Model':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        for connection in self._connections.values():
            connection.close()

    def create_connection(self, db_id: int) -> None:
        if db_id in self._connections:
            return

        connection_string = self._connection_string.replace('#', str(db_id))
        self._connections[db_id] = connect(connection_string, autocommit=True)
        self._cursors[db_id] = self._connections[db_id].cursor()

    def execute_query(self, db_id: int, query: str, *args) -> tuple[list[str, ...], list[list[str, ...]]]:
        self._cursors[db_id].execute(query, *args)
        if self._cursors[db_id].description is None:
            return [], []

        description = [column[0] for column in self._cursors[db_id].description]
        rows_data = self._cursors[db_id].fetchall()

        data = []
        for row_index, row in enumerate(rows_data):
            data.append([''] * len(row))
            for elem_index, elem in enumerate(row):
                if elem is None:
                    data[row_index][elem_index] = '[Empty]'
                elif isinstance(elem, bytes):
                    data[row_index][elem_index] = '[Bytes]'
                else:
                    data[row_index][elem_index] = str(elem)

        return description, data
