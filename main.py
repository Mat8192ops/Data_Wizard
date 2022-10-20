from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
from MplChart_reg import *
import sys


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        Welcome_sc = "_WelcomeScreen.ui"
        try:
            loadUi(Welcome_sc, self)
        except FileNotFoundError:
            msg = "Unfortunately, file " + Welcome_sc + " not found."
            print(msg)
            exit(1)

        self.Login.clicked.connect(self.gotologin)
        self.Register.clicked.connect(self.gotoregister)

    @staticmethod
    def gotologin():
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def gotoregister():
        register = RegisterScreen()
        widget.addWidget(register)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class RegisterScreen(QDialog):
    def __init__(self):
        super(RegisterScreen, self).__init__()
        Register_sc = "_RegisterScreen.ui"
        try:
            loadUi(Register_sc, self)
        except FileNotFoundError:
            msg = "Unfortunately, file " + Register_sc + " not found."
            print(msg)
            exit(1)

        self.Back.clicked.connect(self.gotowelcome)
        self.Confirm.clicked.connect(self.gotomenu)
        self.Password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Confirm_password.setEchoMode(QtWidgets.QLineEdit.Password)

    def gotomenu(self):
        email = self.Email_field.text()
        first_name = self.First_name.text()
        password = self.Password.text()
        confirm_password = self.Confirm_password.text()

        if len(email) == 0 or len(password) == 0 or len(first_name) == 0 or len(confirm_password) == 0:
            self.error.setText("Please input all fields.")
        else:
            if password != confirm_password:
                self.error.setText("Passwords are not the same.")
            else:
                data_login = "_Register_accounts.db"
                con = sqlite3.connect(data_login)
                cur = con.cursor()
                data = [(email, password, first_name)]
                cur.executemany("INSERT INTO login_info VALUES(?, ?, ?)", data)
                con.commit()
                con.close()

                login = LoginScreen()
                widget.addWidget(login)
                widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def gotowelcome():
        welcome_back = WelcomeScreen()
        widget.addWidget(welcome_back)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        Login_sc = "_LoginScreen.ui"
        try:
            loadUi(Login_sc, self)
        except FileNotFoundError:
            msg = "Unfortunately, file " + Login_sc + " not found."
            print(msg)
            exit(1)

        self.Back_button.clicked.connect(self.gotowelcome)
        self.Confirm.clicked.connect(self.gotomenu)
        self.Password_field.setEchoMode(QtWidgets.QLineEdit.Password)

    def gotomenu(self):
        email = self.Email_field.text()
        password = self.Password_field.text()

        if len(email) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")
        else:
            data_login = "_Register_accounts.db"
            con = sqlite3.connect(data_login)
            cur = con.cursor()
            for row in cur.execute("SELECT Password FROM login_info;"):
                for rows in row:
                    if password in rows:
                        self.error.setText("Successfully logged in.")
                        con.commit()
                        con.close()
                        Menu = MenuScreen()
                        widget.addWidget(Menu)
                        widget.setCurrentIndex(widget.currentIndex() + 1)
                        return 0

                    else:
                        self.error.setText("Invalid E-mail or password")

    @staticmethod
    def gotowelcome():
        welcome_back = WelcomeScreen()
        widget.addWidget(welcome_back)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class MenuScreen(QDialog):
    def __init__(self):
        super(MenuScreen, self).__init__()
        Menu_sc = "_MenuScreen.ui"
        try:
            loadUi(Menu_sc, self)
        except FileNotFoundError:
            msg = "Unfortunately, file " + Menu_sc + " not found."
            print(msg)
            exit(1)

        self.SW = None
        self.stackedWidget.setCurrentWidget(self.Dashboard)
        self.analysis.clicked.connect(self.gotoanalysis)
        self.report.clicked.connect(self.gotoreport)
        self.my_profil.clicked.connect(self.gotomy_profil)
        self.calendar.clicked.connect(self.gotocalendar)
        self.back.clicked.connect(self.goback)
        self.log_out.clicked.connect(self.gotowelcome)

    def gotoanalysis(self):
        self.stackedWidget.setCurrentWidget(self.Analysis)
        self.Create.clicked.connect(self.gotochart)

    def gotoreport(self):
        self.stackedWidget.setCurrentWidget(self.Report)

    def gotomy_profil(self):
        self.stackedWidget.setCurrentWidget(self.My_profil)

    def gotocalendar(self):
        self.stackedWidget.setCurrentWidget(self.Calendar)

    def goback(self):
        self.stackedWidget.setCurrentWidget(self.Dashboard)

    def gotochart(self):
        self.SW = SecondWindow()
        self.SW.resize(930, 640)
        self.SW.show()

    @staticmethod
    def gotowelcome():
        welcome_back = WelcomeScreen()
        widget.addWidget(welcome_back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def gotomenu():
        Menu = MenuScreen()
        widget.addWidget(Menu)
        widget.setCurrentIndex(widget.currentIndex() + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(welcome)
    widget.setFixedHeight(540)
    widget.setFixedWidth(930)
    widget.show()
    sys.exit(app.exec_())
