# from datetime import datetime
#
# import pyodbc
#
# conn_str = (
#     'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
#     r'DBQ=D:\Study\DB\7-python\6.accdb;'
# )
#
# connection = pyodbc.connect(conn_str)
# cursor = connection.cursor()
#
# cursor.execute('SELECT * FROM MSysObjects')
#
# headers = [column[0] for column in cursor.description]
# print(*headers, sep='\t|\t')
# for row in cursor.fetchall():
#     for col in row:
#         if col is None:
#             print(f'{"Empty":^7}', end='|')
#         elif isinstance(col, bytes):
#             print(f'{"Bytes":^7}', end='|')
#         elif isinstance(col, datetime):
#             print(' ' + str(col) + ' ', end='|')
#         elif isinstance(col, int):
#             print(f'{col:^13}', end='|')
#         else:
#             print(f'{col:^{len("MSysNavPaneGroupCategoriesMSysNavPaneGroups") + 2}}', end='|')
#     print()
#
# connection.close()

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from win32comext.shell.shell import SetCurrentProcessExplicitAppUserModelID

from src.model import Model
from src.presenter import Presenter
from src.view import View


def main() -> None:
    app = QApplication([])
    myappid = 'databases.labs.7'
    SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setWindowIcon(QIcon('icons/icon.png'))

    with Model() as model:
        window = View()
        Presenter(model, window)

        app.exec()


if __name__ == '__main__':
    main()
