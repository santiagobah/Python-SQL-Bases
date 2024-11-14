from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QDialog, QLineEdit, QSpinBox, QFormLayout, QGridLayout
import sys
#uhfdhasfdbkhjfkbhsd
#prueba 2
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iniciarprograma()

    def iniciarprograma(self):
        self.setGeometry(400,200,400,400)
        self.setWindowTitle("Consultas university")
        self.mostrar_principal()
        self.show()

    def  mostrar_principal(self):
        
        self.bases = ["University"]
        self.widgetprincipal = QWidget()
        self.setCentralWidget(self.widgetprincipal)
        self.layout = QVBoxLayout(self.widgetprincipal)
        self.basesdisponibles = QComboBox()
        
        for bases in self.bases:
            self.basesdisponibles.addItem(bases)
        
        self.layout.addWidget(self.basesdisponibles)
        
        self.tablas = ["Advisor", "Classroom", "Course", "Department", "Instructor", "Prereq", "Section", "Student", "Takes", "Teaches", "Time_slot"]
        self.tablasdisponibles = QComboBox()
        
        for tablas in self.tablas:
            self.tablasdisponibles.addItem(tablas)
            
        self.layout.addWidget(self.tablasdisponibles)
        



app = QApplication(sys.argv)
programa = VentanaPrincipal()
sys.exit(app.exec())