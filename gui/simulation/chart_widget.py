"""
Widget de gráfica usando matplotlib.

NOTA: Matplotlib SOLO se usa aquí para la gráfica y(t).
La animación principal usa QPainter (animation_widget.py).

Este widget muestra:
- Gráfica de posición vs tiempo (y(t))
- Se actualiza en tiempo real
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
import numpy as np


class ChartWidget(QWidget):
    """
    Widget de gráfica usando matplotlib.
    
    IMPORTANTE: matplotlib SOLO se usa para gráficas.
    La animación usa QPainter.
    
    Attributes:
        figure: Figure de matplotlib
        ax: Ejes de la gráfica
    """
    
    def __init__(self, parent=None):
        """
        Inicializa el widget.
        
        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        
        self._setup_ui()
        
        self._t_data = []
        self._y_data = []
    
    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._fig = Figure(figsize=(5, 4), facecolor='#FFFFFF')
        self._ax = self._fig.add_subplot(111)
        self._ax.set_facecolor('#FFFFFF')
        
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        layout.addWidget(self._canvas)
        
        self.setLayout(layout)
        
        self._configurar_grafica()
    
    def _configurar_grafica(self):
        """Configura el estilo de la gráfica."""
        self._ax.set_xlabel('Tiempo (s)', color='#555555', fontsize=9)
        self._ax.set_ylabel('y(t) [m]', color='#555555', fontsize=9)
        self._ax.set_title('Posición vs Tiempo', color='#0078D4', fontsize=10)
        
        self._ax.tick_params(colors='#555555')
        self._ax.grid(True, alpha=0.3, color='#CCCCCC')
        
        for spine in self._ax.spines.values():
            spine.set_color('#CCCCCC')
        
        self._line, = self._ax.plot([], [], color='#0078D4', linewidth=1.5)
        self._ax.set_xlim(0, 10)
        self._ax.set_ylim(-1, 1)
        
        self._canvas.draw()
    
    def update_plot(self, t: list, y: list):
        """
        Actualiza la gráfica.
        
        Args:
            t: Lista de tiempos
            y: Lista de posiciones
        """
        if len(t) == 0:
            return
        
        self._t_data = t
        self._y_data = y
        
        t_arr = np.array(t)
        y_arr = np.array(y)
        
        t_max = max(t_arr) if len(t_arr) > 0 else 10
        t_min = max(0, t_max - 10)
        
        y_max = max(np.abs(y_arr)) if len(y_arr) > 0 else 1
        y_max = max(0.1, y_max * 1.2)
        
        self._ax.clear()
        
        self._ax.set_xlabel('Tiempo (s)', color='#555555', fontsize=9)
        self._ax.set_ylabel('y(t) [m]', color='#555555', fontsize=9)
        self._ax.set_title('Posición vs Tiempo', color='#0078D4', fontsize=10)
        
        self._ax.plot(t_arr, y_arr, color='#0078D4', linewidth=1.5)
        self._ax.fill_between(t_arr, y_arr, alpha=0.2, color='#0078D4')
        
        self._ax.axhline(y=0, color='#CCCCCC', linestyle='--', linewidth=1)
        
        self._ax.set_xlim(t_min, t_max)
        self._ax.set_ylim(-y_max, y_max)
        
        self._ax.grid(True, alpha=0.3, color='#CCCCCC')
        
        for spine in self._ax.spines.values():
            spine.set_color('#CCCCCC')
        
        self._canvas.draw()
    
    def update_plot_arrays(self, t: np.ndarray, y: np.ndarray):
        """
        Actualiza la gráfica con arrays de numpy.
        
        Args:
            t: Array de numpy de tiempos
            y: Array de numpy de posiciones
        """
        self.update_plot(t.tolist(), y.tolist())
    
    def clear(self):
        """Limpia la gráfica."""
        self._t_data = []
        self._y_data = []
        self._configurar_grafica()
    
    def add_point(self, t: float, y: float):
        """
        Agrega un punto a la gráfica.
        
        Args:
            t: Tiempo
            y: Posición
        """
        self._t_data.append(t)
        self._y_data.append(y)
        
        self.update_plot(self._t_data, self._y_data)