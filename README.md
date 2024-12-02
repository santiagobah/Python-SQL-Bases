# Explicación del Código: Interfaz con PyQt6 para Consultas Predefinidas en SQLAlchemy

## Este documento detalla minuciosamente el funcionamiento de cada sección del código proporcionado. El código desarrolla una aplicación gráfica para ejecutar consultas predefinidas y personalizadas a la base de datos 'university' utilizando PyQt6 y SQLAlchemy.

### Realizado por: 
- Gabriel Álvarez Mendoza
- Santiago Bañuelos Hernández
---

## Índice

1. [Importación de Módulos](#importación-de-módulos)
2. [Configuración Inicial](#configuración-inicial)
3. [Clase `LoginDialog`](#clase-logindialog)
4. [Clase `VentanaPrincipal`](#clase-ventanaprincipal)
    - [Estructura General](#estructura-general)
    - [Función `mostrar_principal`](#función-mostrar_principal)
    - [Función `obtener_consultas`](#función-obtener_consultas)
    - [Función `actualizar_descripcion`](#función-actualizar_descripcion)
    - [Función `ejecutar_consulta`](#función-ejecutar_consulta)
    - [Función `ejecutar_consulta_personalizada`](#función-ejecutar_consulta_personalizada)
5. [Clase `ConsultaPersonalizadaDialog`](#clase-consultapersonalizadadialog)
6. [Problema en la Consulta 6](#problema-en-la-consulta-6)
7. [Resumen y Mejoras Sugeridas](#resumen-y-mejoras-sugeridas)

---

## Importación de Módulos

```python
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QPlainTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine, MetaData, Column, String, Numeric, ForeignKey, text, CheckConstraint, func, and_, or_, not_, exists, select
from sqlalchemy.orm import declarative_base, sessionmaker
import sys

```

	•	PyQt6: Se utiliza para crear la interfaz gráfica de usuario (GUI).
	•	SQLAlchemy: Framework ORM (Object-Relational Mapping) que simplifica la interacción con bases de datos relacionales.
	•	sys: Permite acceder a argumentos del sistema y manejar el flujo de la aplicación.

## Configuración Inicial

metadata = MetaData()
Base = declarative_base()

	•	MetaData: Es la colección de esquemas de tabla necesarios para interactuar con la base de datos.
	•	declarative_base: Clase base que permite definir modelos ORM.

## Clase LoginDialog

### Propósito


#### Esta clase crea un diálogo para que el usuario introduzca sus credenciales de conexión a la base de datos.

#### Código
```python
class LoginDialog(QDialog):
    def __init__(self):
        ...
```
## Componentes

	1.	Entrada de Datos:
	•	Campos para usuario, contraseña, base de datos y host.
	•	self.password_input.setEchoMode(QLineEdit.EchoMode.Password) oculta el texto de la contraseña.
	2.	Botón de Conexión:
	•	El botón Conectar invoca self.accept() para capturar las credenciales.

## Función get_credentials
```python
def get_credentials(self):
    ...

	•	Devuelve un diccionario con los datos ingresados, asignando valores predeterminados para base de datos y host si están vacíos.
```
## Clase VentanaPrincipal

## Estructura General

### Esta clase representa la ventana principal de la aplicación y coordina la interacción con la base de datos.
```python
class VentanaPrincipal(QMainWindow):
    def __init__(self, database_url):
        ...
```
	1.	Inicialización:
	•	Recibe la URL de conexión a la base de datos.
	•	Crea un motor de conexión (create_engine).
	2.	Inicio del Programa:
```python
def iniciar_programa(self):
    ...

	•	Configura el tamaño y título de la ventana.
	•	Llama a mostrar_principal para desplegar los elementos de la interfaz.
```
## Función mostrar_principal

### Despliega los elementos de la interfaz gráfica.

## Componentes

	1.	ComboBox para Consultas:
	•	Muestra una lista desplegable con las consultas predefinidas.
	•	currentIndexChanged actualiza la descripción mostrada.
	2.	Botones:
	•	Ejecutar Consulta: Llama a ejecutar_consulta.
	•	Crear Consulta: Llama a ejecutar_consulta_personalizada.
	3.	Tabla de Resultados:
	•	Muestra los datos devueltos por las consultas.

## Función obtener_consultas

```python
def obtener_consultas(self):
    ...
```

#### Crea una lista de consultas SQL predefinidas, cada una asociada a una descripción. Utiliza ORM para definir consultas complejas como:

	1.	Número de estudiantes por departamento.
	2.	Cursos sin prerrequisitos en un semestre específico.
	3.	Instructores con múltiples departamentos asignados.

### Cada consulta retorna un objeto ORM listo para ejecutarse.

## Función actualizar_descripcion

```python
def actualizar_descripcion(self, index):
    ...
```

### Actualiza la descripción de la consulta seleccionada en el ComboBox.

## Función ejecutar_consulta

```python
def ejecutar_consulta(self):
    ...

	1.	Ejecución de Consulta:
	•	Ejecuta la consulta seleccionada utilizando session.query.
	•	Si no devuelve resultados, muestra un mensaje con QMessageBox.
	2.	Presentación de Resultados:
	•	Crea una tabla con columnas y filas basadas en los datos devueltos.
	•	Ajusta el tamaño de las columnas automáticamente.
	3.	Manejo de Errores:
	•	Captura excepciones y muestra un mensaje de error.
```

## Función ejecutar_consulta_personalizada

### Permite al usuario ingresar consultas SQL arbitrarias.

## Clase ConsultaPersonalizadaDialog

### Crea un diálogo para que el usuario introduzca una consulta personalizada. Su funcionalidad es similar al diálogo de inicio.

## Problema en la Consulta 6

### La consulta 6 está diseñada para buscar cursos sin prerrequisitos en un semestre específico. Sin embargo, no retorna resultados debido a un error en los datos o en la lógica:

```python
select(Prereq.course_id).where(Prereq.course_id == Course.course_id)

	•	La consulta asume que existen cursos en la tabla Prereq, pero esto puede no cumplirse.
	•	El filtro para Section.semester y Section.year puede no coincidir con los datos.
```
## Conclusión 

### Este proyecto ha sido una experiencia enriquecedora al combinar el uso de PyQt6 para el diseño de una interfaz gráfica intuitiva con SQLAlchemy para la gestión eficiente de bases de datos. La aplicación desarrollada permite realizar consultas predefinidas y personalizadas de manera ágil, facilitando la interacción del usuario con la información almacenada.

### A lo largo del proceso, enfrentamos desafíos que nos ayudaron a fortalecer habilidades clave, como el manejo de errores y la validación de datos. Además, la implementación de programación orientada a objetos garantizó que el código fuera modular y fácil de mantener. Cada paso del desarrollo nos permitió aprender más sobre la integración de tecnologías modernas para resolver problemas prácticos.

### En resumen, esta aplicación cumple con los objetivos planteados y sienta las bases para futuros desarrollos. Si bien ya es funcional, tiene un gran potencial para seguir evolucionando, incorporando características adicionales que mejoren la experiencia del usuario y amplíen sus capacidades. Este proyecto refleja el compromiso de utilizar la tecnología como una herramienta para crear soluciones innovadoras y efectivas.
