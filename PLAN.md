# Plan Definitivo - Simulador de Tornillo

## PRIORIDAD 1 (Requerido para 5.0)

### Fase 1A: Oscilador Dinámico Integrado

**Objetivo:** Simulación de Segundo Orden que responde a inputs del usuario

**INPUT:**
- F_entrada (desde Calculator)
- VM = (2π × r) / L
- F_salida = F_entrada × VM

**FUERZA MOTRIZ:**
```
F_motor = F_entrada × VM
```

**ECUACIÓN DIFERENCIAL:**
```
y(t) = (F_motor / k) × e^(-γt) × cos(ωt)

Donde:
- k = F_salida / Δx (constante efectiva del resorte)
- Masa proporcional a VM
- γ = c / (2m) (factor de amortiguación)
```

**CAMBIOS EN `simulation_tab.py`:**

1. Agregar nuevos sliders para parámetros del sistema:
   - Masa (m): 0.1 - 10 kg
   - Constante resorte (k): 1 - 100 N/m
   - Amortiguación (c): 0 - 10 Ns/m

2. Mostrar valores derivados automáticamente:
   - F_motor = F_entrada × VM (calculado)
   - k efectiva basada en F_salida

3. Animación en tiempo real:
   - Cursormoviéndose sobre la curva y(t)
   - Overshoot marcado con punto rojo
   - Settling time (tiempo de establecimiento) indicado

4. Indicadores visuales:
   - Overshoot máximo
   - Tiempo de establecimiento (2% margen)
   - Amplitud final = 0

---

### Fase 1B: DCL Interactivo con Animación

**Objetivo:** Diagrama de Cuerpo Libre que se actualiza con valores del usuario

**ELEMENTOS DEL DCL:**

1. **Engrane/Tornillo** (centro)
   - Círculo dentado representando rosca
   - Animación sutil de rotación

2. **Flecha F_entrada** (horizontal)
   - Color: Azul (#0078D4)
   - Dirección: ←
   - Longitud: proporcional a F_entrada

3. **Flecha F_salida** (vertical)
   - Color: Verde (#28A745)
   - Dirección: ↑
   - Longitud: F_salida × escala (escalada por VM)

4. **Vector Torque** (circular)
   - Color: Naranja (#FF6B00)
   - Animación: rota al cambiar velocidad

5. **Leyenda numérica:**
   - F_entrada: [valor] N
   - F_salida: [valor] N
   - VM: [valor]
   - Torque: [valor] N·m

**ANIMACIONES SUTILES:**
- Engrane gira suavemente con slider de velocidad
- Flecha F_salida crece/aumenta al modificar F
- Vector torque rota indicando dirección

---

### Fase 1C: Quiz 3 Niveles

**Objetivo:** Participación activa de la audiencia

**UBICACIÓN:** Panel nuevo en `crypto_tab.py`

---

#### NIVEL 1 - FÍSICA

**Enunciado:**
```
"RET0 #1 - FÍSICA
Aplica una fuerza de entrada para mover una carga de 500N.
¿Cuál debe ser F_entrada si VM = 15.71?"
```

**Input del usuario:**
- Slider de F_entrada

**Validación:**
- F_correcta = 500 / VM
- ✅ Correcto: "¡Correcto! F = X.XX N"
- ❌ Incorrecto: "Intenta de nuevo"

---

#### NIVEL 2 - CRIPTOGRAFÍA

**Enunciado:**
```
"RETO #2 - CRIPTO
Mensaje cifrado: 'HELLO'
Con clave r=0.005m, L=0.002m
¿Cuál es la fuerza de salida?"
```

**Input del usuario:**
- Valores de r y L

**Validación:**
- VM = (2π × r) / L
- F_salida = F_entrada × VM
- ✅ Correcto: "¡Descifrado! Mensaje: ..."
- ❌ Incorrecto: "Clave incorrecta"

---

#### NIVEL 3 - INGENIERÍA

**Enunciado:**
```
"RETO #3 - INGENIERÍA
¡ALERTA DE SEGURIDAD!

F_entrada = 200N excede el límite máximo (150N)
Ajusta r o L para mantener F_salida > 100N
pero con F_entrada < 150N"
```

**Condiciones:**
- F_entrada_actual = 200N (fuera de límite)
- Restricción: F_entrada < 150N
- Objetivo: F_salida > 100N

**Solución:**
- Ajustar r o L para cumplir ambas condiciones
- Feedback: "¡Sistema seguro!" o "Ajusta parámetros"

---

## PRIORIDAD 2 (Mejora)

### Fase 2A: Tooltips Educativos

Agregar hover informativo:

| Elemento | Tooltip |
|----------|---------|
| VM | "Ventaja Mecánica: veces que se multiplica la fuerza" |
| F_salida | "Fuerza de salida = F_entrada × VM" |
| Oscilador | "Sistema que muestra estabilidad dinámica: y(t)" |
| DCL | "Diagrama de Cuerpo Libre: todas las fuerzas sobre el cuerpo" |

### Fase 2B: Contenido de Ayuda

Nueva sección Help (`main_window.py`):

1. **Explicación por pestañas**
2. **Fórmulas con ejemplos**
3. **Glosario técnico**
4. **Controles快捷键**

---

## ARCHIVOS A MODIFICAR

| Archivo | Cambios |
|---------|---------|
| `gui/simulation_tab.py` | Fase 1A: Oscilador integrado |
| `gui/calculator_tab.py` | Fase 1B: DCL interactivo |
| `gui/crypto_tab.py` | Fase 1C: Quiz 3 niveles |
| `gui/main_window.py` | Fase 2B: Help modal |

---

## RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│                    SIMULADOR DE TORNILLO                     │
├─────────────────────────────────────────────────────────────┤
│  CALCULADORA     │   SIMULACIÓN    │   CRIPTOGRAFÍA          │
│  ─────────────   │   ───────────   │   ───────────────       │
│  • VM            │   • Oscilador   │   • Cifrar/Descifrar   │
│  • F_salida      │   • Animación  │   • Bloque cifrado     │
│  • Δx            │   • DCL         │   • Quiz ⭐ NUEVO       │
│                 │     ⭐ NUEVO    │     ⭐ NUEVO           │
└─────────────────────────────────────────────────────────────┘

⭐ = Mejora para nota 5.0
```

---

## CRITERIOS DE CALIFICACIÓN CUMPLIDOS

| Criterio | Implementación |
|----------|----------------|
| Simulación 2do Orden | Fase 1A: Oscilador responde a F_entrada×VM |
| DCL | Fase 1B: DCL interactivo con animación |
| Metodología Inversa | Fase 1C: 3 niveles de quiz |
| Tema claro | Colores negros en texto |
| Tabbar estilo web | Iconos + borde inferior |
| Fórmula dinámica | VM = (2π×r)/L visible |