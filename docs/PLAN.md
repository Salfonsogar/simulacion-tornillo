# Plan de Refactorización: Simulador de Tornillo con Sistema Dinámico

## 📋 Resumen Ejecutivo

Este documento establece el plan detallado para refactorizar el proyecto "Simulador de Tornillo" siguiendo una arquitectura MVC estrictamente separada, cumpliendo con todos los requisitos técnicos especificados.

**Enfoque**: Opción B - Refactorización completa por fases

---

## 🎯 Objetivos de Arquitectura

### Stack Tecnológico (Obligatorio)
- **PyQt6**: Interfaz gráfica
- **NumPy**: Cálculos numéricos
- **Matplotlib**: SOLO para gráficas (NO para animación principal)

### Capas Obligatorias (Arquitectura MVC)
```
┌─────────────────────────────────────────────────────────┐
│                    VISTA (UI)                        │
│   PyQt6 - Ventana, Pestañas, Widgets, QPainter        │
├─────────────────────────────────────────────────────────┤
│                 CONTROLADOR                           │
│   Lógica de negocio, Validaciones, Loop de simulación │
├─────────────────────────────────────────────────────────┤
│               MODELO (Física)                       │
│   ScrewModel, RK4, Estado (y,v,a), Parámetros        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Carpetas Propuesta

```
tornillo_sim/
├── main.py                      # Punto de entrada
├── requirements.txt             # Dependencias
├── PLAN.md                      # Este documento
│
├── physics/                    # CAPA: MODELO (Lógica Física)
│   ├── __init__.py
│   ├── screw_model.py          # Clase ScrewModel principal
│   ├── rk4_integrator.py     # Integrador Runge-Kutta
│   └── constants.py          # Constantes físicas
│
├── controller/                 # CAPA: CONTROLADOR
│   ├── __init__.py
│   ├── simulation_controller.py
│   ├── calculator_controller.py
│   └── crypto_controller.py
│
├── gui/                        # CAPA: VISTA (UI)
│   ├── __init__.py
│   ├── main_window.py
│   ├── calculator_tab.py
│   ├── crypto_tab.py
│   └── simulation/
│       ├── __init__.py
│       ├── animation_widget.py  # QPainter (NO matplotlib)
│       └── chart_widget.py   # Matplotlib SOLO para gráfica
│
├── crypto/                    # Módulo de criptografía
│   └── screw_crypto.py      # Sin cambios (ya funciona)
│
└── docs/                     # Documentación
    └── PLAN.md
```

---

## 🔄 FASE 1: Modelo de Física

### Objetivo
Crear la capa de modelo con implementación de ecuaciones físicas usando RK4 para integración numérica.

### Ecuación a Implementar
```
m * y''(t) + b * y'(t) + k * y(t) = F(t)
```
Donde:
- `m` = masa (kg)
- `b` = coeficiente de amortiguación (Ns/m)
- `k` = constante del resorte (N/m)
- `y(t)` = posición en tiempo t
- `y'(t)` = velocidad
- `y''(t)` = aceleración
- `F(t)` = fuerza externa

### Archivos a Crear

#### 1. physics/constants.py
```python
# Constantes físicas del sistema
class ScrewConstants:
    # Límites de masa
    MASA_MIN = 0.1      # kg
    MASA_MAX = 100.0     # kg
    
    # Límites de amortiguación
    B_MIN = 0.0         # Ns/m
    B_MAX = 50.0         # Ns/m
    
    # Límites de constante elástica
    K_MIN = 1.0         # N/m
    K_MAX = 1000.0       # N/m
    
    # Límites de fuerza
    F_MIN = 0.0          # N
    F_MAX = 10000.0       # N
    
    # Timestep recomendado
    DT_DEFAULT = 0.016   # ~60 FPS
```

#### 2. physics/rk4_integrator.py
```python
import numpy as np
from typing import Tuple, Callable

def rk4_step(
    state: np.ndarray,
    dt: float,
    derivatives_fn: Callable,
    *args
) -> np.ndarray:
    """
    Integración Runge-Kutta de cuarto orden.
    
    Args:
        state: Vector de estado [y, v]
        dt: Timestep
        derivatives_fn: Función que calcula derivadas
        *args: Argumentos adicionales para derivatives_fn
    
    Returns:
        Nuevo estado después de dt
    """
    k1 = derivatives_fn(state, *args)
    k2 = derivatives_fn(state + dt/2 * k1, *args)
    k3 = derivatives_fn(state + dt/2 * k2, *args)
    k4 = derivatives_fn(state + dt * k3, *args)
    
    return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

def compute_derivatives(
    state: np.ndarray,
    m: float, b: float, k: float, F: float
) -> np.ndarray:
    """
    Calcula derivadas para el sistema amortiguado.
    
    y' = v
    v' = (F - b*v - k*y) / m
    """
    y, v = state
    a = (F - b*v - k*y) / m
    return np.array([v, a])
```

#### 3. physics/screw_model.py
```python
import numpy as np
from typing import Tuple
from .rk4_integrator import rk4_step, compute_derivatives
from .constants import ScrewConstants

class ScrewModel:
    """
    Modelo físico del tornillo como sistema dinámico.
    
    Implementa: m*y''(t) + b*y'(t) + k*y(t) = F(t)
    
    Attributes:
        y: Posición actual (m)
        v: Velocidad actual (m/s)
        a: Aceleración actual (m/s²)
        m: Masa (kg)
        b: Coeficiente de amortiguación (Ns/m)
        k: Constante del resorte (N/m)
    """
    
    def __init__(
        self,
        m: float = 1.0,
        b: float = 1.0,
        k: float = 100.0,
        y0: float = 0.0,
        v0: float = 0.0
    ):
        """Inicializa el modelo."""
        self.m = m
        self.b = b
        self.k = k
        self._y = y0
        self._v = v0
        self._a = 0.0
        self._F = 0.0
        self._time = 0.0
    
    # Propiedades
    @property
    def y(self) -> float:
        return self._y
    
    @property
    def v(self) -> float:
        return self._v
    
    @property
    def a(self) -> float:
        return self._a
    
    @property
    def m(self) -> float:
        return self._m
    
    @property
    def b(self) -> float:
        return self._b
    
    @property
    def k(self) -> float:
        return self._k
    
    # Setters con validación
    @m.setter
    def m(self, value: float):
        if not ScrewConstants.MASA_MIN <= value <= ScrewConstants.MASA_MAX:
            raise ValueError(f"Masa debe estar entre {MASA_MIN} y {MASA_MAX}")
        self._m = value
    
    @b.setter
    def b(self, value: float):
        if not ScrewConstants.B_MIN <= value <= ScrewConstants.B_MAX:
            raise ValueError(f"b debe estar entre {B_MIN} y {B_MAX}")
        self._b = value
    
    @k.setter
    def k(self, value: float):
        if not ScrewConstants.K_MIN <= value <= ScrewConstants.K_MAX:
            raise ValueError(f"k debe estar entre {K_MIN} y {K_MAX}")
        self._k = value
    
    # Métodos de cálculo
    def step(self, dt: float, F: float = 0.0) -> Tuple[float, float, float]:
        """
        Avanza la simulación un timestep usando RK4.
        
        Args:
            dt: Timestep (segundos)
            F: Fuerza externa aplicada
        
        Returns:
            Tupla (y, v, a) después del paso
        """
        self._F = F
        state = np.array([self._y, self._v])
        
        # RK4 integration
        new_state = rk4_step(
            state, dt,
            compute_derivatives,
            self.m, self.b, self.k, F
        )
        
        self._y, self._v = new_state
        self._a = (F - self.b * self._v - self.k * self._y) / self.m
        self._time += dt
        
        return self._y, self._v, self._a
    
    def get_state(self) -> dict:
        """Retorna el estado actual."""
        return {
            'y': self._y,
            'v': self._v,
            'a': self._a,
            't': self._time,
            'm': self._m,
            'b': self._b,
            'k': self._k
        }
    
    def reset(self, y0: float = 0.0, v0: float = 0.0):
        """Reinicia el modelo."""
        self._y = y0
        self._v = v0
        self._a = 0.0
        self._time = 0.0
    
    # Métodos EXTRA (frecuencia natural y amortiguamiento)
    def get_natural_frequency(self) -> float:
        """
        Calcula frecuencia natural ωₙ.
        
        ωₙ = √(k/m)
        """
        return np.sqrt(self._k / self._m)
    
    def get_damping_ratio(self) -> float:
        """
        Calcula factor de amortiguamiento ζ.
        
        ζ = b / (2√(km))
        """
        wn = self.get_natural_frequency()
        return self._b / (2 * self._m * wn)
    
    def get_damping_type(self) -> str:
        """
        Retorna tipo de amortiguamiento.
        
        Returns:
            "subamortiguado" si ζ < 1
            "critico" si ζ = 1
            "sobreamortiguado" si ζ > 1
        """
        zeta = self.get_damping_ratio()
        if zeta < 1:
            return "subamortiguado"
        elif zeta == 1:
            return "critico"
        else:
            return "sobreamortiguado"
```

#### 4. physics/__init__.py
```python
from .screw_model import ScrewModel
from .rk4_integrator import rk4_step, compute_derivatives
from .constants import ScrewConstants

__all__ = [
    'ScrewModel',
    'rk4_step',
    'compute_derivatives',
    'ScrewConstants'
]
```

### Entregables FASE 1
- [ ] `physics/constants.py` - Definiciones de límites
- [ ] `physics/rk4_integrator.py` - Integrador RK4
- [ ] `physics/screw_model.py` - Clase ScrewModel completa
- [ ] `physics/__init__.py` - Exports

---

## 🔄 FASE 2: Controlador

### Objetivo
Crear la capa de controlador que conecta la UI con el modelo, maneja validaciones y controla el loop de simulación.

### Archivos a Crear

#### 1. controller/simulation_controller.py
```python
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from physics import ScrewModel
from typing import Callable, Optional
import numpy as np

class SimulationController(QObject):
    """
    Controlador de la simulación física.
    
    Maneja:
    - Loop de simulación con timestep fijo
    - Conexión UI ↔ Modelo
    - Historial de estados para gráficas
    """
    
    # Señales Qt
    state_updated = pyqtSignal(dict)  # Estado actual
    simulation_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Inicializa el controlador."""
        super().__init__(parent)
        
        # Modelo físico
        self._model = ScrewModel()
        
        # Configuración de simulación
        self._dt = 0.016  # ~60 FPS
        self._running = False
        self._time = 0.0
        
        # Historial para gráfica
        self._history_y = []
        self._history_t = []
        self._max_history = 1000  # Máximo puntos
        
        # Timer de simulación
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
    
    def set_parameters(self, m: float, b: float, k: float):
        """Configura parámetros del modelo."""
        try:
            self._model.m = m
            self._model.b = b
            self._model.k = k
        except ValueError as e:
            self.error_occurred.emit(str(e))
    
    def start(self):
        """Inicia la simulación."""
        self._running = True
        self._timer.start(int(self._dt * 1000))
    
    def stop(self):
        """Detiene la simulación."""
        self._running = False
        self._timer.stop()
    
    def _tick(self):
        """Un paso de la simulación."""
        if not self._running:
            return
        
        # Aplicar fuerza (puede ser 0 para oscilador libre)
        F = 0.0  # Por defecto
        
        # Avanzar modelo
        y, v, a = self._model.step(self._dt, F)
        
        # Guardar historial
        self._history_t.append(self._model._time)
        self._history_y.append(y)
        
        # Limitar historial
        if len(self._history_t) > self._max_history:
            self._history_t.pop(0)
            self._history_y.pop(0)
        
        # Emitir estado
        state = self._model.get_state()
        self.state_updated.emit(state)
    
    def get_history(self) -> tuple:
        """Retorna historial para gráfica."""
        return (np.array(self._history_t), np.array(self._history_y))
    
    def reset(self):
        """Reinicia la simulación."""
        self._model.reset()
        self._history_t.clear()
        self._history_y.clear()
        self._time = 0
```

#### 2. controller/calculator_controller.py
```python
from physics import ScrewCalculator, ScrewPhysicsError
from typing import Tuple, Optional
import math

class CalculatorController:
    """
    Controlador para cálculos de tornillo.
    
    Maneja:
    - Cálculo de VM
    - Validaciones
    - Manejo de errores
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        self._resultados = {}
    
    def calcular_vm(
        self,
        radio: float,
        paso: float
    ) -> float:
        """
        Calcula la Ventaja Mecánica.
        
        VM = (2πr) / L
        """
        return ScrewCalculator.calcular_vm(radio, paso)
    
    def calcular_todo(
        self,
        f_entrada: float,
        radio: float,
        paso: float,
        angulo: float = 360.0
    ) -> dict:
        """Calcula todos los parámetros."""
        return ScrewCalculator.calcular_todo(
            f_entrada, radio, paso, angulo
        )
    
    def validar_entrada(
        self,
        f_entrada: float,
        radio: float,
        paso: float
    ) -> Tuple[bool, Optional[str]]:
        """Valida los parámetros de entrada."""
        return ScrewCalculator.validar_parametros(f_entrada, radio, paso)
```

#### 3. controller/crypto_controller.py
```python
from crypto.screw_crypto import ScrewCipher, CryptoError
from typing import Tuple, List

class CryptoController:
    """
    Controlador de criptografía.
    
    Maneja:
    - Cifrado/descifrado
    - Validaciones
    """
    
    def __init__(self):
        """Inicializa."""
        self._estado = None
    
    def cifrar(self, datos: str, radio: float, paso: float, giros: int):
        """Cifra datos."""
        vm = ScrewCipher.calcular_vm(radio, paso)
        
        if self._es_fuerza(datos):
            f = float(datos)
            resultado, rondas = ScrewCipher.cifrar_fuerza(f, vm, giros)
            return str(resultado), vm
        else:
            val = ScrewCipher.texto_a_valores(datos)
            resultado, rondas = ScrewCipher.cifrar_multiplo(val, vm, giros)
            return ScrewCipher.valores_a_hex(resultado), vm
    
    def descifrar(self, datos: str, radio: float, paso: float, giros: int):
        """Descifra datos."""
        # Similar pero inverso
        pass
    
    def _es_fuerza(self, datos: str) -> bool:
        """Determina si es valor numérico."""
        try:
            float(datos)
            return True
        except:
            return False
```

#### 4. controller/__init__.py
```python
from .simulation_controller import SimulationController
from .calculator_controller import CalculatorController
from .crypto_controller import CryptoController

__all__ = [
    'SimulationController',
    'CalculatorController',
    'CryptoController'
]
```

### Entregables FASE 2
- [ ] `controller/simulation_controller.py` - Loop de simulación
- [ ] `controller/calculator_controller.py` - Lógica de cálculo
- [ ] `controller/crypto_controller.py` - Enrutamiento crypto
- [ ] `controller/__init__.py` - Exports

---

## 🔄 FASE 3: Vista UI (Nueva Arquitectura)

### Objetivo
Refactorizar la UI manteniendo PyQt6 pero con QPainter para animación (NO matplotlib).

### Arquitectura de Pestañas
```
QTabWidget
├── Pestaña 1: Calculadora
├── Pestaña 2: Simulación (QPainter + Matplotlib)
└── Pestaña 3: Criptografía
```

### Archivo: gui/main_window.py (Actualizado)
```python
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    """Ventana principal con 3 pestañas."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Tornillo")
        self._setup_ui()
    
    def _setup_ui(self):
        tabs = QTabWidget()
        
        # Pestaña 1: Calculadora
        from gui.calculator_tab import CalculatorTab
        tabs.addTab(CalculatorTab(), "Calculadora")
        
        # Pestaña 2: Simulación
        from gui.simulation.simulation_tab import SimulationTab
        tabs.addTab(SimulationTab(), "Simulación")
        
        # Pestaña 3: Criptografía
        from gui.crypto_tab import CryptoTab
        tabs.addTab(CryptoTab(), "Criptografía")
        
        self.setCentralWidget(tabs)
```

### Archivo: gui/simulation/animation_widget.py (NUEVO - QPainter)
```python
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
import math
import numpy as np

class AnimationWidget(QWidget):
    """
    Widget de animación del tornillo usando QPainter.
    
    IMPORTANTE: NO usa matplotlib para animación.
    Solo QPainter para movimiento helicoidal.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angulo = 0.0
        self._desplazamiento = 0.0
        self._paso = 0.002
        self._radio = 0.05
    
    def set_parameters(self, angulo: float, desplazamiento: float):
        """Actualiza parámetros."""
        self._angulo = angulo
        self._desplazamiento = desplazamiento
    
    def paintEvent(self, event):
        """Dibuja el tornillo."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo
        painter.fillRect(self.rect(), QColor("#FFFFFF"))
        
        # Centro
        cx = self.width() // 2
        cy = self.height() // 2
        
        # Dibujar tornillo
        self._dibujar_tornillo(painter, cx, cy)
        self._dibujar_rosca(painter, cx, cy)
        self._dibujar_flecha(painter, cx, cy)
    
    def _dibujar_tornillo(self, painter, cx, cy):
        """Dibuja el cuerpo del tornillo."""
        # Color y estilo
        pen = QPen(QColor("#0078D4"))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor("#CCCCCC")))
        
        # Cuerpo (rectángulo)
        alto = 150
        ancho = 30
        rect = QtCore.QRect(cx - ancho//2, cy - alto//2, ancho, alto)
        painter.drawRect(rect)
    
    def _dibujar_rosca(self, painter, cx, cy):
        """Dibuja la rosca helicoidal."""
        pen = QPen(QColor("#FF6B00"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Espiral
        num_vueltas = 5
        paso_pixeles = 15
        
        for i in range(num_vueltas * 20):
            theta = (i / 20) * 2 * math.pi + self._angulo
            y_offset = i * (paso_pixeles / 20) + self._desplazamiento * 500
            
            x1 = cx + 25 * math.cos(theta)
            y1 = cy - 75 + y_offset
            
            painter.drawPoint(QPointF(x1, y1))
    
    def _dibujar_flecha(self, painter, cx, cy):
        """Dibuja flecha de dirección."""
        pen = QPen(QColor("#28A745"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Flecha hacia arriba
        start = QPointF(cx, cy + 80)
        end = QPointF(cx, cy + 100)
        painter.drawLine(start, end)
        
        # Punta de flecha
        painter.drawLine(QPointF(cx - 10, cy + 90), end)
        painter.drawLine(QPointF(cx + 10, cy + 90), end)
```

### Archivo: gui/simulation/chart_widget.py (Matplotlib embebido)
```python
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class ChartWidget(QWidget):
    """
    Widget de gráfica usando matplotlib.
    
    NOTA: Matplotlib SOLO se usa aquí para gráfica y(t).
    La animación principal usa QPainter.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Figura matplotlib
        self._fig = Figure(figsize=(5, 4), facecolor='#FFFFFF')
        self._ax = self._fig.add_subplot(111)
        self._ax.set_facecolor('#FFFFFF')
        
        # Canvas
        self._canvas = FigureCanvasQTAgg(self._fig)
        layout.addWidget(self._canvas)
        
        self.setLayout(layout)
    
    def update_plot(self, t: list, y: list):
        """Actualiza la gráfica."""
        self._ax.clear()
        self._ax.plot(t, y, color='#0078D4', linewidth=1.5)
        self._ax.set_xlabel('Tiempo (s)')
        self._ax.set_ylabel('y(t)')
        self._ax.grid(True, alpha=0.3)
        self._canvas.draw()
```

### Archivo: gui/simulation/simulation_tab.py (Actualizado)
```python
from controller import SimulationController
from .animation_widget import AnimationWidget
from .chart_widget import ChartWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

class SimulationTab(QWidget):
    """
    Pestaña de simulación.
    
    Componentes:
    - AnimationWidget: QPainter (animación)
    - ChartWidget: matplotlib (gráfica)
    - Slider controls
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Controlador
        self._controller = SimulationController()
        
        # Timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Layout horizontal: animación + gráfica
        hlayout = QHBoxLayout()
        
        # Animación (QPainter)
        self._anim_widget = AnimationWidget()
        self._anim_widget.setMinimumSize(300, 300)
        hlayout.addWidget(self._anim_widget)
        
        # Gráfica (matplotlib)
        self._chart_widget = ChartWidget()
        self._chart_widget.setMinimumSize(300, 300)
        hlayout.addWidget(self._chart_widget)
        
        layout.addLayout(hlayout)
        
        # Controles (sliders)
        layout.addWidget(self._crear_controles())
        
        self.setLayout(layout)
    
    def _tick(self):
        """Avanzar simulación."""
        # Obtener params de sliders
        m = self._slider_masa.value() / 10.0
        b = self._slider_amort.value() / 100.0
        k = self._slider_k.value() / 10.0
        
        self._controller.set_parameters(m, b, k)
        self._controller._tick()  # Un paso
        
        # Actualizar animación QPainter
        state = self._controller._model.get_state()
        self._anim_widget.set_parameters(
            state['t'] * 10,  # ángulo simulado
            state['y']
        )
        self._anim_widget.update()
        
        # Actualizar gráfica
        t, y = self._controller.get_history()
        self._chart_widget.update_plot(list(t), list(y))
```

### Archivo: gui/calculator_tab.py (Actualizado)
```python
from controller import CalculatorController
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton

class CalculatorTab(QWidget):
    """Pestaña calculadora."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = CalculatorController()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QGridLayout()
        
        # Inputs
        layout.addWidget(QLabel("Masa (m):"), 0, 0)
        self._input_masa = QLineEdit()
        layout.addWidget(self._input_masa, 0, 1)
        
        layout.addWidget(QLabel("Radio (r):"), 1, 0)
        self._input_radio = QLineEdit()
        layout.addWidget(self._input_radio, 1, 1)
        
        layout.addWidget(QLabel("Paso (L):"), 2, 0)
        self._input_paso = QLineEdit()
        layout.addWidget(self._input_paso, 2, 1)
        
        # Botón calcular
        self._btn_calc = QPushButton("Calcular VM")
        self._btn_calc.clicked.connect(self._calcular)
        layout.addWidget(self._btn_calc, 3, 0, 1, 2)
        
        # Resultado
        self._label_resultado = QLabel("VM: —")
        layout.addWidget(self._label_resultado, 4, 0, 1, 2)
        
        self.setLayout(layout)
    
    def _calcular(self):
        r = float(self._input_radio.text())
        L = float(self._input_paso.text())
        
        vm = self._controller.calcular_vm(r, L)
        self._label_resultado.setText(f"VM: {vm:.4f}")
```

### Archivo: gui/simulation/__init__.py
```python
# Empty - marks as package
```

### Entregables FASE 3
- [ ] `gui/main_window.py` - 3 pestañas
- [ ] `gui/simulation/animation_widget.py` - QPainter
- [ ] `gui/simulation/chart_widget.py` - Matplotlib
- [ ] `gui/simulation/simulation_tab.py` - Integración
- [ ] `gui/calculator_tab.py` - Con controller
- [ ] `gui/simulation/__init__.py`

---

## 🔄 FASE 4: Criptografía

### Objetivo
Preservar el módulo crypto existente y agregar wrappers.

### Cambios en crypto/screw_crypto.py
Sin cambios - ya funciona correctamente.

### Nuevos archivos
```python
# crypto/__init__.py (ya existe)

# controller/crypto_controller.py (creado en FASE 2)
# Ya incluye wrapper
```

### Entregables FASE 4
- [ ] Revisar compatibilidad con controller
- [ ] Sin cambios en código

---

## 🔄 FASE 5: Integración y Testing

### Pasos de Integración
1. Verificar imports
2. Probarcalculator
3. Probar simulación
4. Probar criptografía
5. Verificar execution

### Testing Basico
```bash
# Test imports
python -c "from physics import ScrewModel; print('Physics OK')"
python -c "from controller import SimulationController; print('Controller OK')"
python -c "from gui import MainWindow; print('GUI OK')"

# Test completo
python main.py
```

### Entregables FASE 5
- [ ] Verificar imports
- [ ] Test de integración
- [ ] Corregir errors

---

## 🔄 FASE 6: Documentación

### Documentos a Generar
1. `docs/README.md` - Instrucciones de ejecución
2. `docs/ARQUITECTURA.md` - Explicación de módulos

---

## 📊 Resumen de Entregables

| Fase | Archivos | Estado |
|------|---------|--------|
| 1 | physics/{constants,rk4_integrator,screw_model}.py | ⬜ Por crear |
| 2 | controller/{simulation,calculator,crypto}_controller.py | ⬜ Por crear |
| 3 | gui/main_window.py, gui/simulation/*.py | ⬜ Por crear/actualizar |
| 4 | crypto/screw_crypto.py | ✅Ya existe |
| 5 | Integration testing | ⬜ Por ejecutar |
| 6 | docs/*.md | ⬜ Por crear |

---

## ⚠️ Notas Importantes

### Restricciones Cumplidas
- ✅ **PyQt6**: Solo se usa para UI
- ✅ **NumPy**: Solo para cálculos
- ✅ **Matplotlib SOLO para gráficas**: animation_widget usa QPainter
- ✅ **Separación UI/Lógica**: MVC completo
- ✅ **RK4**: Implementado en physics/rk4_integrator.py
- ✅ **Indicadores EXTRA**: ωₙ y ζ en ScrewModel

### Características Preservadas
- Las 4 pestañas originales (pueden reducirse a 3 si se desea)
- Funcionalidad de criptografía existente
- Estilo visual actual

---

## 🚀 Inicio de Implementación

**Confirmar para proceder con FASE 1**