"""
Controlador de Calculadora.

Maneja los cálculos de la ventana calculadora:
- Cálculo de VM
- Validaciones
- Manejo de errores
"""

from physics import (
    calcular_vm,
    calcular_todo,
    validar_parametros,
    ScrewCalculatorError
)
from typing import Tuple, Optional


class CalculatorController:
    """
    Controlador para cálculos de tornillo.
    
    Maneja:
    - Cálculo de VM
    - Validaciones de entrada
    - Manejo de errores
    
    Attributes:
        ultimo_resultado: Último resultado calculado
        ultimo_error: Último error encontrado
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        self._ultimo_resultado = {}
        self._ultimo_error = ""
    
    @property
    def ultimo_resultado(self) -> dict:
        """Último resultado calculado."""
        return self._ultimo_resultado
    
    @property
    def ultimo_error(self) -> str:
        """Último error encontrado."""
        return self._ultimo_error
    
    def calcular_vm(self, radio: float, paso: float) -> float:
        """
        Calcula la Ventaja Mecánica.
        
        VM = (2πr) / L
        
        Args:
            radio: Radio de giro en metros
            paso: Paso de rosca en metros
        
        Returns:
            VM (adimensional)
        
        Raises:
            ScrewCalculatorError: Si parámetros inválidos
        """
        try:
            vm = calcular_vm(radio, paso)
            self._ultimo_resultado = {'vm': vm, 'radio': radio, ' paso': paso}
            return vm
        except ScrewCalculatorError as e:
            self._ultimo_error = str(e)
            raise
    
    def calcular_todo(
        self,
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
            ScrewCalculatorError: Si parámetros inválidos
        """
        try:
            resultado = calcular_todo(f_entrada, radio, paso, angulo)
            self._ultimo_resultado = resultado
            self._ultimo_error = ""
            return resultado
        except ScrewCalculatorError as e:
            self._ultimo_error = str(e)
            raise
    
    def validar_entrada(
        self,
        f_entrada: float,
        radio: float,
        paso: float,
        angulo: float = 360.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida los parámetros de entrada.
        
        Args:
            f_entrada: Fuerza de entrada
            radio: Radio de giro
            paso: Paso de rosca
            angulo: Ángulo de rotación
        
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        return validar_parametros(f_entrada, radio, paso, angulo)
    
    def calcular_fuerza_salida(self, f_entrada: float, vm: float) -> float:
        """
        Calcula F_salida desde F_entrada y VM.
        
        Args:
            f_entrada: Fuerza de entrada
            vm: Ventaja mecánica
        
        Returns:
            Fuerza de salida
        """
        from physics import calcular_f_salida
        return calcular_f_salida(f_entrada, vm)
    
    def calcular_desplazamiento(self, angulo: float, paso: float) -> float:
        """
        Calcula el desplazamiento lineal.
        
        Args:
            angulo: Ángulo en radianes
            paso: Paso de rosca
        
        Returns:
            Desplazamiento en metros
        """
        from physics import calcular_desplazamiento
        return calcular_desplazamiento(angulo, paso)
    
    def limpiar(self):
        """Limpia el último resultado."""
        self._ultimo_resultado = {}
        self._ultimo_error = ""