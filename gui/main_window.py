#!/usr/bin/env python3
"""
Ventana Principal - Aplicación de Simulación del Tornillo

Esta es la ventana principal de la aplicación que une todas las pestañas:
1. Calculadora - Cálculo de VM y fuerzas
2. Simulación - Visualización animada del tornillo
3. Criptografía - Analogía con AES-256

La aplicación está diseñada para talleres universitarios sobre máquinas simples.

Autor: Simulador de Tornillo
Fecha: 2026
"""

import sys

from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QMessageBox,
                            QApplication, QLabel, QStatusBar, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen
from PyQt6.QtGui import QIcon, QKeyEvent


class ScrewSimulatorWindow(QMainWindow):
    """
    Ventana principal del simulador de tornillo.

    Implementa una interfaz de tres pestañas:
    - Calculadora: Cálculos físicos
    - Simulación: Visualización animada
    - Criptografía: Analogía AES-256
    """

    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()

        # Configuración de ventana
        self.setWindowTitle("Simulador de Tornillo - Física & Criptografía")
        
        # Permitir redimensionar libremente
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        # Aplicar estilo
        self._aplicar_estilo()

        # Configurar UI
        self._configurar_ui()

        # Configurar barra de estado
        self._configurar_estado()

    def _aplicar_estilo(self):
        """Aplica el estilo visual claro."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QWidget {
                background-color: #F5F5F5;
            }
            QTabWidget::pane {
                border: 2px solid #0078D4;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #E1E1E1;
                color: #333333;
                padding: 12px 24px;
                margin: 4px;
                border-radius: 6px 6px 0 0;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #0078D4;
                color: #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #D0D0D0;
                color: #000000;
            }
            QStatusBar {
                background-color: #E1E1E1;
                color: #333333;
            }
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QMessageBox QPushButton {
                background-color: #0078D4;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)

    def _configurar_ui(self):
        """Configura la interfaz de usuario."""
        # Crear tab widget central
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Crear pestañas
        from gui.calculator_tab import CalculatorTab
        from gui.simulation_tab import SimulationTab
        from gui.crypto_tab import CryptoTab

        # Pestaña 1: Calculadora
        self.calc_tab = CalculatorTab()
        self.tabs.addTab(self.calc_tab, "Calculadora")

        # Pestaña 2: Simulación
        self.sim_tab = SimulationTab()
        self.tabs.addTab(self.sim_tab, "Simulación")

        # Pestaña 3: Criptografía
        self.crypto_tab = CryptoTab()
        self.tabs.addTab(self.crypto_tab, "Criptografía")

        # Establecer en ventana central
        self.setCentralWidget(self.tabs)

        # Conectar señales entre pestañas (para sincronización)
        self.calc_tab.calculo_realizado.connect(self._on_calculo_externo)

    def _configurar_estado(self):
        """Configura la barra de estado."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo. Ingrese valores en la Calculadora.")

    def _on_calculo_externo(self, resultados):
        """Maneja cálculos desde la pestaña de calculadora."""
        self.status_bar.showMessage(
            f"Calculado: VM={resultados['vm']:.2f}, F_salida={resultados['f_salida']:.2f}N"
        )

    def keyPressEvent(self, event: QKeyEvent):
        """Maneja eventos de teclado."""
        # Ctrl+1: Calculadora
        if event.key() == 49 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.tabs.setCurrentIndex(0)
        # Ctrl+2: Simulación
        elif event.key() == 50 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.tabs.setCurrentIndex(1)
        # Ctrl+3: Criptografía
        elif event.key() == 51 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.tabs.setCurrentIndex(2)
        else:
            super().keyPressEvent(event)

    def _mostrar_ayuda(self):
        """Muestra el diálogo de ayuda."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ayuda - Simulador de Tornillo")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<h2>Simulador de Tornillo</h2>"
            "<p>Aplicación educativa para el taller de Máquinas Simples.</p>"
            "<h3>Controles:</h3>"
            "<ul>"
            "<li><b>F2</b>: Calculadora</li>"
            "<li><b>F3</b>: Simulación</li>"
            "<li><b>F4</b>: Criptografía</li>"
            "<li><b>F1</b>: Esta ayuda</li>"
            "</ul>"
            "<h3>Fórmulas:</h3>"
            "<ul>"
            "<li>VM = (2πr) / L</li>"
            "<li>F_salida = F_entrada × VM</li>"
            "<li>Δx = θ × (L / 2π)</li>"
            "</ul>"
        )
        msg.exec()

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación."""
        reply = QMessageBox.question(
            self,
            "Salir",
            "¿Está seguro que desea salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def crear_aplicacion() -> QApplication:
    # Crea la aplicación
    app = QApplication(sys.argv)

    # Establecer información de la aplicación
    app.setApplicationName("Simulador de Tornillo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Taller de Máquinas Simples")

    # Establecer estilo de widgets
    app.setStyle("Fusion")

    return app


def ejecutar():
    # Crear aplicación
    app = crear_aplicacion()

    # Crear y mostrar ventana
    ventana = ScrewSimulatorWindow()
    ventana.show()

    # Ejecutar bucle de eventos
    sys.exit(app.exec())