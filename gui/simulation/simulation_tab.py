"""
Pestaña de Simulación.

Esta pestaña integra:
- AnimationWidget (QPainter): Animación del tornillo
- ChartWidget (matplotlib): Gráfica y(t)
- Controles: Sliders para parámetros físicos

Cumple con las restricciones:
- QPainter para animación (NO matplotlib)
- Matplotlib SOLO para gráfica
"""

import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSlider, QPushButton, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

from controller import SimulationController
from .animation_widget import AnimationWidget
from .chart_widget import ChartWidget
from physics import ScrewConstants


class SimulationTab(QWidget):
    """
    Pestaña de simulación física.
    
    Integra:
    - Animación QPainter del tornillo
    - Gráfica matplotlib de y(t)
    - Controles de parámetros
    
    Attributes:
        controller: Controlador de simulación
    """
    
    def __init__(self, parent=None):
        """
        Inicializa la pestaña.
        
        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        
        self._controller = SimulationController()
        self._F = 0.0
        
        self._setup_ui()
        self._connect_signals()
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
    
    def _setup_ui(self):
        """Configura la interfaz."""
        c = {
            'primary': '#0078D4',
            'success': '#28A745',
            'danger': '#DC3545',
            'border': '#DEE2E6',
            'text': '#212529',
            'text_secondary': '#6C757D',
        }
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        titulo = QLabel("Simulacion del Tornillo - Sistema Dinamico Amortiguado")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 16px; font-weight: bold;")
        main_layout.addWidget(titulo)
        
        hlayout = QHBoxLayout()
        hlayout.setSpacing(10)
        
        self._anim_widget = AnimationWidget()
        self._anim_widget.setMinimumSize(250, 300)
        self._anim_widget.setStyleSheet(f"border: 1px solid {c['border']}; border-radius: 8px;")
        hlayout.addWidget(self._anim_widget, 1)
        
        self._chart_widget = ChartWidget()
        self._chart_widget.setMinimumSize(250, 300)
        hlayout.addWidget(self._chart_widget, 1)
        
        main_layout.addLayout(hlayout)
        
        self._panel_controles = self._crear_controles()
        main_layout.addWidget(self._panel_controles)
        
        self._panel_info = self._crear_panel_info()
        main_layout.addWidget(self._panel_info)
        
        self.setLayout(main_layout)
    
    def _crear_controles(self) -> QGroupBox:
        """Crea el panel de controles."""
        grupo = QGroupBox("Parámetros del Sistema")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("Masa (m):"), 0, 0)
        self._slider_masa = QSlider(Qt.Orientation.Horizontal)
        self._slider_masa.setMinimum(1)
        self._slider_masa.setMaximum(100)
        self._slider_masa.setValue(10)
        self._slider_masa.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider_masa.setTickInterval(10)
        layout.addWidget(self._slider_masa, 0, 1)
        self._label_masa = QLabel("1.0 kg")
        self._label_masa.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(self._label_masa, 0, 2)
        
        layout.addWidget(QLabel("Amortiguación (b):"), 1, 0)
        self._slider_b = QSlider(Qt.Orientation.Horizontal)
        self._slider_b.setMinimum(0)
        self._slider_b.setMaximum(50)
        self._slider_b.setValue(5)
        self._slider_b.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider_b.setTickInterval(10)
        layout.addWidget(self._slider_b, 1, 1)
        self._label_b = QLabel("0.5 Ns/m")
        self._label_b.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(self._label_b, 1, 2)
        
        layout.addWidget(QLabel("Rigidez (k):"), 2, 0)
        self._slider_k = QSlider(Qt.Orientation.Horizontal)
        self._slider_k.setMinimum(10)
        self._slider_k.setMaximum(500)
        self._slider_k.setValue(100)
        self._slider_k.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider_k.setTickInterval(50)
        layout.addWidget(self._slider_k, 2, 1)
        self._label_k = QLabel("100 N/m")
        self._label_k.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(self._label_k, 2, 2)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #CCCCCC;")
        layout.addWidget(sep, 3, 0, 1, 3)
        
        self._btn_iniciar = QPushButton("▶ Iniciar")
        self._btn_iniciar.setCheckable(True)
        self._btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self._btn_iniciar, 4, 0)
        
        self._btn_reset = QPushButton("↺ Reiniciar")
        self._btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px 20px;
            }
        """)
        layout.addWidget(self._btn_reset, 4, 1)
        
        self._label_estado = QLabel("Detenido")
        self._label_estado.setStyleSheet("color: #E65100; font-weight: bold;")
        layout.addWidget(self._label_estado, 4, 2)
        
        grupo.setLayout(layout)
        return grupo
    
    def _crear_panel_info(self) -> QGroupBox:
        """Crea el panel de información."""
        grupo = QGroupBox("Parámetros Derivados")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("ωₙ (frec. natural):"), 0, 0)
        self._label_omega = QLabel("— rad/s")
        self._label_omega.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(self._label_omega, 0, 1)
        
        layout.addWidget(QLabel("ζ (factor damp.):"), 1, 0)
        self._label_zeta = QLabel("—")
        self._label_zeta.setStyleSheet("color: #FF6B00; font-weight: bold;")
        layout.addWidget(self._label_zeta, 1, 1)
        
        layout.addWidget(QLabel("Tipo:"), 2, 0)
        self._label_tipo = QLabel("—")
        self._label_tipo.setStyleSheet("color: #333333; font-weight: bold;")
        layout.addWidget(self._label_tipo, 2, 1)
        
        grupo.setLayout(layout)
        return grupo
    
    def _connect_signals(self):
        """Conecta las señales."""
        self._btn_iniciar.toggled.connect(self._on_toggle)
        self._btn_reset.clicked.connect(self._on_reset)
        
        self._slider_masa.valueChanged.connect(self._on_masa_changed)
        self._slider_b.valueChanged.connect(self._on_b_changed)
        self._slider_k.valueChanged.connect(self._on_k_changed)
    
    def _on_toggle(self, checked: bool):
        """Maneja toggle de inicio/detención."""
        if checked:
            self._btn_iniciar.setText("⏹ Detener")
            self._btn_iniciar.setStyleSheet("""
                QPushButton {
                    background-color: #DC3545;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    font-weight: bold;
                }
            """)
            self._label_estado.setText("Ejecutando")
            self._label_estado.setStyleSheet("color: #28A745; font-weight: bold;")
            
            self._actualizar_parametros()
            self._controller.start()
            self._timer.start(16)
        else:
            self._btn_iniciar.setText("▶ Iniciar")
            self._btn_iniciar.setStyleSheet("""
                QPushButton {
                    background-color: #28A745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    font-weight: bold;
                }
            """)
            self._label_estado.setText("Detenido")
            self._label_estado.setStyleSheet("color: #E65100; font-weight: bold;")
            
            self._controller.stop()
            self._timer.stop()
    
    def _on_reset(self):
        """Maneja botón de reinicio."""
        self._controller.reset()
        
        if self._btn_iniciar.isChecked():
            self._btn_iniciar.setChecked(False)
            self._on_toggle(False)
        
        self._anim_widget.set_parameters(0, 0)
        self._chart_widget.clear()
        
        self._actualizar_info()
    
    def _on_masa_changed(self, value: int):
        """Maneja cambio de masa."""
        m = value / 10.0
        self._label_masa.setText(f"{m:.1f} kg")
        self._actualizar_parametros()
    
    def _on_b_changed(self, value: int):
        """Maneja cambio de amortiguación."""
        b = value / 10.0
        self._label_b.setText(f"{b:.1f} Ns/m")
        self._actualizar_parametros()
    
    def _on_k_changed(self, value: int):
        """Maneja cambio de rigidez."""
        k = value / 5.0
        self._label_k.setText(f"{k:.1f} N/m")
        self._actualizar_parametros()
    
    def _actualizar_parametros(self):
        """Actualiza parámetros del modelo."""
        m = self._slider_masa.value() / 10.0
        b = self._slider_b.value() / 10.0
        k = self._slider_k.value() / 5.0
        
        self._controller.set_parameters(m, b, k)
        self._actualizar_info()
    
    def _actualizar_info(self):
        """Actualiza panel de información."""
        params = self._controller.get_parameters()
        
        self._label_omega.setText(f"{params['omega_n']:.2f} rad/s")
        
        zeta = params['zeta']
        self._label_zeta.setText(f"{zeta:.3f}")
        
        tipo = params['tipo']
        self._label_tipo.setText(tipo)
        
        if tipo == "subamortiguado":
            color = "#28A745"
        elif tipo == "critico":
            color = "#FF6B00"
        else:
            color = "#DC3545"
        
        self._label_tipo.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _tick(self):
        """Un paso de la animación."""
        if not self._btn_iniciar.isChecked():
            return
        
        # Obtener parámetros actuales de los sliders
        m = self._slider_masa.value() / 10.0
        b = self._slider_b.value() / 10.0
        k = self._slider_k.value() / 5.0
        
        # Actualizar parámetros del modelo
        self._controller.set_parameters(m, b, k)
        
        # Hacer un paso de simulación usando el timer del controlador
        self._controller._tick()
        
        # Obtener estado
        state = self._controller.get_state()
        y = state['y']
        
        # Actualizar animación
        angulo = self._controller.time * 2 * math.pi * 10
        paso = 0.002
        radio = 0.05
        self._anim_widget.set_parameters(angulo, y, paso, radio)
        
        # Actualizar gráfica
        t_arr, y_arr, v_arr, a_arr = self._controller.get_history()
        if len(t_arr) > 0:
            self._chart_widget.update_plot_arrays(t_arr, y_arr)