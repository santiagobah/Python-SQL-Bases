from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine, MetaData, Table, select, Column, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
import sys

# URL de la base de datos (PEDIRSE AL USUARIO EN LA PRÁCTICA)
DATABASE_URL = "mysql+pymysql://usuario:contraseña@localhost/university"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
Base = declarative_base()

# Clase principal de la interfaz
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iniciar_programa()

    def iniciar_programa(self):
        self.setGeometry(400, 200, 800, 600)
        self.setWindowTitle("Consultas Predefinidas de University")
        self.mostrar_principal()
        self.show()

    def mostrar_principal(self):
        self.widget_principal = QWidget()
        self.setCentralWidget(self.widget_principal)
        self.layout = QVBoxLayout(self.widget_principal)

        # ComboBox para seleccionar consultas
        self.layout.addWidget(QLabel("Selecciona una consulta:"))
        self.consultas_disponibles = QComboBox()
        self.consultas = self.obtener_consultas()
        for i, consulta in enumerate(self.consultas):
            self.consultas_disponibles.addItem(f"Consulta {i + 1}")
        self.layout.addWidget(self.consultas_disponibles)

        # Botón para ejecutar la consulta
        self.boton_consultar = QPushButton("Ejecutar Consulta")
        self.boton_consultar.clicked.connect(self.ejecutar_consulta)
        self.layout.addWidget(self.boton_consultar)

        # Tabla para mostrar resultados
        self.resultados = QTableWidget()
        self.layout.addWidget(self.resultados)

    def obtener_consultas(self):
        # LISTA DE CONSULTAS DE EJEMPLO, TENEMOS QUE SACAR UNAS MAMDAS, LO PUSE ASI PARA VER Q PEI
        return [
            ("SELECT * FROM student", "Lista de estudiantes"),
            ("SELECT * FROM instructor WHERE salary > 50000", "Profesores con salario mayor a 50,000"),
            ("SELECT * FROM course", "Lista de cursos"),
            ("SELECT * FROM department WHERE budget > 100000", "Departamentos con presupuesto mayor a 100,000"),
            ("SELECT * FROM section WHERE year = 2024", "Secciones ofrecidas en 2024"),
            ("SELECT student.name, takes.course_id FROM student JOIN takes ON student.ID = takes.ID", "Estudiantes y cursos que toman"),
            ("SELECT instructor.name, teaches.course_id FROM instructor JOIN teaches ON instructor.ID = teaches.ID", "Profesores y cursos que enseñan"),
            ("SELECT * FROM classroom WHERE capacity >= 50", "Aulas con capacidad mayor o igual a 50"),
            ("SELECT course.title, prereq.prereq_id FROM course JOIN prereq ON course.course_id = prereq.course_id", "Cursos con sus prerequisitos"),
            ("SELECT AVG(salary) AS avg_salary FROM instructor", "Salario promedio de los instructores")
        ]

    def ejecutar_consulta(self):
        index = self.consultas_disponibles.currentIndex()
        consulta_sql, descripcion = self.consultas[index]
        try:
            # Ejecutar la consulta seleccionada
            conexion = engine.connect()
            resultados = conexion.execute(consulta_sql).fetchall()
            columnas = conexion.execute(consulta_sql).keys()
            conexion.close()

            # Mostrar resultados en la tabla
            self.resultados.setColumnCount(len(columnas))
            self.resultados.setRowCount(len(resultados))
            self.resultados.setHorizontalHeaderLabels(columnas)
            for i, fila in enumerate(resultados):
                for j, valor in enumerate(fila):
                    self.resultados.setItem(i, j, QTableWidgetItem(str(valor)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta: {e}")

# Definiciones de tablas (no modificadas)
class Classroom(Base):
    __tablename__ = 'classroom'
    building = Column(String(15), primary_key=True)
    room_number = Column(String(7), primary_key=True)
    capacity = Column(Numeric(4, 0))

class Department(Base):
    __tablename__ = 'department'
    dept_name = Column(String(20), primary_key=True)
    building = Column(String(15))
    budget = Column(Numeric(12, 2), CheckConstraint('budget > 0'))

class Course(Base):
    __tablename__ = 'course'
    course_id = Column(String(8), primary_key=True)
    title = Column(String(50))
    dept_name = Column(String(20), ForeignKey('department.dept_name', ondelete='SET NULL'))
    credits = Column(Numeric(2, 0), CheckConstraint('credits > 0'))

class Instructor(Base):
    __tablename__ = 'instructor'
    ID = Column(String(5), primary_key=True)
    name = Column(String(20), nullable=False)
    dept_name = Column(String(20), ForeignKey('department.dept_name', ondelete='SET NULL'))
    salary = Column(Numeric(8, 2), CheckConstraint('salary >= 29000'))

class Section(Base):
    __tablename__ = 'section'
    course_id = Column(String(8), ForeignKey('course.course_id', ondelete='CASCADE'), primary_key=True)
    sec_id = Column(String(8), primary_key=True)
    semester = Column(String(6), primary_key=True)
    year = Column(Numeric(4, 0), primary_key=True)

class Teaches(Base):
    __tablename__ = 'teaches'
    ID = Column(String(5), ForeignKey('instructor.ID', ondelete='CASCADE'), primary_key=True)
    course_id = Column(String(8), primary_key=True)
    sec_id = Column(String(8), primary_key=True)
    semester = Column(String(6), primary_key=True)
    year = Column(Numeric(4, 0), primary_key=True)

class Student(Base):
    __tablename__ = 'student'
    ID = Column(String(5), primary_key=True)
    name = Column(String(20), nullable=False)
    dept_name = Column(String(20), ForeignKey('department.dept_name', ondelete='SET NULL'))
    tot_cred = Column(Numeric(3, 0), CheckConstraint('tot_cred >= 0'))

class Takes(Base):
    __tablename__ = 'takes'
    ID = Column(String(5), ForeignKey('student.ID', ondelete='CASCADE'), primary_key=True)
    course_id = Column(String(8), primary_key=True)
    sec_id = Column(String(8), primary_key=True)
    semester = Column(String(6), primary_key=True)
    year = Column(Numeric(4, 0), primary_key=True)
    grade = Column(String(2))

class Advisor(Base):
    __tablename__ = 'advisor'
    s_ID = Column(String(5), ForeignKey('student.ID', ondelete='CASCADE'), primary_key=True)
    i_ID = Column(String(5), ForeignKey('instructor.ID', ondelete='SET NULL'))

class TimeSlot(Base):
    __tablename__ = 'time_slot'
    time_slot_id = Column(String(4), primary_key=True)
    day = Column(String(1), primary_key=True)
    start_hr = Column(Numeric(2), CheckConstraint('start_hr >= 0 AND start_hr < 24'), primary_key=True)
    start_min = Column(Numeric(2), CheckConstraint('start_min >= 0 AND start_min < 60'), primary_key=True)
    end_hr = Column(Numeric(2), CheckConstraint('end_hr >= 0 AND end_hr < 24'))
    end_min = Column(Numeric(2), CheckConstraint('end_min >= 0 AND end_min < 60'))

class Prereq(Base):
    __tablename__ = 'prereq'
    course_id = Column(String(8), ForeignKey('course.course_id', ondelete='CASCADE'), primary_key=True)
    prereq_id = Column(String(8), ForeignKey('course.course_id', ondelete='CASCADE'), primary_key=True)

# Configuración de relaciones
Department.courses = relationship('Course', back_populates='department', cascade='all, delete-orphan')
Department.instructors = relationship('Instructor', cascade='all, delete-orphan')
Department.students = relationship('Student', cascade='all, delete-orphan')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    programa = VentanaPrincipal()
    sys.exit(app.exec())

#a
#a
#b
#b
#c
#c
#hago esto para ver que el commit se haga bien