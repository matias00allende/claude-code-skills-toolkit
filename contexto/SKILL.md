---
name: contexto
description: >
  Guía y ejecuta controles de contexto de conversación: interrumpir respuesta,
  retroceder en historial, compactar conversación larga o limpiar para tarea nueva.
  Usar cuando el usuario diga "contexto largo", "la conversación está muy larga",
  "vuelve atrás", "retrocede al punto X", "limpia el chat", "empieza de cero",
  "compacta esto", "la conversación tiene mucho ruido", "guarda y limpia",
  "el contexto está lleno", o pida explícitamente gestionar la memoria de la sesión.
model: haiku
disable-model-invocation: false
allowed-tools: Read Write
---

# Contexto - Gestión de la conversación activa

Analiza la situación actual y aplica el control adecuado. Si el usuario no especificó
cuál usar, recomienda el más apropiado según el estado de la sesión.

---

## Los cuatro controles

### 1. Escape (interrupción)

**Qué hace:** detiene la respuesta en curso inmediatamente.

**Cuándo usar:**
- Claude está respondiendo en una dirección equivocada
- Quieres redirigir antes de que termine
- El output se está alargando innecesariamente

**Cómo usarlo:** presionar `Escape` una vez durante la respuesta.

**Combinación poderosa - Escape + memoria (#):**
Si Claude cometió un error repetido, interrumpir y luego usar `#` para guardar
la regla. Ejemplo:
```
[presionar Escape]
# No uses em-dash en ningún archivo - rompe la ejecución en algunas shells
```
Esto previene que el error se repita en el resto de la sesión.

---

### 2. Doble Escape (retroceso en historial)

**Qué hace:** muestra todos los mensajes anteriores y permite saltar a cualquier
punto de la conversación, descartando lo que vino después.

**Cuándo usar:**
- Claude se fue por una tangente y quieres volver al punto donde todo estaba bien
- Hubo varios turnos de debugging inútil y quieres saltarlos
- Cometiste un error en un prompt y quieres reformularlo

**Cómo usarlo:** presionar `Escape` dos veces rápidamente.

**Efecto:** el contexto desde ese punto en adelante desaparece, pero lo que
Claude aprendió del proyecto antes de ese punto se mantiene.

---

### 3. /compact (compactación inteligente)

**Qué hace:** resume toda la historia de la conversación en un bloque compacto,
preservando lo que Claude aprendió, pero eliminando el ruido acumulado.

**Cuándo usar:**
- La conversación tiene 20+ turnos con mucho back-and-forth
- Hay debugging ya resuelto que ocupa contexto innecesariamente
- Claude ya conoce bien el proyecto y quieres liberar espacio para trabajo nuevo
- El sistema activa autocompact automáticamente cuando el contexto está casi lleno

**Cómo usarlo:**
```
/compact
```

**Qué conserva:** un resumen del conocimiento del proyecto, las decisiones tomadas y el estado
actual del trabajo.

**Qué descarta:** mensajes intermedios, iteraciones de debugging, respuestas
duplicadas, intentos fallidos. El resumen puede perder detalles: guarda en un archivo lo que
no puedas permitirte perder antes de compactar.

**Nota:** `autoCompactEnabled: true` en `settings.json` activa esto automáticamente
cuando el contexto se acerca al límite.

---

### 4. /clear (limpieza total)

**Qué hace:** borra toda la historia de la conversación. Claude pierde el contexto
de lo que se hizo en la sesión.

**Cuándo usar:**
- Cambio completo de tarea a un proyecto no relacionado
- Inicio de una sesión completamente nueva
- El contexto acumulado está confundiendo a Claude con información contradictoria

**Cómo usarlo:**
```
/clear
```

**Precaución:** antes de usar `/clear`, guarda en un archivo o en tu sistema de
memoria persistente cualquier trabajo pendiente que no quieras perder. `/clear` no
guarda nada por sí mismo.

---

## Tabla de decisión rápida

| Situación | Control recomendado |
|-----------|---------------------|
| Claude va en dirección equivocada ahora mismo | Escape |
| Claude cometió error repetido | Escape + # (memoria) |
| Quiero retomar desde un punto anterior | Doble Escape |
| Conversación larga con ruido, mismo proyecto | /compact |
| Cambio total de tema o proyecto | Guardar estado + /clear |

---

## Recomendación según el estado actual

Si el usuario no especificó cuál usar, evalúa:

1. Lee el estado de la sesión
2. Si hay trabajo en curso no guardado y la tarea requiere `/clear`: guarda ese estado primero (en memoria persistente o en un archivo del proyecto)
3. Recomienda el control apropiado con justificación de una línea
4. Si el usuario confirma, describe exactamente qué hacer (no puedes ejecutar Escape o doble-Escape tú mismo - son acciones del usuario en el teclado)

---

## Troubleshooting

**"Claude sigue cometiendo el mismo error después de varias correcciones":**
Usar Escape para interrumpir + `#` para guardar la regla en memoria. Es más efectivo
que corregir en cada turno porque la regla persiste en la sesión.

**"La conversación se autocompactó y Claude perdió contexto importante":**
Recargar el contexto persistente del proyecto (memoria, `CLAUDE.md`, notas de estado) si tu
configuración lo soporta. Los datos críticos deben estar en archivos persistentes, no solo
en el historial del chat.

**"Quiero retroceder pero no sé en qué mensaje estaba el estado correcto":**
Usar doble Escape para ver el historial completo y elegir el punto de retorno.
