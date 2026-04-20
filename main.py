#!/usr/bin/env python3
"""
Simulador de Tornillo con Sistema Dinámico.

Punto de entrada de la aplicación.

Ejecuta: python main.py
"""

import sys


def main():
    """Función principal."""
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        print("[ERROR] PyQt6 no está instalado. Instale con: pip install PyQt6")
        sys.exit(1)
    
    try:
        import numpy
    except ImportError:
        print("[ERROR] NumPy no está instalado. Instale con: pip install numpy")
        sys.exit(1)
    
    try:
        import matplotlib
    except ImportError:
        print("[ERROR] Matplotlib no está instalado. Instale con: pip install matplotlib")
        sys.exit(1)
    
    print("=" * 60)
    print("  Simulador de Tornillo con Sistema Dinámico")
    print("  Física de Máquinas Simples & Criptografía")
    print("=" * 60)
    print()
    
    try:
        from gui import ejecutar
        ejecutar()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("\nPresione Enter para salir...")


if __name__ == "__main__":
    main()