# Spec Delta

## Purpose

Define el catálogo de periféricos compatibles y los metadatos que describen sus
capacidades y límites, de forma que la plataforma pueda incorporar nuevos tipos de
periférico sin modificar la interfaz web.

## ADDED Requirements

### Requirement: Metadatos de periférico

El sistema SHALL describir cada periférico con tipo, canales y sentido de
operación, y SHALL incluir unidad, rango, resolución y frecuencia de adquisición
cuando la naturaleza del periférico lo requiera.

#### Scenario: Periférico incompleto

- **GIVEN** un administrador autenticado
- **WHEN** registra un periférico sin declarar su tipo
- **THEN** el sistema rechaza el registro indicando que el tipo es obligatorio

#### Scenario: Sensor con metadatos de medida

- **GIVEN** un administrador autenticado
- **WHEN** registra un periférico de tipo sensor
- **THEN** el sistema exige declarar unidad, rango y resolución

### Requirement: Tipos de periférico soportados

El sistema SHALL soportar al menos los tipos LED, pulsador, entrada digital,
salida digital, sensor, motor con PWM y pantalla.

#### Scenario: Catálogo de tipos base

- **GIVEN** el catálogo de periféricos inicializado
- **WHEN** se consulta la lista de tipos disponibles
- **THEN** incluye los siete tipos base soportados

### Requirement: Validación de valores contra metadatos

El sistema SHALL validar todo valor de operación contra el rango y la resolución
declarados por el periférico, y SHALL rechazar los valores que no cumplan ambas
condiciones.

#### Scenario: Valor fuera de rango

- **GIVEN** un periférico con rango declarado entre un mínimo y un máximo
- **WHEN** se propone un valor superior al máximo
- **THEN** el sistema rechaza el valor e informa el rango permitido

#### Scenario: Valor incompatible con la resolución

- **GIVEN** un periférico con resolución declarada
- **WHEN** se propone un valor que no es múltiplo de esa resolución
- **THEN** el sistema rechaza el valor indicando la resolución admitida

### Requirement: Extensibilidad sin cambios en la interfaz

El sistema SHALL permitir incorporar un tipo de periférico nuevo mediante
metadatos, y SHALL presentarlo en la interfaz web a partir de esa descripción sin
requerir modificaciones en el frontend.

#### Scenario: Nuevo tipo incorporado

- **GIVEN** un tipo de periférico que no existía en el catálogo
- **WHEN** el administrador lo registra con sus metadatos completos
- **THEN** la interfaz web lo muestra y permite operarlo según sus metadatos

### Requirement: Independencia entre catálogo y dispositivo

El sistema SHALL definir el catálogo con independencia de los dispositivos
concretos, de modo que una misma definición de periférico pueda asociarse a más de
un dispositivo sin duplicarse.

#### Scenario: Definición reutilizada

- **GIVEN** un periférico definido en el catálogo
- **WHEN** se asocia a un segundo dispositivo
- **THEN** el sistema reutiliza la misma definición sin crear una copia

### Requirement: Canales únicos por periférico

El sistema SHALL identificar cada canal de forma única dentro de un periférico y
SHALL rechazar la definición de canales duplicados.

#### Scenario: Canal repetido

- **GIVEN** un periférico con un canal ya declarado
- **WHEN** se intenta declarar otro canal con el mismo identificador
- **THEN** el sistema rechaza la definición

### Requirement: Sin frecuencia de adquisición impuesta

El sistema SHALL NOT imponer una frecuencia de adquisición por defecto, y SHALL
aceptar únicamente la frecuencia declarada explícitamente por el periférico cuando
corresponda.

#### Scenario: Periférico sin frecuencia declarada

- **GIVEN** un periférico cuya naturaleza no requiere frecuencia de adquisición
- **WHEN** se registra sin declarar frecuencia
- **THEN** el sistema acepta el registro sin asignar un valor por defecto

### Requirement: Administración del catálogo

El sistema SHALL restringir la creación y la modificación del catálogo al rol
administrador, y SHALL permitir la consulta en modo lectura a los roles docente y
estudiante.

#### Scenario: Docente intenta crear un tipo

- **GIVEN** un docente autenticado
- **WHEN** intenta registrar un tipo de periférico
- **THEN** el sistema rechaza la operación por falta de permisos
