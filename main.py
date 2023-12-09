from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from win32comext.shell.shell import SetCurrentProcessExplicitAppUserModelID

from src.model import Model
from src.presenter import Presenter
from src.view import View


def main() -> None:
    app = QApplication([])
    myappid = "databases.labs.7"
    SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setWindowIcon(QIcon("icons/icon.png"))

    with Model() as model:
        window = View()
        Presenter(model, window)

        app.exec()


if __name__ == "__main__":
    main()
