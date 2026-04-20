"""
Pestaña de Criptografía.

Analogía entre movimiento del tornillo y transformación de datos.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QTextEdit, QSlider, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from controller import CryptoController


class CryptoTab(QWidget):
    """Pestaña de criptografía avanzada."""
    
    COLORS = {
        'primary': '#0078D4',
        'primary_bg': '#F0F7FF',
        'primary_hover': '#005A9E',
        'accent': '#FF6B00',
        'accent_bg': '#FFF5EB',
        'success': '#107C10',
        'success_bg': '#E8F5E9',
        'info': '#0078D4',
        'text': '#201F1E',
        'text_secondary': '#605E5C',
        'border': '#EDEBE9',
        'bg_card': '#FFFFFF',
        'bg_main': '#F3F2F1',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._controller = CryptoController()
        self._ultimo_cifrado = ""
        self._setup_ui()
    
    def _setup_ui(self):
        c = self.COLORS
        
        # Main Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: {c['bg_main']}; border: none;")
        root_layout.addWidget(scroll)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {c['bg_main']};")
        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        scroll.setWidget(container)
        
        # Header Section
        header = QVBoxLayout()
        titulo = QLabel("🔐 Criptografía del Tornillo")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 24px; font-weight: bold; margin-bottom: 5px;")
        header.addWidget(titulo)
        
        desc = QLabel(
            "Descubre cómo la mecánica de precisión se traduce en seguridad digital. "
            "En esta analogía, los parámetros físicos del tornillo actúan como una <b>clave de cifrado</b>."
        )
        desc.setStyleSheet(f"color: {c['text_secondary']}; font-size: 13px; line-height: 1.4;")
        desc.setWordWrap(True)
        header.addWidget(desc)
        layout.addLayout(header)
        
        # Analogy Card
        analogy_card = QFrame()
        analogy_card.setStyleSheet(f"""
            QFrame {{
                background-color: {c['primary_bg']};
                border: 1px solid #FFD8B8;
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)
        analogy_layout = QVBoxLayout(analogy_card)
        analogy_title = QLabel("💡 Analogía: Tornillo ↔ AES-256")
        analogy_title.setStyleSheet(f"color: {c['primary_hover']}; font-weight: bold; font-size: 14px;")
        analogy_layout.addWidget(analogy_title)
        
        analogy_text = QLabel(
            "• <b>Mecánica:</b> Un giro pequeño (Clave) aplica una presión lineal inmensa (Transformación).<br>"
            "• <b>Digital:</b> Una clave pequeña reordena los bits de tal forma que son irrecuperables sin ella."
        )
        analogy_text.setWordWrap(True)
        analogy_text.setStyleSheet(f"color: #856404; font-size: 12px;")
        analogy_layout.addWidget(analogy_text)
        layout.addWidget(analogy_card)
        
        # Step 1: Parameters
        step1_layout = QVBoxLayout()
        step1_title = QLabel("📦 Paso 1: Configurar la Clave (Parámetros)")
        step1_title.setStyleSheet(f"color: {c['primary']}; font-size: 16px; font-weight: bold;")
        step1_layout.addWidget(step1_title)
        
        params_group = QFrame()
        params_group.setStyleSheet(f"background-color: {c['bg_main']}; border-radius: 8px; border: 1px solid {c['border']};")
        params_layout = QGridLayout(params_group)
        params_layout.setContentsMargins(20, 20, 20, 20)
        params_layout.setSpacing(15)
        
        # Radio
        params_layout.addWidget(QLabel("Radio del Brazo (r):"), 0, 0)
        self._input_radio = QLineEdit("0.05")
        self._input_radio.setPlaceholderText("m")
        self._input_radio.setMinimumHeight(35)
        self._input_radio.setMaximumWidth(200)
        self._input_radio.setStyleSheet(self._input_style())
        params_layout.addWidget(self._input_radio, 0, 1)
        params_layout.addWidget(QLabel("metros"), 0, 2)
        
        # Paso
        params_layout.addWidget(QLabel("Paso de Rosca (L):"), 1, 0)
        self._input_paso = QLineEdit("0.002")
        self._input_paso.setPlaceholderText("m")
        self._input_paso.setMinimumHeight(35)
        self._input_paso.setMaximumWidth(200)
        self._input_paso.setStyleSheet(self._input_style())
        params_layout.addWidget(self._input_paso, 1, 1)
        params_layout.addWidget(QLabel("metros"), 1, 2)
        
        # Giros
        params_layout.addWidget(QLabel("Número de Giros:"), 2, 0)
        self._slider_giros = QSlider(Qt.Orientation.Horizontal)
        self._slider_giros.setMinimum(1)
        self._slider_giros.setMaximum(10)
        self._slider_giros.setValue(1)
        params_layout.addWidget(self._slider_giros, 2, 1)
        self._lbl_giros = QLabel("1")
        self._lbl_giros.setStyleSheet(f"font-weight: bold; color: {c['primary']}; font-size: 14px;")
        params_layout.addWidget(self._lbl_giros, 2, 2)
        
        self._slider_giros.valueChanged.connect(lambda v: self._lbl_giros.setText(str(v)))
        
        step1_layout.addWidget(params_group)
        layout.addLayout(step1_layout)
        
        # Step 2: Input/Output
        step2_layout = QVBoxLayout()
        step2_title = QLabel("📝 Paso 2: Transformar Información")
        step2_title.setStyleSheet(f"color: {c['primary']}; font-size: 16px; font-weight: bold;")
        step2_layout.addWidget(step2_title)
        
        transform_group = QFrame()
        transform_group.setStyleSheet(f"background-color: {c['bg_card']}; border-radius: 10px; border: 1px solid {c['border']};")
        transform_layout = QVBoxLayout(transform_group)
        transform_layout.setContentsMargins(20, 20, 20, 20)
        transform_layout.setSpacing(15)
        
        transform_layout.addWidget(QLabel("<b>Texto de Entrada:</b>"))
        self._txt_input = QTextEdit()
        self._txt_input.setPlaceholderText("Ingrese el mensaje a procesar...")
        self._txt_input.setMinimumHeight(100)
        self._txt_input.setStyleSheet(f"border: 1px solid {c['border']}; border-radius: 6px; padding: 10px;")
        transform_layout.addWidget(self._txt_input)
        
        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(15)
        
        self._btn_cifrar = QPushButton("Cifrar Mensaje")
        self._btn_cifrar.setMinimumHeight(45)
        self._btn_cifrar.setStyleSheet(self._button_style(c['success']))
        self._btn_cifrar.clicked.connect(self._on_cifrar)
        btn_box.addWidget(self._btn_cifrar)
        
        self._btn_descifrar = QPushButton("Descifrar Mensaje")
        self._btn_descifrar.setMinimumHeight(45)
        self._btn_descifrar.setStyleSheet(self._button_style(c['info']))
        self._btn_descifrar.clicked.connect(self._on_descifrar)
        btn_box.addWidget(self._btn_descifrar)
        
        transform_layout.addLayout(btn_box)
        
        transform_layout.addWidget(QLabel("<b>Resultado:</b>"))
        self._txt_output = QTextEdit()
        self._txt_output.setReadOnly(True)
        self._txt_output.setMinimumHeight(100)
        self._txt_output.setStyleSheet(f"border: 1px solid {c['border']}; border-radius: 6px; padding: 10px; background-color: {c['bg_main']}; font-family: 'Consolas', monospace;")
        transform_layout.addWidget(self._txt_output)

        step2_layout.addWidget(transform_group)
        layout.addLayout(step2_layout)

        # Status Label
        self._lbl_estado = QLabel("")
        self._lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_estado.setWordWrap(True)
        self._lbl_estado.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self._lbl_estado)

        # Diagram Section
        diagram_group = QGroupBox("Diagrama del Algoritmo")
        diagram_layout = QHBoxLayout()

        # Simple Visual Flow using Labels
        def create_flow_box(text, color):
            box = QLabel(text)
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.setFixedSize(140, 70)
            box.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; font-weight: bold; font-size: 11px; border: none;")
            return box

        diagram_layout.addStretch()
        diagram_layout.addWidget(create_flow_box("INPUT\n(Mensaje)", c['primary']))
        flecha1 = QLabel(" ➔ ")
        flecha1.setStyleSheet("font-size: 20px; color: #999;")
        diagram_layout.addWidget(flecha1)
        diagram_layout.addWidget(create_flow_box("PROCESS\n(VM = 2πr/L)", c['accent']))
        flecha2 = QLabel(" ➔ ")
        flecha2.setStyleSheet("font-size: 20px; color: #999;")
        diagram_layout.addWidget(flecha2)
        diagram_layout.addWidget(create_flow_box("OUTPUT\n(Cifrado)", c['success']))
        diagram_layout.addStretch()
        
        diagram_group.setLayout(diagram_layout)
        layout.addWidget(diagram_group)
        
        layout.addStretch()
    
    def _input_style(self):
        return f"""
            QLineEdit {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 5px;
                padding-left: 10px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.COLORS['primary']};
                background-color: #F0F7FF;
            }}
        """
        
    def _button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {color}CC;
                margin-top: -2px;
            }}
            QPushButton:pressed {{
                background-color: {color}AA;
                margin-top: 0px;
            }}
        """

    def _on_cifrar(self):
        try:
            radio = float(self._input_radio.text() or "0.05")
            paso = float(self._input_paso.text() or "0.002")
            num_giros = self._slider_giros.value()
            
            texto = self._txt_input.toPlainText().strip()
            if not texto:
                self._lbl_estado.setText("⚠️ Por favor ingrese un texto para cifrar")
                self._lbl_estado.setStyleSheet(f"color: {self.COLORS['primary']};")
                return
            
            texto_cifrado, rondas = self._controller.cifrar_texto(texto, radio, paso, num_giros)
            self._ultimo_cifrado = texto_cifrado
            
            self._txt_output.setPlainText(texto_cifrado)
            self._lbl_estado.setText(f"✅ Éxito: {rondas} rondas de transformación aplicadas.")
            self._lbl_estado.setStyleSheet(f"color: {self.COLORS['success']}; padding: 10px; background-color: {self.COLORS['success_bg']}; border-radius: 5px;")
            
        except Exception as e:
            self._lbl_estado.setText(f"❌ Error: {str(e)}")
            self._lbl_estado.setStyleSheet(f"color: {self.COLORS['danger']};")
    
    def _on_descifrar(self):
        try:
            radio = float(self._input_radio.text() or "0.05")
            paso = float(self._input_paso.text() or "0.002")
            num_giros = self._slider_giros.value()
            
            texto = self._txt_input.toPlainText().strip()
            if not texto:
                if self._ultimo_cifrado:
                    texto = self._ultimo_cifrado
                    self._txt_input.setPlainText(texto)
                else:
                    self._lbl_estado.setText("⚠️ Ingrese el texto cifrado (hexadecimal)")
                    self._lbl_estado.setStyleSheet(f"color: {self.COLORS['primary']};")
                    return
            
            # Validación simple de formato hex
            for parte in texto.split():
                try:
                    int(parte, 16)
                except ValueError:
                    self._lbl_estado.setText(f"❌ Formato inválido. Use hexadecimal (ej: 6A 67)")
                    self._lbl_estado.setStyleSheet(f"color: {self.COLORS['danger']};")
                    return
            
            resultado = self._controller.descifrar_texto(texto, radio, paso, num_giros)
            self._txt_output.setPlainText(resultado)
            self._lbl_estado.setText("✅ Mensaje descifrado correctamente.")
            self._lbl_estado.setStyleSheet(f"color: {self.COLORS['primary']}; padding: 10px; background-color: {self.COLORS['accent_bg']}; border-radius: 5px;")
            
        except Exception as e:
            self._lbl_estado.setText(f"❌ Error: {str(e)}")
            self._lbl_estado.setStyleSheet(f"color: {self.COLORS['danger']};")
    
    def _copiar_a_entrada(self):
        output = self._txt_output.toPlainText().strip()
        if output:
            self._txt_input.setPlainText(output)
            self._lbl_estado.setText("📝 Texto copiado. Pulse 'Descifrar' con la clave correcta.")
            self._lbl_estado.setStyleSheet(f"color: {self.COLORS['primary']};")