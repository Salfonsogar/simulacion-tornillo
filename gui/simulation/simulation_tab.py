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
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self._controller = SimulationController()
        self._F = 0.0
        
        self._setup_ui()
        self._connect_signals()
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
    
    def _setup_ui(self):
        """Configura la interfaz."""
    COLORS = {
        'primary': '#0078D4',
        'primary_hover': '#005A9E',
        'accent': '#FF6B00',
        'success': '#107C10',
        'danger': '#A4262C',
        'border': '#EDEBE9',
        'text': '#201F1E',
        'text_secondary': '#605E5C',
        'bg_card': '#FFFFFF',
        'bg_main': '#F3F2F1',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = SimulationController()
        self._F = 0.0
        self._setup_ui()
        self._connect_signals()
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
    
    def _setup_ui(self):
        """Configura la interfaz."""
        c = self.COLORS
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("🎬 Simulador de Sistema Dinámico (RK4)")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 20px; font-weight: bold;")
        main_layout.addWidget(titulo)
        
        hlayout = QHBoxLayout()
        hlayout.setSpacing(15)
        
        self._anim_widget = AnimationWidget()
        self._anim_widget.setMinimumSize(350, 400)
        self._anim_widget.setStyleSheet(f"border: 1px solid {c['border']}; border-radius: 12px; background-color: white;")
        hlayout.addWidget(self._anim_widget, 1)
        
        self._chart_widget = ChartWidget()
        self._chart_widget.setMinimumSize(350, 400)
        hlayout.addWidget(self._chart_widget, 1)
        
        main_layout.addLayout(hlayout)
        
        # Dashboard Controles
        controles_frame = QFrame()
        controles_frame.setStyleSheet(f"background-color: {c['bg_card']}; border-radius: 10px; border: 1px solid {c['border']};")
        controles_layout = QHBoxLayout(controles_frame)
        controles_layout.setContentsMargins(15, 15, 15, 15)
        
        self._panel_controles = self._crear_controles()
        controles_layout.addWidget(self._panel_controles, 2)
        
        self._panel_info = self._crear_panel_info()
        controles_layout.addWidget(self._panel_info, 1)
        
        main_layout.addWidget(controles_frame)
        self.setLayout(main_layout)
    
    def _crear_controles(self) -> QWidget:
        """Crea el panel de controles."""
        c = self.COLORS
        container = QWidget()
        container.setStyleSheet("border: none; background: transparent;")
        layout = QGridLayout(container)
        layout.setSpacing(15)
        
        def add_slider_row(label, row, min_v, max_v, init_v, target_label_attr):
            layout.addWidget(QLabel(label), row, 0)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(min_v)
            slider.setMaximum(max_v)
            slider.setValue(init_v)
            slider.setStyleSheet(f"QSlider::handle:horizontal {{ background: {c['primary']}; }}")
            layout.addWidget(slider, row, 1)
            
            lbl_val = QLabel("")
            lbl_val.setStyleSheet(f"color: {c['primary']}; font-weight: bold; min-width: 60px;")
            layout.addWidget(lbl_val, row, 2)
            setattr(self, f"_slider_{target_label_attr}", slider)
            setattr(self, f"_label_{target_label_attr}", lbl_val)
            return slider

        add_slider_row("Masa (m):", 0, 1, 100, 10, "masa")
        add_slider_row("Amortiguación (b):", 1, 0, 50, 5, "b")
        add_slider_row("Rigidez (k):", 2, 0, 500, 100, "k")
        add_slider_row("Fuerza (F):", 3, 0, 1000, 100, "fuerza")
        
        btn_layout = QHBoxLayout()
        self._btn_iniciar = QPushButton("▶ Iniciar Simulación")
        self._btn_iniciar.setCheckable(True)
        self._btn_iniciar.setMinimumHeight(40)
        self._btn_iniciar.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_iniciar.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['success']};
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }}
        """)
        btn_layout.addWidget(self._btn_iniciar)
        
        self._btn_reset = QPushButton("↺ Reiniciar")
        self._btn_reset.setMinimumHeight(40)
        self._btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_reset.setStyleSheet(f"background-color: {c['text_secondary']}; color: white; border-radius: 6px;")
        btn_layout.addWidget(self._btn_reset)
        
        layout.addLayout(btn_layout, 4, 0, 1, 2)
        
        self._label_estado = QLabel("Estado: Detenido")
        self._label_estado.setStyleSheet(f"color: {c['danger']}; font-weight: bold;")
        layout.addWidget(self._label_estado, 4, 2)
        
        # Initial labels
        self._label_masa.setText("1.0 kg")
        self._label_b.setText("0.5 Ns/m")
        self._label_k.setText("20.0 N/m")
        self._label_fuerza.setText("10.0 N")
        
        return container
    
    def _crear_panel_info(self) -> QWidget:
        """Crea el panel de información."""
        c = self.COLORS
        container = QWidget()
        container.setStyleSheet("border: none; background: transparent; border-left: 1px solid #EDEBE9; border-radius: 0;")
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        def add_info_row(label, attr):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            lbl = QLabel("—")
            lbl.setStyleSheet(f"color: {c['primary']}; font-weight: bold;")
            row.addWidget(lbl)
            setattr(self, f"_label_{attr}", lbl)
            layout.addLayout(row)

        layout.addWidget(QLabel("<b>Análisis de Estabilidad</b>"))
        add_info_row("Frec. Natural (ωₙ):", "omega")
        add_info_row("Coef. Amort. (ζ):", "zeta")
        
        self._label_tipo = QLabel("Determinado...")
        self._label_tipo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_tipo.setStyleSheet(f"background-color: {c['bg_main']}; padding: 8px; border-radius: 4px; font-weight: bold;")
        layout.addWidget(self._label_tipo)
        
        return container
    
    def _connect_signals(self):
        """Conecta las señales."""
        self._btn_iniciar.toggled.connect(self._on_toggle)
        self._btn_reset.clicked.connect(self._on_reset)
        
        self._slider_masa.valueChanged.connect(self._on_masa_changed)
        self._slider_b.valueChanged.connect(self._on_b_changed)
        self._slider_k.valueChanged.connect(self._on_k_changed)
        self._slider_fuerza.valueChanged.connect(self._on_fuerza_changed)
    
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
    
    def _on_fuerza_changed(self, value: int):
        """Maneja cambio de fuerza."""
        f = value / 10.0
        self._label_fuerza.setText(f"{f:.1f} N")
        self._actualizar_parametros()
    
    def _actualizar_parametros(self):
        """Actualiza parámetros del modelo."""
        m = self._slider_masa.value() / 10.0
        b = self._slider_b.value() / 10.0
        k = self._slider_k.value() / 5.0
        f = self._slider_fuerza.value() / 10.0
        
        self._controller.set_parameters(m, b, k)
        self._controller.set_F(f)
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
        f = self._slider_fuerza.value() / 10.0
        
        # Actualizar parámetros del modelo
        self._controller.set_parameters(m, b, k)
        self._controller.set_F(f)
        
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