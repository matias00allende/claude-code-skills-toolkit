---
name: debug
description: >
  Diagnostica bugs, errores, comportamientos inesperados o fallos de sistema mediante
  un enfoque sistemático de 4 fases: reproducir, analizar, hipotetizar, corregir. Evita
  saltar a soluciones antes de entender el problema. Usar cuando el usuario diga
  "debug", "depurar", "no funciona", "hay un error", "falla", "bug", "qué está
  pasando", "por qué falla", "investiga el error", "diagnostica", "troubleshoot".
model: sonnet
disable-model-invocation: false
allowed-tools: Read Glob Grep Bash
---

# Debugging sistemático - 4 fases

No saltes a soluciones. Sigue las 4 fases en orden. Cada fase tiene un entregable antes de pasar a la siguiente.

---

## Paso 0 - Adjuntar archivos críticos con @

Antes de diagnosticar, verifica que los archivos del código que falla están en el contexto.

Si el usuario no los adjuntó con `@archivo`, pídelos:

- **Archivo donde ocurre el error:** `@[proyecto]/src/[archivo].[ext]`
- **Log completo del error:** si está en un archivo, `@[ruta/al/log.txt]`
- **Configuración relevante:** `@[proyecto]/.env.example` o `@[proyecto]/config.json`
- **Handler o entrypoint:** `@[proyecto]/main.py` o equivalente

Ejemplo: "Para diagnosticar el error, necesito ver el handler. ¿Puedes adjuntarlo
con `@mi-proyecto/src/handler.py`?"

Si ya tienes el stack trace completo y el código en contexto: proceder directamente a Fase 1.

---

## Fase 1 - Reproducir

**Objetivo:** confirmar que el problema es real y entender sus condiciones exactas.

1. Lee el mensaje de error o síntoma completo tal como lo reporta el usuario o el sistema.
2. Identifica:
   - ¿Qué comportamiento se esperaba?
   - ¿Qué comportamiento se observa?
   - ¿En qué condiciones ocurre? (siempre, a veces, solo con ciertos inputs)
   - ¿Cuándo empezó? (¿hubo un cambio reciente?)
3. Si hay logs, léelos. Busca el primer error, no el último síntoma.
4. Si hay stack trace: el error real está en la primera línea del trace, no al fondo.

**Entregable Fase 1:**
```
Síntoma: [qué pasa exactamente]
Condición: [cuándo ocurre]
Error exacto: [mensaje de error o stack trace - sin parafrasear]
Contexto de cambio: [qué cambió antes de que apareciera]
```

---

## Fase 2 - Analizar

**Objetivo:** entender el sistema suficientemente para generar hipótesis precisas.

1. Lee el código relevante (no todo el proyecto - solo la ruta de ejecución que falla).
2. Identifica los componentes involucrados: función/módulo de entrada, dependencias, servicios externos.
3. Busca patrones conocidos de fallo:
   - **Nulls/undefined:** acceso a propiedad de objeto null
   - **Asincronismo:** await faltante, race condition, callback que no se llama
   - **Scope de variables:** variable redefinida en loop o closure
   - **Encoding:** bytes vs strings, UTF-8 vs ASCII
   - **Permisos:** IAM, filesystem, red
   - **Configuración:** variable de entorno faltante o incorrecta
   - **Dependencias:** versión incompatible, módulo no instalado
   - **Estado externo:** BD caída, API externa que cambió, token expirado
   - **Cache stale:** dato viejo en memoria, sesión no invalidada
4. Verifica supuestos con datos: lee el archivo de configuración real, ejecuta el query real, revisa el log real.

**Regla:** No asumas. Verifica. "Debería estar configurado como X" no es análisis - léelo.

---

## Fase 3 - Hipótesis ordenadas

**Objetivo:** lista priorizada de causas, de más probable a menos probable.

Formato:

```
H1 (más probable): [causa específica] - [por qué es probable, con evidencia]
H2: [causa específica] - [por qué es candidata]
H3: [causa específica] - [por qué es candidata]
```

**Reglas:**
- Máximo 3 hipótesis. Si tienes más, estás haciendo inventario, no análisis.
- Cada hipótesis debe ser falseable: debe haber un comando o lectura que la confirme o descarte.
- Ordena por: frecuencia del patrón, evidencia disponible, impacto si es correcta.

**Red flags que cambian el análisis:**
- El error ocurre solo en producción → busca diferencias de configuración o datos reales
- El error ocurre intermitentemente → busca race condition, timeout o dependencia de red
- El error apareció sin cambios de código → busca cambio en dependencias, infra o datos externos
- El error tiene stack trace en librería de terceros → el bug está en tu llamada a esa librería, no en ella

---

## Fase 4 - Fix y verificación

**Objetivo:** aplicar la solución mínima que resuelve H1, luego verificar.

1. Aplica el fix para H1.
2. Ejecuta la verificación correspondiente (ver skill `verificar` de esta colección) - sin evidencia de que el fix funciona, no está resuelto.
3. Si el fix no funciona: descarta H1, pasa a H2. No acumules fixes para múltiples hipótesis a la vez.
4. Si el fix funciona: verifica que no introdujo efectos secundarios en la ruta de código adyacente.

**Entregable final:**

```
## Debug completado

Problema: [descripción concisa]
Causa raíz: [la hipótesis que resultó correcta - con evidencia]
Fix aplicado: [archivo:línea - cambio específico]
Verificación: [comando ejecutado + resultado]

Lecciones operativas: [si aplica - qué patrón evitar en el futuro]
```

---

## Qué NO hacer

- No probar fixes al azar esperando que algo funcione.
- No leer todo el codebase cuando el problema está en una función.
- No declarar "resuelto" sin ejecutar la verificación.
- No confundir el síntoma con la causa: el error que aparece en el log no es necesariamente donde está el bug.

---

## Troubleshooting

**El error ocurre solo en producción y no es reproducible localmente:** Buscar diferencias concretas entre entornos: variables de entorno, versiones de dependencias, configuración de red, datos reales vs datos de prueba. Nunca asumir que ambos entornos son idénticos.

**El stack trace apunta a una librería de terceros:** El bug está en la llamada a esa librería, no dentro de ella. Revisar los argumentos que se le pasan: tipo incorrecto, valor nulo, formato inesperado. Solo en casos raros es un bug real de la librería.

**Se aplicaron varios fixes simultáneos y el problema desapareció:** No está resuelto, está enmascarado. Revertir los fixes uno a uno para identificar cuál fue la causa raíz. Dejar solo el fix necesario y eliminar los demás para no introducir deuda técnica.
