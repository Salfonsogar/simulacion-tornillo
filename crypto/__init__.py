"""
Módulo de Criptografía del Tornillo

Este módulo proporciona la analogía entre el tornillo como máquina simple
y los algoritmos de cifrado tipo AES-256.

Uso:
    from crypto.screw_crypto import ScrewCipher, ScrewCryptoState, CryptoError
    
    # Calcular VM (clave)
    vm = ScrewCipher.calcular_vm(radio=0.05, paso=0.002)
    
    # Cifrar datos
    datos_cifrados, rondas = ScrewCipher.cifrar_multiplo([72, 101, 108, 108], vm, 1)
    
    # Descifrar
    datos_originales = ScrewCipher.descifrar_multiplo(datos_cifrados, vm, 1)

Autor: Simulador de Tornillo
Fecha: 2026
"""

from .screw_crypto import (
    ScrewCipher,
    ScrewCryptoState,
    CryptoError
)

__all__ = ['ScrewCipher', 'ScrewCryptoState', 'CryptoError']