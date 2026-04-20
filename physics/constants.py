"""
Constantes físicas del sistema de tornillo.

Define los límites y valores por defecto para los parámetros
físicos del modelo de sistema dinámico amortiguado.

Ecuación: m*y''(t) + b*y'(t) + k*y(t) = F(t)
"""

from typing import Final


class ScrewConstants:
    """
    Constantes físicas para el modelo del tornillo.
    
    Attributes:
        MASA_MIN: Masa mínima (kg)
        MASA_MAX: Masa máxima (kg)
        B_MIN: Amortiguación mínima (Ns/m)
        B_MAX: Amortiguación máxima (Ns/m)
        K_MIN: Constante elástica mínima (N/m)
        K_MAX: Constante elástica máxima (N/m)
        F_MIN: Fuerza mínima (N)
        F_MAX: Fuerza máxima (N)
        DT_DEFAULT: Timestep por defecto (segundos)
        MAX_HISTORY: Máximo puntos en historial para gráfica
    """
    
    MASA_MIN: Final[float] = 0.1
    MASA_MAX: Final[float] = 100.0
    
    B_MIN: Final[float] = 0.0
    B_MAX: Final[float] = 50.0
    
    K_MIN: Final[float] = 1.0
    K_MAX: Final[float] = 1000.0
    
    F_MIN: Final[float] = 0.0
    F_MAX: Final[float] = 10000.0
    
    DT_DEFAULT: Final[float] = 0.016
    
    MAX_HISTORY: Final[int] = 1000
    
    RADIO_MIN: Final[float] = 0.001
    RADIO_MAX: Final[float] = 0.5
    
    PASO_MIN: Final[float] = 0.0001
    PASO_MAX: Final[float] = 0.05
    
    @classmethod
    def validar_masa(cls, m: float) -> tuple[bool, str]:
        """Valida el valor de masa."""
        if m < cls.MASA_MIN:
            return False, f"Masa mínima: {cls.MASA_MIN}kg"
        if m > cls.MASA_MAX:
            return False, f"Masa máxima: {cls.MASA_MAX}kg"
        return True, ""
    
    @classmethod
    def validar_amortiguacion(cls, b: float) -> tuple[bool, str]:
        """Valida el valor de amortiguación."""
        if b < cls.B_MIN:
            return False, f"Amortiguación mínima: {cls.B_MIN}Ns/m"
        if b > cls.B_MAX:
            return False, f"Amortiguación máxima: {cls.B_MAX}Ns/m"
        return True, ""
    
    @classmethod
    def validar_rigidez(cls, k: float) -> tuple[bool, str]:
        """Valida el valor de constante elástica."""
        if k < cls.K_MIN:
            return False, f"Constante mínima: {cls.K_MIN}N/m"
        if k > cls.K_MAX:
            return False, f"Constante máxima: {cls.K_MAX}N/m"
        return True, ""
    
    @classmethod
    def validar_fuerza(cls, F: float) -> tuple[bool, str]:
        """Valida el valor de fuerza."""
        if F < cls.F_MIN:
            return False, f"Fuerza mínima: {cls.F_MIN}N"
        if F > cls.F_MAX:
            return False, f"Fuerza máxima: {cls.F_MAX}N"
        return True, ""
    
    @classmethod
    def validar_radio(cls, r: float) -> tuple[bool, str]:
        """Valida el valor de radio."""
        if r < cls.RADIO_MIN:
            return False, f"Radio mínimo: {cls.RADIO_MIN}m"
        if r > cls.RADIO_MAX:
            return False, f"Radio máximo: {cls.RADIO_MAX}m"
        return True, ""
    
    @classmethod
    def validar_paso(cls, L: float) -> tuple[bool, str]:
        """Valida el valor de paso."""
        if L < cls.PASO_MIN:
            return False, f"Paso mínimo: {cls.PASO_MIN}m"
        if L > cls.PASO_MAX:
            return False, f"Paso máximo: {cls.PASO_MAX}m"
        return True, ""