# Claude Code Skills Toolkit

Colección curada de [Skills de Claude Code](https://docs.claude.com/en/docs/claude-code/skills)
de uso general: planificación, debugging, revisión de seguridad, análisis de
documentos y gestión de contexto de conversación. Cada skill es una carpeta
autocontenida con su propio `SKILL.md` (y, cuando aplica, scripts de soporte),
lista para copiar directamente a tu directorio de skills de Claude Code.

Todas las skills son de propósito general, sin dependencias de ningún contexto,
dominio, credencial ni dato institucional específico.

## Qué es una Skill de Claude Code

Una skill es un archivo `SKILL.md` con frontmatter YAML (`name`, `description`,
`model`, `allowed-tools`) más instrucciones en Markdown. Claude Code la carga
automáticamente cuando el `description` calza con lo que el usuario pide, o el
usuario la invoca explícitamente con `/nombre-skill`. El campo `description`
debe listar triggers explícitos (frases que el usuario diría) para que la
detección automática funcione bien.

## Catálogo

| Skill | Modelo sugerido | Qué hace | Cuándo usarla |
|---|---|---|---|
| [`plan`](plan/) | sonnet | Descompone una tarea de implementación en pasos atómicos verificables antes de escribir código. Gate de diseño. | Antes de implementar algo con más de 3 pasos o decisiones de arquitectura. |
| [`brainstorm`](brainstorm/) | sonnet | Explora 2-4 alternativas de diseño con tabla comparativa y recomendación justificada. Incluye plantilla de ADR. | Cuando hay más de un enfoque válido y hay que decidir con criterio, no por default. |
| [`debug`](debug/) | sonnet | Depuración sistemática en 4 fases: reproducir, analizar, generar hipótesis ordenadas, corregir y verificar. | Cuando algo falla y hay presión por saltar directo a un fix sin entender la causa. |
| [`review`](review/) | sonnet | Code review de seguridad y calidad: OWASP Top 10, secretos hardcodeados, compliance CIS/NIST/ISO 27001, patrones inseguros por lenguaje. | Antes de mergear o entregar código, o para una revisión puntual de un archivo/proyecto. |
| [`auditar`](auditar/) | sonnet | Auditoría de seguridad de un proyecto o componente completo (no solo código): credenciales, control de acceso, red, observabilidad. Entrega hallazgos con severidad. | Auditorías de seguridad más amplias que un code review, incluyendo infraestructura. |
| [`verificar`](verificar/) | haiku | Gate obligatorio antes de declarar cualquier tarea "completa": exige ejecutar un comando de verificación real y adjuntar evidencia. | Al cerrar cualquier tarea, para evitar reportar como listo algo no probado. |
| [`pdf`](pdf/) | haiku | Convierte PDF/DOCX/XLSX/PPTX/HTML/CSV a Markdown para análisis por texto en vez de LLM vision (70-90% menos tokens). Incluye script wrapper. | Cada vez que haya que analizar un documento que no sea código fuente. |
| [`transcribir`](transcribir/) | haiku | Transcribe audio/video a texto con `openai-whisper` local (con soporte GPU), descargando primero con `yt-dlp` si el input es una URL. Incluye script wrapper. | Reuniones, capacitaciones, videos que hay que convertir a texto. |
| [`contexto`](contexto/) | haiku | Guía sobre los 4 controles de contexto de conversación de Claude Code (Escape, doble Escape, `/compact`, `/clear`) y cuál usar según la situación. | Conversaciones largas, ruido acumulado, o necesidad de retroceder a un punto anterior. |

## Instalación

Cada skill es independiente. Copia la carpeta completa de la skill que quieras
usar a tu directorio de skills de Claude Code:

```bash
# Windows
cp -r nombre-skill/ "$USERPROFILE/.claude/skills/nombre-skill/"

# macOS / Linux
cp -r nombre-skill/ "$HOME/.claude/skills/nombre-skill/"
```

O para instalar toda la colección:

```bash
cp -r */ "$HOME/.claude/skills/"
```

Claude Code detecta automáticamente cualquier carpeta con un `SKILL.md` válido
en ese directorio. No requiere reiniciar la sesión en la mayoría de los casos,
pero si la skill no aparece, reinicia Claude Code.

## Skills con script wrapper (`pdf`, `transcribir`)

Estas dos skills incluyen un script Python en su carpeta `scripts/`, con sus
propios requisitos de dependencias (ver la sección "Requisitos" dentro de cada
`SKILL.md`). El resto de las skills son puramente instrucciones para el modelo
y no requieren instalar nada adicional.

## Convenciones de esta colección

- **`allowed-tools` mínimo:** cada skill declara solo las herramientas que
  realmente necesita (principio de mínimo privilegio aplicado a agentes de IA).
- **`model` sugerido por costo/complejidad:** las skills mecánicas (`verificar`,
  `pdf`, `transcribir`, `contexto`) están marcadas para modelos más económicos;
  las que requieren razonamiento (`plan`, `brainstorm`, `debug`, `review`,
  `auditar`) para modelos de mayor capacidad. Ajusta según los modelos
  disponibles en tu configuración.
- **Sección `Troubleshooting` obligatoria:** cada `SKILL.md` termina con casos
  reales de fallo y cómo resolverlos, no solo el camino feliz.
- **Distinción Verificado / Inferido / Recomendado:** las skills de análisis
  (`debug`, `review`, `auditar`, `verificar`) fuerzan esta distinción explícita
  para evitar que el modelo presente una suposición como un hecho comprobado.

## Skills relacionadas, en repos separados

Esta colección solo incluye skills de propósito general (aplicables a
cualquier tipo de proyecto). Skills de dominio específico viven en repos
propios para no diluir el catálogo:

- [`claude-code-security-skills`](https://github.com/matias00allende/claude-code-security-skills) -
  colección de skills de integración con herramientas de seguridad (SSL Labs,
  y las que se sumen a futuro).
- [`premortem-skill`](https://github.com/matias00allende/premortem-skill) -
  skill única de análisis de fracaso anticipado (premortem), publicada aparte
  por ser una técnica de análisis estratégico, no una skill de flujo de
  desarrollo general.

## Licencia

MIT. Ver [LICENSE](LICENSE).
