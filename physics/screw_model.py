"""
Modelo físico del tornillo como sistema dinámico amortiguado.

Implementa la ecuación de segundo orden:
    m*y''(t) + b*y'(t) + k*y(t) = F(t)

Donde:
- m: masa (kg)
- b: coeficiente de amortiguación (Ns/m)
- k: constante del resorte (N/m)
- y(t): posición en tiempo t
- y'(t): velocidad
- y''(t): aceleración
- F(t): fuerza externa

Este modelo representa el sistema mecánico del tornillo como un
oscilador amortiguado, útil para estudiar la respuesta dinámica.
"""

import numpy as np
from typing import Tuple
from .rk4_integrator import rk4_step, compute_derivatives
from .constants import ScrewConstants


class ScrewModelError(Exception):
    """Excepción para errores del modelo."""
    pass


class ScrewModel:
    """
    Modelo físico del tornillo como sistema dinámico.
    
    Implementa la integración numérica usando RK4 para resolver
    la ecuación diferencial del oscilador amortiguado.
    
    Attributes:
        y: Posición actual (m)
        v: Velocidad actual (m/s)
        a: Aceleración actual (m/s²)
        m: Masa (kg)
        b: Coeficiente de amortiguación (Ns/m)
        k: Constante del resorte (N/m)
    
    Example:
        >>> model = ScrewModel(m=1.0, b=0.5, k=100.0)
        >>> for _ in range(100):
        ...     y, v, a = model.step(0.016, 10.0)
        >>> print(f"y={y:.4f}, v={v:.4f}")
    """
    
    def __init__(
        self,
        m: float = 1.0,
        b: float = 0.5,
        k: float = 100.0,
        y0: float = 0.0,
        v0: float = 0.0
    ):
        """
        Inicializa el modelo del tornillo.
        
        Args:
            m: Masa en kg (default: 1.0)
            b: Coeficiente de amortiguación en Ns/m (default: 0.5)
            k: Constante del resorte en N/m (default: 100.0)
            y0: Posición inicial en m (default: 0.0)
            v0: Velocidad inicial en m/s (default: 0.0)
        """
        self._m = m
        self._b = b
        self._k = k
        self._y = y0
        self._v = v0
        self._a = 0.0
        self._F = 0.0
        self._time = 0.0
    
    @property
    def y(self) -> float:
        """Posición actual (m)."""
        return self._y
    
    @property
    def v(self) -> float:
        """Velocidad actual (m/s)."""
        return self._v
    
    @property
    def a(self) -> float:
        """Aceleración actual (m/s²)."""
        return self._a
    
    @property
    def m(self) -> float:
        """Masa (kg)."""
        return self._m
    
    @m.setter
    def m(self, value: float):
        """Establece masa con validación."""
        valido, msg = ScrewConstants.validar_masa(value)
        if not valido:
            raise ScrewModelError(msg)
        self._m = value
    
    @property
    def b(self) -> float:
        """Coeficiente de amortiguación (Ns/m)."""
        return self._b
    
    @b.setter
    def b(self, value: float):
        """Establece amortiguación con validación."""
        valido, msg = ScrewConstants.validar_amortiguacion(value)
        if not valido:
            raise ScrewModelError(msg)
        self._b = value
    
    @property
    def k(self) -> float:
        """Constante del resorte (N/m)."""
        return self._k
    
    @k.setter
    def k(self, value: float):
        """Establece constante elástica con validación."""
        valido, msg = ScrewConstants.validar_rigidez(value)
        if not valido:
            raise ScrewModelError(msg)
        self._k = value
    
    @property
    def tiempo(self) -> float:
        """Tiempo actual de simulación."""
        return self._time
    
    @property
    def F(self) -> float:
        """Última fuerza aplicada."""
        return self._F
    
    def step(self, dt: float, F: float = 0.0) -> Tuple[float, float, float]:
        """
        Avanza la simulación un timestep usando RK4.
        
        Args:
            dt: Timestep en segundos (típicamente 0.016 para ~60 FPS)
            F: Fuerza externa aplicada en N (default: 0.0)
        
        Returns:
            Tupla (y, v, a) después del paso
        
        Example:
            >>> model = ScrewModel()
            >>> y, v, a = model.step(0.016, 10.0)
            >>> print(f"Posición: {y:.4f}m")
        """
        if dt <= 0:
            raise ScrewModelError("dt debe ser positivo")
        
        valido, msg = ScrewConstants.validar_fuerza(F)
        if not valido:
            raise ScrewModelError(msg)
        
        self._F = F
        
        state = np.array([self._y, self._v])
        
        new_state = rk4_step(
            state,
            dt,
            compute_derivatives,
            self._m,
            self._b,
            self._k,
            F
        )
        
        self._y, self._v = new_state
        self._a = (F - self._b * self._v - self._k * self._y) / self._m
        self._time += dt
        
        return self._y, self._v, self._a
    
    def get_state(self) -> dict:
        """
        Retorna el estado actual del modelo.
        
        Returns:
            Diccionario con:
            - y: posición
            - v: velocidad
            - a: aceleración
            - t: tiempo
            - m: masa
            - b: amortiguación
            - k: constante elástica
            - F: fuerza aplicada
        """
        return {
            'y': self._y,
            'v': self._v,
            'a': self._a,
            't': self._time,
            'm': self._m,
            'b': self._b,
            'k': self._k,
            'F': self._F
        }
    
    def reset(self, y0: float = 0.0, v0: float = 0.0):
        """
        Reinicia el modelo a condiciones iniciales.
        
        Args:
            y0: Nueva posición inicial
            v0: Nueva velocidad inicial
        """
        self._y = y0
        self._v = v0
        self._a = 0.0
        self._F = 0.0
        self._time = 0.0
    
    def get_natural_frequency(self) -> float:
        """
        Calcula la frecuencia natural no amortiguada.
        
        ωn = √(k/m)
        
        Returns:
            Frecuencia natural en rad/s
        """
        if self._m <= 0:
            raise ScrewModelError("Masa debe ser positiva")
        return np.sqrt(self._k / self._m)
    
    def get_damping_ratio(self) -> float:
        """
        Calcula el factor de amortiguamiento (zeta).
        
        ζ = b / (2√(km))
        
        Returns:
            Factor de amortiguamiento (adimensional)
        
        Note:
            ζ < 1: Subamortiguado
            ζ = 1: Crítico
            ζ > 1: Sobreamortiguado
        """
        wn = self.get_natural_frequency()
        if wn <= 0:
            return 0.0
        return self._b / (2.0 * self._m * wn)
    
    def get_damping_type(self) -> str:
        """
        Determina el tipo de amortiguamiento.
        
        Returns:
            "subamortiguado" si ζ < 1
            "critico" si ζ = 1
            "sobreamortiguado" si ζ > 1
        """
        zeta = self.get_damping_ratio()
        if zeta < 1.0:
            return "subamortiguado"
        elif zeta == 1.0:
            return "critico"
        else:
            return "sobreamortiguado"
    
    def get_damped_frequency(self) -> float:
        """
        Calcula la frecuencia amortiguada.
        
        ωd = ωn√(1 - ζ²)
        
        Returns:
            Frecuencia amortiguada en rad/s
        """
        zeta = self.get_damping_ratio()
        wn = self.get_natural_frequency()
        
        if zeta >= 1.0:
            return 0.0
        
        return wn * np.sqrt(1.0 - zeta**2)
    
    def get_parameters(self) -> dict:
        """
        Retorna todos los parámetros derivados.
        
        Returns:
            Diccionario con:
            - omega_n: frecuencia natural
            - omega_d: frecuencia amortiguada
            - zeta: factor de amortiguamiento
            - tipo: tipo de amortiguamiento
        """
        return {
            'omega_n': self.get_natural_frequency(),
            'omega_d': self.get_damped_frequency(),
            'zeta': self.get_damping_ratio(),
            'tipo': self.get_damping_type()
        }
    
    def apply_impulse(self, impulse: float):
        """
        Aplica un impulso instantáneo al sistema.
        
        Args:
            impulse: Impulso en Ns (cambia velocidad)
        """
        self._v += impulse / self._m
    
    def apply_step_force(self, F: float, duration: float) -> Tuple[float, float, float]:
        """
        Aplica una fuerza constante por una duración.
        
        Args:
            F: Fuerza en N
            duration: Duración en segundos
        
        Returns:
            Estado final (y, v, a)
        """
        n_steps = max(1, int(duration / ScrewConstants.DT_DEFAULT))
        dt = duration / n_steps
        
        for _ in range(n_steps):
            self.step(dt, F)
        
        return self._y, self._v, self._a
    
    def __repr__(self) -> str:
        return (f"ScrewModel(m={self._m}, b={self._b}, k={self._k}, "
                f"y={self._y:.4f}, v={self._v:.4f})")
    
    def __str__(self) -> str:
        params = self.get_parameters()
        return (f"ScrewModel\n"
                f"  Parámetros: m={self._m}kg, b={self._b}Ns/m, k={self._k}N/m\n"
                f"  Estado: y={self._y:.4f}m, v={self._v:.4f}m/s, a={self._a:.4f}m/s²\n"
                f"  ωn={params['omega_n']:.2f}rad/s, ζ={params['zeta']:.3f} ({params['tipo']})")