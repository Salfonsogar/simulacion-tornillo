import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, 
    QSlider, QGroupBox, QCheckBox, QFrame, QSizePolicy, QLineEdit, 
    QComboBox, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

sys.path.insert(0, 'C:/Users/santy/source/repos/tornillo_sim')
from crypto.screw_crypto import ScrewCipher, ScrewCryptoState, CryptoError


class CryptoTab(QWidget):
    """ 
    Pestaña de visualización de la analogía criptografía-tornillo. 
    Muestra cómo un "giro pequeño" (input) transforma "datos crudos" 
    en "bloque cifrado" (output fijo). 
    """
    
    def __init__(self, parent=None):
        """Inicializa la pestaña de criptografía."""
        super().__init__(parent)
        self._estado_animacion = 0
        self._crypto_state = ScrewCryptoState()
        self._modo = "fuerza"
        self._datos_procesados = False
        
        self._setup_ui()
        self._actualizar_presentacion()
        self._on_reiniciar()

    def _setup_ui(self):
        """Configura la interfaz."""
        self.setStyleSheet(""" 
            QWidget { font-family: 'Segoe UI', sans-serif; } 
            QLabel { color: #555555; font-size: 12px; } 
            QLabel titulo { color: #0078D4; font-size: 20px; font-weight: bold; } 
            QLabel subtitulo { color: #00ACC1; font-size: 14px; font-weight: bold; } 
            QLabel info { color: #888888; font-size: 11px; } 
            QLabel titulo_seccion { color: #0078D4; font-size: 13px; font-weight: bold; } 
            QPushButton { background-color: #0078D4; color: #FFFFFF; border: none; border-radius: 6px; padding: 8px 16px; font-size: 12px; font-weight: bold; } 
            QPushButton:hover { background-color: #106EBE; } 
            QPushButton:pressed { background-color: #005A9E; } 
            QPushButton:disabled { background-color: #CCCCCC; } 
            QGroupBox { border: 1px solid #444444; border-radius: 8px; margin-top: 12px; padding-top: 12px; color: #555555; } 
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; color: #0078D4; font-weight: bold; } 
            QLineEdit, QTextEdit { border: 1px solid #444444; border-radius: 4px; padding: 6px; background-color: #FFFFFF; color: #555555; font-size: 12px; } 
            QLineEdit:focus, QTextEdit:focus { border: 2px solid #0078D4; } 
            QSlider::groove:horizontal { background: #E0E0E0; height: 8px; border-radius: 4px; } 
            QSlider::handle:horizontal { background: #0078D4; width: 18px; margin: -5px 0; border-radius: 9px; } 
            QCheckBox { color: #555555; font-size: 12px; } 
        """)
        
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        
        layout_explicacion = self._crear_explicacion()
        layout_principal.addLayout(layout_explicacion)
        layout_principal.addWidget(self._crear_panel_entrada())
        
        layout_proceso = QHBoxLayout()
        layout_proceso.setSpacing(12)
        layout_proceso.addWidget(self._crear_panel_parametros())
        layout_proceso.addWidget(self._crear_panel_transform())
        layout_principal.addLayout(layout_proceso)
        
        layout_resultado = QHBoxLayout()
        layout_resultado.setSpacing(12)
        layout_resultado.addWidget(self._crear_panel_resultado())
        layout_resultado.addWidget(self._crear_panel_bloque())
        layout_principal.addLayout(layout_resultado)
        
        layout_principal.addWidget(self._crear_panel_estado())
        layout_principal.addStretch()
        
        self.setLayout(layout_principal)

    def _crear_explicacion(self) -> QVBoxLayout:
        """Crea el frame de explicación."""
        layout = QVBoxLayout()
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        frame.setStyleSheet(""" 
            QFrame { background-color: #F0F7FF; border-radius: 8px; border: 1px solid #B8D4F0; padding: 12px; } 
        """)
        layout.addWidget(frame)
        return layout

    def _crear_panel_entrada(self) -> QFrame:
        """Crea el panel de entrada de datos."""
        frame = QFrame()
        frame.setStyleSheet(""" 
            QFrame { background-color: #FFFFFF; border-radius: 8px; border: 1px solid #DDDDDD; padding: 12px; } 
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        self._toggle_modo = QCheckBox("Modo Texto")
        self._toggle_modo.setStyleSheet(""" 
            QCheckBox { font-weight: bold; } 
            QCheckBox::indicator { width: 18px; height: 18px; } 
        """)
        self._toggle_modo.stateChanged.connect(self._on_cambiar_modo)
        layout.addWidget(self._toggle_modo)
        layout.addWidget(QLabel("Entrada:"))
        
        self._panel_fuerza = QWidget()
        layout_fuerza = QHBoxLayout()
        layout_fuerza.setContentsMargins(0, 0, 0, 0)
        
        self._slider_fuerza = QSlider(Qt.Orientation.Horizontal)
        self._slider_fuerza.setMinimum(1)
        self._slider_fuerza.setMaximum(1000)
        self._slider_fuerza.setValue(100)
        self._slider_fuerza.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider_fuerza.setTickInterval(100)
        self._slider_fuerza.valueChanged.connect(self._on_cambiar_fuerza)
        layout_fuerza.addWidget(self._slider_fuerza)
        
        self._label_fuerza_valor = QLabel("100 N")
        self._label_fuerza_valor.setMinimumWidth(60)
        self._label_fuerza_valor.setStyleSheet("font-weight: bold; color: #FF6B00;")
        layout_fuerza.addWidget(self._label_fuerza_valor)
        
        self._panel_fuerza.setLayout(layout_fuerza)
        layout.addWidget(self._panel_fuerza)
        
        self._panel_texto = QWidget()
        layout_texto = QHBoxLayout()
        layout_texto.setContentsMargins(0, 0, 0, 0)
        
        self._edit_texto = QLineEdit()
        self._edit_texto.setMaxLength(16)
        self._edit_texto.setPlaceholderText("Texto a cifrar (máx 16)")
        self._edit_texto.setMinimumWidth(150)
        layout_texto.addWidget(self._edit_texto)
        
        self._label_texto_valor = QLabel("")
        self._label_texto_valor.setMinimumWidth(60)
        layout_texto.addWidget(self._label_texto_valor)
        
        self._panel_texto.setLayout(layout_texto)
        self._panel_texto.hide()
        layout.addWidget(self._panel_texto)
        
        layout.addStretch()
        frame.setLayout(layout)
        
        return frame

    def _crear_panel_parametros(self) -> QWidget:
        """Crea el panel de parámetros."""
        grupo = QGroupBox("Parámetros de Cifrado")
        layout = QGridLayout()
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("Radio (r) [m]:"), 0, 0)
        self._edit_radio = QLineEdit("0.005")
        self._edit_radio.setMaximumWidth(80)
        self._edit_radio.textChanged.connect(self._actualizar_vm_visible)
        layout.addWidget(self._edit_radio, 0, 1)
        
        layout.addWidget(QLabel("Paso (L) [m]:"), 1, 0)
        self._edit_paso = QLineEdit("0.002")
        self._edit_paso.setMaximumWidth(80)
        self._edit_paso.textChanged.connect(self._actualizar_vm_visible)
        layout.addWidget(self._edit_paso, 1, 1)
        
        layout.addWidget(QLabel("Clave (VM):"), 2, 0)
        self._label_vm = QLabel("15.71")
        self._label_vm.setStyleSheet("color: #0078D4; font-weight: bold; font-size: 14px;")
        layout.addWidget(self._label_vm, 2, 1)
        
        layout.addWidget(QLabel("Giros:"), 3, 0)
        self._slider_giros = QSlider(Qt.Orientation.Horizontal)
        self._slider_giros.setMinimum(1)
        self._slider_giros.setMaximum(20)
        self._slider_giros.setValue(1)
        self._slider_giros.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider_giros.setTickInterval(5)
        self._slider_giros.valueChanged.connect(self._on_cambiar_giros)
        layout.addWidget(self._slider_giros, 3, 1)
        
        self._label_giros = QLabel("1")
        self._label_giros.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(self._label_giros, 3, 2)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self._btn_cifrar = QPushButton("Cifrar")
        self._btn_cifrar.setStyleSheet("background-color: #28A745;")
        self._btn_cifrar.clicked.connect(self._on_cifrar)
        btn_layout.addWidget(self._btn_cifrar)
        
        self._btn_descifrar = QPushButton("Descifrar")
        self._btn_descifrar.setStyleSheet("background-color: #FF6B00; color: #FFFFFF;")
        self._btn_descifrar.clicked.connect(self._on_descifrar)
        self._btn_descifrar.setEnabled(False)
        btn_layout.addWidget(self._btn_descifrar)
        
        self._btn_reiniciar = QPushButton("Reiniciar")
        self._btn_reiniciar.setStyleSheet("background-color: #757575;")
        self._btn_reiniciar.clicked.connect(self._on_reiniciar)
        btn_layout.addWidget(self._btn_reiniciar)
        
        layout.addLayout(btn_layout, 4, 0, 1, 3)
        grupo.setLayout(layout)
        
        return grupo

    def _crear_panel_transform(self) -> QWidget:
        """Crea el panel de transformación visual."""
        grupo = QGroupBox("Visualización")
        layout = QVBoxLayout()
        
        self._fig_transform = Figure(figsize=(4, 3), facecolor='#FFFFFF')
        self._ax_transform = self._fig_transform.add_subplot(111)
        self._ax_transform.set_facecolor('#FFFFFF')
        
        self._canvas_transform_widget = FigureCanvasQTAgg(self._fig_transform)
        self._canvas_transform_widget.setMinimumSize(200, 150)
        self._canvas_transform_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._inicializar_transform()
        layout.addWidget(self._canvas_transform_widget)
        grupo.setLayout(layout)
        
        return grupo

    def _inicializar_transform(self):
        """Inicializa la visualización."""
        self._ax_transform.clear()
        self._ax_transform.set_xlim(-1.2, 1.2)
        self._ax_transform.set_ylim(-0.8, 0.8)
        self._ax_transform.set_facecolor('#FAFAFA')
        self._ax_transform.set_title('Listo para cifrar', color='#666666', fontsize=12)
        self._ax_transform.axis('off')
        self._canvas_transform_widget.draw()

    def _dibujar_tornillo(self, angulo, estado="procesando"):
        """Dibuja el tornillo."""
        self._ax_transform.clear()
        self._ax_transform.set_xlim(-1.2, 1.2)
        self._ax_transform.set_ylim(-0.8, 0.8)
        self._ax_transform.set_facecolor('#FAFAFA')
        
        if estado == "cifrado":
            titulo = "✓ CIFRADO"
            color_titulo = "#28A745"
        elif estado == "descifrado":
            titulo = "✓ DESCIFRADO"
            color_titulo = "#17A2B8"
        elif estado == "error":
            titulo = "✗ ERROR"
            color_titulo = "#DC3545"
        else:
            titulo = "Procesando..."
            color_titulo = "#E65100"
            
        self._ax_transform.set_title(titulo, color=color_titulo, fontsize=12, fontweight='bold')
        self._ax_transform.axis('off')
        
        color_tornillo = "#0078D4"
        color_hilo = "#005A9E"
        
        for i in range(4):
            y_base = -0.5 + i * 0.35
            theta = np.linspace(0, 2 * np.pi, 40)
            x = 0.25 * np.cos(theta + angulo + i * 0.8)
            y = y_base + 0.08 * np.sin(theta + i * 0.5)
            self._ax_transform.plot(x, y, color=color_hilo, linewidth=2, alpha=0.8)
            
        self._ax_transform.plot([-0.35, 0.35], [0.6, 0.6], color='#333333', linewidth=3)
        self._ax_transform.plot([0], [0.6], marker='o', markersize=8, color='#333333')
        self._ax_transform.annotate('', xy=(0.5, 0.1), xytext=(-0.5, 0.1), arrowprops=dict(arrowstyle='->', color='#E65100', lw=2))
        self._ax_transform.text(0, 0.2, 'Input', color='#E65100', fontsize=9, ha='center')
        self._ax_transform.annotate('', xy=(0, -0.3), xytext=(0, -0.6), arrowprops=dict(arrowstyle='->', color='#00ACC1', lw=2))
        self._ax_transform.text(0.35, -0.45, 'VM', color='#00ACC1', fontsize=9, ha='center')
        self._canvas_transform_widget.draw()

    def _crear_panel_resultado(self) -> QWidget:
        """Crea el panel de resultado."""
        grupo = QGroupBox("Resultado")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.addWidget(QLabel("Salida:"))
        
        self._label_resultado = QLabel("—")
        self._label_resultado.setStyleSheet(""" 
            font-size: 16px; font-weight: bold; color: #0078D4; padding: 8px; background-color: #F5F5F5; border-radius: 4px; 
        """)
        self._label_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label_resultado)
        
        self._label_estado = QLabel("Esperando...")
        self._label_estado.setStyleSheet("color: #888888; font-style: italic;")
        self._label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label_estado)
        
        layout.addStretch()
        grupo.setLayout(layout)
        return grupo

    def _crear_panel_bloque(self) -> QWidget:
        """Crea el panel de visualización de bloque."""
        grupo = QGroupBox("Bloque Cifrado (形式 AES)")
        layout = QVBoxLayout()
        
        self._text_bloque = QTextEdit()
        self._text_bloque.setReadOnly(True)
        self._text_bloque.setMaximumHeight(80)
        self._text_bloque.setStyleSheet(""" 
            background-color: #1E1E1E; color: #00FF00; font-family: 'Consolas', monospace; font-size: 11px; 
        """)
        self._text_bloque.setPlainText("┌──────────────────────┐\n│ 00 00 00 00 00 00... │\n└──────────────────────┘")
        layout.addWidget(self._text_bloque)
        
        layout.addWidget(QLabel("Rondas aplicadas:"))
        self._label_rondas = QLabel("0")
        self._label_rondas.setStyleSheet("color: #0078D4; font-weight: bold;")
        layout.addWidget(self._label_rondas)
        
        grupo.setLayout(layout)
        return grupo

    def _crear_panel_estado(self) -> QWidget:
        """Crea el panel de estado."""
        grupo = QGroupBox("Estado")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        self._label_mensaje = QLabel("Listo")
        self._label_mensaje.setStyleSheet("color: #28A745; font-weight: bold;")
        layout.addWidget(QLabel("Estado:"), 0, 0)
        layout.addWidget(self._label_mensaje, 0, 1)
        
        self._label_info = QLabel("")
        self._label_info.setStyleSheet("color: #888888;")
        layout.addWidget(QLabel("Info:"), 1, 0)
        layout.addWidget(self._label_info, 1, 1)
        
        grupo.setLayout(layout)
        return grupo

    def _on_cambiar_modo(self, checked: int):
        """Cambia entre modo fuerza y texto."""
        if checked:
            self._modo = "texto"
        else:
            self._modo = "fuerza"
        self._on_reiniciar()

    def _on_cambiar_fuerza(self, valor: int):
        """Maneja cambio de fuerza."""
        self._label_fuerza_valor.setText(f"{valor/10.0:.1f} N")

    def _on_cambiar_giros(self, valor: int):
        """Maneja cambio de giros."""
        self._label_giros.setText(str(valor))

    def _actualizar_vm_visible(self):
        """Actualiza el valor de VM mostrado."""
        try:
            radio = float(self._edit_radio.text())
            paso = float(self._edit_paso.text())
            vm = ScrewCipher.calcular_vm(radio, paso)
            self._label_vm.setText(f"{vm:.2f}")
        except:
            self._label_vm.setText("—")

    def _actualizar_presentacion(self):
        """Actualiza la presentación inicial."""
        self._actualizar_vm_visible()

    def _on_cifrar(self):
        """Ejecuta el cifrado."""
        try:
            radio = float(self._edit_radio.text())
            paso = float(self._edit_paso.text())
            vm = ScrewCipher.calcular_vm(radio, paso)
            num_giros = self._slider_giros.value()
            
            self._btn_cifrar.setEnabled(False)
            self._btn_cifrar.setText("Cifrando...")
            self._datos_procesados = True
            self._estado_animacion = 0
            
            self.timer_animacion = QTimer()
            self.timer_animacion.timeout.connect(self._actualizar_animacion)
            self.timer_animacion.start(30)
            
            self._crypto_state.input_mode = self._modo
            if self._modo == "fuerza":
                self._crypto_state.input_datos = str(self._slider_fuerza.value() / 10.0)
            else:
                self._crypto_state.input_datos = self._edit_texto.text() or "TEST"
                
            self._crypto_state.radio = radio
            self._crypto_state.paso = paso
            self._crypto_state.num_giros = num_giros
            self._crypto_state.calcular_vm()
            
            self._on_cifrar_real()
            
        except CryptoError as e:
            self._mostrar_error(str(e))
        except Exception as e:
            self._mostrar_error(f"Error: {str(e)}")

    def _on_cifrar_real(self):
        """Ejecuta el cifrado real."""
        try:
            if self._modo == "fuerza":
                f_entrada = float(self._crypto_state.input_datos)
                f_salida, rondas = ScrewCipher.cifrar_fuerza(
                    f_entrada, self._crypto_state.vm, self._crypto_state.num_giros
                )
                self._resultado_valor = f"{f_salida:.2f} N"
                self._resultado_hex = [int(f_salida / 10.0) % 256]
                self._rondas = rondas
            else:
                valores = ScrewCipher.texto_a_valores(self._crypto_state.input_datos)
                resultado, rondas = ScrewCipher.cifrar_multiplo(
                    valores, self._crypto_state.vm, self._crypto_state.num_giros
                )
                self._resultado_hex = resultado
                self._resultado_valor = ScrewCipher.valores_a_hex(resultado)
                self._rondas = rondas
                
            self._actualizar_ui_resultado()
            
        except CryptoError as e:
            self._mostrar_error(str(e))
        except Exception as e:
            self._mostrar_error(f"Error: {str(e)}")

    def _actualizar_animacion(self):
        """Actualiza la animación."""
        self._estado_animacion += 0.15
        if self._estado_animacion >= 2 * np.pi:
            self.timer_animacion.stop()
            self._dibujar_tornillo(2 * np.pi, "cifrado")
            return
        self._dibujar_tornillo(self._estado_animacion, "procesando")

    def _actualizar_ui_resultado(self):
        """Actualiza la UI con el resultado."""
        self._dibujar_tornillo(2 * np.pi, "cifrado")
        self._label_resultado.setText(self._resultado_valor)
        self._label_estado.setText("✓ CIFRADO")
        self._label_estado.setStyleSheet("color: #28A745; font-weight: bold;")
        
        bloque = ScrewCipher.generar_bloque_visual(self._resultado_hex, 16)
        self._text_bloque.setPlainText(ScrewCipher.formatear_bloque_hex(bloque))
        
        self._label_rondas.setText(str(self._rondas))
        self._label_mensaje.setText("Cifrado exitoso")
        self._label_mensaje.setStyleSheet("color: #28A745; font-weight: bold;")
        self._label_info.setText(f"VM={self._crypto_state.vm:.2f}, Giros={self._crypto_state.num_giros}")
        
        self._btn_cifrar.setText("Cifrar")
        self._btn_cifrar.setEnabled(True)
        self._btn_descifrar.setEnabled(True)

    def _on_descifrar(self):
        """Intenta descifrar."""
        try:
            if not self._datos_procesados:
                return
                
            vm = self._crypto_state.vm
            if self._modo == "fuerza":
                f_cifrada = float(self._resultado_valor.replace(" N", ""))
                f_original = ScrewCipher.descifrar_fuerza(
                    f_cifrada, vm, self._crypto_state.num_giros
                )
                self._label_resultado.setText(f"{f_original:.2f} N")
                self._resultado_valor = f"{f_original:.2f} N"
            else:
                resultado = ScrewCipher.descifrar_multiplo(
                    self._resultado_hex, vm, self._crypto_state.num_giros
                )
                texto = ScrewCipher.valores_a_texto(resultado)
                self._label_resultado.setText(texto)
                self._resultado_valor = texto
                
            self._dibujar_tornillo(0, "descifrado")
            self._label_estado.setText("✓ DESCIFRADO")
            self._label_estado.setStyleSheet("color: #17A2B8; font-weight: bold;")
            self._label_mensaje.setText("Descifrado exitoso")
            self._label_mensaje.setStyleSheet("color: #17A2B8; font-weight: bold;")
            self._btn_descifrar.setEnabled(False)
            
        except CryptoError as e:
            self._mostrar_error(f"Descifrado falló: {str(e)}")
        except Exception as e:
            self._mostrar_error(f"Error: {str(e)}")

    def _on_reiniciar(self):
        """Reinicia el estado."""
        self._datos_procesados = False
        self._estado_animacion = 0
        self._label_resultado.setText("—")
        self._label_estado.setText("Esperando...")
        self._label_estado.setStyleSheet("color: #666666;")
        self._text_bloque.setPlainText("┌──────────────────────┐\n│ 00 00 00 00 00 00... │\n└──────────────────────┘")
        self._label_rondas.setText("0")
        self._label_mensaje.setText("Listo")
        self._label_mensaje.setStyleSheet("color: #28A745; font-weight: bold;")
        self._label_info.setText("")
        self._inicializar_transform()
        
        self._btn_cifrar.setText("Cifrar")
        self._btn_cifrar.setEnabled(True)
        self._btn_descifrar.setEnabled(False)
        
        self._crypto_state = ScrewCryptoState()
        self._crypto_state.input_mode = self._modo
        
        if self._modo == "texto":
            self._panel_fuerza.hide()
            self._panel_texto.show()
        else:
            self._panel_texto.hide()
            self._panel_fuerza.show()

    def _mostrar_error(self, mensaje: str):
        """Muestra un error."""
        self._label_mensaje.setText(mensaje)
        self._label_mensaje.setStyleSheet("color: #DC3545; font-weight: bold;")
        self._label_estado.setText("✗ ERROR")
        self._label_estado.setStyleSheet("color: #DC3545; font-weight: bold;")
        self._dibujar_tornillo(0, "error")
        
        self._btn_cifrar.setEnabled(True)
        self._btn_cifrar.setText("Cifrar")