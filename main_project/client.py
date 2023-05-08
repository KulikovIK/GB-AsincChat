from src.core import get_app_arguments
from client_config.runner import Client
from src.ui.ui_window import Ui_MainWindow
import sys
from PyQt5 import QtWidgets

_DESCRIPTOR = "client"


def main():
    args = get_app_arguments(_DESCRIPTOR)
    app = Client(host=args.host, port=args.port)
    app.run()

    # ui_app = QtWidgets.QApplication(sys.argv)
    # window = QtWidgets.QMainWindow()

    # ui = Ui_MainWindow()

    # ui.setupUi(window)
    # # ui.btnQuit.clicked.connect(QtWidgets.qApp.quit)
    # window.show()
    # sys.exit(ui_app.exec_())

if __name__ == "__main__":
    main()
