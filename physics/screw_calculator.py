"""
Calculadora física del tornillo - Cálculo de VM y parámetros.

Este módulo proporciona funciones para calcular la Ventaja Mecánica (VM)
y otros parámetros del tornillo como máquina simple.

Fórmulas:
- VM = (2πr) / L  (Ventaja mecánica)
- F_salida = F_entrada × VM
- Δx = θ × (L / 2π)  (Desplazamiento)
"""

import math
from typing import Tuple, Optional


class ScrewCalculatorError(Exception):
    """Excepción para errores de cálculo."""
    pass


def calcular_vm(radio: float, paso: float) -> float:
    """
    Calcula la Ventaja Mecánica del tornillo.
    
    VM = (2πr) / L
    
    La VM representa cuántas veces se amplifica la fuerza de entrada.
    
    Args:
        radio: Radio de giro en metros (r > 0)
        paso: Paso de la rosca en metros (L > 0)
    
    Returns:
        Ventaja mecánica (adimensional)
    
    Raises:
        ScrewCalculatorError: Si los parámetros son inválidos
    
    Example:
        >>> vm = calcular_vm(0.05, 0.002)
        >>> print(f"VM = {vm:.2f}")
        VM = 157.08
    """
    if paso <= 0:
        raise ScrewCalculatorError("El paso (L) debe ser positivo")
    if radio <= 0:
        raise ScrewCalculatorError("El radio (r) debe ser positivo")
    
    vm = (2.0 * math.pi * radio) / paso
    return vm


def calcular_f_salida(f_entrada: float, vm: float) -> float:
    """
    Calcula la fuerza de salida usando la VM.
    
    F_salida = F_entrada × VM
    
    Args:
        f_entrada: Fuerza de entrada en Newtons
        vm: Ventaja mecánica
    
    Returns:
        Fuerza de salida en Newtons
    """
    return f_entrada * vm


def calcular_desplazamiento(angulo: float, paso: float) -> float:
    """
    Calcula el desplazamiento lineal del tornillo.
    
    Δx = θ × (L / 2π)
    
    Args:
        angulo: Ángulo de rotación en radianes
        paso: Paso de la rosca en metros
    
    Returns:
        Desplazamiento lineal en metros
    """
    return angulo * (paso / (2.0 * math.pi))


def validar_parametros(
    f_entrada: float,
    radio: float,
    paso: float,
    angulo: float = 360.0
) -> Tuple[bool, Optional[str]]:
    """
    Valida los parámetros del tornillo.
    
    Args:
        f_entrada: Fuerza de entrada en Newtons
        radio: Radio de giro en metros
        paso: Paso de rosca en metros
        angulo: Ángulo de rotación en grados
    
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    from .constants import ScrewConstants
    
    if f_entrada < ScrewConstants.F_MIN:
        return False, f"Fuerza mínima: {ScrewConstants.F_MIN}N"
    if f_entrada > ScrewConstants.F_MAX:
        return False, f"Fuerza máxima: {ScreConstants.F_MAX}N"
    
    if radio < ScrewConstants.RADIO_MIN:
        return False, f"Radio mínimo: {ScrewConstants.RADIO_MIN}m"
    if radio > ScrewConstants.RADIO_MAX:
        return False, f"Radio máximo: {ScrewConstants.RADIO_MAX}m"
    
    if paso < ScrewConstants.PASO_MIN:
        return False, f"Paso mínimo: {ScrewConstants.PASO_MIN}m"
    if paso > ScrewConstants.PASO_MAX:
        return False, f"Paso máximo: {ScrewConstants.PASO_MAX}m"
    
    if angulo < 0:
        return False, "El ángulo no puede ser negativo"
    
    return True, None


def calcular_todo(
    f_entrada: float,
    radio: float,
    paso: float,
    angulo: float = 360.0
) -> dict:
    """
    Calcula todos los parámetros del tornillo.
    
    Args:
        f_entrada: Fuerza de entrada en Newtons
        radio: Radio de giro en metros
        paso: Paso de rosca en metros
        angulo: Ángulo de rotación en grados
    
    Returns:
        Diccionario con:
        - vm: ventaja mecánica
        - f_salida: fuerza de salida
        - desplazamiento: desplazamiento lineal
        - angulo_rad: ángulo en radianes
    
    Raises:
        ScrewCalculatorError: Si los parámetros son inválidos
    """
    valido, mensaje = validar_parametros(f_entrada, radio, paso, angulo)
    if not valido:
        raise ScrewCalculatorError(mensaje)
    
    vm = calcular_vm(radio, paso)
    f_salida = calcular_f_salida(f_entrada, vm)
    angulo_rad = math.radians(angulo)
    desplazamiento = calcular_desplazamiento(angulo_rad, paso)
    
    return {
        'vm': vm,
        'f_salida': f_salida,
        'desplazamiento': desplazamiento,
        'angulo_rad': angulo_rad
    }