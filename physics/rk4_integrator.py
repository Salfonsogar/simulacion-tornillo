"""
Integrador Runge-Kutta de cuarto orden (RK4).

Implementa la integración numérica para sistemas de ecuaciones
diferenciales ordinarias (EDO) de primer orden.

Este módulo se usa para resolver la ecuación del sistema amortiguado:
    m*y''(t) + b*y'(t) + k*y(t) = F(t)

Convirtiendo a sistema de primer orden:
    dy/dt = v
    dv/dt = (F - b*v - k*y) / m
"""

import numpy as np
from typing import Callable, Tuple


def rk4_step(
    state: np.ndarray,
    dt: float,
    derivatives_fn: Callable,
    *args
) -> np.ndarray:
    """
    Integración Runge-Kutta de cuarto orden para un paso.
    
    El método RK4 evalúa la derivada en 4 puntos dentro del intervalo
    y las combina ponderadamente para obtener mayor precisión que Euler.
    
    Args:
        state: Vector de estado actual [y, v]
        dt: Timestep (intervalo de tiempo)
        derivatives_fn: Función que calcula las derivadas
            Signature: fn(state, *args) -> np.ndarray
        *args: Argumentos adicionales para derivatives_fn
    
    Returns:
        Nuevo vector de estado después de dt
    
    Example:
        >>> state = np.array([0.0, 1.0])  # y=0, v=1
        >>> new_state = rk4_step(state, 0.016, compute_derivatives, 1.0, 0.5, 100.0, 10.0)
    """
    if dt <= 0:
        raise ValueError("dt debe ser positivo")
    
    if len(state) != 2:
        raise ValueError("state debe tener dimensión 2: [y, v]")
    
    k1 = derivatives_fn(state, *args)
    
    k2 = derivatives_fn(state + 0.5 * dt * k1, *args)
    
    k3 = derivatives_fn(state + 0.5 * dt * k2, *args)
    
    k4 = derivatives_fn(state + dt * k3, *args)
    
    new_state = state + (dt / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
    
    return new_state


def compute_derivatives(
    state: np.ndarray,
    m: float,
    b: float,
    k: float,
    F: float = 0.0
) -> np.ndarray:
    """
    Calcula las derivadas para el sistema amortiguado de segundo orden.
    
    Convierte: m*y'' + b*y' + k*y = F
    En sistema de primer orden:
        y' = v
        v' = (F - b*v - k*y) / m
    
    Args:
        state: Vector de estado [y, v]
        m: Masa (kg)
        b: Coeficiente de amortiguación (Ns/m)
        k: Constante del resorte (N/m)
        F: Fuerza externa (N), por defecto 0
    
    Returns:
        Vector de derivadas [dy/dt, dv/dt]
    
    Example:
        >>> state = np.array([0.1, 0.0])  # y=0.1m, v=0
        >>> derivs = compute_derivatives(state, 1.0, 0.5, 100.0, 10.0)
        >>> print(derivs)  # [v, a]
    """
    y, v = state
    
    a = (F - b * v - k * y) / m
    
    return np.array([v, a])


def rk4_multi_step(
    state: np.ndarray,
    dt: float,
    n_steps: int,
    derivatives_fn: Callable,
    *args
) -> np.ndarray:
    """
    Ejecuta múltiples pasos de integración RK4.
    
    Args:
        state: Estado inicial
        dt: Timestep
        n_steps: Número de pasos
        derivatives_fn: Función de derivadas
        *args: Argumentos adicionales
    
    Returns:
        Estado después de n_steps
    """
    state_current = state.copy()
    
    for _ in range(n_steps):
        state_current = rk4_step(state_current, dt, derivatives_fn, *args)
    
    return state_current


def compute_analytical_solution(
    t: np.ndarray,
    y0: float,
    v0: float,
    m: float,
    b: float,
    k: float,
    F: float = 0.0
) -> np.ndarray:
    """
    Calcula la solución analítica del oscilador amortiguado.
    
    Útil para comparar con la solución numérica de RK4.
    
    Args:
        t: Vector de tiempos
        y0: Posición inicial
        v0: Velocidad inicial
        m: Masa
        b: Amortiguación
        k: Constante elástica
        F: Fuerza externa (opcional)
    
    Returns:
        Vector de posiciones y(t)
    """
    if m <= 0:
        raise ValueError("m debe ser positivo")
    
    w0 = np.sqrt(k / m)
    zeta = b / (2 * m * w0)
    
    A = y0
    B = (v0 + zeta * w0 * y0) / w0 if w0 > 0 else v0
    
    if zeta < 1:
        wd = w0 * np.sqrt(1 - zeta**2)
        y = np.exp(-zeta * w0 * t) * (
            A * np.cos(wd * t) + 
            B * np.sin(wd * t)
        )
    elif zeta == 1:
        y = (A + B * t) * np.exp(-w0 * t)
    else:
        y = np.exp(-zeta * w0 * t) * (
            A * np.cosh(w0 * np.sqrt(zeta**2 - 1) * t) +
            B * np.sinh(w0 * np.sqrt(zeta**2 - 1) * t)
        )
    
    if F != 0:
        y += (F / k) * (1 - np.exp(-zeta * w0 * t) * (
            np.cos(wd * t) + 
            (zeta * w0 / wd) * np.sin(wd * t)
        )) if zeta < 1 else (F / k) * (1 - np.exp(-w0 * t))
    
    return y


def validate_rk4_accuracy(
    dt: float,
    m: float,
    b: float,
    k: float,
    t_end: float = 1.0
) -> dict:
    """
    Valida la precisión del integrador RK4 comparando con solución analítica.
    
    Args:
        dt: Timestep a probar
        m: Masa
        b: Amortiguación
        k: Constante elástica
        t_end: Tiempo final de simulación
    
    Returns:
        Diccionario con error máximo y error RMS
    """
    t = np.arange(0, t_end, dt)
    y0, v0 = 0.1, 0.0
    
    y_analytical = compute_analytical_solution(t, y0, v0, m, b, k)
    
    state = np.array([y0, v0])
    y_numerical = []
    
    for _ in t:
        state = rk4_step(state, dt, compute_derivatives, m, b, k, 0.0)
        y_numerical.append(state[0])
    
    y_numerical = np.array(y_numerical)
    
    error = np.abs(y_analytical[:-1] - y_numerical)
    
    return {
        'dt': dt,
        'max_error': np.max(error),
        'rms_error': np.sqrt(np.mean(error**2)),
        't_end': t_end
    }