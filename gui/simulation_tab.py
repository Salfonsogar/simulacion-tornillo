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
                            QCheckBox, QSizePolicy)
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

        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Layout de canvases (2 columnas)
        layout_canvas = QHBoxLayout()
        layout_canvas.setSpacing(15)

        # Canvas de animación del tornillo
        self.canvas_tornillo_group = self._crear_canvas_tornillo()
        layout_canvas.addWidget(self.canvas_tornillo_group)

        # Canvas del oscilador
        self.canvas_oscilador_group = self._crear_canvas_oscilador()
        layout_canvas.addWidget(self.canvas_oscilador_group)

        layout_principal.addLayout(layout_canvas)

        # Botón mostrar/ocultar controles
        self.btn_mostrar_controles = QPushButton("Ocultar Controles")
        self.btn_mostrar_controles.setCheckable(True)
        self.btn_mostrar_controles.setChecked(True)
        self.btn_mostrar_controles.clicked.connect(self._toggle_controles)
        layout_principal.addWidget(self.btn_mostrar_controles)

        # Controles (inicialmente visibles)
        self.controles_widget = self._crear_controles()
        layout_principal.addWidget(self.controles_widget)

        # Info del estado
        self.label_estado = QLabel("Estado: Detenido")
        self.label_estado.setStyleSheet("color: #E65100;")
        layout_principal.addWidget(self.label_estado)

        self.setLayout(layout_principal)

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
        self.canvas_tornillo_widget.setMinimumSize(400, 400)
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
        self.canvas_oscilador_widget.setMinimumSize(400, 400)
        self.canvas_oscilador_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Inicializar gráfico
        self._inicializar_oscilador()

        layout.addWidget(self.canvas_oscilador_widget)
        grupo.setLayout(layout)
        return grupo

    def _inicializar_oscilador(self):
        """Inicializa el gráfico del oscilador."""
        self.ax_oscilador.clear()

        # Parámetros del oscilador
        self.tiempo = np.linspace(0, 10, 500)
        self.A = 1.0
        self.gamma = 0.5
        self.omega = 2.0

        # Calcular y(t)
        self.y_t = self.A * np.exp(-self.gamma * self.tiempo) * np.cos(self.omega * self.tiempo)

        # Graficar
        self.ax_oscilador.plot(self.tiempo, self.y_t, color='#0078D4', linewidth=1.5,
                              label='y(t)')
        self.ax_oscilador.fill_between(self.tiempo, self.y_t, alpha=0.2, color='#0078D4')

        # Línea de referencia
        self.ax_oscilador.axhline(y=0, color='#CCCCCC', linestyle='--', linewidth=1)

        self.ax_oscilador.set_title('Estabilidad del Sistema y(t)',
                                  color='#0078D4', fontsize=10)
        self.ax_oscilador.set_xlabel('Tiempo (s)', color='#555555', fontsize=9)
        self.ax_oscilador.set_ylabel('Amplitud y(t)', color='#555555', fontsize=9)
        self.ax_oscilador.tick_params(colors='#555555')
        for spine in self.ax_oscilador.spines.values():
            spine.set_color('#CCCCCC')

        self.ax_oscilador.legend(loc='upper right', facecolor='#2D2D2D',
                              edgecolor='#CCCCCC', labelcolor='#555555')

        # Cursor para tiempo actual
        self.linea_tiempo = self.ax_oscilador.axvline(x=0, color='#E65100',
                                                      linestyle='--', linewidth=2)

        self.canvas_oscilador_widget.draw()

    def _actualizar_oscilador(self, tiempo_actual):
        """Actualiza la posición del cursor en el gráfico."""
        if hasattr(self, 'linea_tiempo'):
            self.linea_tiempo.set_xdata([tiempo_actual])
            self.canvas_oscilador_widget.draw_idle()

    def _crear_controles(self) -> QWidget:
        """Crea los controles interactivos."""
        grupo = QGroupBox("Controles")
        layout = QGridLayout()
        layout.setSpacing(15)

        # Botón iniciar/detener
        layout.addWidget(QLabel("Animación:"), 0, 0)
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.setCheckable(True)
        layout.addWidget(self.btn_iniciar, 0, 1, 1, 2)

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
        self.label_velocidad.setStyleSheet("color: #0078D4;")
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
        self.label_paso.setStyleSheet("color: #0078D4;")
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
        self.label_radio.setStyleSheet("color: #0078D4;")
        layout.addWidget(self.label_radio, 3, 2)

        # Checkbox oscilador
        self.chk_oscilador = QCheckBox("Mostrar oscilador")
        self.chk_oscilador.setChecked(True)
        layout.addWidget(self.chk_oscilador, 4, 0, 1, 2)

        grupo.setLayout(layout)

        # Conectar señales
        self.btn_iniciar.toggled.connect(self._on_toggle_animacion)
        self.slider_velocidad.valueChanged.connect(self._on_cambiar_velocidad)
        self.slider_paso.valueChanged.connect(self._on_cambiar_paso)
        self.slider_radio.valueChanged.connect(self._on_cambiar_radio)

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

    def _actualizar_parametros(self):
        """Actualiza los parámetros de simulación."""
        # Recalcular VM si es necesario
        try:
            paso = self.slider_paso.value() / 10000.0
            radio = self.slider_radio.value() / 1000.0
            if paso > 0:
                self.vm_current = (2 * np.pi * radio) / paso
        except:
            self.vm_current = 157.0  # Default

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
                self.btn_mostrar_controles.setText("Ocultar Controles")
            else:
                self.controles_widget.hide()
                self.btn_mostrar_controles.setText("Mostrar Controles")