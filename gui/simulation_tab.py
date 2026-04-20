#!/usr/bin/env python3
"""
Pestaña de Simulación Visual - Animación del Tornillo

Cette pestaña muestra la simulación visual dinámica del tornillo:
1. Animación del tornillo helicoidal girando
2. Gráfico del oscilador amortiguado y(t)
3. Controles interactivos (slider de velocidad)

La visualización ayuda a entender la transformación:
- Movimiento circular (entrada) → Movimiento lineal (salida)

Autor: Simulador de Tornillo
Fecha: 2026
"""

import numpy as np
import math

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QSlider, QGroupBox,
                            QCheckBox, QSizePolicy, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches


class SimulationTab(QWidget):
    """
    Pestaña de simulación visual del tornillo.

    Muestra:
    - Animación del tornillo rotando y moviéndose linealmente
    - Gráfico del oscilador amortiguado
    - Controles interactivos
    """

    # Señal cuando cambia la velocidad
    velocidad_cambiada = pyqtSignal(float)

    def __init__(self, parent=None):
        """Inicializa la pestaña de simulación."""
        super().__init__(parent)
        self._angulo_actual = 0.0
        self._velocidad = 1.0
        self._animacion_activa = False
        self._desplazamiento = 0.0
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz."""
        self.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 12px;
            }
            QLabel titulo {
                color: #0078D4;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #555555;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #0078D4;
            }
            QSlider::groove:horizontal {
                background: #E0E0E0;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078D4;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QCheckBox {
                color: #555555;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                background: #FFFFFF;
                border: 1px solid #CCCCCC;
            }
            QCheckBox::indicator:checked {
                background: #0078D4;
                border: 1px solid #0078D4;
            }
        """)

        # Scroll area para pantallas pequeñas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(8)
        layout_principal.setContentsMargins(8, 8, 8, 8)

        # Layout de canvases - horizontal (lado a lado)
        layout_canvas = QHBoxLayout()
        layout_canvas.setSpacing(8)

        # Canvas de animación del tornillo - horizontal
        self.canvas_tornillo_group = self._crear_canvas_tornillo()
        self.canvas_tornillo_group.setMinimumHeight(200)
        layout_canvas.addWidget(self.canvas_tornillo_group, 1)

        # Canvas del oscilador - horizontal
        self.canvas_oscilador_group = self._crear_canvas_oscilador()
        self.canvas_oscilador_group.setMinimumHeight(200)
        layout_canvas.addWidget(self.canvas_oscilador_group, 1)

        layout_principal.addLayout(layout_canvas)

        # Panel de valores derivados - colapsable
        self.btn_valores = QPushButton("Valores (+)")
        self.btn_valores.setCheckable(True)
        self.btn_valores.setChecked(False)
        self.btn_valores.clicked.connect(self._toggle_valores)
        layout_principal.addWidget(self.btn_valores)
        
        self.panel_valores = self._crear_panel_valores()
        self.panel_valores.hide()
        layout_principal.addWidget(self.panel_valores)

        # Botón mostrar/ocultar controles
        self.btn_mostrar_controles = QPushButton("Controles (+)")
        self.btn_mostrar_controles.setCheckable(True)
        self.btn_mostrar_controles.setChecked(False)
        self.btn_mostrar_controles.clicked.connect(self._toggle_controles)
        layout_principal.addWidget(self.btn_mostrar_controles)

        # Controles
        self.controles_widget = self._crear_controles()
        self.controles_widget.hide()
        layout_principal.addWidget(self.controles_widget)

        # Info del estado
        self.label_estado = QLabel("Estado: Detenido")
        self.label_estado.setStyleSheet("color: #E65100; font-size: 11px;")
        layout_principal.addWidget(self.label_estado)

        container.setLayout(layout_principal)
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _crear_panel_valores(self) -> QWidget:
        """Crea el panel de valores derivados."""
        grupo = QGroupBox("Valores Derivados")
        grupo.setToolTip("Valores calculados automáticamente desde los parámetros del tornillo.\n📐 F_motor = F_entrada × VM")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("F_entrada:"), 0, 0)
        self._label_f_entrada = QLabel("10.0 N")
        self._label_f_entrada.setStyleSheet("color: #0078D4; font-weight: bold;")
        self._label_f_entrada.setToolTip("Fuerza de entrada actual.")
        layout.addWidget(self._label_f_entrada, 0, 1)
        
        layout.addWidget(QLabel("VM:"), 0, 2)
        self._label_vm = QLabel("15.71")
        self._label_vm.setStyleSheet("color: #0078D4; font-weight: bold;")
        self._label_vm.setToolTip("Ventaja Mecánica: VM = 2πr / L")
        layout.addWidget(self._label_vm, 0, 3)
        
        layout.addWidget(QLabel("F_motor:"), 1, 0)
        self._label_f_motor = QLabel("157.1 N")
        self._label_f_motor.setStyleSheet("color: #28A745; font-weight: bold; font-size: 14px;")
        self._label_f_motor.setToolTip("Fuerza resultantes después del tornillo.\n📐 F_motor = F_entrada × VM")
        layout.addWidget(self._label_f_motor, 1, 1)
        
        layout.addWidget(QLabel("γ (amort.):"), 1, 2)
        self._label_gamma = QLabel("0.50")
        self._label_gamma.setStyleSheet("color: #FF6B00;")
        self._label_gamma.setToolTip("Factor de amortiguación: γ = c / (2m)")
        layout.addWidget(self._label_gamma, 1, 3)
        
        layout.addWidget(QLabel("ω (frec.):"), 2, 0)
        self._label_omega = QLabel("3.16 rad/s")
        self._label_omega.setStyleSheet("color: #0078D4;")
        self._label_omega.setToolTip("Frecuencia natural: ω = √(k/m - γ²)")
        layout.addWidget(self._label_omega, 2, 1)
        
        layout.addWidget(QLabel("k_equiv:"), 2, 2)
        self._label_k = QLabel("157.1 N/m")
        self._label_k.setStyleSheet("color: #0078D4;")
        self._label_k.setToolTip("Constante elástica equivalente.")
        layout.addWidget(self._label_k, 2, 3)
        
        self._actualizar_panel_valores()
        
        grupo.setLayout(layout)
        return grupo

    def _actualizar_panel_valores(self):
        """Actualiza los valores del panel."""
        if not hasattr(self, 'slider_masa'):
            return
        masa = self.slider_masa.value() / 10.0
        k = self.slider_k.value() / 10.0
        c = self.slider_amort.value() / 100.0
        
        paso = self.slider_paso.value() / 10000.0
        radio = self.slider_radio.value() / 1000.0
        
        if paso > 0:
            vm = (2 * np.pi * radio) / paso
        else:
            vm = 1.0
        
        f_entrada = 10.0
        f_motor = f_entrada * vm
        
        gamma = c / (2 * masa) if masa > 0 else 0
        omega_sq = max(k / masa - gamma**2, 0.01)
        omega = np.sqrt(omega_sq)
        
        self._label_f_entrada.setText(f"{f_entrada:.1f} N")
        self._label_vm.setText(f"{vm:.2f}")
        self._label_f_motor.setText(f"{f_motor:.1f} N")
        self._label_gamma.setText(f"{gamma:.2f}")
        self._label_omega.setText(f"{omega:.2f} rad/s")
        self._label_k.setText(f"{k:.1f} N/m")

    def _crear_canvas_tornillo(self) -> QWidget:
        """Crea el canvas de animación del tornillo."""
        grupo = QGroupBox("Animación del Tornillo")
        layout = QVBoxLayout()

        # Figura matplotlib para el tornillo
        self.fig_tornillo = Figure(figsize=(6, 6), facecolor='#FFFFFF')
        self.ax_tornillo = self.fig_tornillo.add_subplot(111)
        self.ax_tornillo.set_facecolor('#FFFFFF')

        # Canvas
        self.canvas_tornillo_widget = FigureCanvasQTAgg(self.fig_tornillo)
        self.canvas_tornillo_widget.setMinimumSize(280, 200)
        self.canvas_tornillo_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Inicializar visualización
        self._inicializar_tornillo()

        layout.addWidget(self.canvas_tornillo_widget)
        grupo.setLayout(layout)
        return grupo

    def _inicializar_tornillo(self):
        """Inicializa la visualización del tornillo."""
        self.ax_tornillo.clear()
        self.ax_tornillo.set_xlim(-0.5, 0.5)
        self.ax_tornillo.set_ylim(-2, 2)
        self.ax_tornillo.set_title('Rotación → Desplazamiento', color='#0078D4', fontsize=10)
        self.ax_tornillo.set_xlabel('Posición angular', color='#555555', fontsize=9)
        self.ax_tornillo.set_ylabel('Desplazamiento (m)', color='#555555', fontsize=9)
        self.ax_tornillo.tick_params(colors='#555555')
        for spine in self.ax_tornillo.spines.values():
            spine.set_color('#CCCCCC')

        # Dibujar tornillo inicial (representación simplificada)
        self.tornillo_patch = []
        self._dibujar_tornillo(0)
        self.canvas_tornillo_widget.draw()

    def _dibujar_tornillo(self, angulo):
        """Dibuja el tornillo en una posición dada."""
        self.ax_tornillo.clear()
        self.ax_tornillo.set_xlim(-0.5, 0.5)
        self.ax_tornillo.set_ylim(-2, 2)

        # Título con ángulo actual
        angulo_deg = math.degrees(angulo) % 360
        self.ax_tornillo.set_title(f'Ángulo: {angulo_deg:.1f}° → Δx: {self._desplazamiento:.4f}m',
                              color='#0078D4', fontsize=10)
        self.ax_tornillo.set_xlabel('Posición angular', color='#555555', fontsize=9)
        self.ax_tornillo.set_ylabel('Desplazamiento (m)', color='#555555', fontsize=9)
        self.ax_tornillo.tick_params(colors='#555555')
        for spine in self.ax_tornillo.spines.values():
            spine.set_color('#CCCCCC')

        # Representación del eje del tornillo (línea vertical)
        self.ax_tornillo.axhline(y=-2 + self._desplazamiento, color='#CCCCCC',
                               linestyle='-', linewidth=2, alpha=0.5)

        # Dibujar rosca del tornillo (espiral)
        num_vueltas = 8
        paso_visual = 0.4

        for i in range(num_vueltas):
            y_base = -1.5 + i * paso_visual + self._desplazamiento
            if y_base > 1.5:
                break

            # Espiral representada como elipse
            theta = np.linspace(0, 2*np.pi, 50)
            x = 0.15 * np.cos(theta + angulo)
            y = y_base + 0.08 * np.sin(theta)

            self.ax_tornillo.plot(x, y, color='#0078D4', linewidth=1.5, alpha=0.8)

            # Conexiones de la rosca
            self.ax_tornillo.plot([0.15, 0.15], [y_base - 0.08, y_base + 0.08],
                               color='#00CED1', linewidth=1, alpha=0.6)

        # Indicador de rotación
        radio_giro = 0.3
        x_arrow = radio_giro * np.cos(angulo)
        y_arrow = radio_giro * np.sin(angulo) - 1.8

        self.ax_tornillo.annotate('', xy=(x_arrow, y_arrow), xytext=(0, -1.8),
                            arrowprops=dict(arrowstyle='->', color='#E65100', lw=2))

        # Flecha de dirección del movimiento
        self.ax_tornillo.annotate('', xy=(0, 0.1), xytext=(0, -0.1),
                                 arrowprops=dict(arrowstyle='->', color='#0078D4', lw=3))

        # Texto de dirección
        self.ax_tornillo.text(0.35, 0, 'Δx', color='#0078D4', fontsize=12,
                             ha='left', va='center')

    def _crear_canvas_oscilador(self) -> QWidget:
        """Crea el canvas del oscilador amortiguado."""
        grupo = QGroupBox("Oscilador Amortiguado y(t)")
        layout = QVBoxLayout()

        # Figura matplotlib
        self.fig_oscilador = Figure(figsize=(6, 6), facecolor='#FFFFFF')
        self.ax_oscilador = self.fig_oscilador.add_subplot(111)
        self.ax_oscilador.set_facecolor('#FFFFFF')

        # Canvas
        self.canvas_oscilador_widget = FigureCanvasQTAgg(self.fig_oscilador)
        self.canvas_oscilador_widget.setMinimumSize(280, 200)
        self.canvas_oscilador_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Inicializar gráfico
        self._inicializar_oscilador()

        layout.addWidget(self.canvas_oscilador_widget)
        grupo.setLayout(layout)
        return grupo

    def _inicializar_oscilador(self):
        """Inicializa el gráfico del oscilador."""
        if not hasattr(self, 'slider_masa'):
            self.ax_oscilador.set_title('Cargando...', color='#0078D4', fontsize=10)
            self.canvas_oscilador_widget.draw()
            return
        self._actualizar_oscilador_dinamico()

    def _actualizar_oscilador_dinamico(self):
        """Actualiza el oscilador con parâmetros dinámicos."""
        self.ax_oscilador.clear()

        masa = self.slider_masa.value() / 10.0
        k = self.slider_k.value() / 10.0
        c = self.slider_amort.value() / 100.0
        
        paso = self.slider_paso.value() / 10000.0
        radio = self.slider_radio.value() / 1000.0
        
        if paso > 0:
            vm = (2 * np.pi * radio) / paso
        else:
            vm = 1.0
        
        f_entrada = 10.0
        f_motor = f_entrada * vm
        
        gamma = c / (2 * masa) if masa > 0 else 0
        omega_sq = max(k / masa - gamma**2, 0.01)
        omega = np.sqrt(omega_sq)
        
        self.tiempo = np.linspace(0, 10, 500)
        A_amp = f_motor / k if k > 0 else 1.0
        self.y_t = A_amp * np.exp(-gamma * self.tiempo) * np.cos(omega * self.tiempo)
        
        self.ax_oscilador.plot(self.tiempo, self.y_t, color='#0078D4', linewidth=1.5, label='y(t)')
        self.ax_oscilador.fill_between(self.tiempo, self.y_t, alpha=0.2, color='#0078D4')
        
        self.ax_oscilador.axhline(y=0, color='#CCCCCC', linestyle='--', linewidth=1)
        
        overshoot = max(self.y_t) if len(self.y_t) > 0 else 0
        idx_settle = np.where(np.abs(self.y_t) < 0.02 * A_amp)[0]
        t_settle = self.tiempo[idx_settle[0]] if len(idx_settle) > 0 else 10.
        
        self.ax_oscilador.axhline(y=0.02 * A_amp, color='#28A745', linestyle=':', linewidth=1, alpha=0.7)
        self.ax_oscilador.axhline(y=-0.02 * A_amp, color='#28A745', linestyle=':', linewidth=1, alpha=0.7)
        
        titulo = f'Estabilidad y(t): VM={vm:.1f}, F_motor={f_motor:.1f}N'
        self.ax_oscilador.set_title(titulo, color='#0078D4', fontsize=10)
        self.ax_oscilador.set_xlabel('Tiempo (s)', color='#555555', fontsize=9)
        self.ax_oscilador.set_ylabel('Amplitud y(t)', color='#555555', fontsize=9)
        self.ax_oscilador.tick_params(colors='#555555')
        for spine in self.ax_oscilador.spines.values():
            spine.set_color('#CCCCCC')
        
        info_text = f' Overshoot: {overshoot:.2f}\n Settling: {t_settle:.2f}s\n γ: {gamma:.2f}'
        self.ax_oscilador.text(8, A_amp * 0.8, info_text, fontsize=8, color='#0078D4',
                          bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))
        
        self.linea_tiempo = self.ax_oscilador.axvline(x=0, color='#E65100', linestyle='--', linewidth=2)
        
        self.canvas_oscilador_widget.draw()

        self.canvas_oscilador_widget.draw()

    def _actualizar_oscilador(self, tiempo_actual):
        """Actualiza la posición del cursor en el gráfico."""
        if hasattr(self, 'linea_tiempo'):
            self.linea_tiempo.set_xdata([tiempo_actual])
            self.canvas_oscilador_widget.draw_idle()

    def _crear_controles(self) -> QWidget:
        """Crea los controles interactivos."""
        grupo = QGroupBox("Controles del Sistema")
        layout = QGridLayout()
        layout.setSpacing(18)
        layout.setColumnStretch(1, 1)

        # Botón iniciar/detener
        layout.addWidget(QLabel("Animación:"), 0, 0)
        self.btn_iniciar = QPushButton("▶ Iniciar")
        self.btn_iniciar.setCheckable(True)
        self.btn_iniciar.setMinimumWidth(100)
        self.btn_iniciar.setStyleSheet("padding: 8px; font-weight: bold;")
        layout.addWidget(self.btn_iniciar, 0, 1)

        # Slider de velocidad
        layout.addWidget(QLabel("Velocidad:"), 1, 0)
        self.slider_velocidad = QSlider(Qt.Orientation.Horizontal)
        self.slider_velocidad.setMinimum(1)
        self.slider_velocidad.setMaximum(10)
        self.slider_velocidad.setValue(5)
        self.slider_velocidad.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_velocidad.setTickInterval(1)
        layout.addWidget(self.slider_velocidad, 1, 1)
        self.label_velocidad = QLabel("5x")
        self.label_velocidad.setStyleSheet("color: #0078D4; font-weight: bold; min-width: 40px;")
        layout.addWidget(self.label_velocidad, 1, 2)

        # Slider de paso
        layout.addWidget(QLabel("Paso (L):"), 2, 0)
        self.slider_paso = QSlider(Qt.Orientation.Horizontal)
        self.slider_paso.setMinimum(1)
        self.slider_paso.setMaximum(100)
        self.slider_paso.setValue(20)  # 0.002m
        self.slider_paso.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_paso.setTickInterval(10)
        layout.addWidget(self.slider_paso, 2, 1)
        self.label_paso = QLabel("0.002 m")
        self.label_paso.setStyleSheet("color: #0078D4; font-weight: bold; min-width: 50px;")
        layout.addWidget(self.label_paso, 2, 2)

        # Slider de radio
        layout.addWidget(QLabel("Radio (r):"), 3, 0)
        self.slider_radio = QSlider(Qt.Orientation.Horizontal)
        self.slider_radio.setMinimum(1)
        self.slider_radio.setMaximum(100)
        self.slider_radio.setValue(5)  # 0.05m
        self.slider_radio.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_radio.setTickInterval(10)
        layout.addWidget(self.slider_radio, 3, 1)
        self.label_radio = QLabel("0.05 m")
        self.label_radio.setStyleSheet("color: #0078D4; font-weight: bold; min-width: 50px;")
        layout.addWidget(self.label_radio, 3, 2)

        # Checkbox oscilador
        self.chk_oscilador = QCheckBox("Mostrar oscilador")
        self.chk_oscilador.setChecked(True)
        self.chk_oscilador.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.chk_oscilador, 4, 0, 1, 3)
        
        # Separator línea
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #CCCCCC; margin: 10px 0;")
        layout.addWidget(sep, 5, 0, 1, 3)
        
        # Parámetros del oscilador
        layout.addWidget(QLabel("Masa (m):"), 6, 0)
        self.slider_masa = QSlider(Qt.Orientation.Horizontal)
        self.slider_masa.setMinimum(1)
        self.slider_masa.setMaximum(100)
        self.slider_masa.setValue(10)  # 1.0 kg
        self.slider_masa.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_masa.setTickInterval(10)
        layout.addWidget(self.slider_masa, 6, 1)
        self.label_masa = QLabel("1.0 kg")
        self.label_masa.setStyleSheet("color: #0078D4; font-weight: bold; min-width: 50px;")
        layout.addWidget(self.label_masa, 6, 2)
        
        layout.addWidget(QLabel("Resorte (k):"), 7, 0)
        self.slider_k = QSlider(Qt.Orientation.Horizontal)
        self.slider_k.setMinimum(10)
        self.slider_k.setMaximum(1000)
        self.slider_k.setValue(100)  # 100 N/m
        self.slider_k.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_k.setTickInterval(100)
        layout.addWidget(self.slider_k, 7, 1)
        self.label_k = QLabel("100 N/m")
        self.label_k.setStyleSheet("color: #0078D4; font-weight: bold; min-width: 60px;")
        layout.addWidget(self.label_k, 7, 2)
        
        layout.addWidget(QLabel("Amortiguación (c):"), 8, 0)
        self.slider_amort = QSlider(Qt.Orientation.Horizontal)
        self.slider_amort.setMinimum(0)
        self.slider_amort.setMaximum(100)
        self.slider_amort.setValue(10)  # 1.0 Ns/m
        self.slider_amort.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_amort.setTickInterval(10)
        layout.addWidget(self.slider_amort, 8, 1)
        self.label_amort = QLabel("1.0 Ns/m")
        self.label_amort.setStyleSheet("color: #0078D4; font-weight: bold; min-width: 60px;")
        layout.addWidget(self.label_amort, 8, 2)

        grupo.setLayout(layout)

        # Conectar señales
        self.btn_iniciar.toggled.connect(self._on_toggle_animacion)
        self.slider_velocidad.valueChanged.connect(self._on_cambiar_velocidad)
        self.slider_paso.valueChanged.connect(self._on_cambiar_paso)
        self.slider_radio.valueChanged.connect(self._on_cambiar_radio)
        self.slider_masa.valueChanged.connect(self._on_cambiar_masa)
        self.slider_k.valueChanged.connect(self._on_cambiar_k)
        self.slider_amort.valueChanged.connect(self._on_cambiar_amort)

        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self._actualizar_animacion)

        return grupo

    def _on_toggle_animacion(self, checked):
        """Maneja el toggle de animación."""
        if checked:
            self.btn_iniciar.setText("Detener")
            self.label_estado.setText("Estado: Animando")
            self.label_estado.setStyleSheet("color: #0078D4;")
            self.timer.start(50)
        else:
            self.btn_iniciar.setText("Iniciar")
            self.label_estado.setText("Estado: Detenido")
            self.label_estado.setStyleSheet("color: #E65100;")
            self.timer.stop()

    def _on_cambiar_velocidad(self, valor):
        """Maneja el cambio de velocidad."""
        self._velocidad = valor / 5.0
        self.label_velocidad.setText(f"{valor}x")

    def _on_cambiar_paso(self, valor):
        """Maneja el cambio de paso."""
        paso = valor / 10000.0  # 1-100 → 0.0001-0.01
        self.label_paso.setText(f"{paso:.4f} m")
        self._actualizar_parametros()

    def _on_cambiar_radio(self, valor):
        """Maneja el cambio de radio."""
        radio = valor / 1000.0  # 1-100 → 0.001-0.1
        self.label_radio.setText(f"{radio:.3f} m")
        self._actualizar_parametros()

    def _on_cambiar_masa(self, valor):
        """Maneja el cambio de masa."""
        masa = valor / 10.0  # 1-100 → 0.1-10 kg
        self.label_masa.setText(f"{masa:.1f} kg")
        self._actualizar_oscilador_dinamico()
        self._actualizar_panel_valores()

    def _on_cambiar_k(self, valor):
        """Maneja el cambio de constante del resorte."""
        k = valor / 10.0  # 10-1000 → 1-100 N/m
        self.label_k.setText(f"{k:.1f} N/m")
        self._actualizar_oscilador_dinamico()
        self._actualizar_panel_valores()

    def _on_cambiar_amort(self, valor):
        """Maneja el cambio de amortiguación."""
        c = valor / 100.0  # 0-100 → 0-1 Ns/m
        self.label_amort.setText(f"{c:.2f} Ns/m")
        self._actualizar_oscilador_dinamico()
        self._actualizar_panel_valores()

    def _actualizar_parametros(self):
        """Actualiza los parámetros de simulación."""
        try:
            paso = self.slider_paso.value() / 10000.0
            radio = self.slider_radio.value() / 1000.0
            if paso > 0:
                self.vm_current = (2 * np.pi * radio) / paso
        except:
            self.vm_current = 157.0  # Default
        
        self._actualizar_oscilador_dinamico()
        self._actualizar_panel_valores()

    def _actualizar_animacion(self):
        """Actualiza la animación del tornillo."""
        # Incrementar ángulo
        self._angulo_actual += 0.05 * self._velocidad

        # Calcular desplazamiento
        paso = self.slider_paso.value() / 10000.0
        self._desplazamiento = self._angulo_actual * (paso / (2 * np.pi))

        # Actualizar visualización
        self._dibujar_tornillo(self._angulo_actual)
        self.canvas_tornillo_widget.draw()

        # Actualizar oscilador
        if self.chk_oscilador.isChecked():
            tiempo = (self._angulo_actual / (2 * np.pi)) % 10
            self._actualizar_oscilador(tiempo)

    def iniciar_animacion(self):
        """Inicia la animación programáticamente."""
        if not self.btn_iniciar.isChecked():
            self.btn_iniciar.click()

    def detener_animacion(self):
        """Detiene la animación programáticamente."""
        if self.btn_iniciar.isChecked():
            self.btn_iniciar.click()

    def _toggle_controles(self, checked):
        """Muestra u oculta los controles."""
        if hasattr(self, 'controles_widget'):
            if checked:
                self.controles_widget.show()
                self.btn_mostrar_controles.setText("Controles (-)")
            else:
                self.controles_widget.hide()
                self.btn_mostrar_controles.setText("Controles (+)")

    def _toggle_valores(self, checked):
        """Muestra u oculta el panel de valores."""
        if hasattr(self, 'panel_valores'):
            if checked:
                self.panel_valores.show()
                self.btn_valores.setText("Valores (-)")
            else:
                self.panel_valores.hide()
                self.btn_valores.setText("Valores (+)")