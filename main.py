from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine, MetaData, Table, select
import sys

DATABASE_URL = "mysql+pymysql://usuario:contraseña@localhost/university"  # PEDIRSELO AL USUARIO
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Clase principal
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iniciar_programa()

    def iniciar_programa(self):
        self.setGeometry(400, 200, 600, 400)
        self.setWindowTitle("Consultas University")
        self.mostrar_principal()
        self.show()

    def mostrar_principal(self):
        # Configuración de widgets principales
        self.widget_principal = QWidget()
        self.setCentralWidget(self.widget_principal)
        self.layout = QVBoxLayout(self.widget_principal)

        # ComboBox para tablas
        self.tablas = [
            "Advisor", "Classroom", "Course", "Department", 
            "Instructor", "Prereq", "Section", "Student", 
            "Takes", "Teaches", "Time_slot"
        ]
        self.tablas_disponibles = QComboBox()
        for tabla in self.tablas:
            self.tablas_disponibles.addItem(tabla)
        self.layout.addWidget(QLabel("Selecciona una tabla:"))
        self.layout.addWidget(self.tablas_disponibles)

        # Botón que corre la consulta, esto va a estar horrible
        self.boton_consultar = QPushButton("Consultar")
        self.boton_consultar.clicked.connect(self.ejecutar_consulta)
        self.layout.addWidget(self.boton_consultar)

        self.resultados = QTableWidget()
        self.layout.addWidget(self.resultados)

    def ejecutar_consulta(self):

        tabla_seleccionada = self.tablas_disponibles.currentText()

        try:
            # Obtener datos 
            tabla = Table(tabla_seleccionada, metadata, autoload_with=engine)
            consulta = select(tabla)
            conexion = engine.connect()
            resultados = conexion.execute(consulta).fetchall()
            conexion.close()

            # Mostrar resultados 
            self.resultados.setColumnCount(len(tabla.columns))
            self.resultados.setRowCount(len(resultados))
            self.resultados.setHorizontalHeaderLabels(tabla.columns.keys())

            for fila_idx, fila in enumerate(resultados):
                for col_idx, valor in enumerate(fila):
                    self.resultados.setItem(fila_idx, col_idx, QTableWidgetItem(str(valor)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo realizar la consulta: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    programa = VentanaPrincipal()
    sys.exit(app.exec())
