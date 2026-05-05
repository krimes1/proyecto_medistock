# AGENTS.md

## Autoridad Principal del Proyecto

Toda decisión de arquitectura, implementación y diseño debe alinearse con este documento y con los archivos fuente:

* /docs/Evaluación Parcial 2 Caso 1.docx
* /docs/contexto medistock.txt

Si existe conflicto entre decisiones técnicas y requisitos académicos, priorizar SIEMPRE el cumplimiento de la evaluación.

---

## Objetivo del Proyecto

Desarrollar la fase de construcción e integración de la plataforma MEDISTOCK modernizando su arquitectura mediante una solución web multicapa con integración de APIs/Webservices.

---

## Requisitos Arquitectónicos Obligatorios

* Utilizar arquitectura por capas.
* Utilizar lenguaje backend apropiado para APIs/Webservices.
* Integración obligatoria con base de datos propia.
* Aplicar buenas prácticas y patrones de diseño.
* Diseñar solución robusta, intuitiva y segura.

---

## Requisitos Funcionales Principales

### 1. API Propia Obligatoria

Construir API REST/Webservice que exponga:

* Catálogo de productos
* Precios
* Stock actualizado en tiempo real

Endpoint mínimo esperado:

* GET /api/v1/productos/{codigo_producto}

Propósito:
Permitir que ERPs de clínicas consuman información automáticamente.

---

### 2. Integraciones Externas Obligatorias

#### API de Pagos

Integrar pasarela de pagos:

* Webpay Plus / MercadoPago / equivalente autorizado

Uso:
Procesar compras B2C de pacientes particulares.

#### API de Logística

Integrar API de logística/tracking:

* Shippo / Chilexpress / equivalente autorizado

Uso:

* Generar número de seguimiento
* Permitir trazabilidad de pedidos

---

## Roles y Vistas Obligatorias del Sistema

### Cliente (Institución/Paciente)

* Ver catálogo en tiempo real
* Comprar mediante carrito
* Elegir despacho express/normal
* Seleccionar método de pago

### Ejecutivo de Cuentas

* Revisar stock de múltiples bodegas
* Aprobar compras institucionales
* Derivar órdenes a logística

### Operador Logístico

* Ver órdenes priorizadas por urgencia médica
* Confirmar preparación
* Despachar pedidos

### Analista de Finanzas

* Confirmar transferencias
* Auditar pagos

### Administrador

* Gestionar reportes de venta
* Gestionar alianzas estratégicas

---

## Contexto de Negocio a Respetar

* Sector salud con alta criticidad operacional
* Inventario debe ser estricto y en tiempo real
* Priorizar rapidez de respuesta
* Considerar trazabilidad y urgencia médica
* MEDISTOCK opera múltiples bodegas/sucursales

---

## Criterios de Evaluación que Deben Maximizarse

### Arquitectura / Componentes

La solución debe demostrar separación clara de componentes reutilizables y lógica de negocio bien estructurada.

### Implementación Técnica

Objetivo mínimo de excelencia:

* Implementar 8+ componentes funcionales integrados con BD

### Integraciones

Objetivo mínimo de excelencia:

* Implementar 3 APIs/Webservices integradas:

  1. API Propia MEDISTOCK
  2. API de Pagos
  3. API de Logística

---

## Restricciones

* No implementar features fuera del alcance académico sin justificación.
* Toda funcionalidad debe mapearse a un criterio evaluado.
* Priorizar cumplimiento de rúbrica sobre complejidad innecesaria.

---

## Instrucción Permanente para el Agente

Antes de implementar cualquier cambio:

1. Verificar alineación con este documento.
2. Justificar técnicamente la decisión según requisitos de evaluación.
3. Priorizar soluciones que maximicen puntaje académico.
4. Si una propuesta no aporta a la rúbrica, evitar implementarla.

---

## Comando de Autoevaluación Obligatorio

Después de cada implementación importante, revisar:

* Qué criterio de la rúbrica cumple
* Qué componente arquitectónico representa
* Qué integración/API utiliza
* Qué requisito funcional satisface
