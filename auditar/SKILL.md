---
name: auditar
description: >
  Ejecuta auditoria de seguridad sobre un proyecto o componente, entregando
  hallazgos priorizados con severidad, impacto, evidencia y recomendación
  concreta. Usar cuando el usuario diga "auditar", "audit", "audita",
  "hallazgos de seguridad", "revisar seguridad", "análisis de vulnerabilidades",
  "busca vulnerabilidades en", "revisa seguridad de", "que tan seguro esta",
  "compliance", "CIS", "NIST", o pida un informe de seguridad. No usar para
  revisiones generales de calidad de código (usar la skill review en esos casos).
model: sonnet
disable-model-invocation: false
allowed-tools: Read Glob Grep
---

# Auditar - Análisis de seguridad

Ejecuta auditoría de seguridad sobre: **$ARGUMENTS**

## Paso 0 - Adjuntar archivos críticos con @

Antes de auditar, verifica que los archivos de mayor superficie de ataque están en el contexto.

Si el usuario no los adjuntó con `@archivo`, pídelos según el tipo de proyecto:

- **IaC / infraestructura como código:** `@[proyecto]/template.yaml` - expone IAM, puertos, accesos
- **Código de aplicación:** `@[proyecto]/src/[handler].py` o `.js` principal
- **Variables de entorno / configuración:** `@[proyecto]/.env.example` (nunca `.env` real)
- **Políticas de acceso:** si están en archivos separados, `@[proyecto]/iam/policy.json`
- **Dependencias:** `@[proyecto]/requirements.txt` o `@[proyecto]/package.json`

Ejemplo: "Para la auditoría necesito el template de infraestructura y el handler principal.
¿Puedes adjuntarlos con `@mi-proyecto/template.yaml` y `@mi-proyecto/src/handler.py`?"

Si el directorio del proyecto está accesible y los archivos se pueden leer: proceder directamente.

---

## Paso 1: Reconocimiento inicial

Antes de analizar, determina:
1. Tipo de proyecto (función serverless, VM, contenedor, app web, script, IaC)
2. Busca archivos de hallazgos previos: `docs/SEGURIDAD_HALLAZGOS.md` o similar
3. Identifica el perímetro: qué archivos/recursos están en scope

## Paso 2: Análisis por dominio

Revisa según aplique al tipo de proyecto:

**Credenciales y secretos**
- Hardcoded credentials, API keys, passwords en código
- Variables de entorno expuestas, `.env` en repositorio
- Secretos en IaC como parámetros sin protección de valor (ej. sin `NoEcho` en CloudFormation)

**Control de acceso**
- Políticas de permisos demasiado amplias (acceso administrador total, wildcards)
- Recursos sin autenticación o con autenticación débil
- MFA no requerido para operaciones críticas

**Red y exposición**
- Puertos abiertos innecesarios, grupos de seguridad abiertos a `0.0.0.0/0`
- Servicios sin TLS o con versiones vulnerables (TLS 1.0/1.1)
- Buckets/almacenamiento con acceso público no intencional

**Aplicación**
- Validación de entrada ausente (SQLi, XSS, command injection)
- Manejo de errores que expone información sensible
- Dependencias con CVEs conocidos

**Observabilidad y trazabilidad**
- Logging ausente o insuficiente para acciones críticas
- Retención de logs inadecuada
- Sin alertas en eventos de seguridad

## Paso 3: Formato de hallazgos

Para cada hallazgo:

```
[ID] SEVERIDAD - Título del hallazgo
Evidencia: [archivo:línea o recurso concreto]
Impacto: [qué puede pasar si se explota]
Recomendación: [acción concreta y específica]
Estado: [Nuevo | Ya conocido]
Clasificación: [Verificado | Inferido | Recomendado]
```

Severidades: CRÍTICO / ALTO / MEDIO / BAJO / INFORMATIVO

Marco de referencia: ISO 27001, NIST CSF, CIS Controls, buenas prácticas de seguridad del proveedor cloud correspondiente.

## Paso 4: Resumen ejecutivo

Al finalizar:
1. Total de hallazgos por severidad
2. Top 3 más urgentes con acción inmediata recomendada
3. Comparación con hallazgos previos si existe `docs/SEGURIDAD_HALLAZGOS.md`
4. Riesgo residual estimado: ALTO / MEDIO / BAJO

**Regla crítica:** No inventes vulnerabilidades. Todo hallazgo debe tener evidencia en código, configuración o recurso observable. Diferencia siempre: Verificado / Inferido / Recomendado.

## Troubleshooting

**No se encuentra el proyecto en $ARGUMENTS:** Pedir ruta exacta o confirmar el nombre/ubicación del proyecto.

**Archivos binarios o de estado (`.tfstate`, etc.) en el análisis:** Solo analizar por referencia de nombres, nunca leer binarios directamente.
