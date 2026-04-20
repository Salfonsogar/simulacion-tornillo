"""
Controlador de Criptografía.

Wrapea el módulo crypto existente y proporciona
una interfaz unificada para cifrado/descifrado.
"""

from typing import Tuple, Optional


class CryptoController:
    """
    Controlador de criptografía.
    
    Maneja:
    - Cifrado de datos
    - Descifrado
    - Validaciones
    
    Attributes:
        estado: Estado actual de cifrado
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        self._estado = None
        self._ultimo_error = ""
        self._ScrewCipher = None
        self._ScrewCryptoState = None
        self._CryptoError = None
        self._importar_modulo()
    
    def _importar_modulo(self):
        """Importa el módulo crypto de forma segura."""
        try:
            from crypto.screw_crypto import ScrewCipher, ScrewCryptoState, CryptoError
            self._ScrewCipher = ScrewCipher
            self._ScrewCryptoState = ScrewCryptoState
            self._CryptoError = CryptoError
            self._estado = ScrewCryptoState()
        except ImportError as e:
            self._ultimo_error = f"No se pudo importar crypto: {e}"
    
    @property
    def disponible(self) -> bool:
        """Si el módulo crypto está disponible."""
        return self._ScrewCipher is not None
    
    @property
    def estado(self):
        """Estado actual."""
        return self._estado
    
    @property
    def ultimo_error(self) -> str:
        """Último error."""
        return self._ultimo_error
    
    def calcular_vm(self, radio: float, paso: float) -> float:
        """
        Calcula la VM desde radio y paso.
        
        Args:
            radio: Radio de giro
            paso: Paso de rosca
        
        Returns:
            VM (ventaja mecánica)
        """
        if not self.disponible:
            raise RuntimeError(self._ultimo_error)
        return self._ScrewCipher.calcular_vm(radio, paso)
    
    def cifrar_fuerza(
        self,
        f_entrada: float,
        radio: float,
        paso: float,
        num_giros: int = 1
    ) -> Tuple[float, int]:
        """
        Cifra un valor de fuerza.
        
        Args:
            f_entrada: Fuerza de entrada
            radio: Radio de giro
            paso: Paso de rosca
            num_giros: Número de giros
        
        Returns:
            Tupla (fuerza_cifrada, rondas)
        """
        if not self.disponible:
            raise RuntimeError(self._ultimo_error)
        vm = self.calcular_vm(radio, paso)
        return self._ScrewCipher.cifrar_fuerza(f_entrada, vm, num_giros)
    
    def descifrar_fuerza(
        self,
        f_cifrada: float,
        radio: float,
        paso: float,
        num_giros: int = 1
    ) -> float:
        """
        Descifra un valor de fuerza.
        
        Args:
            f_cifrada: Fuerza cifrada
            radio: Radio original
            paso: Paso original
            num_giros: Giros originales
        
        Returns:
            Fuerza descifrada
        """
        if not self.disponible:
            raise RuntimeError(self._ultimo_error)
        vm = self.calcular_vm(radio, paso)
        return self._ScrewCipher.descifrar_fuerza(f_cifrada, vm, num_giros)
    
    def cifrar_texto(
        self,
        texto: str,
        radio: float,
        paso: float,
        num_giros: int = 1
    ) -> Tuple[str, int]:
        """
        Cifra texto.
        
        Args:
            texto: Texto a cifrar
            radio: Radio de giro
            paso: Paso de rosca
            num_giros: Número de giros
        
        Returns:
            Tupla (texto_cifrado, rondas)
        """
        if not self.disponible:
            raise RuntimeError(self._ultimo_error)
        vm = self.calcular_vm(radio, paso)
        valores = self._ScrewCipher.texto_a_valores(texto)
        resultado, rondas = self._ScrewCipher.cifrar_multiplo(valores, vm, num_giros)
        texto_cifrado = self._ScrewCipher.valores_a_hex(resultado)
        return texto_cifrado, rondas
    
    def descifrar_texto(
        self,
        texto_cifrado: str,
        radio: float,
        paso: float,
        num_giros: int = 1
    ) -> str:
        """
        Descifra texto.
        
        Args:
            texto_cifrado: Texto cifrado (hex)
            radio: Radio original
            paso: Paso original
            num_giros: Giros originales
        
        Returns:
            Texto descifrado
        """
        if not self.disponible:
            raise RuntimeError(self._ultimo_error)
        vm = self.calcular_vm(radio, paso)
        valores_cifrados = [int(x, 16) for x in texto_cifrado.split()]
        resultado = self._ScrewCipher.descifrar_multiplo(valores_cifrados, vm, num_giros)
        return self._ScrewCipher.valores_a_texto(resultado)
    
    def validar_parametros(
        self,
        f_entrada: float,
        radio: float,
        paso: float,
        num_giros: int = 1
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida parámetros.
        
        Args:
            f_entrada: Fuerza de entrada
            radio: Radio de giro
            paso: Paso de rosca
            num_giros: Número de giros
        
        Returns:
            Tupla (es_válido, mensaje)
        """
        if not self.disponible:
            return False, self._ultimo_error
        return self._ScrewCipher.validar_parametros(f_entrada, radio, paso, num_giros)
    
    def generar_bloque_visual(self, datos: list, tamano: int = 16) -> list:
        """
        Genera bloque visual tipo AES.
        
        Args:
            datos: Lista de valores
            tamano: Tamaño del bloque
        
        Returns:
            Matriz 4x4
        """
        if not self.disponible:
            return []
        return self._ScrewCipher.generar_bloque_visual(datos, tamano)
    
    def formatear_bloque_hex(self, bloque: list) -> str:
        """
        Formatea bloque como string.
        
        Args:
            bloque: Matriz 4x4
        
        Returns:
            String formateado
        """
        if not self.disponible:
            return ""
        return self._ScrewCipher.formatear_bloque_hex(bloque)
    
    def limpiar(self):
        """Limpia el estado."""
        if self._ScrewCryptoState:
            self._estado = self._ScrewCryptoState()
        self._ultimo_error = ""