from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine, text, MetaData, Column, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
import sys

metadata = MetaData()
Base = declarative_base()

# Clase para solicitar credenciales
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conexión a la Base de Datos")
        self.setGeometry(500, 300, 300, 150)

        layout = QFormLayout(self)

        # Campos de entrada para usuario, contraseña y base de datos
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.database_input = QLineEdit(self)
        self.host_input = QLineEdit(self)

        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Ocultar texto de la contraseña
        self.database_input.setPlaceholderText("university")
        self.host_input.setPlaceholderText("localhost")

        layout.addRow("Usuario:", self.username_input)
        layout.addRow("Contraseña:", self.password_input)
        layout.addRow("Base de datos:", self.database_input)
        layout.addRow("Host:", self.host_input)

        # Botón para conectar
        self.boton_conectar = QPushButton("Conectar", self)
        self.boton_conectar.clicked.connect(self.accept)
        layout.addWidget(self.boton_conectar)

        self.setLayout(layout)

    def get_credentials(self):
        return {
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "database": self.database_input.text() or "university",
            "host": self.host_input.text() or "localhost",
        }

# Clase principal de la interfaz
class VentanaPrincipal(QMainWindow):
    def __init__(self, database_url):
        super().__init__()
        self.database_url = database_url
        self.engine = create_engine(self.database_url)
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
        for i, (consulta_sql, descripcion) in enumerate(self.consultas):
            self.consultas_disponibles.addItem(f"Consulta {i + 1}")
        self.layout.addWidget(self.consultas_disponibles)

        # QLabel para mostrar la descripción de la consulta seleccionada
        self.descripcion_consulta = QLabel()
        self.layout.addWidget(self.descripcion_consulta)

        # Conectar el cambio de selección del ComboBox a una función
        self.consultas_disponibles.currentIndexChanged.connect(self.actualizar_descripcion)

        # Botón para ejecutar la consulta
        self.boton_consultar = QPushButton("Ejecutar Consulta")
        self.boton_consultar.clicked.connect(self.ejecutar_consulta)
        self.layout.addWidget(self.boton_consultar)

        # Tabla para mostrar resultados
        self.resultados = QTableWidget()
        self.layout.addWidget(self.resultados)

        # Inicializar la descripción con la primera consulta
        self.actualizar_descripcion(0)

    def obtener_consultas(self):
        # Lista de consultas (10 en total)
        return [
            (
                text("""
                SELECT S.name
                FROM student S
                WHERE NOT EXISTS (
                    SELECT C.course_id
                    FROM course C
                    WHERE C.dept_name = 'Computer Science'
                    AND NOT EXISTS (
                        SELECT T.ID
                        FROM takes T
                        WHERE T.ID = S.ID AND T.course_id = C.course_id
                    )
                )
                """),
                "Estudiantes que han tomado todos los cursos de 'Computer Science'"
            ),
            (
                text("""
                SELECT I.name
                FROM instructor I
                WHERE NOT EXISTS (
                    SELECT *
                    FROM teaches T
                    WHERE T.ID = I.ID
                )
                """),
                "Instructores que nunca han enseñado un curso"
            ),
            (
                text("""
                SELECT dept_name
                FROM instructor
                GROUP BY dept_name
                HAVING AVG(salary) = (
                    SELECT MAX(avg_salary)
                    FROM (
                        SELECT dept_name, AVG(salary) AS avg_salary
                        FROM instructor
                        GROUP BY dept_name
                    ) AS dept_avg
                )
                """),
                "Departamentos con el salario promedio más alto de instructores"
            ),
            (
                text("""
                SELECT DISTINCT S.name
                FROM student S
                JOIN takes T ON S.ID = T.ID
                JOIN teaches Te ON T.course_id = Te.course_id AND T.sec_id = Te.sec_id AND T.semester = Te.semester AND T.year = Te.year
                JOIN instructor I ON Te.ID = I.ID
                WHERE I.name = 'Dr. Smith'
                """),
                "Estudiantes que han tomado al menos un curso impartido por 'Dr. Smith'"
            ),
            (
                text("""
                SELECT C.course_id, C.title
                FROM course C
                WHERE NOT EXISTS (
                    SELECT *
                    FROM takes T
                    WHERE T.course_id = C.course_id
                )
                """),
                "Cursos que no han sido tomados por ningún estudiante"
            ),
            (
                text("""
                SELECT D.dept_name, SUM(C.credits) AS total_credits
                FROM department D
                JOIN student S ON D.dept_name = S.dept_name
                JOIN takes T ON S.ID = T.ID
                JOIN course C ON T.course_id = C.course_id
                GROUP BY D.dept_name
                """),
                "Total de créditos tomados por estudiantes en cada departamento"
            ),
            (
                text("""
                SELECT I.dept_name, I.name, I.salary
                FROM instructor I
                WHERE I.salary = (
                    SELECT MAX(salary)
                    FROM instructor
                    WHERE dept_name = I.dept_name
                )
                """),
                "Instructores con el salario más alto en su departamento"
            ),
            (
                text("""
                SELECT dept_name, AVG(credits) AS avg_credits
                FROM course
                GROUP BY dept_name
                """),
                "Créditos promedio de los cursos por departamento"
            ),
            (
                text("""
                SELECT DISTINCT I.name, I.dept_name AS instructor_dept, C.dept_name AS course_dept
                FROM instructor I
                JOIN teaches Te ON I.ID = Te.ID
                JOIN course C ON Te.course_id = C.course_id
                WHERE I.dept_name <> C.dept_name
                """),
                "Instructores que enseñan cursos en departamentos distintos al suyo"
            ),
            (
                text("""
                SELECT dept_name
                FROM course
                GROUP BY dept_name
                HAVING COUNT(*) = (
                    SELECT MAX(course_count)
                    FROM (
                        SELECT dept_name, COUNT(*) AS course_count
                        FROM course
                        GROUP BY dept_name
                    ) AS dept_courses
                )
                """),
                "Departamentos que ofrecen el mayor número de cursos"
            )
        ]

    def actualizar_descripcion(self, index):
        _, descripcion = self.consultas[index]
        self.descripcion_consulta.setText(f"Descripción: {descripcion}")

    def ejecutar_consulta(self):
        index = self.consultas_disponibles.currentIndex()
        consulta_sql, descripcion = self.consultas[index]
        try:
            # Ejecutar la consulta seleccionada
            with self.engine.connect() as conexion:
                resultados = conexion.execute(consulta_sql).fetchall()

                # Validar si hay resultados
                if not resultados:
                    QMessageBox.information(self, "Resultados", "La consulta no devolvió resultados.")
                    self.resultados.clear()
                    return

                # Obtener nombres de columnas
                columnas = resultados[0]._fields if hasattr(resultados[0], '_fields') else resultados[0].keys()

                # Mostrar resultados en la tabla
                self.resultados.setColumnCount(len(columnas))
                self.resultados.setRowCount(len(resultados))
                self.resultados.setHorizontalHeaderLabels(columnas)
                for i, fila in enumerate(resultados):
                    for j, valor in enumerate(fila):
                        self.resultados.setItem(i, j, QTableWidgetItem(str(valor)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta: {e}")

# Configuración de tablas
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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Mostrar ventana de inicio de sesión
    login_dialog = LoginDialog()
    if login_dialog.exec():
        credentials = login_dialog.get_credentials()

        # Crear URL de la base de datos
        DATABASE_URL = f"mysql+pymysql://{credentials['username']}:{credentials['password']}@{credentials['host']}/{credentials['database']}"
        
        # Iniciar la aplicación principal
        programa = VentanaPrincipal(DATABASE_URL)
        sys.exit(app.exec())
    else:
        sys.exit()
