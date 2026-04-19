import sys

# Verificar versión de Python
if sys.version_info < (3, 9):
    print("[CRITICAL ERROR] Se requiere Python 3.9 o superior")
    sys.exit(1)

# Importar dependencias necesarias
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("[CRITICAL ERROR] No se encontró PyQt6. Instale con: pip install PyQt6")
    sys.exit(1)

try:
    import matplotlib
except ImportError:
    print("[CRITICAL ERROR] No se encontró matplotlib. Instale con: pip install matplotlib")
    sys.exit(1)

try:
    import numpy
except ImportError:
    print("[CRITICAL ERROR] No se encontró numpy. Instale con: pip install numpy")
    sys.exit(1)


def main():
    """
    Función principal de la aplicación.
    Inicia la ventana principal y ejecuta el bucle de eventos.
    """
    from gui.main_window import ejecutar

    # Mensaje de inicio
    print("=" * 60)
    print("  Simulador de Tornillo - Física de Máquinas Simples")
    print("  Taller Universitario")
    print("=" * 60)
    print()
    print("Iniciando aplicación...")
    print()

    # Ejecutar aplicación
    ejecutar()


if __name__ == "__main__":
    main()