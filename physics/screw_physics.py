#!/usr/bin/env python3
"""
Módulo de Física del Tornillo - Motor de Cálculo

Este módulo implementa las ecuaciones físicas fundamentales del tornillo como máquina simple.
El tornillo es una transformación de estado profunda similar a algoritmos criptográficos como AES-256:
- Input: movimiento circular (rotación) + energía
- Transformación: ventaja mecánica basada en geometría
- Output: movimiento lineal (fuerza amplificada)
- La transformación es irreversible: sin el torque correcto no hay avance lineal

Fórmulas implementadas:
1. VM = (2πr)/L - Ventaja mecánica basada en radio y paso
2. F_salida = F_entrada * VM - Fuerza de salida amplificada
3. Δx = θ(L/2π) - Desplazamiento lineal por rotación
4. y(t) = Ae^(-γt)cos(ωt + φ) - Oscilador amortiguado (2do orden)

Autor: Simulador de Tornillo - Física de Máquinas Simples
Fecha: 2026
"""

import math
from typing import Tuple, Optional


class ScrewPhysicsError(Exception):
    """Excepción personalizada para errores físicos del tornillo."""
    pass


class ScrewParameters:
    """
    Clase contenedor para parámetros del tornillo.

    Esta estructura de datos representa el "estado" del tornillo,
    análoga a un bloque de datos en criptografía AES-256.
    """
    def __init__(self,
                 f_entrada: float,
                 radio: float,
                 paso: float,
                 angulo: float = 360.0):
        """
        Inicializa parámetros del tornillo.

        Args:
            f_entrada: Fuerza de entrada en Newtons (N)
            radio: Radio de giro del braço en metros (m)
            paso: Paso de la rosca en metros (m)
            angulo: Ángulo de rotación en grados (por defecto 360° = 1 vuelta)
        """
        self.f_entrada = f_entrada
        self.radio = radio
        self.paso = paso
        self.angulo = math.radians(angulo)  # Convertir a radianes

    def to_dict(self) -> dict:
        """Convierte parámetros a diccionario."""
        return {
            'f_entrada': self.f_entrada,
            'radio': self.radio,
            'paso': self.paso,
            'angulo': math.degrees(self.angulo)
        }


class ScrewLimits:
    """
    Define los límites de seguridad física para el tornillo.

    Similar a los límites de un sistema criptográfico:
    - Fuerza máxima: resistencia del material
    - Radio mínimo: precisión de ingeniería
    - Paso máximo: límite del proceso de fabricación
    """
    # Límites de fuerza (N)
    F_ENTRADA_MIN = 0.1
    F_ENTRADA_MAX = 10000.0

    # Límites de radio (m)
    RADIO_MIN = 0.01
    RADIO_MAX = 1.0

    # Límites de paso (m)
    PASO_MIN = 0.0001
    PASO_MAX = 0.05

    # Límites de ángulo (grados)
    ANGULO_MIN = 0.0
    ANGULO_MAX = 10800.0  # 30 vueltas máximo

    # Umbral crítico para fallo estructural (N)
    # Cuando F_salida supera este valor, el material falla
    FUERZA_SALIDA_CRITICA = 500000.0


class ScrewCalculator:
    """
    Calculadora física del tornillo.

    Implementa la transformación de energía mecánica:
    Input: Fuerza pequeña + distancia larga → Output: Fuerza grande + distancia corta

    Esta relación es análoga a la criptografía:
    - La "llave" (radio, paso) transforma datos crudos (F_entrada)
    - El resultado (F_salida) es "fijo" e irreversible sin la llave correcta
    - Similar a cómo AES-256 firma digitalmente un bloque
    """

    @staticmethod
    def calcular_vm(radio: float, paso: float) -> float:
        """
        Calcula la Ventaja Mecánica del tornillo.

        La VM representa cuántas veces se amplifica la fuerza de entrada.
        Es similar a la "factor de expansión" en algoritmos de hash.

        Fórmula: VM = (2πr) / L

        Args:
            radio: Radio de giro del braço en metros
            paso: Paso de la rosca en metros

        Returns:
            Ventaja mecánica (adimensional)

        Ejemplo:
            Un tornillo con r=0.05m y L=0.002m tiene VM = (2π×0.05)/0.002 ≈ 157
            Esto significa que una fuerza de 1N se convierte en 157N de salida
        """
        if paso <= 0:
            raise ScrewPhysicsError("[CRITICAL ERROR] El paso debe ser positivo")
        vm = (2.0 * math.pi * radio) / paso
        return vm

    @staticmethod
    def calcular_f_salida(f_entrada: float, vm: float) -> float:
        """
        Calcula la fuerza de salida usando la VM.

        F_salida = F_entrada × VM

        Esta transformación es unidireccional: no puedes obtener F_entrada
        de F_salida sin conocer la VM (la "llave" del tornillo).

        Args:
            f_entrada: Fuerza de entrada en Newtons
            vm: Ventaja mecánica

        Returns:
            Fuerza de salida en Newtons
        """
        return f_entrada * vm

    @staticmethod
    def calcular_desplazamiento(angulo: float, paso: float) -> float:
        """
        Calcula el desplazamiento lineal del tornillo.

        Δx = θ × (L / 2π)

        Esta fórmula muestra la correspondencia entre rotación y traslación:
        - Una vuelta completa (2π rad) = un paso de rosca
        - Fracciones de vuelta = fracciones proporcionales de paso

        Args:
            angulo: Ángulo de rotación en radianes
            paso: Paso de la rosca en metros

        Returns:
            Desplazamiento lineal en metros
        """
        return angulo * (paso / (2.0 * math.pi))

@staticmethod
    def validar_parametros(f_entrada: float, radio: float,
                          paso: float, angulo: float = 360.0) -> Tuple[bool, Optional[str]]:
        """
        Valida los parámetros физические del tornillo.

        Args:
            f_entrada: Fuerza de entrada
            radio: Radio de giro
            paso: Paso de rosca
            angulo: Ángulo de rotación

        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Validar fuerza de entrada
        if f_entrada < ScrewLimits.F_ENTRADA_MIN:
            return False, f"[CRITICAL ERROR] La fuerza mínima es {ScrewLimits.F_ENTRADA_MIN}N"
        if f_entrada > ScrewLimits.F_ENTRADA_MAX:
            return False, f"[CRITICAL ERROR] La fuerza excede {ScrewLimits.F_ENTRADA_MAX}N - ¡Riesgo de rotura!"

        # Validar radio
        if radio < ScrewLimits.RADIO_MIN:
            return False, f"[CRITICAL ERROR] Radio demasiado pequeño (mín {ScrewLimits.RADIO_MIN}m)"
        if radio > ScrewLimits.RADIO_MAX:
            return False, f"[CRITICAL ERROR] Radio demasiado grande (máx {ScrewLimits.RADIO_MAX}m)"

        # Validar paso
        if paso < ScrewLimits.PASO_MIN:
            return False, f"[CRITICAL ERROR] Paso demasiado pequeño (mín {ScrewLimits.PASO_MIN}m)"
        if paso > ScrewLimits.PASO_MAX:
            return False, f"[CRITICAL ERROR] Paso demasiado grande (máx {ScrewLimits.PASO_MAX}m)"

        # Validar ángulo
        if angulo < ScrewLimits.ANGULO_MIN:
            return False, "[CRITICAL ERROR] El ángulo no puede ser negativo"
        if angulo > ScrewLimits.ANGULO_MAX:
            return False, f"[CRITICAL ERROR] Ángulo máximo excedido ({ScrewLimits.ANGULO_MAX}°)"

        return True, None

    @staticmethod
    def validar_f_salida_critica(f_salida: float) -> Tuple[bool, Optional[str]]:
        """
        Valida si la fuerza de salida supera el umbral crítico del material.
        
        Cuando F_salida > FUERZA_SALIDA_CRITICA, el material falla estructuralmente.
        En términos criptográficos, esto representa "datos corruptos" irrecoverables.

        Args:
            f_salida: Fuerza de salida calculada

        Returns:
            Tupla (es_seguro, mensaje)
        """
        if f_salida > ScrewLimits.FUERZA_SALIDA_CRITICA:
            return False, (
                f"[CRITICAL ERROR] Fallo estructural: "
                f"F_salida={f_salida:.0f}N excede el límite del material "
                f"({ScrewLimits.FUERZA_SALIDA_CRITICA}N) - DATOS CORRUPTOS"
            )
        return True, None

    @staticmethod
    def calcular_todo(f_entrada: float, radio: float,
                      paso: float, angulo: float = 360.0) -> dict:
        """
        Calcula todos los parámetros del tornillo.

        Args:
            f_entrada: Fuerza de entrada en Newtons
            radio: Radio de giro en metros
            paso: Paso de rosca en metros
            angulo: Ángulo de rotación en grados

        Returns:
            Diccionario con todos los results

        Raises:
            ScrewPhysicsError: Si los parámetros son inválidos
        """
        # Validar primero
        es_valido, mensaje = ScrewCalculator.validar_parametros(
            f_entrada, radio, paso, angulo
        )
        if not es_valido:
            raise ScrewPhysicsError(mensaje)

        # Calcular VM (la "llave" criptográfica)
        vm = ScrewCalculator.calcular_vm(radio, paso)

        # Calcular fuerza de salida (el "bloque cifrado")
        f_salida = ScrewCalculator.calcular_f_salida(f_entrada, vm)

        # Calcular desplazamiento (transformación lineal)
        angulo_rad = math.radians(angulo)
        desplazamiento = ScrewCalculator.calcular_desplazamiento(angulo_rad, paso)

        return {
            'vm': vm,
            'f_salida': f_salida,
            'desplazamiento': desplazamiento,
            'angulo_rad': angulo_rad,
            'es_valido': True
        }


class OscillatorSimulation:
    """
    Simulación del oscilador amortiguado de segundo orden.

    Cuando el motor del tornillo arranca de golpe, el sistema puede oscilar
    antes de estabilizarse. Este modelo describe esa respuesta transitoria:

    y(t) = A × e^(-γt) × cos(ωt + φ)

    Donde:
    - A = amplitud inicial de la oscilación
    - γ = coeficiente de amortiguación
    - ω = frecuencia natural del sistema
    - φ = fase inicial
    - t = tiempo

    Esta ecuación es similar a la respuesta transitoria en sistemas de control.
    """

    @staticmethod
    def calcular_y(t: float, A: float = 1.0, gamma: float = 0.5,
                   omega: float = 2.0, phi: float = 0.0) -> float:
        """
        Calcula la posición y(t) en el tiempo t.

        Args:
            t: Tiempo en segundos
            A: Amplitud inicial
            gamma: Coeficiente de amortiguación
            omega: Frecuencia angular natural
            phi: Fase inicial

        Returns:
            Posición en el tiempo t
        """
        return A * math.exp(-gamma * t) * math.cos(omega * t + phi)

    @staticmethod
    def generar_curva(tiempo_max: float, num_puntos: int = 500,
                      A: float = 1.0, gamma: float = 0.5,
                      omega: float = 2.0, phi: float = 0.0) -> Tuple[list, list]:
        """
        Genera los datos para graficar y(t).

        Args:
            tiempo_max: Tiempo máximo de simulación
            num_puntos: Número de puntos a generar
            A: Amplitud inicial
            gamma: Coeficiente de amortiguación
            omega: Frecuencia angular
            phi: Fase inicial

        Returns:
            Tupla (tiempos, posiciones)
        """
        tiempos = []
        posiciones = []

        dt = tiempo_max / num_puntos
        for i in range(num_puntos + 1):
            t = i * dt
            y = OscillatorSimulation.calcular_y(t, A, gamma, omega, phi)
            tiempos.append(t)
            posiciones.append(y)

        return tiempos, posiciones