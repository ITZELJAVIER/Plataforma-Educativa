# peripheral-catalog

Catálogo descriptivo de periféricos. Las definiciones son independientes de los
dispositivos concretos: una misma definición puede reutilizarse sin duplicarse.
Las rutas están versionadas bajo `/api/v1` y requieren una sesión válida enviada
como `Authorization: Bearer <token>`.

## Tipos base

El catálogo inicial incluye exactamente estos siete tipos:

- `LED`
- `pulsador`
- `entrada digital`
- `salida digital`
- `sensor`
- `motor con PWM`
- `pantalla`

Se pueden incorporar tipos nuevos registrando sus metadatos; el tipo no está
limitado a esta lista.

## Modelo de metadatos

| Campo | Descripción |
| --- | --- |
| `tipo` | Identificador del tipo de periférico; obligatorio. |
| `canales` | Lista de identificadores de canal; deben ser únicos dentro del periférico. |
| `sentido` | Sentido de operación declarado; obligatorio en una definición registrada. |
| `unidad` | Unidad de medida, cuando corresponda. |
| `rango` | Límites `minimo` y `maximo`, cuando corresponda. |
| `resolucion` | Paso o resolución admitida, cuando corresponda. |
| `frecuencia` | Frecuencia de adquisición declarada explícitamente; nunca se asigna por defecto. |

Un `sensor` requiere `unidad`, `rango` y `resolución`. La validación de un valor
comprueba el rango y la resolución declarados; si no se declaran, no se impone
ningún límite adicional.

## Rutas

| Método y ruta | Uso | Acceso |
| --- | --- | --- |
| `GET /api/v1/peripherals/types` | Lista los tipos del catálogo | Administrador, docente y estudiante |
| `GET /api/v1/peripherals/types/{tipo}` | Consulta un tipo por su identificador | Administrador, docente y estudiante |
| `POST /api/v1/peripherals/types` | Registra un tipo con sus metadatos | Administrador |
| `PATCH /api/v1/peripherals/types/{tipo}` | Modifica los metadatos de un tipo | Administrador |
| `POST /api/v1/peripherals/types/{tipo}/validate-value` | Valida un valor contra rango y resolución | Administrador, docente y estudiante |

Las operaciones no explícitamente permitidas se deniegan. Una petición sin
sesión válida se rechaza con error de autenticación.

## Escenarios cubiertos

- Consulta del catálogo con los siete tipos base.
- Rechazo de un registro sin tipo y de un sensor sin unidad, rango o resolución.
- Rechazo de canales duplicados dentro de un periférico.
- Validación de valores fuera de rango y valores no compatibles con la resolución.
- Registro de tipos nuevos mediante metadatos, sin cambiar el frontend.
- Persistencia a través de repositorios PostgreSQL e implementaciones en memoria.
