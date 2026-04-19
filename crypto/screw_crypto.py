#!/usr/bin/env python3
"""
Módulo de Criptografía del Tornillo - Analogía con AES-256

Este módulo implementa la analogía entre el tornillo como máquina simple
y los algoritmos de cifrado tipo AES-256:

RELACIÓN FÍSICA-CRIPTOGRÁFICA:
==============================
- VM (Ventaja Mecánica)     ↔  Clave criptográfica
- F_entrada (Fuerza input)  ↔  Datos crudos (texto claro)
- F_salida (Fuerza output)  ↔  Datos cifrados (ciphertext)
- Giro del tornillo         ↔  Ronda de cifrado
- Rotación completa (360°)  ↔  Una iteración completa del algoritmo
- Δx (Desplazamiento)       ↔  Estado transformado

El tornillo representa una transformación de estado profunda, análoga a 
algoritmos como AES-256, donde múltiples iteraciones controladas por una 
clave generan un resultado difícil de revertir sin la clave correcta.

MÉTODO DE CIFRADO:
==================
 nuevo_valor = (valor_ascii + clave) % 256

Este método de sustitución monoalfabética representa una vuelta simple.
Para mayor seguridad análoga a AES-256, se encadenan múltiples rondas.

Autor: Simulador de Tornillo - Física de Máquinas Simples
Fecha: 2026
"""

import math
from typing import Tuple, Optional, List, Union


class CryptoError(Exception):
    """Excepción personalizada para errores criptográficos."""
    pass


class ScrewCipher:
    """
    Implementa el cifrado basado en la física del tornillo.
    
    Cada vuelta del tornillo representa una ronda de transformación,
    donde la VM actúa como clave criptográfica.
    
    La transformación es similar a:
    - Input: Caracteres ASCII o valores numéricos
    - Clave: VM (Ventaja Mecánica calculada desde radio y paso)
    - Transformación: nueva = (valor + clave) % 256
    - Rondas: Número de giros del tornillo
    
    Esta estructura imita el funcionamiento de AES-256:
    - Múltiples rondas (giros) transforman el estado
    - La clave (VM) debe ser conocida para revertir
    - Sin la clave correcta, los datos son irrecuperables
    """

    # Constantes de configuración
    RONDAS_POR_GIRO = 10  # Cada vuelta = 10 rondas de cifrado
    TAMANO_BLOQUE = 16    # Similar a AES-128/256 (16 bytes)
    UMBRAL_CRITICO = 500000  # Fuerza de salida máxima antes de fallo estructural

    @staticmethod
    def calcular_vm(radio: float, paso: float) -> float:
        """
        Calcula la Ventaja Mecánica del tornillo.
        
        VM = (2πr) / L
        
        Esta VM actúa como la "clave" en el cifrado.
        
        Args:
            radio: Radio de giro en metros (r > 0)
            paso: Paso de la rosca en metros (L > 0)
            
        Returns:
            Ventaja mecánica (clave criptográfica)
            
        Raises:
            CryptoError: Si los parámetros físicos son inválidos
        """
        if paso <= 0:
            raise CryptoError("[CRITICAL ERROR] El paso (L) debe ser positivo")
        if radio <= 0:
            raise CryptoError("[CRITICAL ERROR] El radio (r) debe ser positivo")
            
        vm = (2.0 * math.pi * radio) / paso
        
        if vm <= 0:
            raise CryptoError("[CRITICAL ERROR] VM calculada es inválida")
            
        return vm

    @staticmethod
    def texto_a_valores(texto: str) -> List[int]:
        """
        Convierte texto a lista de valores ASCII.
        
        Args:
            texto: Cadena de texto a convertir
            
        Returns:
            Lista de valores ASCII [0-255]
        """
        return [ord(c) % 256 for c in texto]

    @staticmethod
    def valores_a_texto(valores: List[int]) -> str:
        """
        Convierte valores ASCII a texto.
        
        Args:
            valores: Lista de valores [0-255]
            
        Returns:
            Cadena de texto
        """
        return ''.join(chr(v % 256) for v in valores)

    @staticmethod
    def valores_a_hex(valores: List[int]) -> str:
        """
        Convierte valores a representación hexadecimal.
        
        Args:
            valores: Lista de valores [0-255]
            
        Returns:
            Cadena hexadecimal separada por espacios
        """
        return ' '.join(f'{v:02X}' for v in valores)

    @staticmethod
    def cifrar_ronda(datos: List[int], clave: float) -> List[int]:
        """
        Aplica UNA ronda de cifrado por sustitución.
        
        Fórmula: nuevo_valor = (valor_original + clave) % 256
        
        Args:
            datos: Lista de valores a cifrar [0-255]
            clave: VM como clave criptográfica
            
        Returns:
            Lista de valores cifrados
        """
        clave_entera = int(clave) % 256
        return [(dato + clave_entera) % 256 for dato in datos]

    @staticmethod
    def descifrar_ronda(datos: List[int], clave: float) -> List[int]:
        """
        Descifra UNA ronda usando la clave inversa.
        
        Fórmula: valor_original = (valor_cifrado - clave) % 256
        
        Args:
            datos: Lista de valores cifrados
            clave: VM como clave criptográfica
            
        Returns:
            Lista de valores descifrados
        """
        clave_entera = int(clave) % 256
        return [(dato - clave_entera) % 256 for dato in datos]

    @staticmethod
    def cifrar_multiplo(datos: List[int], vm: float, 
                        num_giros: int = 1) -> Tuple[List[int], int]:
        """
        Aplica múltiples rondas de cifrado (una por cada giro del tornillo).
        
        Cada vuelta del tornillo = RONDAS_POR_GIRO iteraciones del cifrado.
        
        Args:
            datos: Lista de valores a cifrar
            vm: Ventaja mecánica (clave)
            num_giros: Número de vueltas del tornillo
            
        Returns:
            Tupla (datos_cifrados, total_rondas_aplicadas)
            
        Example:
            >>> ScrewCipher.cifrar_multiplo([72, 111, 108, 97], 157.08, 1)
            ([229, 84, 59, 254], 10)  # 1 giro = 10 rondas
        """
        if num_giros < 1:
            num_giros = 1
        if num_giros > 100:
            raise CryptoError("[CRITICAL ERROR] Máximo 100 giros permitidos")
            
        total_rondas = num_giros * ScrewCipher.RONDAS_POR_GIRO
        
        resultado = datos.copy()
        for _ in range(total_rondas):
            resultado = ScrewCipher.cifrar_ronda(resultado, vm)
            
        return resultado, total_rondas

    @staticmethod
    def descifrar_multiplo(datos: List[int], vm: float,
                           num_giros: int = 1) -> List[int]:
        """
        Descifra múltiples rondas si la clave es correcta.
        
        Args:
            datos: Lista de valores cifrados
            vm: Ventaja mecánica (debe ser EXACTAMENTE la misma que en cifrado)
            num_giros: Número de giros original
            
        Returns:
            Lista de valores descifrados
            
        Raises:
            CryptoError: Si la clave no coincide exactamente
        """
        if num_giros < 1:
            num_giros = 1
            
        total_rondas = num_giros * ScrewCipher.RONDAS_POR_GIRO
        
        resultado = datos.copy()
        for _ in range(total_rondas):
            resultado = ScrewCipher.descifrar_ronda(resultado, vm)
            
        return resultado

    @staticmethod
    def verificar_clave(datos_originales: List[int], 
                        datos_cifrados: List[int],
                        vm: float, num_giros: int) -> bool:
        """
        Verifica si una clave es correcta para descifrar.
        
        Args:
            datos_originales: Datos originales (known plaintext)
            datos_cifrados: Datos cifrados
            vm: Clave a verificar
            num_giros: Número de giros original
            
        Returns:
            True si la clave es correcta
        """
        try:
            descifrado = ScrewCipher.descifrar_multiplo(datos_cifrados, vm, num_giros)
            return descifrado == datos_originales
        except:
            return False

    @staticmethod
    def cifrar_fuerza(f_entrada: float, vm: float, 
                      num_giros: int = 1) -> Tuple[float, int]:
        """
        Cifra el valor de fuerza de entrada (método numérico).
        
        Convierte F_entrada en un valor procesable y aplica transformación.
        
        Args:
            f_entrada: Fuerza de entrada en Newtons
            vm: Ventaja mecánica (clave)
            num_giros: Número de vueltas del tornillo
            
        Returns:
            Tupla (fuerza_cifrada, total_rondas)
        """
        # Convertir fuerza a representación numérica (escalar a rango [0, 255])
        valor_base = int(f_entrada * 10) % 256
        
        # Aplicar cifrado
        resultado, rondas = ScrewCipher.cifrar_multiplo([valor_base], vm, num_giros)
        
        # Reconvertir a fuerza (escalar de vuelta)
        f_salida = resultado[0] * 10.0
        
        # Verificar umbral crítico
        if f_salida > ScrewCipher.UMBRAL_CRITICO:
            raise CryptoError(
                f"[CRITICAL ERROR] Fallo estructural: F_salida={f_salida:.0f}N "
                f"excede el límite del material ({ScrewCipher.UMBRAL_CRITICO}N)"
            )
        
        return f_salida, rondas

    @staticmethod
    def descifrar_fuerza(f_cifrada: float, vm: float,
                         num_giros: int = 1) -> float:
        """
        Descifra el valor de fuerza (método numérico).
        
        Args:
            f_cifrada: Fuerza cifrada
            vm: Clave (debe ser exactamente la misma)
            num_giros: Número de giros original
            
        Returns:
            Fuerza descifrada
            
        Raises:
            CryptoError: Si la clave es incorrecta
        """
        # Convertir a valor base
        valor_cifrado = int(f_cifrada / 10.0) % 256
        
        # Intentar descifrado
        resultado = ScrewCipher.descifrar_multiplo([valor_cifrado], vm, num_giros)
        
        # Verificar si la clave era correcta (resultado debe ser razonable)
        f_original = resultado[0] * 10.0
        
        # Validar rango físico
        if f_original < 0.1 or f_original > ScrewCipher.UMBRAL_CRITICO / 10:
            raise CryptoError("[CRYPTO ERROR] Clave incorrecta - Descifrado inválido")
        
        return f_original

    @staticmethod
    def generar_bloque_visual(datos: List[int], 
                              tamano: int = 16) -> List[List[int]]:
        """
        Genera una matriz de bloque tipo AES para visualización.
        
        Args:
            datos: Lista de valores a formatear
            tamano: Tamaño del bloque (default 16 = AES block)
            
        Returns:
            Matriz bidimensional para visualización
        """
        # Padding al tamaño del bloque
        datos_padded = datos.copy()
        while len(datos_padded) < tamano:
            datos_padded.append(0)
            
        # Crear matriz 4x4
        bloque = []
        for i in range(0, len(datos_padded), 4):
            fila = datos_padded[i:i+4]
            bloque.append(fila)
            
        return bloque

    @staticmethod
    def formatear_bloque_hex(bloque: List[List[int]]) -> str:
        """
        Formatea el bloque como matriz hexadecimal visual.
        
        Args:
            bloque: Matriz de valores
            
        Returns:
            Cadena con formato de matriz
        """
        lineas = []
        lineas.append("┌─────────────────────────────┐")
        
        for i, fila in enumerate(bloque):
            hex_str = ' '.join(f'{v:02X}' for v in fila)
            lineas.append(f"│ {hex_str} │")
            
        lineas.append("└─────────────────────────────┘")
        return '\n'.join(lineas)

    @staticmethod
    def validar_parametros(f_entrada: float, radio: float,
                          paso: float, num_giros: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Valida los parámetros físico-criptográficos.
        
        Args:
            f_entrada: Fuerza de entrada
            radio: Radio de giro
            paso: Paso de rosca
            num_giros: Número de giros
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Validar radio
        if radio <= 0:
            return False, "[CRITICAL ERROR] El radio debe ser positivo"
        if radio > 1.0:
            return False, "[CRITICAL ERROR] Radio excesivo (máx 1.0m)"
            
        # Validar paso
        if paso <= 0:
            return False, "[CRITICAL ERROR] El paso debe ser positivo"
        if paso > 0.05:
            return False, "[CRITICAL ERROR] Paso excesivo (máx 0.05m)"
            
        # Validar fuerza de entrada
        if f_entrada <= 0:
            return False, "[CRITICAL ERROR] La fuerza debe ser positiva"
        if f_entrada > 10000:
            return False, "[CRITICAL ERROR] Fuerza excesiva (máx 10000N)"
            
        # Validar giros
        if num_giros < 1:
            return False, "[CRITICAL ERROR] Mínimo 1 giro"
        if num_giros > 100:
            return False, "[CRITICAL ERROR] Máximo 100 giros"
            
        return True, None


class ScrewCryptoState:
    """
    Mantiene el estado de la sesión de cifrado.
    
    Almacena los parámetros actuales para permitir:
    - Descifrado posterior
    - Verificación de clave
    - Visualización de progreso
    """
    
    def __init__(self):
        """Inicializa el estado."""
        self._reset()
        
    def _reset(self):
        """Reinicia el estado."""
        self.input_mode = "fuerza"  # "fuerza" o "texto"
        self.input_datos = ""
        self.input_valores = []
        self.radio = 0.05
        self.paso = 0.002
        self.vm = 0.0
        self.num_giros = 1
        self.output_valores = []
        self.output_cifrado = ""
        self.estado = "listo"  # listo, cifrando, cifrado, error
        self.mensaje_error = ""
        self.rondas_aplicadas = 0
        
    def calcular_vm(self):
        """Calcula la VM desde radio y paso."""
        self.vm = ScrewCipher.calcular_vm(self.radio, self.paso)
        
    def cifrar(self) -> bool:
        """
        Ejecuta el cifrado con los parámetros actuales.
        
        Returns:
            True si el cifrado fue exitoso
        """
        try:
            # Validar parámetros
            valido, error = ScrewCipher.validar_parametros(
                self._obtener_fuerza(),
                self.radio,
                self.paso,
                self.num_giros
            )
            if not valido:
                raise CryptoError(error)
                
            # Calcular VM
            self.calcular_vm()
            
            self.estado = "cifrando"
            
            if self.input_mode == "fuerza":
                f_salida, rondas = ScrewCipher.cifrar_fuerza(
                    self._obtener_fuerza(),
                    self.vm,
                    self.num_giros
                )
                self.output_valores = [int(f_salida / 10.0) % 256]
                self.output_cifrado = f"{f_salida:.2f} N"
                self.rondas_aplicadas = rondas
                
            else:  # modo texto
                self.input_valores = ScrewCipher.texto_a_valores(self.input_datos)
                self.output_valores, self.rondas_aplicadas = ScrewCipher.cifrar_multiplo(
                    self.input_valores,
                    self.vm,
                    self.num_giros
                )
                self.output_cifrado = ScrewCipher.valores_a_hex(self.output_valores)
                
            self.estado = "cifrado"
            return True
            
        except CryptoError as e:
            self.estado = "error"
            self.mensaje_error = str(e)
            return False
        except Exception as e:
            self.estado = "error"
            self.mensaje_error = f"[CRITICAL ERROR] {str(e)}"
            return False
            
    def descifrar(self, vm_verificar: float) -> bool:
        """
        Intenta descifrar con la clave proporcionada.
        
        Args:
            vm_verificar: Clave a verificar
            
        Returns:
            True si el descifrado fue exitoso (clave correcta)
        """
        try:
            if self.estado != "cifrado":
                self.mensaje_error = "[CRYPTO ERROR] No hay datos cifrados"
                return False
                
            if abs(vm_verificar - self.vm) > 0.001:
                self.mensaje_error = "[CRYPTO ERROR] Clave incorrecta"
                return False
                
            if self.input_mode == "fuerza":
                f_original = ScrewCipher.descifrar_fuerza(
                    float(self.output_valores[0] * 10.0),
                    vm_verificar,
                    self.num_giros
                )
                self.output_cifrado = f"{f_original:.2f} N"
                self.output_valores = [int(f_original * 10) % 256]
                
            else:
                valores_descifrados = ScrewCipher.descifrar_multiplo(
                    self.output_valores,
                    vm_verificar,
                    self.num_giros
                )
                self.output_cifrado = ScrewCipher.valores_a_texto(valores_descifrados)
                self.output_valores = valores_descifrados
                
            self.estado = "listo"
            return True
            
        except CryptoError as e:
            self.mensaje_error = str(e)
            return False
        except Exception as e:
            self.mensaje_error = f"[CRYPTO ERROR] {str(e)}"
            return False
            
    def _obtener_fuerza(self) -> float:
        """Obtiene el valor de fuerza desde el input."""
        try:
            return float(self.input_datos)
        except:
            return 10.0
            
    def obtener_bloque_visual(self) -> str:
        """Retorna el bloque en formato visual."""
        return ScrewCipher.formatear_bloque_hex(
            ScrewCipher.generar_bloque_visual(self.output_valores)
        )
        
    def obtener_input_visual(self) -> str:
        """Retorna el input en formato visual."""
        if self.input_mode == "fuerza":
            return f"{self.input_datos} N"
        else:
            return self.input_datos
            
    def reiniciar(self):
        """Reinicia el estado."""
        self._reset()