#!/usr/bin/env python3
"""
Pestaña de Modo Inverso - Reto de Diseño

Esta pestaña implementa la metodología inversa donde el estudiante debe
encontrar los parámetros del tornillo given una carga objetivo.

Flujo del "Reto de Diseño":
1. El usuario define la carga a mover (F_salida necesaria)
2. El programa indica la capacidad máx de F_entrada disponible
3. El estudiante ajusta radio y/o paso para lograr el objetivo
4. Feedback visual: ÉXITO o [CRITICAL ERROR]

Autor: Simulador de Tornillo
Fecha: 2026
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QLineEdit, QPushButton, QGroupBox,
                            QMessageBox, QSizePolicy, QScrollArea,
                            QSlider, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette

import math
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class InverseTab(QWidget):
    """
    Pestaña de Modo Inverso / Reto de Diseño.

    El estudiante debe diseñar un sistema de tornillo que pueda
    mover una carga específica given limitaciones de fuerza.
    """

    # Señal para notificar éxito en el reto
    reto_completado = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Inicializa la pestaña."""
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._setup_ui()
        self._connect_signals()
        self._generar_reto()

    def _setup_ui(self):
        """Configura la interfaz."""
        self.setStyleSheet("""
            QLabel {
                color: #201F1E;
                font-size: 12px;
            }
            QLabel#titulo {
                color: #0078D4;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#subtitulo {
                color: #0078D4;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#objetivo {
                color: #A4262C;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#exito {
                color: #107C10;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#insuficiencia {
                color: #FF6B00;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #EDEBE9;
                border-radius: 4px;
                padding: 8px;
                color: #201F1E;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078D4;
            }
            QLineEdit.error {
                border: 2px solid #A4262C;
                background-color: #FDE7E9;
            }
            QLineEdit.exito {
                border: 2px solid #107C10;
                background-color: #DFF6DD;
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
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton#btn_verificar {
                background-color: #107C10;
            }
            QPushButton#btn_verificar:hover {
                background-color: #0B5A0B;
            }
            QPushButton#btn_nuevo_reto {
                background-color: #FF6B00;
            }
            QPushButton#btn_nuevo_reto:hover {
                background-color: #E65100;
            }
            QGroupBox {
                border: 1px solid #EDEBE9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #201F1E;
                font-size: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #0078D4;
                font-weight: bold;
            }
            QSlider::groove:horizontal {
                border: 1px solid #EDEBE9;
                height: 6px;
                background: #F3F2F1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078D4;
                border: 1px solid #005A9E;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QProgressBar {
                border: 1px solid #EDEBE9;
                border-radius: 4px;
                text-align: center;
                background-color: #F3F2F1;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
            }
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(10)
        layout_principal.setContentsMargins(10, 10, 10, 10)

        titulo = QLabel("🔧 MODO INVERSO: Reto de Diseño")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(titulo)

        descripcion = QLabel(
            "Diseña un tornillo que pueda mover la carga objetivo.\n"
            "Ajusta el radio (r) y el paso (L) para lograr la fuerza necesaria.\n\n"
            "💡 ANALOGÍA CRIPTOGRÁFICA: Encontrar los parámetros correctos (r, L)\n"
            "es como encontrar la 'llave' correcta para AES-256.\n"
            "¡Sin la llave exacta, la resistencia es infinita!"
        )
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("color: #666666; font-size: 11px;")
        layout_principal.addWidget(descripcion)

        self.panel_objetivo = self._crear_panel_objetivo()
        layout_principal.addWidget(self.panel_objetivo)

        self.panel_diseno = self._crear_panel_diseno()
        layout_principal.addWidget(self.panel_diseno)

        self.panel_resultado = self._crear_panel_resultado()
        layout_principal.addWidget(self.panel_resultado)

        botones = self._crear_botones()
        layout_principal.addWidget(botones)

        container.setLayout(layout_principal)
        scroll.setWidget(container)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _crear_panel_objetivo(self) -> QGroupBox:
        """Crea el panel de objetivo del reto."""
        grupo = QGroupBox("Paso 1: Definir Objetivo")
        layout = QGridLayout()
        layout.setSpacing(8)

        layout.addWidget(QLabel("Carga a mover (F_salida necesaria):"), 0, 0)
        self.input_f_salida = QLineEdit()
        self.input_f_salida.setPlaceholderText("Ej: 500.0")
        self.input_f_salida.setToolTip("Fuerza necesaria para mover la carga objetivo en Newtons")
        layout.addWidget(self.input_f_salida, 0, 1)
        layout.addWidget(QLabel("N"), 0, 2)

        layout.addWidget(QLabel("Capacidad máx del motor/usuario:"), 1, 0)
        self.input_f_entrada_max = QLineEdit()
        self.input_f_entrada_max.setPlaceholderText("Ej: 50.0")
        self.input_f_entrada_max.setToolTip("Fuerza máxima que puedes aplicar")
        layout.addWidget(self.input_f_entrada_max, 1, 1)
        layout.addWidget(QLabel("N"), 1, 2)

        self.label_mensaje_objetivo = QLabel("💡 Define Ambos valores y haz clic en 'Generar Reto'")
        self.label_mensaje_objetivo.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.label_mensaje_objetivo, 2, 0, 1, 3)

        grupo.setLayout(layout)
        return grupo

    def _crear_panel_diseno(self) -> QGroupBox:
        """Crea el panel de diseño del estudiante."""
        grupo = QGroupBox("Paso 2: Diseña tu Tornillo")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Ajusta los parámetros para lograr la F_salida necesaria:"))

        layout_radio = QHBoxLayout()
        layout_radio.setSpacing(10)
        label_radio = QLabel("Radio (r):")
        label_radio.setFixedWidth(100)
        layout_radio.addWidget(label_radio)

        self.slider_radio = QSlider(Qt.Orientation.Horizontal)
        self.slider_radio.setMinimum(10)
        self.slider_radio.setMaximum(100)
        self.slider_radio.setValue(50)
        self.slider_radio.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_radio.setTickInterval(10)
        self.slider_radio.setToolTip("Radio del brazo de giro en cm")
        layout_radio.addWidget(self.slider_radio)

        self.label_valor_radio = QLabel("0.050 m")
        self.label_valor_radio.setFixedWidth(80)
        self.label_valor_radio.setStyleSheet("font-weight: bold; color: #7B1FA2;")
        layout_radio.addWidget(self.label_valor_radio)

        self.input_radio = QLineEdit()
        self.input_radio.setPlaceholderText("0.050")
        self.input_radio.setFixedWidth(80)
        self.input_radio.setToolTip("O ingresa directamente el valor en metros")
        layout_radio.addWidget(self.input_radio)

        layout.addLayout(layout_radio)

        layout_paso = QHBoxLayout()
        layout_paso.setSpacing(10)
        label_paso = QLabel("Paso (L):")
        label_paso.setFixedWidth(100)
        layout_paso.addWidget(label_paso)

        self.slider_paso = QSlider(Qt.Orientation.Horizontal)
        self.slider_paso.setMinimum(1)
        self.slider_paso.setMaximum(50)
        self.slider_paso.setValue(10)
        self.slider_paso.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_paso.setTickInterval(10)
        self.slider_paso.setToolTip("Paso de rosca en mm")
        layout_paso.addWidget(self.slider_paso)

        self.label_valor_paso = QLabel("0.002 m")
        self.label_valor_paso.setFixedWidth(80)
        self.label_valor_paso.setStyleSheet("font-weight: bold; color: #7B1FA2;")
        layout_radio.addWidget(self.label_valor_paso)

        self.input_paso = QLineEdit()
        self.input_paso.setPlaceholderText("0.002")
        self.input_paso.setFixedWidth(80)
        self.input_paso.setToolTip("O ingresa directamente el valor en metros")
        layout_paso.addWidget(self.input_paso)

        layout.addLayout(layout_paso)

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setMinimum(0)
        self.barra_progreso.setMaximum(100)
        self.barra_progreso.setValue(0)
        self.barra_progreso.setFormat("%p%")
        layout.addWidget(self.barra_progreso)

        grupo.setLayout(layout)
        return grupo

    def _crear_panel_resultado(self) -> QGroupBox:
        """Crea el panel de resultados."""
        grupo = QGroupBox("Paso 3: Resultado")
        layout = QGridLayout()
        layout.setSpacing(8)

        layout.addWidget(QLabel("VM conseguida:"), 0, 0)
        self.label_vm = QLabel("—")
        self.label_vm.setStyleSheet("font-weight: bold; color: #7B1FA2;")
        layout.addWidget(self.label_vm, 0, 1)

        layout.addWidget(QLabel("F_salida lograda:"), 1, 0)
        self.label_f_salida = QLabel("—")
        self.label_f_salida.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label_f_salida, 1, 1)

        layout.addWidget(QLabel("vs Objetivo:"), 2, 0)
        self.label_objetivo = QLabel("—")
        self.label_objetivo.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label_objetivo, 2, 1)

        self.label_estado = QLabel("🎯 Esperando diseño...")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.label_estado, 3, 0, 1, 2)

        grupo.setLayout(layout)
        return grupo

    def _crear_botones(self) -> QWidget:
        """Crea los botones."""
        container = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.btn_generar_reto = QPushButton("🎲 Generar Reto")
        self.btn_generar_reto.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_generar_reto)

        self.btn_verificar = QPushButton("✓ Verificar Diseño")
        self.btn_verificar.setObjectName("btn_verificar")
        self.btn_verificar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_verificar)

        self.btn_nuevo_reto = QPushButton("🔄 Nuevo Reto")
        self.btn_nuevo_reto.setObjectName("btn_nuevo_reto")
        self.btn_nuevo_reto.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_nuevo_reto)

        container.setLayout(layout)
        return container

    def _connect_signals(self):
        """Conecta las señales."""
        self.btn_generar_reto.clicked.connect(self._generar_reto)
        self.btn_verificar.clicked.connect(self._verificar_diseno)
        self.btn_nuevo_reto.clicked.connect(self._nuevo_reto)

        self.slider_radio.valueChanged.connect(self._on_slider_radio)
        self.slider_paso.valueChanged.connect(self._on_slider_paso)

        self.input_radio.editingFinished.connect(self._on_input_radio)
        self.input_paso.editingFinished.connect(self._on_input_paso)

    def _on_slider_radio(self, valor):
        """Maneja cambios en el slider de radio."""
        radio_m = valor / 1000.0
        self.label_valor_radio.setText(f"{radio_m:.3f} m")
        self.input_radio.setText(f"{radio_m:.3f}")
        self._actualizar_preview()

    def _on_slider_paso(self, valor):
        """Maneja cambios en el slider de paso."""
        paso_m = valor / 10000.0
        self.label_valor_paso.setText(f"{paso_m:.4f} m")
        self.input_paso.setText(f"{paso_m:.4f}")
        self._actualizar_preview()

    def _on_input_radio(self):
        """Maneja entrada manual de radio."""
        try:
            radio = float(self.input_radio.text())
            if 0.01 <= radio <= 1.0:
                self.slider_radio.setValue(int(radio * 1000))
        except ValueError:
            pass

    def _on_input_paso(self):
        """Maneja entrada manual de paso."""
        try:
            paso = float(self.input_paso.text())
            if 0.0001 <= paso <= 0.05:
                self.slider_paso.setValue(int(paso * 10000))
        except ValueError:
            pass

    def _generar_reto(self):
        """Genera un nuevo reto."""
        try:
            self.f_salida_necesaria = float(self.input_f_salida.text() or "500.0")
            self.f_entrada_max = float(self.input_f_entrada_max.text() or "50.0")

            if self.f_salida_necesaria <= 0 or self.f_entrada_max <= 0:
                self.label_mensaje_objetivo.setText("⚠️ Los valores deben ser positivos")
                return

            if self.f_entrada_max >= self.f_salida_necesaria:
                self.label_mensaje_objetivo.setText(
                    f"⚠️ F_entrada ({self.f_entrada_max}N) ≥ F_salida ({self.f_salida_necesaria}N). "
                    f"¡Ya puedes moverla directamente!"
                )
                return

            self.vm_necesaria = self.f_salida_necesaria / self.f_entrada_max
            self.label_mensaje_objetivo.setText(
                f"📐 VM necesaria: ≥ {self.vm_necesaria:.1f}x\n"
                f"💡 Ajusta radio y paso para lograr esa ventaja mecánica"
            )
            self.label_mensaje_objetivo.setStyleSheet("color: #7B1FA2; font-weight: bold;")

            # Restablecer mensaje de éxito de retos anteriores
            self.label_estado.setText("🎯 Esperando diseño...")
            self.label_estado.setStyleSheet("font-size: 14px; padding: 10px; color: #201F1E; background-color: transparent;")

            # Forzar al usuario a mover los parámetros (reiniciar a valores mínimos)
            self.slider_radio.setValue(self.slider_radio.minimum())
            self.slider_paso.setValue(self.slider_paso.maximum()) # El paso máximo es el "peor" para VM
            self.input_radio.setText(f"{self.slider_radio.minimum()/1000.0:.3f}")
            self.input_paso.setText(f"{self.slider_paso.maximum()/10000.0:.4f}")

            self.btn_verificar.setEnabled(True)
            self._actualizar_preview()

        except ValueError:
            self.label_mensaje_objetivo.setText("⚠️ Ingrese valores numéricos válidos")

    def _actualizar_preview(self):
        """Actualiza la preview de valores."""
        try:
            radio = float(self.input_radio.text()) if self.input_radio.text() else 0.05
            paso = float(self.input_paso.text()) if self.input_paso.text() else 0.002

            from physics.screw_physics import ScrewCalculator
            vm = ScrewCalculator.calcular_vm(radio, paso)
            f_salida_logro = self.f_entrada_max * vm if hasattr(self, 'f_entrada_max') else 0

            self.label_vm.setText(f"{vm:.2f}x")
            self.label_f_salida.setText(f"{f_salida_logro:.1f} N")

            if hasattr(self, 'f_salida_necesaria'):
                diferencia = f_salida_logro - self.f_salida_necesaria
                self.label_objetivo.setText(f"{diferencia:+.1f} N")

                if f_salida_logro >= self.f_salida_necesaria:
                    self.barra_progreso.setValue(100)
                else:
                    progreso = min(100, int((f_salida_logro / self.f_salida_necesaria) * 100))
                    self.barra_progreso.setValue(progreso)

        except (ValueError, AttributeError):
            pass

    def _verificar_diseno(self):
        """Verifica si el diseño logra el objetivo."""
        try:
            radio = float(self.input_radio.text())
            paso = float(self.input_paso.text())
            f_entrada = self.f_entrada_max

            from physics.screw_physics import ScrewCalculator, InverseScrewCalculator

            vm = ScrewCalculator.calcular_vm(radio, paso)
            f_salida_logro = ScrewCalculator.calcular_f_salida(f_entrada, vm)

            self.label_vm.setText(f"{vm:.2f}x")
            self.label_f_salida.setText(f"{f_salida_logro:.1f} N")
            self.label_objetivo.setText(f"{f_salida_logro - self.f_salida_necesaria:+.1f} N")

            if f_salida_logro >= self.f_salida_necesaria:
                self.label_estado.setText("🎉 ¡ÉXITO! Has diseñado un tornillo capaz de mover la carga")
                self.label_estado.setStyleSheet(
                    "color: #FFFFFF; background-color: #388E3C; font-size: 16px; "
                    "font-weight: bold; padding: 15px; border-radius: 8px;"
                )
                self.input_radio.setObjectName("exito")
                self.input_paso.setObjectName("exito")
                self.input_radio.setStyleSheet("")
                self.input_paso.setStyleSheet("")
            else:
                diferencia = self.f_salida_necesaria - f_salida_logro
                self.label_estado.setText(
                    f"⚠️ Faltan {diferencia:.1f}N\n"
                    f"💡 Aumenta el radio o reduce el paso"
                )
                self.label_estado.setStyleSheet(
                    "color: #E65100; background-color: #FFF3E0; font-size: 13px; "
                    "padding: 10px; border-radius: 8px;"
                )
                self.input_radio.setObjectName("error")
                self.input_paso.setObjectName("error")

        except ValueError as e:
            self.label_estado.setText(f"⚠️ Error: {e}")
        except Exception as e:
            self.label_estado.setText(f"⚠️ [CRITICAL ERROR]: {e}")

    def _nuevo_reto(self):
        """Genera un nuevo reto aleatorio."""
        import random

        self.f_entrada_max = random.uniform(10, 100)
        self.f_salida_necesaria = random.uniform(500, 5000)

        self.input_f_salida.setText(f"{self.f_salida_necesaria:.1f}")
        self.input_f_entrada_max.setText(f"{self.f_entrada_max:.1f}")

        self._generar_reto()