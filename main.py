from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QPlainTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine, MetaData, Column, String, Numeric, ForeignKey, text, CheckConstraint, func, and_, or_, not_, exists, select
from sqlalchemy.orm import declarative_base, sessionmaker
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
        
        # Botón para ejecutar consulta personalizada
        self.boton_consultapropia = QPushButton("Crear Consulta")
        self.boton_consultapropia.clicked.connect(self.ejecutar_consulta_personalizada)
        self.layout.addWidget(self.boton_consultapropia)

        # Tabla para mostrar resultados
        self.resultados = QTableWidget()
        self.layout.addWidget(self.resultados)

        # Inicializar la descripción con la primera consulta
        self.actualizar_descripcion(0)

    def obtener_consultas(self):
        # Crear una sesión de SQLAlchemy
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Lista de consultas complejas utilizando ORM
        return [
            (
                # Consulta 1: Número de estudiantes por departamento, ordenados de mayor a menor
                session.query(
                    Department.dept_name.label('Departamento'),
                    func.count(Student.ID).label('Número de Estudiantes')
                ).join(Student, Department.dept_name == Student.dept_name).group_by(
                    Department.dept_name
                ).order_by(
                    func.count(Student.ID).desc()
                ),
                "Número de estudiantes por departamento, ordenados de mayor a menor"
            ),
            (
                # Consulta 2: Cursos con más de 3 créditos y el número de secciones que tienen
                session.query(
                    Course.title.label('Curso'),
                    func.count(Section.sec_id).label('Número de Secciones')
                ).join(Section, Course.course_id == Section.course_id).filter(
                    Course.credits > 3
                ).group_by(
                    Course.course_id, Course.title
                ),
                "Cursos con más de 3 créditos y el número de secciones que tienen"
            ),
            (
                # Consulta 3: Instructores que han enseñado en más de un departamento
                session.query(
                    Instructor.name.label('Instructor'),
                    func.count(Department.dept_name.distinct()).label('Departamentos Diferentes')
                ).join(Teaches, Instructor.ID == Teaches.ID).join(
                    Course, Teaches.course_id == Course.course_id
                ).join(
                    Department, Course.dept_name == Department.dept_name
                ).group_by(
                    Instructor.ID, Instructor.name
                ).having(
                    func.count(Department.dept_name.distinct()) > 1
                ),
                "Instructores que han enseñado en más de un departamento"
            ),
            (
                # Consulta 4: Estudiantes asesorados por un profesor que también les imparte clases
                session.query(
                    Student.name.label('Estudiante'),
                    Instructor.name.label('Asesor'),
                    Course.title.label('Curso Tomado')
                ).join(
                    Advisor, Student.ID == Advisor.s_ID
                ).join(
                    Instructor, Advisor.i_ID == Instructor.ID
                ).join(
                    Takes, Student.ID == Takes.ID
                ).join(
                    Teaches,
                    and_(
                        Teaches.ID == Instructor.ID,
                        Teaches.course_id == Takes.course_id,
                        Teaches.sec_id == Takes.sec_id,
                        Teaches.semester == Takes.semester,
                        Teaches.year == Takes.year
                    )
                ).join(
                    Course, Course.course_id == Takes.course_id
                ).distinct(),
                "Estudiantes asesorados por un profesor que también les imparte clases"
            ),
            (
                # Consulta 5: Promedio de salarios por departamento, mostrando solo los departamentos con promedio superior al promedio general
                session.query(
                    Department.dept_name.label('Departamento'),
                    func.avg(Instructor.salary).label('Salario Promedio')
                ).join(Instructor, Department.dept_name == Instructor.dept_name).group_by(
                    Department.dept_name
                ).having(
                    func.avg(Instructor.salary) > session.query(func.avg(Instructor.salary)).scalar_subquery()
                ),
                "Departamentos con salario promedio superior al promedio general"
            ),
            (
                # Consulta 6: Cursos que no tienen prerrequisitos y se imparten en el semestre 'Fall' de 2017
                session.query(
                    Course.title.label('Curso'),
                    Section.sec_id.label('Sección'),
                    Section.semester.label('Semestre'),
                    Section.year.label('Año')
                ).join(Section, Course.course_id == Section.course_id).filter(
                    and_(
                        ~exists(
                            select(Prereq.course_id).where(Prereq.course_id == Course.course_id)
                        ),
                        Section.semester == 'Fall',
                        Section.year == 2017
                    )
                ),
                "Cursos sin prerrequisitos impartidos en otoño de 2017"
            ),
            (
                # Consulta 7: Nombre de estudiantes y sus asesores, incluyendo estudiantes sin asesor asignado
                session.query(
                    Student.name.label('Estudiante'),
                    Instructor.name.label('Asesor')
                ).outerjoin(Advisor, Student.ID == Advisor.s_ID).outerjoin(
                    Instructor, Advisor.i_ID == Instructor.ID
                ),
                "Estudiantes y sus asesores, incluyendo aquellos sin asesor"
            ),
            (
                # Consulta 8: Instructores que enseñan más de un curso
                session.query(
                    Instructor.name.label('Instructor'),
                    func.count(Teaches.course_id.distinct()).label('Número de Cursos')
                ).join(
                    Teaches, Instructor.ID == Teaches.ID
                ).group_by(
                    Instructor.ID, Instructor.name
                ).having(
                    func.count(Teaches.course_id.distinct()) > 1
                ),
                "Instructores que enseñan más de un curso"
            ),
            (
                # Consulta 9: Estudiantes que han tomado cursos con instructores de departamentos diferentes al suyo
                session.query(
                    Student.name.label('Estudiante'),
                    Course.title.label('Curso'),
                    Instructor.name.label('Instructor'),
                    Student.dept_name.label('Dept. Estudiante'),
                    Instructor.dept_name.label('Dept. Instructor')
                ).join(
                    Takes, Student.ID == Takes.ID
                ).join(
                    Section, and_(
                        Takes.course_id == Section.course_id,
                        Takes.sec_id == Section.sec_id,
                        Takes.semester == Section.semester,
                        Takes.year == Section.year
                    )
                ).join(
                    Teaches, and_(
                        Section.course_id == Teaches.course_id,
                        Section.sec_id == Teaches.sec_id,
                        Section.semester == Teaches.semester,
                        Section.year == Teaches.year
                    )
                ).join(
                    Instructor, Teaches.ID == Instructor.ID
                ).join(
                    Course, Course.course_id == Takes.course_id
                ).filter(
                    Student.dept_name != Instructor.dept_name
                ),
                "Estudiantes que han tomado cursos con instructores de departamentos diferentes al suyo"
            ),
            (
                # Consulta 10: Capacidad total por edificio, mostrando solo aquellos con capacidad total mayor a 100
                session.query(
                    Classroom.building.label('Edificio'),
                    func.sum(Classroom.capacity).label('Capacidad Total')
                ).group_by(
                    Classroom.building
                ).having(
                    func.sum(Classroom.capacity) > 100
                ),
                "Capacidad total por edificio con capacidad mayor a 100"
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
            resultados = consulta_sql.all()

            # Validar si hay resultados
            if not resultados:
                QMessageBox.information(self, "Resultados", "La consulta no devolvió resultados.")
                self.resultados.clear()
                return

            # Obtener nombres de columnas
            if hasattr(resultados[0], '_fields'):
                columnas = resultados[0]._fields
            else:
                columnas = resultados[0].keys()

            # Mostrar resultados en la tabla
            self.resultados.setColumnCount(len(columnas))
            self.resultados.setRowCount(len(resultados))
            self.resultados.setHorizontalHeaderLabels(columnas)
            for i, fila in enumerate(resultados):
                for j, valor in enumerate(fila):
                    valor_mostrado = str(valor) if valor is not None else ''
                    self.resultados.setItem(i, j, QTableWidgetItem(valor_mostrado))
            # Ajustar el tamaño de las columnas
            self.resultados.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta: {e}")
            

    def ejecutar_consulta_personalizada(self):
        # Crear y mostrar el diálogo para ingresar la consulta
        dialogo = ConsultaPersonalizadaDialog()
        if dialogo.exec():
            consulta_usuario = dialogo.get_query()
            try:
                # Ejecutar la consulta ingresada por el usuario
                with self.engine.connect() as conexion:
                    resultados = conexion.execute(text(consulta_usuario)).fetchall()

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
                            valor_mostrado = str(valor) if valor is not None else ''
                            self.resultados.setItem(i, j, QTableWidgetItem(valor_mostrado))
                    # Ajustar el tamaño de las columnas
                    self.resultados.resizeColumnsToContents()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo ejecutar la consulta: {e}")

        
class ConsultaPersonalizadaDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consulta Personalizada")
        self.setGeometry(600, 350, 600, 400)

        layout = QVBoxLayout(self)

        # Campo de texto para ingresar la consulta
        self.texto_consulta = QPlainTextEdit(self)
        layout.addWidget(QLabel("Escriba su consulta SQL:"))
        layout.addWidget(self.texto_consulta)

        # Botones de acción
        botones = QHBoxLayout()
        self.boton_ejecutar = QPushButton("Ejecutar")
        self.boton_cancelar = QPushButton("Cancelar")
        botones.addWidget(self.boton_ejecutar)
        botones.addWidget(self.boton_cancelar)
        layout.addLayout(botones)

        self.boton_ejecutar.clicked.connect(self.accept)
        self.boton_cancelar.clicked.connect(self.reject)

        self.setLayout(layout)
    
    def get_query(self):
        return self.texto_consulta.toPlainText()


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
