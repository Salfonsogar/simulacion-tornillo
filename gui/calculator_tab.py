#!/usr/bin/env python3
"""
Pestaña de Calculadora - Interfaz de Cálculo del Tornillo

Cette pestaña permite al usuario ingresar los parámetros físicos del tornillo
y obtener los resultados calculados. Incluye validación en tiempo real
y alertas visuales para errores.

Componentes:
- QLineEdit para entrada de datos
- Labels con unidades (N, m, grados)
- Área de resultados con formato destacado
- Botones de acción

Autor: Simulador de Tornillo
Fecha: 2026
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QLineEdit, QPushButton, QGroupBox,
                            QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette

import math


class CalculatorTab(QWidget):
    """
    Pestaña de calculadora para el tornillo.

    Permite al usuario ingresar:
    - Fuerza de entrada (F_entrada)
    - Radio del brazo (r)
    - Paso de rosca (L)
    - Ángulo de rotación (opcional)

    Y obtener:
    - Ventaja mecánica (VM)
    - Fuerza de salida (F_salida)
    - Desplazamiento lineal (Δx)
    """

    # Señal para notificar cálculo exitoso
    calculo_realizado = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Inicializa la pestaña de calculadora."""
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Estilo general
        self.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 12px;
            }
            QLabel titulo {
                color: #0078D4;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel resultado {
                color: #0078D4;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                color: #333333;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078D4;
            }
            QLineEdit.error {
                border: 1px solid #D32F2F;
                background-color: #FFEBEE;
            }
            QPushButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton#btn_limpiar {
                background-color: #757575;
                color: #FFFFFF;
            }
            QPushButton#btn_limpiar:hover {
                background-color: #616161;
            }
            QPushButton#btn_default {
                background-color: #00ACC1;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333333;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #0078D4;
            }
        """)

        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Grupo de Entrada
        grupo_entrada = self._crear_grupo_entrada()
        layout_principal.addWidget(grupo_entrada)

        # Grupo de Resultados
        grupo_resultados = self._crear_grupo_resultados()
        layout_principal.addWidget(grupo_resultados)

        # Botones
        botones = self._crear_botones()
        layout_principal.addWidget(botones)

        # Espacio expandible
        layout_principal.addStretch()

        self.setLayout(layout_principal)

    def _crear_grupo_entrada(self) -> QGroupBox:
        """Crea el grupo de parámetros de entrada."""
        grupo = QGroupBox("Parámetros de Entrada")
        layout = QGridLayout()
        layout.setSpacing(12)

        # Fuerza de entrada
        layout.addWidget(QLabel("Fuerza de Entrada (F_entrada):"), 0, 0)
        self.input_fuerza = QLineEdit()
        self.input_fuerza.setPlaceholderText("Ej: 10.0")
        self.input_fuerza.setToolTip("Fuerza aplicada en Newtons (N)")
        layout.addWidget(self.input_fuerza, 0, 1)
        layout.addWidget(QLabel("N"), 0, 2)

        # Radio del brazo
        layout.addWidget(QLabel("Radio del Brazo (r):"), 1, 0)
        self.input_radio = QLineEdit()
        self.input_radio.setPlaceholderText("Ej: 0.05")
        self.input_radio.setToolTip("Radio de giro en metros (m)")
        layout.addWidget(self.input_radio, 1, 1)
        layout.addWidget(QLabel("m"), 1, 2)

        # Paso de rosca
        layout.addWidget(QLabel("Paso de Rosca (L):"), 2, 0)
        self.input_paso = QLineEdit()
        self.input_paso.setPlaceholderText("Ej: 0.002")
        self.input_paso.setToolTip("Paso de la rosca en metros (m)")
        layout.addWidget(self.input_paso, 2, 1)
        layout.addWidget(QLabel("m"), 2, 2)

        # Ángulo de rotación
        layout.addWidget(QLabel("Ángulo de Rotación:"), 3, 0)
        self.input_angulo = QLineEdit()
        self.input_angulo.setPlaceholderText("360 (opcional)")
        self.input_angulo.setToolTip("Ángulo de rotación en grados")
        layout.addWidget(self.input_angulo, 3, 1)
        layout.addWidget(QLabel("°"), 3, 2)

        grupo.setLayout(layout)
        return grupo

    def _crear_grupo_resultados(self) -> QGroupBox:
        """Crea el grupo de resultados."""
        grupo = QGroupBox("Resultados")
        layout = QGridLayout()
        layout.setSpacing(12)

        # VM
        layout.addWidget(QLabel("Ventaja Mecánica (VM):"), 0, 0)
        self.label_vm = QLabel("—")
        self.label_vm.setObjectName("resultado")
        layout.addWidget(self.label_vm, 0, 1)

        # Fuerza de salida
        layout.addWidget(QLabel("Fuerza de Salida (F_salida):"), 1, 0)
        self.label_f_salida = QLabel("—")
        self.label_f_salida.setObjectName("resultado")
        layout.addWidget(self.label_f_salida, 1, 1)

        # Desplazamiento
        layout.addWidget(QLabel("Desplazamiento Lineal (Δx):"), 2, 0)
        self.label_desplazamiento = QLabel("—")
        self.label_desplazamiento.setObjectName("resultado")
        layout.addWidget(self.label_desplazamiento, 2, 1)

        # Mensaje de estado
        layout.addWidget(QLabel("Estado:"), 3, 0)
        self.label_estado = QLabel("Esperando datos...")
        self.label_estado.setStyleSheet("color: #E65100;")
        layout.addWidget(self.label_estado, 3, 1)

        grupo.setLayout(layout)
        return grupo

    def _crear_botones(self) -> QWidget:
        """Crea los botones de acción."""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Botón calcular
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_calcular)

        # Botón valores por defecto
        self.btn_default = QPushButton("Valores por Defecto")
        self.btn_default.setObjectName("btn_default")
        self.btn_default.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_default)

        # Botón limpiar
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_limpiar)

        container.setLayout(layout)
        return container

    def _connect_signals(self):
        """Conecta las señales de los botones."""
        self.btn_calcular.clicked.connect(self._on_calcular)
        self.btn_limpiar.clicked.connect(self._on_limpiar)
        self.btn_default.clicked.connect(self._on_default)
        self.input_fuerza.editingFinished.connect(self._validar_campo_fuerza)
        self.input_radio.editingFinished.connect(self._validar_campo_radio)
        self.input_paso.editingFinished.connect(self._validar_campo_paso)

    def _on_calcular(self):
        """Maneja el evento de cálculo."""
        try:
            # Obtener valores
            f_entrada = float(self.input_fuerza.text())
            radio = float(self.input_radio.text())
            paso = float(self.input_paso.text())
            angulo = float(self.input_angulo.text()) if self.input_angulo.text() else 360.0

            # Importar calculadora
            from physics.screw_physics import ScrewCalculator, ScrewPhysicsError

            # Calcular
            resultados = ScrewCalculator.calcular_todo(f_entrada, radio, paso, angulo)

            # Mostrar resultados
            self.label_vm.setText(f"{resultados['vm']:.4f}")
            self.label_f_salida.setText(f"{resultados['f_salida']:.4f} N")
            self.label_desplazamiento.setText(f"{resultados['desplazamiento']:.6f} m")

            # Mensaje de éxito
            self.label_estado.setText("✓ Cálculo exitoso")
            self.label_estado.setStyleSheet("color: #00FF7F;")

            # Emitir señal
            self.calculo_realizado.emit(resultados)

        except ValueError:
            self._mostrar_error("[CRITICAL ERROR] Ingrese valores numéricos válidos")
        except ScrewPhysicsError as e:
            self._mostrar_error(str(e))
        except Exception as e:
            self._mostrar_error(f"[CRITICAL ERROR] {str(e)}")

    def _on_limpiar(self):
        """Limpia todos los campos."""
        self.input_fuerza.clear()
        self.input_radio.clear()
        self.input_paso.clear()
        self.input_angulo.clear()

        self.label_vm.setText("—")
        self.label_f_salida.setText("—")
        self.label_desplazamiento.setText("—")

        self.label_estado.setText("Esperando datos...")
        self.label_estado.setStyleSheet("color: #E65100;")

        # Quitar estilos de error
        self.input_fuerza.setStyleSheet("")
        self.input_radio.setStyleSheet("")
        self.input_paso.setStyleSheet("")

    def _on_default(self):
        """Carga valores por defecto educativos."""
        # Valores típicos para un tornillo de учебник
        self.input_fuerza.setText("10.0")
        self.input_radio.setText("0.05")
        self.input_paso.setText("0.002")
        self.input_angulo.setText("360")

        self.label_estado.setText("Valores educativos cargados")
        self.label_estado.setStyleSheet("color: #00CED1;")

    def _validar_campo_fuerza(self):
        """Valida el campo de fuerza."""
        try:
            valor = float(self.input_fuerza.text())
            if valor < 0.1 or valor > 10000:
                self.input_fuerza.setObjectName("error")
                self.input_fuerza.setStyleSheet("border: 1px solid #FF4444; background-color: #3D2D2D;")
            else:
                self.input_fuerza.setObjectName("")
                self.input_fuerza.setStyleSheet("")
        except ValueError:
            pass

    def _validar_campo_radio(self):
        """Valida el campo de radio."""
        try:
            valor = float(self.input_radio.text())
            if valor < 0.01 or valor > 1.0:
                self.input_radio.setObjectName("error")
                self.input_radio.setStyleSheet("border: 1px solid #FF4444; background-color: #3D2D2D;")
            else:
                self.input_radio.setObjectName("")
                self.input_radio.setStyleSheet("")
        except ValueError:
            pass

    def _validar_campo_paso(self):
        """Valida el campo de paso."""
        try:
            valor = float(self.input_paso.text())
            if valor <= 0 or valor > 0.05:
                self.input_paso.setObjectName("error")
                self.input_paso.setStyleSheet("border: 1px solid #FF4444; background-color: #3D2D2D;")
            else:
                self.input_paso.setObjectName("")
                self.input_paso.setStyleSheet("")
        except ValueError:
            pass

    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        self.label_estado.setText(mensaje)
        self.label_estado.setStyleSheet("color: #FF4444; font-weight: bold;")

    def obtener_resultados(self) -> dict:
        """Retorna los últimos resultados calculados."""
        return {
            'vm': self.label_vm.text(),
            'f_salida': self.label_f_salida.text(),
            'desplazamiento': self.label_desplazamiento.text()
        }