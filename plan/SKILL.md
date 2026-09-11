---
name: plan
description: >
  Descompone una tarea de implementación no trivial en tareas atómicas verificables
  antes de escribir código. Gate obligatorio para trabajo de más de 3 pasos o con
  decisiones arquitectónicas significativas. Usar cuando el usuario diga "plan",
  "planifica", "diseña el plan", "cómo lo hacemos", "qué hay que hacer para",
  "planifica la implementación de", "antes de implementar", "qué pasos seguimos".
model: sonnet
disable-model-invocation: false
allowed-tools: Read Glob Grep Write
---

# Planificación antes de implementar

No escribas código antes de que el plan esté aprobado. Este es el gate de diseño.

---

## Paso 0 - Adjuntar archivos críticos con @

Antes de planificar, identifica si los archivos más importantes están en el contexto.

Si el usuario no los adjuntó con `@archivo`, pídelos explícitamente:

- **IaC (Terraform / CloudFormation / etc.):** `@[proyecto]/template.tf` o `@[proyecto]/template.yaml`
- **Código principal:** `@[proyecto]/src/[handler].py` o equivalente
- **Schema de base de datos:** `@[proyecto]/sql/schema.sql` o `@[proyecto]/docs/schema.md`
- **Documento de contexto del proyecto:** `@[proyecto]/README.md` si existe y tiene contexto crítico

Ejemplo: "Para planificar bien, necesito ver el template de infraestructura actual. ¿Puedes adjuntarlo
con `@mi-proyecto/template.yaml`?"

Si el contexto ya tiene los archivos relevantes (fueron leídos en esta sesión): continuar directamente.

---

## Fase 1 - Entender el problema real

Antes de descomponer tareas, confirma que entiendes qué se pide:

1. **Objetivo concreto:** ¿Qué debe ser verdad cuando esto esté hecho? (no proceso, sino resultado)
2. **Restricciones no negociables:** seguridad, compatibilidad, presupuesto, normativa, autorización pendiente
3. **Dependencias externas:** ¿qué necesita estar listo primero? ¿qué bloquea?
4. **Alcance explícito:** ¿qué NO está incluido? (igual de importante que lo que sí)
5. **Riesgos conocidos:** ¿qué puede salir mal? ¿qué lo haría más complejo?

Si alguno de estos puntos no está claro: señalarlo antes de planificar. Un plan construido sobre supuestos incorrectos es trabajo tirado.

---

## Fase 2 - Descomposición en tareas atómicas

Descompone el trabajo en tareas que cumplan todos estos criterios:

- **Duración:** 2-15 minutos de implementación real (no "implementar el módulo X" - demasiado grande)
- **Verificable:** cada tarea tiene un criterio claro de "hecho" - si no puedes definirlo, la tarea no está bien definida
- **Independiente cuando sea posible:** minimize dependencias entre tareas
- **Un responsable:** cada tarea la hace una persona o un agente - sin ambigüedad

**Formato de tarea:**

```
T-NN: [Verbo de acción] [objeto específico]
- Entrada: [qué necesita para empezar]
- Salida: [qué produce / cómo se verifica]
- Dependencias: [T-XX, T-YY] o "ninguna"
- Riesgo: [si aplica]
```

---

## Fase 3 - Ordenar y estimar

1. Construye el grafo de dependencias (qué debe ir antes de qué).
2. Identifica el camino crítico (secuencia más larga de tareas dependientes).
3. Marca qué tareas pueden ejecutarse en paralelo.
4. Señala los puntos de decisión: momentos donde el usuario debe aprobar antes de continuar.

---

## Fase 4 - Presentar el plan para aprobación

Presenta al usuario:

```
## Plan: [nombre de la funcionalidad/proyecto]
Objetivo: [resultado concreto cuando esté listo]
Alcance: [qué está incluido - qué NO está incluido]

### Tareas
[Lista numerada con formato T-NN]

### Orden de ejecución
[Secuencia o diagrama ASCII si el grafo es complejo]

### Decisiones pendientes antes de empezar
[Lista de puntos que requieren confirmación del usuario]

### Riesgos
[Lista de lo que puede complicar la implementación]

### Gate de aprobación
¿Aprobamos este plan para iniciar implementación? [Sí / Modificar: ...]
```

---

## Regla absoluta

**No implementes nada antes de que el usuario apruebe el plan explícitamente.**

Si el usuario dice "sí, adelante" o equivalente, empieza con T-01. Si pide modificaciones, actualiza el plan y presenta nuevamente antes de implementar.

Excepción: si el trabajo es trivial (< 3 pasos, sin decisiones de arquitectura, completamente reversible), puedes omitir la fase de presentación e implementar directamente informando al usuario qué harás.

---

## Guardar el plan

Si el proyecto lo amerita (trabajo de más de 1 sesión o más de 10 tareas), guarda el plan en:

`<proyecto>/docs/plan-[descripcion]-[YYYY-MM-DD].md`

Formato compacto para archivo:
```markdown
# Plan: [nombre]
Fecha: [YYYY-MM-DD]
Estado: [En curso / Completado / Cancelado]

## Tareas
- [x] T-01: [tarea completada]
- [ ] T-02: [tarea pendiente]
```

---

## Troubleshooting

**El usuario aprueba el plan y pide implementar, pero hay dependencias no resueltas:** Detener antes de T-01. Listar explícitamente qué debe estar listo antes de empezar (acceso, credenciales, aprobaciones, infraestructura previa). No iniciar implementación con bloqueos conocidos.

**El plan tiene tareas demasiado grandes ("implementar el módulo X"):** Forzar la descomposición: preguntar qué archivos se crean o modifican, qué comando verifica que está listo, cuántos minutos toma realmente. Si la respuesta es "varios" o "no sé", la tarea no está bien definida.

**El usuario modifica el alcance a mitad del plan:** Actualizar el plan antes de continuar. No mezclar el alcance original con el nuevo en la misma lista de tareas. Crear versión nueva del plan si el cambio es significativo.
