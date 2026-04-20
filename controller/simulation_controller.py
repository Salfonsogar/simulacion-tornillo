"""
Controlador de Simulación.

Maneja el loop de simulación física con timestep constante,
conecta la UI con el modelo físico, y gestiona el historial
para las gráficas.
"""

from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from physics import ScrewModel, ScrewConstants
import numpy as np
from typing import Optional


class SimulationController(QObject):
    """
    Controlador de la simulación física.
    
    Maneja:
    - Loop de simulación con timestep fijo (~60 FPS)
    - Conexión UI ↔ Modelo
    - Historial de estados para gráficas
    - Inicio/detener/pausa
    
    Signals:
        state_updated(dict): Estado actual del modelo
        simulation_finished(): Simulación completada
        error_occurred(str): Error en la simulación
    
    Attributes:
        running: Si la simulación está activa
        paused: Si la simulación está pausada
        dt: Timestep actual
    """
    
    state_updated = pyqtSignal(dict)
    simulation_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QObject] = None):
        """
        Inicializa el controlador.
        
        Args:
            parent: Objeto padre (opcional)
        """
        super().__init__(parent)
        
        self._model = ScrewModel()
        self._dt = ScrewConstants.DT_DEFAULT
        self._running = False
        self._paused = False
        self._time = 0.0
        
        self._history_y = []
        self._history_v = []
        self._history_a = []
        self._history_t = []
        self._max_history = ScrewConstants.MAX_HISTORY
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
    
    @property
    def model(self) -> ScrewModel:
        """Modelo físico."""
        return self._model
    
    @property
    def running(self) -> bool:
        """Si la simulación está activa."""
        return self._running
    
    @property
    def paused(self) -> bool:
        """Si la simulación está pausada."""
        return self._paused
    
    @property
    def dt(self) -> float:
        """Timestep actual."""
        return self._dt
    
    @property
    def time(self) -> float:
        """Tiempo actual de simulación."""
        return self._time
    
    def set_parameters(self, m: float, b: float, k: float) -> bool:
        """
        Configura parámetros del modelo.
        
        Args:
            m: Masa en kg
            b: Amortiguación en Ns/m
            k: Constante elástica en N/m
        
        Returns:
            True si fue exitoso
        """
        try:
            self._model.m = m
            self._model.b = b
            self._model.k = k
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def set_F(self, F: float) -> bool:
        """
        Configura la fuerza externa.
        
        Args:
            F: Fuerza en Newtons
        
        Returns:
            True si fue exitoso
        """
        try:
            valido, msg = ScrewConstants.validar_fuerza(F)
            if not valido:
                self.error_occurred.emit(msg)
                return False
            self._F = F
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def set_dt(self, dt: float):
        """
        Establece el timestep.
        
        Args:
            dt: Timestep en segundos
        """
        if dt > 0:
            self._dt = dt
    
    def start(self):
        """Inicia la simulación."""
        if not self._running:
            self._running = True
            self._paused = False
            self._timer.start(int(self._dt * 1000))
    
    def stop(self):
        """Detiene la simulación."""
        self._running = False
        self._paused = False
        self._timer.stop()
    
    def pause(self):
        """Pausa la simulación."""
        if self._running:
            self._paused = True
            self._timer.stop()
    
    def resume(self):
        """Reanuda la simulación."""
        if self._paused:
            self._running = True
            self._paused = False
            self._timer.start(int(self._dt * 1000))
    
    def reset(self):
        """Reinicia la simulación."""
        self.stop()
        self._model.reset()
        self._history_y.clear()
        self._history_v.clear()
        self._history_a.clear()
        self._history_t.clear()
        self._time = 0.0
    
    def _tick(self):
        """Un paso de la simulación."""
        # Ejecutar paso aunque no esté corriendo (para UI)
        F = getattr(self, '_F', 0.0)
        
        y, v, a = self._model.step(self._dt, F)
        
        self._history_t.append(self._time)
        self._history_y.append(y)
        self._history_v.append(v)
        self._history_a.append(a)
        self._time += self._dt
        
        if len(self._history_t) > self._max_history:
            self._history_t.pop(0)
            self._history_y.pop(0)
            self._history_v.pop(0)
            self._history_a.pop(0)
        
        if self._running:
            state = self._model.get_state()
            self.state_updated.emit(state)
    
    def get_history(self) -> tuple:
        """
        Retorna el historial para gráfica.
        
        Returns:
            Tupla (tiempos, posiciones, velocidades, aceleraciones)
        """
        return (
            np.array(self._history_t),
            np.array(self._history_y),
            np.array(self._history_v),
            np.array(self._history_a)
        )
    
    def get_y_history(self) -> np.ndarray:
        """Retorna historial de posiciones."""
        return np.array(self._history_y)
    
    def get_t_history(self) -> np.ndarray:
        """Retorna historial de tiempos."""
        return np.array(self._history_t)
    
    def get_parameters(self) -> dict:
        """
        Retorna parámetros del modelo y derivados.
        
        Returns:
            Diccionario con parámetros
        """
        model_params = self._model.get_parameters()
        return {
            'm': self._model.m,
            'b': self._model.b,
            'k': self._model.k,
            'omega_n': model_params['omega_n'],
            'omega_d': model_params['omega_d'],
            'zeta': model_params['zeta'],
            'tipo': model_params['tipo']
        }
    
    def get_state(self) -> dict:
        """Retorna estado actual."""
        return self._model.get_state()
    
    def step_once(self, F: float = 0.0) -> dict:
        """
        Executa un solo paso (para testing).
        
        Args:
            F: Fuerza aplicada
        
        Returns:
            Estado después del paso
        """
        y, v, a = self._model.step(self._dt, F)
        return self._model.get_state()
    
    def __repr__(self) -> str:
        status = "running" if self._running else ("paused" if self._paused else "stopped")
        return f"SimulationController({status}, t={self._time:.2f}s)"