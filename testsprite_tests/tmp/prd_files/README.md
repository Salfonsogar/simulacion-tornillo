# Simulador de Tornillo con Sistema Dinámico

## Descripción

Aplicación de escritorio que simula el comportamiento físico de un tornillo como sistema dinámico amortiguado, implementado con arquitectura MVC en Python.

## Estructura del Proyecto

```
tornillo_sim/
├── main.py                     # Punto de entrada
├── requirements.txt            # Dependencias
│
├── physics/                   # MODELO (Capa física)
│   ├── __init__.py
│   ├── constants.py          # Constantes físicas
│   ├── rk4_integrator.py    # Integrador Runge-Kutta
│   ├── screw_model.py        # Clase ScrewModel
│   └── screw_calculator.py   # Calculadora VM
│
├── controller/                # CONTROLADOR
│   ├── __init__.py
│   ├── simulation_controller.py
│   ├── calculator_controller.py
│   └── crypto_controller.py
│
├── gui/                      # VISTA (UI)
│   ├── __init__.py
│   ├── main_window.py
│   ├── calculator_tab.py
│   ├── crypto_tab.py
│   └── simulation/
│       ├── __init__.py
│       ├── animation_widget.py   # QPainter (animación)
│       ├── chart_widget.py       # matplotlib (gráfica)
│       └── simulation_tab.py
│
├── crypto/                   # Módulo criptografía
│   ├── __init__.py
│   └── screw_crypto.py
│
└── docs/
    ├── PLAN.md
    └── README.md
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

## Funcionalidades

### 1. Calculadora
- Calcula la Ventaja Mecánica (VM)
- Fórmula: VM = (2πr) / L

### 2. Simulación
- Animación QPainter del tornillo (NO matplotlib)
- Gráfica matplotlib de y(t) (SOLO gráfica)
- Parámetros:
  - Masa (m)
  - Amortiguación (b)
  - Rigidez (k)
- Indicadores EXTRA:
  - ωₙ (frecuencia natural)
  - ζ (factor de amortiguamiento)
  - Tipo: subamortiguado / crítico / sobreamortiguado

### 3. Criptografía
- Cifrado/descifrado usando VM como clave
- Analogía tornillo ↔ AES

## Restricciones Técnicas Cumplidas

- ✅ PyQt6 para UI
- ✅ NumPy para cálculos
- ✅ Matplotlib SOLO para gráfica (NO para animación)
- ✅ QPainter para animación del tornillo
- ✅ RK4 para integración numérica
- ✅ Separación MVC (Modelo/Vista/Controlador)
- ✅ Indicadores ωₙ y ζ

## Ecuación Física

```
m * y''(t) + b * y'(t) + k * y(t) = F(t)
```

Solucionada numéricamente con Runge-Kutta 4to orden.

## Licencia

MIT