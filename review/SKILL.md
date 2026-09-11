---
name: review
description: >
  Revisa e inspecciona código fuente por seguridad, calidad, buenas prácticas y
  correctitud. Cubre OWASP Top 10, secretos hardcodeados y compliance CIS/NIST/ISO 27001.
  Usar cuando el usuario diga "review", "revisar código", "revisa el
  código", "analiza el código", "busca problemas en", "qué tan bueno está el código",
  "code review de", "revisa este archivo", "detecta secretos en".
model: sonnet
disable-model-invocation: false
allowed-tools: Read Glob Grep Write
---

Ejecuta revisión de código completa sobre: **$ARGUMENTS**

Si no se especifica argumento, analiza el proyecto activo en el contexto actual.

---

## Fase 1 - Inventario del código

1. Mapear todos los archivos de código fuente en el objetivo (`.py`, `.js`, `.ts`, `.rs`, `.ps1`, `.sh`, `.tf`, `.json`, `.yaml`, `.toml`, `.sql`)
2. Identificar lenguajes, frameworks y dependencias declaradas
3. Identificar archivos de configuración, credenciales y secretos potenciales (`.env`, `config.*`, `secrets.*`, `*.key`, `*.pem`, `appsettings.*`)
4. Identificar puntos de entrada externos: handlers HTTP, event processors, CLI entrypoints

---

## Fase 2 - Análisis de seguridad (prioridad máxima)

### 2.1 Detección de secretos y credenciales

Buscar patrones de:
- Claves API hardcodeadas (`api_key`, `apikey`, `API_KEY`, `secret`, `password`, `passwd`, `token`, `credentials`)
- AWS: `AKIA`, `AWS_ACCESS_KEY`, `AWS_SECRET`, `aws_access_key_id`
- Strings que parezcan tokens JWT, base64 de credenciales, connection strings con contraseña
- Contraseñas en comentarios o variables de entorno en código
- Archivos `.env` con valores reales (no placeholders)

**Severidad base:** CRÍTICO si está en código fuente o archivo versionable.

### 2.2 OWASP Top 10 (adaptar al stack)

| ID | Categoría | Qué revisar |
|----|-----------|-------------|
| A01 | Control de acceso roto | Verificaciones de autorización faltantes; acceso a recursos sin validar ownership |
| A02 | Fallos criptográficos | MD5/SHA1 para passwords; HTTP sin TLS; datos sensibles en logs; cifrado débil |
| A03 | Inyección | SQL injection (concatenación directa de strings en queries); XSS (outputs sin escapar); Command injection (subprocess con input del usuario); LDAP injection |
| A04 | Diseño inseguro | Lógica de negocio bypass; ausencia de rate limiting; flujos sin validación de estado |
| A05 | Misconfiguracion de seguridad | Debug mode activo; stack traces al usuario; CORS abierto (`*`); headers de seguridad faltantes |
| A06 | Componentes vulnerables | Dependencias con versiones pinned antiguas; imports de librerías abandonadas |
| A07 | Fallos de autenticación | Tokens sin expiración; passwords sin hashing (bcrypt/argon2); sesiones sin invalidación |
| A08 | Integridad de software | Deserialización de datos no confiables; eval/exec con input externo; pickle inseguro |
| A09 | Logging insuficiente | Eventos de seguridad sin log; passwords o tokens en logs; sin alertas ante fallos repetidos |
| A10 | SSRF | Fetch/requests a URLs controladas por el usuario sin validación de destino |

### 2.3 Desarrollo seguro - patrones específicos por lenguaje

Ver [reference/patterns.md](reference/patterns.md) para la lista completa por lenguaje: Python, JavaScript/TypeScript, PowerShell, Bash/Shell, Rust, SQL/IaC.

### 2.4 Compliance de ciberseguridad

Verificar alineación con:
- **CIS Controls v8:** Control 4 (config segura), Control 14 (protección datos), Control 16 (seguridad app)
- **NIST SP 800-53:** SI-10 (validación input), IA-5 (gestión credenciales), AU-3 (contenido de auditoría)
- **ISO 27001 A.14:** Requisitos de seguridad en sistemas de información
- **Normativa de protección de datos personales aplicable a la jurisdicción del proyecto:** datos personales en código o logs sin enmascarar, transferencia internacional sin declarar. Ejemplos según jurisdicción: GDPR (UE), Ley 21.719 (Chile), LGPD (Brasil), CCPA (California). Identificar cuál aplica según dónde opera el sistema, no asumir una por defecto.

---

## Fase 3 - Calidad y buenas prácticas

### 3.1 Manejo de errores
- Errores silenciados (`except: pass`, `catch {}` vacío)
- Stack traces expuestos al cliente
- Diferencia entre errores operacionales y de programación

### 3.2 Validación de entrada
- Inputs del usuario validados antes de usar
- Tipos de datos verificados
- Límites de tamaño (file uploads, string lengths)
- Sanitización vs escapado - usar el método correcto para cada contexto

### 3.3 Logging y observabilidad
- Logs sin datos personales o credenciales
- Nivel de log apropiado (no DEBUG en producción)
- Eventos de seguridad relevantes registrados (autenticación fallida, acceso denegado, cambios críticos)

### 3.4 Dependencias
- Versiones pinneadas (no rangos abiertos `>=x`)
- Dependencias innecesarias o abandonadas
- Licencias incompatibles con el uso previsto del proyecto

### 3.5 Código limpio
- Funciones > 80 líneas sin justificación
- Complejidad ciclomática alta (> 10 branches en una función)
- Variables globales mutables compartidas
- TODO/FIXME/HACK con issues de seguridad pendientes

---

## Fase 4 - Formato de salida

### Para cada hallazgo:

```
[ID-NNN] SEVERIDAD - Título conciso
Archivo: [ruta:línea]
Categoría: [OWASP A0X | Secreto | Crypto | Inyección | etc.]
Evidencia: [fragmento de código exacto - máximo 3 líneas]
Impacto: [qué puede ocurrir si se explota / si falla]
Recomendación: [corrección concreta con ejemplo de código si aplica]
Marco: [CIS Control X | NIST SI-X | OWASP A0X]
```

Severidades: **CRÍTICO** / **ALTO** / **MEDIO** / **BAJO** / **INFORMATIVO**

### Resumen final:

```
## Resumen de revisión - [nombre del proyecto/archivo]
Archivos analizados: N
Líneas de código: N

| Severidad  | Cantidad |
|------------|---------|
| CRÍTICO    |         |
| ALTO       |         |
| MEDIO      |         |
| BAJO       |         |
| INFORMATIVO|         |

Top 3 hallazgos que requieren acción inmediata:
1. [ID] - descripción - acción
2. [ID] - descripción - acción
3. [ID] - descripción - acción

Calificación general: [APROBADO | APROBADO CON CONDICIONES | RECHAZADO]
Criterio: RECHAZADO si hay hallazgos CRÍTICOS sin mitigación. APROBADO CON CONDICIONES si hay ALTO sin plan.
```

---

## Salida en archivo (si el argumento es un proyecto completo)

Guardar resultado en `docs/CODE_REVIEW_[FECHA].md` dentro del proyecto.

Si ya existe `docs/SEGURIDAD_HALLAZGOS.md`, comparar y señalar hallazgos nuevos vs conocidos.

---

**Diferencia siempre:** Verificado (evidencia en código) / Inferido (deducción por contexto) / Recomendado (best practice sin evidencia de desviación).

No inventes vulnerabilidades. Solo reporta lo que tiene evidencia directa en el código analizado.

---

## Troubleshooting

**El directorio tiene demasiados archivos para revisar en un solo contexto:** Priorizar por superficie de ataque: handlers de entrada de datos externos primero, luego archivos de configuración y credenciales, luego código de negocio. Dejar librerías de terceros al final (verificar solo versiones).

**El proyecto mezcla múltiples lenguajes (Python + JS + PowerShell):** Hacer una pasada completa por cada lenguaje usando los patrones de la sección 2.3. No mezclar hallazgos entre lenguajes en la misma revisión - separarlos por sección en el informe.

**El hallazgo es real pero ya está documentado en `SEGURIDAD_HALLAZGOS.md`:** Marcarlo como `Estado: Conocido (ref: ID-anterior)` y no repetir la recomendación. Si la recomendación cambió desde la última revisión, actualizarla con nota de cambio.
