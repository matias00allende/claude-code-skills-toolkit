---
name: brainstorm
description: >
  Explora opciones de diseño y evalúa alternativas arquitectónicas cuando hay más de un
  enfoque válido. Fuerza análisis estructurado antes de comprometer una solución. Usar
  cuando el usuario diga "brainstorm", "qué opciones tenemos", "cómo podríamos hacer
  esto", "evalúa las alternativas", "qué arquitectura usamos", "cuál es la mejor forma
  de", "piensa en cómo resolver", "analiza las opciones para".
model: sonnet
disable-model-invocation: false
allowed-tools: Read Glob Grep
---

# Diseño antes de implementar - Exploración estructurada

Este espacio es para pensar, no para implementar. El output es una decisión documentada, no código.

---

## Fase 1 - Encuadre del problema

Antes de explorar soluciones, asegúrate de que el problema esté bien definido:

1. **Problema raíz:** ¿Qué limitación real hay? ¿Por qué el estado actual es insuficiente?
2. **Criterios de éxito:** ¿Cómo sabremos que la solución funciona? (medibles cuando sea posible)
3. **Restricciones duras:** qué no puede cambiar (presupuesto, stack tecnológico, normativa, plazos, capacidad del equipo)
4. **Restricciones blandas:** qué preferimos pero podría ceder
5. **Contexto organizacional:** ¿hay implicaciones políticas, presupuestarias, de gobernanza o de adopción?

Si el problema no está claro: señalarlo. Una buena solución al problema equivocado es un fracaso.

---

## Fase 2 - Generación de alternativas

Genera entre 2 y 4 opciones reales. Reglas:

- Cada opción debe ser genuinamente distinta (no variantes menores de la misma idea)
- Incluir al menos una opción conservadora (bajo riesgo, menor cambio) y una opción agresiva (mayor impacto, mayor riesgo)
- No descartar opciones prematuramente - el objetivo de esta fase es amplitud

**Formato por opción:**

```
## Opción [N]: [nombre descriptivo]

Descripción: [qué es, cómo funciona]
Stack/componentes: [qué tecnologías o servicios involucra]

Ventajas:
- [ventaja concreta]
- [ventaja concreta]

Desventajas / riesgos:
- [desventaja o riesgo concreto]
- [desventaja o riesgo concreto]

Complejidad de implementación: Baja / Media / Alta
Reversibilidad: Fácil / Difícil / Irreversible
Costo estimado: [si aplica]
Dependencias: [qué debe estar listo para que esto funcione]
```

---

## Fase 3 - Análisis comparativo

Construye una tabla de trade-offs con los criterios más relevantes para este problema:

```
| Criterio              | Opción 1 | Opción 2 | Opción 3 |
|-----------------------|----------|----------|----------|
| [criterio 1]          |          |          |          |
| [criterio 2]          |          |          |          |
| Seguridad             |          |          |          |
| Costo                 |          |          |          |
| Mantenibilidad        |          |          |          |
| Velocidad de entrega  |          |          |          |
| Riesgo operativo      |          |          |          |
```

Criterios siempre presentes (adaptar al contexto):
- Seguridad / compliance
- Costo (implementación + operación mensual)
- Mantenibilidad a largo plazo
- Riesgo operativo (qué puede fallar en producción)
- Velocidad de entrega
- Reversibilidad (qué tan fácil es hacer rollback)
- Adopción (si involucra usuarios o equipos)

---

## Fase 4 - Recomendación

Presenta una recomendación concreta con justificación:

```
## Recomendación: Opción [N] - [nombre]

Por qué es la mejor opción para este contexto:
[Argumentos específicos - no genéricos. Referencia a restricciones y criterios de la Fase 1]

Por qué no las otras:
- Opción X: [razón específica de descarte]
- Opción Y: [razón específica de descarte]

Riesgos aceptados conscientemente:
[Los trade-offs negativos de la opción elegida que se asumen con esta decisión]

Condiciones para que esta recomendación cambie:
[Si X ocurre, reconsiderar Opción Y]
```

---

## Gate de implementación

**No se implementa nada hasta que el usuario apruebe la recomendación.**

Si el usuario aprueba → invocar la skill `plan` de esta colección para descomponer la implementación.
Si el usuario pide modificaciones → actualizar el análisis y presentar nuevamente.

---

## Registro de decisión (ADR)

Si la decisión tiene implicaciones de mediano o largo plazo, guardar en:

`<proyecto>/docs/ADR-[NNN]-[descripcion].md`

Formato y criterios de cuándo crear un ADR: ver [reference/adr-template.md](reference/adr-template.md)

---

## Troubleshooting

**El usuario ya tiene una solución en mente y solo pide validarla:** Ejecutar igual las 4 fases. Si la solución es la mejor, la recomendación la confirma con evidencia. Si no, el análisis estructurado lo muestra antes de comprometer trabajo.

**El problema tiene demasiadas variables para 2-4 opciones:** Reducir el alcance: separar decisiones independientes y hacer un brainstorm por cada eje. Un brainstorm con 8 opciones no es análisis, es inventario.

**Las opciones parecen todas iguales (variantes menores):** Forzar al menos una opción que cambie radicalmente el enfoque: no agregar un servicio sino eliminarlo, no migrar sino reescribir, no integrar sino separar. La diversidad real revela trade-offs que las variantes no muestran.

**El usuario aprueba pero el plan posterior es inimplementable:** El brainstorm no exploró dependencias ni restricciones reales. Volver a Fase 1 con las restricciones concretas antes de reiterar.
