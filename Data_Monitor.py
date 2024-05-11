import sys
import redis
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget




class Ui_Form(object):
    def __init__(self):
        self.patient_name = ""
        self.patient_id = ""
        self.format = "utf-8"
        self.database = redis.Redis(host="localhost", port=6379, password=None)
        self.received_data = []
        self.temperature_values = []
        self.timer = QtCore.QTimer()  
        self.current_index = 0
        self.sort_descending = False
        
    def reset_table_clicked(self):
        # Clear previous data and initialize for new data
        self.Patients_Temperature_Graph.clear()
        self.temperature_values = []
        self.current_index = 0
        # Retrieve all data from the database
        self.receive_data()
        if self.sort_descending:
            self.sort_table_ascending()
        else:
            self.sort_table_descending()
   
    def update_plot_dynamically(self):
        if self.current_index < len(self.temperature_values):
            next_temperature = self.temperature_values[self.current_index]
            self.append_temperature_point(self.current_index + 1, next_temperature)
            self.current_index += 1
        else:
            self.timer.stop()

    def append_temperature_point(self, index, temperature):
        if index > 1:
            # Connect the new point to the previous point
            last_index = index - 1
            last_temperature = self.temperature_values[index - 2]
            self.Patients_Temperature_Graph.plot([last_index, index], [last_temperature, temperature], pen='r', symbol='o', name='Temperature vs. Index')
        else:
            # Plot the first point without connecting
            self.Patients_Temperature_Graph.plot([index], [temperature], pen='r', symbol='o', name='Temperature vs. Index')

        # Update x-axis range based on number of points plotted
        if index > 10:
            # Shift x-axis to show the most recent points
            self.Patients_Temperature_Graph.setXRange(index - 10, index, padding=0.05)

    def on_table_item_clicked(self, item):
    # Clear previous data and initialize for new data
        self.Patients_Temperature_Graph.clear()
        self.temperature_values = []
        self.current_index = 0

        # Get the selected patient ID from the clicked item
        row = item.row()
        patient_id_item = self.Data_Table.item(row, 0)
        if patient_id_item:
            patient_id = patient_id_item.text()

            # Retrieve all temperature values for the selected patient ID
            search_key = f"*_{patient_id}"
            keys = self.database.keys(search_key)

            for key in keys:
                key_str = key.decode(self.format) if isinstance(key, bytes) else key
                values = self.database.lrange(key_str, 0, -1)
                for value in values:
                    value_str = value.decode(self.format)
                    try:
                        # Extract temperature component from value string
                        temperature_str = value_str.split(',')[0].strip()
                        temperature = float(temperature_str)
                        self.temperature_values.append(temperature)
                    except (ValueError, IndexError):
                        print(f"Error: Invalid temperature value in {value_str}")

            # Start the QTimer to begin dynamic plotting from the beginning
            if self.temperature_values:
                self.timer.stop()  
                self.timer.start()  

                # Reset x-axis range to show the initial data points
                num_points = len(self.temperature_values)
                if num_points > 10:
                    self.Patients_Temperature_Graph.setXRange(0, 10, padding=0.05)
                else:
                    self.Patients_Temperature_Graph.setXRange(0, num_points, padding=0.05)

    def receive_data(self, patient_id=None):
        if patient_id:
            # Fetch patient name from database using patient_id
            patient_name = self.get_patient_name(patient_id)

            # Search for a specific patient ID
            search_key = f"*_{patient_id}"
            keys = self.database.keys(search_key)
            self.received_data = []

            for key in keys:
                key_str = key.decode(self.format) if isinstance(key, bytes) else key
                values = self.database.lindex(key_str, 0)
                if values:
                    values_str = values.decode(self.format)
                    self.received_data.append((key_str, values_str))

            if not self.received_data:
                print(f"No data found for patient ID: {patient_id}")
        else:
            # Fetch all data
            keys = self.database.keys('*')
            self.received_data = []

            for key in keys:
                key_str = key.decode(self.format) if isinstance(key, bytes) else key
                values = self.database.lindex(key_str, 0)
                if values:
                    values_str = values.decode(self.format)
                    self.received_data.append((key_str, values_str))

        self.update_table()

    def search_patient(self):
        patient_id = self.Search_Text_Edit.toPlainText().strip()
        print(f"Searching for patient ID: {patient_id}")

        if not patient_id:
            print("No patient ID entered. Displaying all patients.")
            self.receive_data()  # Display all patients
        else:
            # Fetch patient name from database using patient_id
            patient_name = self.get_patient_name(patient_id)

            if patient_name:
                print(f"Found patient name: {patient_name}")
                self.receive_data(patient_id=patient_id)
            else:
                print(f"Patient with ID {patient_id} not found in database.")
                self.receive_data()  

    def get_patient_name(self, patient_id):
        # Retrieve patient's name from Redis using patient_id
        key_pattern = f"*_{patient_id}"
        keys = self.database.keys(key_pattern)

        if keys:
            key = keys[0].decode(self.format)
            patient_name, _ = key.split('_')
            return patient_name
        else:
            return None
        
    def update_table(self):
        self.Data_Table.clearContents()

        # Determine the sorting key based on the selected combo box item
        sorting_key = self.Sorting_Combo_Box.currentText()

        # Map the sorting key to corresponding column index in the table
        column_mapping = {
            "ID": 0,
            "Name": 1
        }

        # Get the corresponding column index from the mapping
        sort_column = column_mapping.get(sorting_key, None)

        if sort_column is not None:
            try:
                # Sort the received_data based on the selected column using get_sort_value function
                sorted_data = sorted(self.received_data, key=lambda item: self.get_sort_value(item[0], sort_column), reverse=self.sort_descending)

                # Set the number of rows based on sorted data
                self.Data_Table.setRowCount(len(sorted_data))

                for row_index, (key_str, values_str) in enumerate(sorted_data):
                    # Extract components from the key_str and values_str
                    parts = key_str.split('_')
                    patient_id = parts[-1]
                    patient_name = parts[0]
                    temperature, _, _ = values_str.split(',')  
                    _, date, _ = values_str.split(',')
                    _, _, time = values_str.split(',')

                    # Populate table with extracted data
                    self.Data_Table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(patient_id))
                    self.Data_Table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(patient_name))
                    self.Data_Table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(temperature))
                    self.Data_Table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(date))
                    self.Data_Table.setItem(row_index, 4, QtWidgets.QTableWidgetItem(time))

            except Exception as e:
                print(f"Error updating table: {e}")
        else:
            print("Invalid sorting column selected.")

        self.Data_Table.update()

    def get_sort_value(self, key_str, sort_column):
        parts = key_str.split('_')

        if sort_column == 0:
            # Sorting by ID (extract and convert the numeric ID part)
            if len(parts) > 1:
                try:
                    return int(parts[-1])  # Convert the last part to an integer (assuming it's the ID)
                except ValueError:
                    return 0  # Return 0 if conversion fails or no valid ID found
            else:
                return 0  # Return 0 if no valid ID found
        elif sort_column == 1:
            # Sorting by Name (extract the name part)
            if len(parts) > 0:
                return parts[0]  # First part is the name
            else:
                return ""  # Return empty string if no valid name found
        else:
            return None  

    def sort_table_ascending(self):
        self.sort_descending = False
        self.update_table()

    def sort_table_descending(self):
        self.sort_descending = True
        self.update_table()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1138, 455)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        Form.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Assets/donut-chart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Search_Text_Edit = QtWidgets.QTextEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Search_Text_Edit.sizePolicy().hasHeightForWidth())
        self.Search_Text_Edit.setSizePolicy(sizePolicy)
        self.Search_Text_Edit.setMinimumSize(QtCore.QSize(700, 0))
        self.Search_Text_Edit.setMaximumSize(QtCore.QSize(16777215, 60))
        self.Search_Text_Edit.setObjectName("Search_Text_Edit")
        self.horizontalLayout.addWidget(self.Search_Text_Edit)
        self.Search_Button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Search_Button.sizePolicy().hasHeightForWidth())
        self.Search_Button.setSizePolicy(sizePolicy)
        self.Search_Button.setMinimumSize(QtCore.QSize(100, 0))
        self.Search_Button.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.Search_Button.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Assets/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Search_Button.setIcon(icon1)
        self.Search_Button.setIconSize(QtCore.QSize(20, 20))
        self.Search_Button.setObjectName("Search_Button")
        self.horizontalLayout.addWidget(self.Search_Button)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Data_Table_Label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Data_Table_Label.setFont(font)
        self.Data_Table_Label.setObjectName("Data_Table_Label")
        self.verticalLayout.addWidget(self.Data_Table_Label)
        self.Data_Table = QtWidgets.QTableWidget(Form)
        self.Data_Table.setMinimumSize(QtCore.QSize(510, 270))
        self.Data_Table.setMaximumSize(QtCore.QSize(650, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Data_Table.setFont(font)
        self.Data_Table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.Data_Table.setDragDropOverwriteMode(False)
        self.Data_Table.setObjectName("Data_Table")
        self.Data_Table.setColumnCount(5)
        self.Data_Table.setRowCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("Assets/list.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon2)
        self.Data_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("Assets/id-card.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon3)
        self.Data_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("Assets/thermometer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon4)
        self.Data_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("Assets/calendar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon5)
        self.Data_Table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("Assets/hourglass.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon6)
        self.Data_Table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.Data_Table.setItem(0, 4, item)
        self.verticalLayout.addWidget(self.Data_Table)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Patients_Temperature_Label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Patients_Temperature_Label.setFont(font)
        self.Patients_Temperature_Label.setObjectName("Patients_Temperature_Label")
        self.verticalLayout_5.addWidget(self.Patients_Temperature_Label)
        self.Patients_Temperature_Graph = PlotWidget(Form)
        self.Patients_Temperature_Graph.setMinimumSize(QtCore.QSize(580, 0))
        self.Patients_Temperature_Graph.setObjectName("Patients_Temperature_Graph")
        self.verticalLayout_5.addWidget(self.Patients_Temperature_Graph)
        self.horizontalLayout_5.addLayout(self.verticalLayout_5)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.Table_Sorting_Label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Table_Sorting_Label.setFont(font)
        self.Table_Sorting_Label.setObjectName("Table_Sorting_Label")
        self.verticalLayout_3.addWidget(self.Table_Sorting_Label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Ascending_Radio_Button = QtWidgets.QRadioButton(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.Ascending_Radio_Button.setFont(font)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("Assets/list (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Ascending_Radio_Button.setIcon(icon7)
        self.Ascending_Radio_Button.setIconSize(QtCore.QSize(20, 20))
        self.Ascending_Radio_Button.setObjectName("Ascending_Radio_Button")
        self.horizontalLayout_2.addWidget(self.Ascending_Radio_Button)
        self.Descending_Radio_Button = QtWidgets.QRadioButton(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.Descending_Radio_Button.setFont(font)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("Assets/list (2).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Descending_Radio_Button.setIcon(icon8)
        self.Descending_Radio_Button.setIconSize(QtCore.QSize(20, 20))
        self.Descending_Radio_Button.setObjectName("Descending_Radio_Button")
        self.horizontalLayout_2.addWidget(self.Descending_Radio_Button)
        self.Sorting_Combo_Box = QtWidgets.QComboBox(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.Sorting_Combo_Box.setFont(font)
        self.Sorting_Combo_Box.setObjectName("Sorting_Combo_Box")
        self.Sorting_Combo_Box.addItem(icon2, "")
        self.Sorting_Combo_Box.addItem(icon3, "")
        self.horizontalLayout_2.addWidget(self.Sorting_Combo_Box)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Table_Controls_Label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.Table_Controls_Label.setFont(font)
        self.Table_Controls_Label.setObjectName("Table_Controls_Label")
        self.verticalLayout_2.addWidget(self.Table_Controls_Label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.Reset_Table_Button = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.Reset_Table_Button.setFont(font)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("Assets/refresh-arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Reset_Table_Button.setIcon(icon9)
        self.Reset_Table_Button.setIconSize(QtCore.QSize(16, 16))
        self.Reset_Table_Button.setObjectName("Reset_Table_Button")
        self.horizontalLayout_3.addWidget(self.Reset_Table_Button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.Search_Button.clicked.connect(self.search_patient)
        self.Data_Table.itemClicked.connect(self.on_table_item_clicked)
        self.Ascending_Radio_Button.clicked.connect(self.sort_table_ascending)
        self.Descending_Radio_Button.clicked.connect(self.sort_table_descending)
        self.Reset_Table_Button.clicked.connect(self.reset_table_clicked)
        self.Sorting_Combo_Box.currentIndexChanged.connect(self.update_table)




        # Update table initially to show all patients
        self.receive_data()
        self.sort_table_ascending() 
        self.Ascending_Radio_Button.setChecked(True)

        self.timer.timeout.connect(self.update_plot_dynamically)
        self.timer.setInterval(1000)  

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Data_Monitor"))
        self.Search_Button.setText(_translate("Form", "Search"))
        self.Data_Table_Label.setText(_translate("Form", "Data Table"))
        item = self.Data_Table.verticalHeaderItem(0)
        # item.setText(_translate("Form", "Patient"))
        item = self.Data_Table.verticalHeaderItem(1)
        # item.setText(_translate("Form", "Patient"))
        item = self.Data_Table.horizontalHeaderItem(0)
        item.setText(_translate("Form", "ID"))
        item = self.Data_Table.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Name"))
        item = self.Data_Table.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Temperature"))
        item = self.Data_Table.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Date"))
        item = self.Data_Table.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Time"))
        self.Patients_Temperature_Label.setText(_translate("Form", "Patients Temperature Graph"))
        self.Table_Sorting_Label.setText(_translate("Form", "Table Sorting"))
        self.Ascending_Radio_Button.setText(_translate("Form", "Ascending"))
        self.Descending_Radio_Button.setText(_translate("Form", "Descending"))
        self.Sorting_Combo_Box.setItemText(0, _translate("Form", "ID"))
        self.Sorting_Combo_Box.setItemText(1, _translate("Form", "Name"))
        self.Sorting_Combo_Box.setItemText(2, _translate("Form", "Temperature"))
        self.Sorting_Combo_Box.setItemText(3, _translate("Form", "Date"))
        self.Sorting_Combo_Box.setItemText(4, _translate("Form", "Time"))
        self.Table_Controls_Label.setText(_translate("Form", "Table Controls"))
        self.Reset_Table_Button.setText(_translate("Form", "Reset Table"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    ui.update_table()
    Form.show()
    sys.exit(app.exec_())
