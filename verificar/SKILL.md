---
name: verificar
description: >
  Gate obligatorio antes de declarar cualquier tarea completa. Fuerza la ejecución de
  un comando de verificación y adjunta evidencia real. Activar también proactivamente
  antes de reportar trabajo como listo. Usar cuando el usuario diga "verificar",
  "verifica que funciona", "confirma que quedó bien", "está listo?", "tarea completa?",
  "terminar la tarea", "marcar como hecho".
model: haiku
disable-model-invocation: false
allowed-tools: Read Glob Grep Bash
---

# Gate de verificación obligatorio

Antes de declarar cualquier tarea como completada, ejecuta este protocolo sin excepción.

---

## Paso 1 - Identifica el comando de verificación

Según el tipo de trabajo realizado, determina qué comando confirma que el resultado es correcto:

| Tipo de trabajo | Comando de verificación |
|----------------|------------------------|
| Script o código nuevo | Ejecutar el script con caso de prueba; verificar salida esperada |
| Cambio en infraestructura como código (Terraform/CloudFormation) | Comando de validación de sintaxis del proveedor (`terraform validate`, `aws cloudformation validate-template`, etc.) |
| Deploy a un entorno cloud | Comando de estado del proveedor (`aws cloudformation describe-stacks`, `terraform show`, etc.) - verificar que el estado reportado sea el esperado |
| Modificación de archivo de configuración | Leer el archivo modificado y confirmar que el cambio está presente |
| Creación de archivo | Confirmar que el archivo existe en la ruta esperada con `Glob` |
| Cambio en función serverless / servicio desplegado | Verificar que el código desplegado corresponde a la versión esperada |
| Modificación de skill/hook de Claude Code | Leer el archivo `SKILL.md` o `settings.json` y confirmar el cambio |
| Documentación actualizada | Leer la sección actualizada del documento |

Si el tipo de trabajo no está en la tabla: define explícitamente qué condición verifica que la tarea está completa antes de ejecutar.

---

## Paso 2 - Ejecuta la verificación

- Ejecuta el comando concreto.
- Captura la salida real (no inferida).
- Si el comando falla: **no declarar la tarea completa**. Diagnostica, corrige, y vuelve al Paso 1.

---

## Paso 3 - Adjunta evidencia

Presenta al usuario:

```
## Verificación completada

Tarea: [descripción concisa de qué se hizo]
Comando ejecutado: [comando exacto]
Resultado:
[output real del comando]

Estado: VERIFICADO ✓
```

Si no fue posible ejecutar verificación (sin acceso, sin TTY, sin herramienta):

```
Estado: NO VERIFICADO - [razón exacta]
Pendiente: [qué debe hacer el usuario para confirmar]
```

---

## Reglas irrenunciables

- **Nunca declarar "listo" o "completado" sin evidencia ejecutada.** "Debería funcionar" no es verificación.
- **Nunca inferir el resultado.** Si el comando no se ejecutó, el estado es PENDIENTE DE VERIFICACIÓN.
- **Diferencia siempre:** Verificado (evidencia real) / Inferido (deducción) / Asumido (sin evidencia).
- Si la verificación muestra un problema: corregir antes de entregar. No reportar el problema como si fuera aceptable.

---

## Troubleshooting

**No hay comando de verificación obvio para el tipo de trabajo:** Definir explícitamente la condición de éxito antes de ejecutar. Ejemplo: para un cambio de documentación, la condición es "el archivo existe y contiene la sección X". Para una política IAM, la condición es "el simulador de políticas del proveedor retorna 'allowed'".

**El comando de verificación requiere credenciales o acceso que no está disponible:** Registrar como `Estado: NO VERIFICADO` con la razón exacta y la instrucción concreta para que el usuario lo verifique manualmente. No omitir el paso ni marcarlo como verificado.

**La verificación pasa pero el comportamiento observado es incorrecto:** La verificación fue insuficiente - no probó el caso real. Redefinir el comando de verificación para cubrir el escenario que falla y ejecutarlo de nuevo antes de reportar.
