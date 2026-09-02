# 12. Respuestas a la guía del taller

La página del taller en Canvas —*Taller ABP · Entrega 1: Ecosistema Interactivo Mobile*—
es una guía interactiva de trabajo, no un formulario que se entregue: no tiene botón de
envío porque la entrega es el enlace público de este repositorio.

Este documento responde cada campo de esa guía, para poder rellenarla de un vistazo y para
que el contenido quede versionado junto al proyecto.

---

## 1. Datos del proyecto

**Título formal del proyecto móvil**

> **EcoRuta — Aplicación móvil multiplataforma en Flutter para el reporte georreferenciado
> y la priorización automática de puntos críticos de residuos sólidos urbanos**

Delimita la solución (reporte y priorización de puntos críticos), nombra la tecnología del
cliente (Flutter, multiplataforma) e identifica al usuario final y su problema (el ciudadano
que hoy no tiene cómo reportar con evidencia y ubicación).

**Integrantes del equipo**

> Diego Gamba · Mariana Diez

**Metodología de desarrollo móvil**

> **Scrum adaptado al ciclo de vida móvil**, con sprints de dos semanas.

Cada sprint recorre diseño UX/UI, prototipado, sprint de código y pruebas en dispositivos,
y cierra con un incremento instalable, no con un documento. Se consideró **Mobile-D**, una
metodología específica para móviles, pero sus cinco fases resultan pesadas para un equipo
de una persona en ocho semanas. Detalle en
[1.4.1 Metodología](01-analisis-problema.md#141-metodología-de-desarrollo).

**Enlace al repositorio**

> https://github.com/DiegoGamba/ecoruta

No se elaboró prototipo en Figma: la guía admite repositorio **y/o** Figma, y el prototipo
navegable de este proyecto es la [demostración local ejecutable](../demo/README.md), que
además corre la lógica real del backend.

---

## 2. Planteamiento del problema

**Contexto y diagnóstico**

> En las ciudades colombianas, parte de los residuos sólidos no llega al sistema formal de
> recolección: se acumula en **puntos críticos** —esquinas, separadores, orillas de
> quebrada— que aparecen, se erradican y reaparecen a media cuadra. Los inventarios que
> levantan las entidades de aseo se desactualizan en semanas.
>
> Desde la experiencia del usuario, los canales de reporte disponibles hoy —línea
> telefónica, formulario web no adaptativo, redes sociales— comparten tres fallas: exigen
> **transcribir manualmente** una dirección en vez de capturar la ubicación, **no admiten
> evidencia** fotográfica asociada al punto, y **fallan en zonas de baja conectividad**,
> que es justamente donde se concentran los puntos críticos. El resultado es que el
> reporte se pierde o llega sin la información mínima para actuar, y obliga a una
> verificación en campo antes de programar cualquier intervención.

Ampliado en [1.1 Situación problema](01-analisis-problema.md).

**Pregunta problema**

> ¿De qué manera el diseño de una aplicación móvil multiplataforma en Flutter, con captura
> georreferenciada y sincronización *offline-first*, permite reducir a menos de 60 segundos
> el tiempo de reporte de un punto crítico de residuos sólidos y sostener una tasa de envío
> exitoso superior al 95 % en zonas con conectividad intermitente?

---

## 3. Objetivos SMART

**Objetivo general**

> Desarrollar una aplicación móvil multiplataforma en Flutter con sincronización
> *offline-first*, que permita a un ciudadano registrar un punto crítico de residuos
> sólidos —georreferenciado y con evidencia fotográfica— en menos de 60 segundos,
> sosteniendo una tasa de envío exitoso superior al 95 % en zonas con conectividad
> intermitente, antes del 10 de septiembre de 2026.

Estructura pedida: *verbo* (Desarrollar) + *tecnología móvil* (Flutter multiplataforma con
offline-first) + *métrica de usabilidad y rendimiento* (< 60 s de registro, > 95 % de envío)
+ *plazo* (10 de septiembre de 2026).

**Paso 1 · Investigación de usuario y prototipado UX/UI**

> Diseñar el flujo de captura y las tres pantallas de la aplicación —reporte, mapa de
> puntos críticos y navegación—, evaluando las heurísticas de usabilidad de Nielsen y
> verificando contraste accesible AA y objetivos táctiles de al menos 48 dp, en la semana 3.

**Paso 2 · Desarrollo del frontend móvil e integración con el backend**

> Programar los módulos del cliente en Flutter —captura con cámara y GPS, cola local de
> envíos y mapa— e integrar el consumo de la API REST desplegada sobre AWS con
> autenticación mediante Cognito, en la semana 6.

**Paso 3 · Pruebas en dispositivos reales y medición de rendimiento**

> Medir en dispositivos Android e iOS el tiempo de registro de un reporte, la tasa de envío
> exitoso en modo avión y con red intermitente, el consumo de batería durante una sesión de
> captura y la usabilidad percibida mediante el cuestionario SUS, en la semana 8.

---

## 4. Arquitectura y costos

**Enfoque tecnológico seleccionado**

> Multiplataforma / Cross-Platform — **Flutter 3.22**

Un solo código base para Android e iOS. La alternativa nativa (Kotlin + Swift) daba mejor
acceso a APIs del sistema, pero duplicaba el esfuerzo de un equipo de una persona sin
aportar nada que este producto necesite: cámara, GPS y almacenamiento seguro están
cubiertos por complementos maduros.

**Simulador de costos — primer año**

| Concepto / servicio móvil | Proveedor | Frecuencia | Costo USD | Subtotal |
|---|---|---|---|---|
| Google Play Console | Google | Pago único | 25,00 | 25,00 |
| Apple Developer Program | Apple | Suscripción anual | 99,00 | 99,00 |
| Backend serverless (Lambda, API Gateway, DynamoDB, S3) | AWS | Mensual | 0,24 | 2,88 |
| Clasificación de imágenes (Rekognition) | AWS | Mensual | 3,00 | 36,00 |
| Notificaciones push (SNS) | AWS | Mensual | 0,10 | 1,20 |
| Observabilidad (CloudWatch, EventBridge) | AWS | Mensual | 0,50 | 6,00 |
| Mapas (OpenStreetMap) | OSMF | — | 0,00 | 0,00 |

> **Costo total estimado del proyecto móvil: 170,08 USD**
> **Presupuesto asignado: 300 USD**
> **Eficiencia de presupuesto: 43,3 % libre**

Años siguientes: **145,08 USD** (desaparece el pago único de Play).
Solo Android: **71,08 USD** el primer año.

Un despliegue de demostración cabe en la capa gratuita de AWS, así que validar la solución
no consume presupuesto. Desglose completo en
[2.7 Costo de operación](02-arquitectura.md#27-costo-de-operación).

**Estrategia de seguridad en el dispositivo**

> Los tokens de sesión los custodia Amplify en el **almacenamiento seguro del sistema
> operativo**: Keychain en iOS y EncryptedSharedPreferences respaldado por el Android
> Keystore. La aplicación nunca los escribe por su cuenta.
>
> La app es un **cliente público sin secreto** —un secreto embebido en un APK distribuido
> no es un secreto— y autentica con **SRP**, de modo que la contraseña nunca viaja. Cada
> petición lleva un **JWT sobre TLS 1.2+**, con token de acceso de 60 minutos y revocación
> habilitada. Quien valida la firma es API Gateway, no el cliente.
>
> La cola de reportes sin conexión guarda únicamente el contenido del reporte, nunca
> credenciales. La autorización por rol se lee del claim firmado del token, no de un campo
> que la aplicación pueda alterar.
>
> Pendiente reconocido: no hay *certificate pinning* ni detección de dispositivo rooteado.

Detalle en [4.3.1 Seguridad en el dispositivo](04-seguridad.md#431-seguridad-en-el-dispositivo).

---

Anterior: [Guion de video](11-guion-video.md)
