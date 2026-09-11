# Plantilla ADR (Architecture Decision Record)

Guardar en: `<proyecto>/docs/ADR-[NNN]-[descripcion].md`

## Formato

```markdown
# ADR-NNN: [título de la decisión]
Fecha: [YYYY-MM-DD]
Estado: Aprobada

## Decisión
[Qué se decidió]

## Contexto
[Por qué era necesario decidir]

## Opciones evaluadas
[Lista con pros/cons resumidos - ver análisis completo en el brainstorm correspondiente]

## Justificación
[Por qué se eligió esta opción]

## Consecuencias
[Qué implica esta decisión a futuro]
```

## Cuándo crear un ADR

Crear cuando la decisión:
- Tiene implicaciones de mediano o largo plazo (más de 3 meses de vida operativa)
- Cambia la arquitectura de un componente existente en producción
- Selecciona una tecnología o servicio difícil de reemplazar después
- Establece un patrón que otros proyectos seguirán

No crear para decisiones de implementación reversibles o de alcance local a una sesión.
