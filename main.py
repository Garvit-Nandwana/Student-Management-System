from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, \
    QMainWindow, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)

        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setting the Main Window Title
        self.setWindowTitle("Student Management System")

        # Fixed width of the Main Window
        self.setFixedWidth(500)
        self.setFixedHeight(500)

        # Setting up the Menu Bar Items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Edit")

        # Sub Actions for the Menu Bar Items
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert_student_data)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        search_student_data_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_student_data_action.triggered.connect(self.search_student_data)
        search_menu_item.addAction(search_student_data_action)

        # The Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Setting up the Tool Bar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student_data_action)

        # Creating the status bar and adding the status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    # This loads the data from the database to the Main Window table
    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert_student_data(self):
        dialog = InsertDialog()
        dialog.exec()

    def search_student_data(self):
        dialog = SearchStudent(main_window)
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


# Class for the add student sub item for the menu bar
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Insert Student Data")

        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Student Name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add Combo Box of Courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add Mobile Widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile No.")
        layout.addWidget(self.mobile)

        submit_button = QPushButton("Register")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (Name, Course, Mobile) VALUES (?, ?, ?)", (name, course, mobile))

        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


# Class for the search sub item of the menu bar
class SearchStudent(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Student")

        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.name_label = QLineEdit()
        self.name_label.setPlaceholderText("Name")
        layout.addWidget(self.name_label)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)

        self.main_window = main_window

    def search(self):
        student_data = self.name_label.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        student_info = cursor.execute("SELECT * FROM students WHERE Name = ?", (student_data,))
        rows = list(student_info)
        print(rows)

        items = main_window.table.findItems(student_data, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


# Class for the edit button in the status bar
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Update Student Data")

        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Get student course name
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Get Student Mobile Number
        mobile_no = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile_no)
        self.mobile.setPlaceholderText("Mobile No.")
        layout.addWidget(self.mobile)

        # Get Student Id
        self.student_id = main_window.table.item(index, 0).text()

        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_student)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET Name = ?, Course = ?, Mobile = ? WHERE Id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))

        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


# Class for the delete button in the status bar
class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        # The Confirmation Window
        confirmation = QLabel("Are you sure you want to delete this data?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row index and student id
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE Id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        # Successful Deletion prompt message
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


# Class for the 'about' sub item in the help tab in the menubar
class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")

        content = """
        This app helps keep a record of the currently 
        registered students in this institute. 
        """
        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
