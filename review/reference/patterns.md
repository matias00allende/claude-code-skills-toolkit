# Patrones de seguridad por lenguaje

## Python

- `subprocess.shell=True` con input del usuario - riesgo de command injection
- `eval()`, `exec()`, `pickle.loads()` con datos externos - ejecución arbitraria
- `assert` para validaciones de seguridad (desactivado con -O en producción)
- SQLAlchemy: raw SQL con f-strings en lugar de parámetros - SQLi
- Requests: `verify=False` deshabilita verificación TLS

## JavaScript / TypeScript

- `innerHTML` con datos del usuario - XSS
- `dangerouslySetInnerHTML` (React) - XSS
- `document.write()` con input externo - XSS
- `JSON.parse()` sin try/catch en inputs de red - crash no controlado
- `require(userControlledPath)` - path traversal
- npm packages: versiones pinned antiguas con CVEs conocidos (reportar versiones)

## PowerShell

- `Invoke-Expression` con strings dinámicas - command injection
- `-ExecutionPolicy Bypass` innecesario - debilita postura de seguridad
- Credenciales en `ConvertTo-SecureString` con strings hardcodeados - secreto expuesto
- `[System.Net.WebClient]` con URL `http://` o sin versión mínima de TLS configurada - revisar el esquema de la URL: HTTP viaja en claro

## Bash / Shell

- Variables sin comillas en comandos (`rm $var` vs `rm "$var"`) - word splitting / inyección
- `eval` con input del usuario - command injection
- Permisos de archivos (chmod 777, scripts world-writable)
- Rutas sin comillas en scripts con espacios posibles - comportamiento indefinido

## Rust

- `unsafe {}` blocks sin comentario explicativo del invariante de seguridad
- `unwrap()` / `expect()` en paths críticos - panic en producción
- Dependencias con `*` en versiones - builds no reproducibles

## SQL / IaC

- Queries con interpolación directa de variables - SQLi
- CloudFormation/Terraform: recursos sin política de eliminación explícita, sin tags, sin cifrado declarado
- IAM: `"*"` en actions o resources sin justificación documentada en comentario
