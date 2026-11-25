# Política de seguridad

La seguridad de esta plataforma y de las personas que la usan es prioritaria.
Gracias por ayudarnos a mantenerla.

## Versiones con soporte

| Versión | Estado |
| --- | --- |
| `main` (desarrollo activo) | ✅ Soporte y correcciones |

## Cómo reportar una vulnerabilidad

**No abras un issue público** si el problema puede permitir acceso no
autorizado, exposición de datos o ejecución de código.

Envía el reporte de forma privada a **am25021820@iteshu.edu.mx** con:

- Título breve y tipo de problema (p. ej. "bypass de autenticación").
- Pasos concretos para reproducirlo.
- Versión/commit afectado y entorno (local, servidor de pruebas, producción).
- Impacto estimado y, si tienes una propuesta de corrección, un bosquejo.

Recibirás confirmación en un plazo razonable. Una vez corregido, publicaremos
el avance y te daremos crédito si así lo deseas.

## Buenas prácticas para colaboradores

- Nunca subas `.env`, contraseñas, tokens ni archivos de credenciales. Todos
  ellos están excluidos por `.gitignore`; usa `.env.example` como plantilla.
- Las contraseñas se almacenan con hashes derivados (PBKDF2), nunca en texto
  plano. No cambies este mecanismo sin revisión.
- Si encuentras un secreto expuesto en el historial de git, avisa de inmediato
  para rotarlo y limpiar el historial.
- Para despliegues, usa HTTPS y cambia los valores de ejemplo de
  `.env.example` antes de exponer el servicio.

## Alcance

Esta política aplica al código del backend, frontend, infraestructura y a los
scripts de despliegue incluidos en este repositorio.
