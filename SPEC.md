# Especificación del Proyecto: Simulador de Tornillo

## 1. Información General

- **Nombre del Proyecto**: Simulador de Tornillo - Física de Máquinas Simples
- **Tipo de Aplicación**: Aplicación de escritorio con simulación física
- **Idioma**: Español
- **Descripción**: Aplicación educativa para talleres universitarios sobre máquinas simples, específicamente el tornillo como преобразователь de movimiento circular a lineal. Incluye analogía con criptografía AES-256.

## 2. Especificación UI/UX

### Estructura de Ventanas

- **Ventana Principal**: QMainWindow con QTabWidget (3 pestañas)
- **Tamaño**: 1100x750 píxeles (mínimo)
- **Título**: "Simulador de Tornillo - Física & Criptografía"
- **Tema**: Oscuro (Dark Theme) con acentos en verde técnico

### Layout Visual

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo] Simulador de Tornillo                    [─][□][X] │
├─────────────────────────────────────────────────────────────┤
│  [Calculadora] [Simulación] [Criptografía]                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    CONTENIDO DE PESTAÑA                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Paleta de Colores

| Elemento | Color | Hex |
|----------|-------|-----|
| Fondo principal | Negro | #1E1E1E |
| Fondo secundario | Gris oscuro | #2D2D2D |
| Acento principal | Verde técnico | #00FF7F |
| Acento secundario | Cian | #00CED1 |
| Texto principal | Blanco | #FFFFFF |
| Texto secundario | Gris claro | #B0B0B0 |
| Error | Rojo brillante | #FF4444 |
| Warning | Naranja | #FFA500 |

### Tipografía

- **Familia**: "Segoe UI", "Roboto", sans-serif
- **Título**: 16px negrita
- **Cuerpo**: 12px regular
- **Labels**: 11px regular
- **Resultados**: 14px bold

### Componentes UI

| Componente | Estados | Comportamiento |
|------------|---------|-----------------|
| QLineEdit | Normal, Focus, Error | Borde verde = focus, rojo = error |
| QPushButton | Normal, Hover, Pressed, Disabled | Hover: fondo más claro |
| QLabel | Normal, Result | Resultado en verde-bold |
| QTabWidget | Selected, Unselected | Tabs con indicador verde |

## 3. Especificación Funcional

### 3.1 Motor de Cálculo (Física)

#### Fórmulas Principales

1. **Ventaja Mecánica (VM)**:
   ```
   VM = (2 * π * r) / L
   ```
   - `r` = radio de giro del tornillo (m)
   - `L` = paso de la rosca (m)

2. **Fuerza de Salida**:
   ```
   F_salida = F_entrada * VM
   ```
   - `F_entrada` = fuerza aplicada por el usuario (N)

3. **Desplazamiento Lineal**:
   ```
   Δx = θ * (L / 2π)
   ```
   - `θ` = ángulo de rotación (radianes)

4. **Oscilador Amortiguado (2do orden)**:
   ```
   y(t) = A * e^(-γt) * cos(ωt + φ)
   ```
   - `A` = amplitud inicial
   - `γ` = coeficiente de amortiguación
   - `ω` = frecuencia natural
   - `φ` = fase inicial

#### Límites de Seguridad

| Parámetro | M��nimo | Máximo | Mensaje Error |
|----------|--------|--------|---------------|
| F_entrada | 0.1 N | 10000 N | "[CRITICAL ERROR] Fuerza fuera de rango" |
| Radio (r) | 0.01 m | 1.0 m | "[CRITICAL ERROR] Radio inválido" |
| Paso (L) | 0.0001 m | 0.05 m | "[CRITICAL ERROR] Paso inválido" |

### 3.2 Pestaña Calculadora

**Campos de Entrada**:
- Fuerza de entrada (F_entrada): QLineEdit, float, rango [0.1, 10000] N
- Radio del brazo (r): QLineEdit, float, rango [0.01, 1.0] m
- Paso de rosca (L): QLineEdit, float, rango [0.0001, 0.05] m
- Ángulo de rotación (θ): QLineEdit, float, opcional, grados

**Campos de Salida**:
- Ventaja Mecánica (VM): float, solo lectura
- Fuerza de salida (F_salida): float, solo lectura
- Desplazamiento lineal (Δx): float, solo lectura

**Botones**:
- "Calcular": Ejecuta cálculos
- "Limpiar": Limpia todos los campos
- "Valores por defecto": Carga ejemplo educativo

### 3.3 Pestaña Simulación Visual

**Componentes**:
- Canvas matplotlib con animación del tornillo
- Gráfico en tiempo real de y(t) vs t
- Slider para controlar velocidad de giro
- Indicador visual de rotación angular

**Animación del Tornillo**:
- Tornillo helicoidal que rota visualmente
- Movimiento lineal hacia abajo según rotación
- Escala temporal para mostrar desplazamiento

### 3.4 Pestaña Criptografía (Analogía)

**Concepto Visual**:
- "Llave" kleine (input de giro) = clave criptográfica
- "Tornillo" = algoritmo AES-256
- "Bloque cifrado" = resultado fijo/inamovible

**Animación**:
- Bloque de "datos crudos" (texto claro)
- Aplicar "llave" (girar tornillo)
- Transformación a "bloque cifrado" (fixto)
- Indicador de irreversibilidad

## 4. Criterios de Aceptación

### Funcionales

- [ ] VM se calcula correctamente: VM = 2πr/L
- [ ] F_salida se calcula: F_salida = F_entrada * VM
- [ ] Validación de entrada muestra errores claros
- [ ] Alertas [CRITICAL ERROR] cuando se exceden límites
- [ ] Animación del tornillo responde a inputs del usuario

### Interfaz

- [ ] Tema oscuro aplicado consistentemente
- [ ] Todas las etiquetas en español
- [ ] Campos numéricos con validación visual
- [ ] Resultados se muestran en verde bold

### Simulación

- [ ] Animaciónmatplotlib muestra tornillo girando
- [ ] Gráfico y(t) del oscilador amortiguado visible
- [ ] Controles interactivos (sliders) funcionan

### Código

- [ ] Comentarios explican relación física-software
- [ ] Referencia a AES-256 en comentarios
- [ ] Código limpio y documentado

## 5. Dependencias

```
PyQt6>=6.7.0
matplotlib>=3.8.0
numpy>=1.26.0
```

## 6. Notas de Implementación

- El tornillo es una "profunda transformación de estado" similar a AES-256:
  - Input: movimiento circular + llave (fuerza)
  - Transformación:VM = (2πr)/L
  - Output: movimiento lineal (fuerza amplificada)
  - Irreversibilidad: sin el torque correcto, no hay avance