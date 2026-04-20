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
                            QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette

import math
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


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

        # Panel DCL (diagrama de cuerpo libre)
        panel_dcl = self._crear_panel_dcl()
        layout_principal.addWidget(panel_dcl)

        # Layout horizontal para entrada y resultados
        layout_horizontal = QHBoxLayout()
        layout_horizontal.setSpacing(15)

        # Grupo de Entrada
        grupo_entrada = self._crear_grupo_entrada()
        layout_horizontal.addWidget(grupo_entrada)

        # Grupo de Resultados
        grupo_resultados = self._crear_grupo_resultados()
        layout_horizontal.addWidget(grupo_resultados)

        layout_principal.addLayout(layout_horizontal)

        # Botones
        botones = self._crear_botones()
        layout_principal.addWidget(botones)

        # Espacio expandible
        layout_principal.addStretch()

        self.setLayout(layout_principal)

    def _crear_panel_dcl(self) -> QGroupBox:
        """Crea el panel de Diagrama de Cuerpo Libre (DCL)."""
        grupo = QGroupBox("Diagrama de Cuerpo Libre (DCL)")
        grupo.setToolTip("DCL: Diagrama que muestra todas las fuerzas actúan sobre el cuerpo.\n📐 Flecha azul: F_entrada | Flecha verde: F_salida | Arco naranja: Torque")
        layout = QVBoxLayout()
        
        self.fig_dcl = Figure(figsize=(5, 3), facecolor='#FFFFFF')
        self.ax_dcl = self.fig_dcl.add_subplot(111)
        self.ax_dcl.set_facecolor('#FFFFFF')
        
        self.canvas_dcl = FigureCanvasQTAgg(self.fig_dcl)
        self.canvas_dcl.setMinimumSize(400, 200)
        self.canvas_dcl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.canvas_dcl)
        
        self._inicializar_dcl()
        
        grupo.setLayout(layout)
        return grupo

    def _inicializar_dcl(self):
        """Inicializa el DCL."""
        self.ax_dcl.clear()
        self.ax_dcl.set_xlim(-2.5, 2.5)
        self.ax_dcl.set_ylim(-1.5, 2.5)
        self.ax_dcl.set_aspect('equal')
        self.ax_dcl.axis('off')
        
        self.ax_dcl.set_title('DCL - Fuerzas sobre el Tornillo', color='#0078D4', fontsize=12)
        
        radio = 0.5
        theta = np.linspace(0, 2*np.pi, 20)
        x_engrane = radio * np.cos(theta)
        y_engrane = radio * np.sin(theta)
        self.ax_dcl.fill(x_engrane, y_engrane, color='#CCCCCC', edgecolor='#666666', linewidth=2, alpha=0.5)
        
        for i in range(8):
            angle = i * np.pi / 4
            x_diente = (radio + 0.1) * np.cos(angle)
            y_diente = (radio + 0.1) * np.sin(angle)
            self.ax_dcl.plot([radio * np.cos(angle), x_diente], [radio * np.sin(angle), y_diente], 
                         color='#666666', linewidth=2)
        
        self.ax_dcl.annotate('', xy=(-1.5, 0), xytext=(-0.6, 0),
                       arrowprops=dict(arrowstyle='->', color='#0078D4', lw=3))
        self.ax_dcl.text(-1.8, -0.2, 'F_entrada', color='#0078D4', fontsize=10, fontweight='bold')
        
        self.ax_dcl.annotate('', xy=(0, 1.8), xytext=(0, 0.6),
                       arrowprops=dict(arrowstyle='->', color='#28A745', lw=3))
        self.ax_dcl.text(0.2, 1.2, 'F_salida', color='#28A745', fontsize=10, fontweight='bold')
        
        theta_arrow = np.linspace(0, np.pi/2, 15)
        x_arc = 0.7 * np.cos(theta_arrow)
        y_arc = 0.7 * np.sin(theta_arrow)
        self.ax_dcl.plot(x_arc, y_arc, color='#FF6B00', lw=2)
        self.ax_dcl.annotate('', xy=(0.5, 0.5), xytext=(0.6, 0.3),
                         arrowprops=dict(arrowstyle='->', color='#FF6B00', lw=2))
        self.ax_dcl.text(0.55, 0.65, 'τ', color='#FF6B00', fontsize=12, fontweight='bold')
        
        self.ax_dcl.text(-2.3, -1.0, 'F_in: 10N', color='#0078D4', fontsize=9)
        self.ax_dcl.text(-2.3, -1.2, 'F_out: 157N', color='#28A745', fontsize=9)
        self.ax_dcl.text(-2.3, -1.4, 'τ: 0.5Nm', color='#FF6B00', fontsize=9)
        
        self.canvas_dcl.draw()

    def _actualizar_dcl(self, f_entrada, f_salida, radio, vm):
        """Actualiza el DCL con nuevos valores."""
        self.ax_dcl.clear()
        self.ax_dcl.set_xlim(-2.8, 2.8)
        self.ax_dcl.set_ylim(-2.0, 2.8)
        self.ax_dcl.set_aspect('equal')
        self.ax_dcl.axis('off')
        
        self.ax_dcl.set_title('DCL - Diagrama de Cuerpo Libre', color='#0078D4', fontsize=13, fontweight='bold')
        self.ax_dcl.title.set_position((0.5, 1.02))
        
        r_engrane = 0.5
        theta = np.linspace(0, 2*np.pi, 20)
        x_engrane = r_engrane * np.cos(theta)
        y_engrane = r_engrane * np.sin(theta)
        self.ax_dcl.fill(x_engrane, y_engrane, color='#E8E8E8', edgecolor='#666666', linewidth=2, alpha=0.7)
        
        for i in range(8):
            angle = i * np.pi / 4
            x_diente = (r_engrane + 0.12) * np.cos(angle)
            y_diente = (r_engrane + 0.12) * np.sin(angle)
            self.ax_dcl.plot([r_engrane * np.cos(angle), x_diente], [r_engrane * np.sin(angle), y_diente], 
                         color='#555555', linewidth=2)
        
        f_arrow_len = min(1.5, max(0.3, f_entrada / 20))
        self.ax_dcl.annotate('', xy=(-r_engrane - f_arrow_len, 0), xytext=(-r_engrane, 0),
                         arrowprops=dict(arrowstyle='->', color='#0078D4', lw=4))
        self.ax_dcl.text(-r_engrane - f_arrow_len - 0.5, -0.25, 'F_entrada', color='#0078D4', fontsize=11, fontweight='bold')
        
        fs_arrow_len = min(2.0, max(0.3, f_salida / 200))
        self.ax_dcl.annotate('', xy=(0, r_engrane + fs_arrow_len), xytext=(0, r_engrane),
                       arrowprops=dict(arrowstyle='->', color='#28A745', lw=4))
        self.ax_dcl.text(0.25, r_engrane + fs_arrow_len + 0.1, 'F_salida', color='#28A745', fontsize=11, fontweight='bold')
        
        theta_arrow = np.linspace(0, np.pi/2, 15)
        x_arc = 0.75 * np.cos(theta_arrow)
        y_arc = 0.75 * np.sin(theta_arrow)
        self.ax_dcl.plot(x_arc, y_arc, color='#FF6B00', lw=2.5)
        torque = f_entrada * radio
        self.ax_dcl.annotate('', xy=(0.55 * np.cos(np.pi/4), 0.55 * np.sin(np.pi/4)), xytext=(0.65, 0.35),
                         arrowprops=dict(arrowstyle='->', color='#FF6B00', lw=2.5))
        self.ax_dcl.text(0.6, 0.7, 'τ', color='#FF6B00', fontsize=14, fontweight='bold')
        
        bbox_props = dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', edgecolor='#CCCCCC', alpha=0.95)
        self.ax_dcl.text(-2.5, -1.7, f'F_in: {f_entrada:.1f}N', color='#0078D4', fontsize=10, 
                      fontweight='bold', bbox=bbox_props, ha='center')
        self.ax_dcl.text(0, -1.7, f'F_out: {f_salida:.1f}N', color='#28A745', fontsize=10, 
                      fontweight='bold', bbox=bbox_props, ha='center')
        self.ax_dcl.text(2.5, -1.7, f'τ: {torque:.3f}Nm', color='#FF6B00', fontsize=10, 
                      fontweight='bold', bbox=bbox_props, ha='center')
        self.ax_dcl.text(0, -1.9, f'VM: {vm:.2f}x', color='#333333', fontsize=11, 
                      fontweight='bold', fontstyle='italic', ha='center')
        
        self.canvas_dcl.draw()

    def _crear_grupo_entrada(self) -> QGroupBox:
        """Crea el grupo de parámetros de entrada."""
        grupo = QGroupBox("Parámetros de Entrada")
        layout = QGridLayout()
        layout.setSpacing(12)

        # Fuerza de entrada
        layout.addWidget(QLabel("Fuerza de Entrada (F_entrada):"), 0, 0)
        self.input_fuerza = QLineEdit()
        self.input_fuerza.setPlaceholderText("Ej: 10.0")
        self.input_fuerza.setToolTip("Fuerza aplicada en Newtons (N).\n💡 F_entrada es la fuerza que aplicas manualmente al tornillo.")
        layout.addWidget(self.input_fuerza, 0, 1)
        layout.addWidget(QLabel("N"), 0, 2)

        # Radio del brazo
        layout.addWidget(QLabel("Radio del Brazo (r):"), 1, 0)
        self.input_radio = QLineEdit()
        self.input_radio.setPlaceholderText("Ej: 0.05")
        self.input_radio.setToolTip("Radio de giro en metros (m).\n💡 Distancia desde el centro hasta donde se aplica la fuerza.")
        layout.addWidget(self.input_radio, 1, 1)
        layout.addWidget(QLabel("m"), 1, 2)

        # Paso de rosca
        layout.addWidget(QLabel("Paso de Rosca (L):"), 2, 0)
        self.input_paso = QLineEdit()
        self.input_paso.setPlaceholderText("Ej: 0.002")
        self.input_paso.setToolTip("Paso de la rosca en metros (m).\n💡 Distancia que avanza el tornillo por cada vuelta completa.")
        layout.addWidget(self.input_paso, 2, 1)
        layout.addWidget(QLabel("m"), 2, 2)

        # Ángulo de rotación
        layout.addWidget(QLabel("Ángulo de Rotación:"), 3, 0)
        self.input_angulo = QLineEdit()
        self.input_angulo.setPlaceholderText("360 (opcional)")
        self.input_angulo.setToolTip("Ángulo de rotación en grados.\n💡 360° = 1 vuelta completa.")
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
        self.label_vm.setToolTip("Ventaja Mecánica: número de veces que se multiplica la fuerza.\n📐 VM = 2πr / L")
        layout.addWidget(self.label_vm, 0, 1)

        # Fuerza de salida
        layout.addWidget(QLabel("Fuerza de Salida (F_salida):"), 1, 0)
        self.label_f_salida = QLabel("—")
        self.label_f_salida.setObjectName("resultado")
        self.label_f_salida.setToolTip("Fuerza resultante después del tornillo.\n📐 F_salida = F_entrada × VM")
        layout.addWidget(self.label_f_salida, 1, 1)

        # Desplazamiento
        layout.addWidget(QLabel("Desplazamiento Lineal (Δx):"), 2, 0)
        self.label_desplazamiento = QLabel("—")
        self.label_desplazamiento.setObjectName("resultado")
        self.label_desplazamiento.setToolTip("Distancia que avanza el tornillo.\n📐 Δx = θ × (L / 2π)")
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

            # Actualizar DCL
            self._actualizar_dcl(f_entrada, resultados['f_salida'], radio, resultados['vm'])

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