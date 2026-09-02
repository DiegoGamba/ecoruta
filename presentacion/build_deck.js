/**
 * Genera la presentación del proyecto EcoRuta.
 *   node build_deck.js
 */
const pptxgen = require("pptxgenjs");

const C = {
  forest: "2C5F2D",
  deep: "1A3A1B",
  moss: "97BC62",
  cream: "F5F5F0",
  white: "FFFFFF",
  ink: "1C2620",
  muted: "6B7A70",
  alert: "B85042",
  line: "DCE3DA",
};

const HEAD = "Cambria";
const BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Diego Gamba, Mariana Diez";
pres.title = "EcoRuta";

const W = 13.3;
const M = 0.7;
const CW = W - M * 2;

/* ---------- helpers ---------- */

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: C.deep };
  return s;
}

function lightSlide(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  if (kicker) {
    s.addText(kicker.toUpperCase(), {
      x: M, y: 0.42, w: CW, h: 0.25,
      fontFace: BODY, fontSize: 11, bold: true, color: C.moss,
      charSpacing: 2, isTextBox: true, margin: 0,
    });
  }
  s.addText(title, {
    x: M, y: 0.68, w: CW, h: 0.62,
    fontFace: HEAD, fontSize: 34, bold: true, color: C.forest,
    isTextBox: true, margin: 0,
  });
  return s;
}

function card(s, { x, y, w, h, fill }) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: fill || C.cream },
    line: { color: C.line, width: 1 },
  });
}

function iconCircle(s, { x, y, d, glyph, bg, fg }) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: d, h: d, fill: { color: bg || C.forest }, line: { color: bg || C.forest },
  });
  s.addText(glyph, {
    x, y, w: d, h: d, align: "center", valign: "middle",
    fontFace: BODY, fontSize: 15, bold: true, color: fg || C.white,
    isTextBox: true, margin: 0,
  });
}

function statCard(s, { x, y, w, value, label, note, color }) {
  card(s, { x, y, w, h: 1.75 });
  s.addText(value, {
    x: x + 0.25, y: y + 0.18, w: w - 0.5, h: 0.75,
    fontFace: HEAD, fontSize: 40, bold: true, color: color || C.forest,
    isTextBox: true, margin: 0,
  });
  s.addText(label, {
    x: x + 0.25, y: y + 0.95, w: w - 0.5, h: 0.3,
    fontFace: BODY, fontSize: 13, bold: true, color: C.ink,
    isTextBox: true, margin: 0,
  });
  s.addText(note, {
    x: x + 0.25, y: y + 1.25, w: w - 0.5, h: 0.42,
    fontFace: BODY, fontSize: 10.5, color: C.muted,
    isTextBox: true, margin: 0,
  });
}

function footer(s, n) {
  s.addText("EcoRuta · Taller ABP · Diseño de Aplicaciones Móviles", {
    x: M, y: 6.95, w: 7, h: 0.28,
    fontFace: BODY, fontSize: 9, color: C.muted, isTextBox: true, margin: 0,
  });
  s.addText(String(n), {
    x: W - M - 0.7, y: 6.95, w: 0.7, h: 0.28, align: "right",
    fontFace: BODY, fontSize: 9, color: C.muted, isTextBox: true, margin: 0,
  });
}

/* ---------- 1 · portada ---------- */
{
  const s = darkSlide();
  s.addShape(pres.ShapeType.ellipse, {
    x: 9.4, y: -1.6, w: 5.6, h: 5.6,
    fill: { color: C.forest, transparency: 45 }, line: { color: C.forest, transparency: 100 },
  });
  s.addShape(pres.ShapeType.ellipse, {
    x: 11.0, y: 4.2, w: 3.4, h: 3.4,
    fill: { color: C.moss, transparency: 78 }, line: { color: C.moss, transparency: 100 },
  });

  s.addText("TALLER ABP · ENTREGA 1", {
    x: M, y: 1.55, w: 8, h: 0.3,
    fontFace: BODY, fontSize: 12, bold: true, color: C.moss, charSpacing: 3,
    isTextBox: true, margin: 0,
  });
  s.addText("EcoRuta", {
    x: M, y: 1.95, w: 8.6, h: 1.35,
    fontFace: HEAD, fontSize: 66, bold: true, color: C.white,
    isTextBox: true, margin: 0,
  });
  s.addText(
    "Reporte ciudadano y priorización automática\nde puntos críticos de residuos sólidos",
    {
      x: M, y: 3.32, w: 8.6, h: 1.0,
      fontFace: HEAD, fontSize: 21, italic: true, color: C.moss,
      lineSpacing: 30, isTextBox: true, margin: 0,
    },
  );
  s.addText(
    "App móvil Flutter  ·  Arquitectura serverless en AWS  ·  Infraestructura como código",
    {
      x: M, y: 4.55, w: 8.8, h: 0.32,
      fontFace: BODY, fontSize: 13, color: C.cream, isTextBox: true, margin: 0,
    },
  );
  s.addShape(pres.ShapeType.rect, {
    x: M, y: 5.35, w: 2.2, h: 0.03, fill: { color: C.moss }, line: { color: C.moss },
  });
  s.addText("Diego Gamba  ·  Mariana Diez", {
    x: M, y: 5.6, w: 8, h: 0.32,
    fontFace: BODY, fontSize: 15, bold: true, color: C.white, isTextBox: true, margin: 0,
  });
  s.addText("Diseño de Aplicaciones Móviles · Facultad de Ingeniería y Ciencias Ambientales", {
    x: M, y: 5.95, w: 9, h: 0.32,
    fontFace: BODY, fontSize: 11, color: C.moss, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Presento EcoRuta: una solución móvil respaldada por una arquitectura serverless en AWS " +
    "para capturar, clasificar y priorizar puntos críticos de residuos sólidos a partir del reporte ciudadano.",
  );
}

/* ---------- 2 · el problema ---------- */
{
  const s = lightSlide("Los puntos críticos aparecen, se erradican y reaparecen", "El problema");

  s.addText(
    "Parte de los residuos sólidos urbanos no llega al sistema formal de recolección: se acumula " +
    "en esquinas, separadores y orillas de quebrada. El fenómeno tiene tres rasgos que lo hacen " +
    "difícil de atender con los instrumentos actuales.",
    {
      x: M, y: 1.5, w: CW, h: 0.7,
      fontFace: BODY, fontSize: 14, color: C.ink, lineSpacing: 21, isTextBox: true, margin: 0,
    },
  );

  const items = [
    ["Es dinámico", "Un punto se erradica y reaparece a media cuadra. Los inventarios manuales quedan obsoletos en semanas."],
    ["Es local", "Quien mejor lo detecta es el vecino que pasa a diario, no el operador que recorre la macro-ruta."],
    ["No fluye la información", "Los canales actuales producen texto libre sin coordenadas ni evidencia: obligan a verificar en campo."],
  ];
  const cw = (CW - 0.6) / 3;
  items.forEach(([t, d], i) => {
    const x = M + i * (cw + 0.3);
    card(s, { x, y: 2.45, w: cw, h: 2.25 });
    iconCircle(s, { x: x + 0.3, y: 2.72, d: 0.5, glyph: String(i + 1) });
    s.addText(t, {
      x: x + 0.3, y: 3.36, w: cw - 0.6, h: 0.32,
      fontFace: HEAD, fontSize: 16, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: x + 0.3, y: 3.72, w: cw - 0.6, h: 0.85,
      fontFace: BODY, fontSize: 12, color: C.ink, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  card(s, { x: M, y: 5.0, w: CW, h: 1.05, fill: C.deep });
  s.addText(
    "Consecuencia operativa: recolección reactiva y no optimizada, riesgo sanitario por vectores, " +
    "obstrucción de sumideros y deterioro del espacio público.",
    {
      x: M + 0.4, y: 5.22, w: CW - 0.8, h: 0.62,
      fontFace: BODY, fontSize: 13.5, italic: true, color: C.cream,
      lineSpacing: 20, isTextBox: true, margin: 0,
    },
  );
  footer(s, 2);
  s.addNotes(
    "PROBLEMA (90 s). Empiece con un caso concreto: 'todos conocemos una esquina del barrio donde aparece basura; la recogen y a la semana vuelve media cuadra mas alla'. Luego los tres rasgos sin leerlos: es dinamico (el inventario queda obsoleto en semanas), es local (lo detecta el vecino, no el operador de la macro-ruta), la informacion no fluye (texto libre sin coordenadas obliga a verificar en campo). Cierre con la consecuencia operativa.",
  );
}

/* ---------- 3 · pregunta y objetivos ---------- */
{
  const s = lightSlide("Qué nos preguntamos y qué nos propusimos", "Delimitación");

  card(s, { x: M, y: 1.5, w: CW, h: 1.15, fill: C.cream });
  s.addText("PREGUNTA QUE GUÍA EL PROYECTO", {
    x: M + 0.4, y: 1.68, w: CW - 0.8, h: 0.25,
    fontFace: BODY, fontSize: 10, bold: true, color: C.moss, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s.addText(
    "¿Puede un flujo de reporte ciudadano georreferenciado, con evidencia fotográfica y agrupamiento " +
    "espacial automático, producir un inventario de puntos críticos más actualizado y accionable que " +
    "el levantamiento manual periódico?",
    {
      x: M + 0.4, y: 1.95, w: CW - 0.8, h: 0.6,
      fontFace: HEAD, fontSize: 15, italic: true, color: C.forest,
      lineSpacing: 22, isTextBox: true, margin: 0,
    },
  );

  s.addText("Objetivos específicos", {
    x: M, y: 2.95, w: 6, h: 0.35,
    fontFace: HEAD, fontSize: 18, bold: true, color: C.forest, isTextBox: true, margin: 0,
  });

  const objs = [
    "Capturar un reporte georreferenciado con evidencia en menos de 60 segundos, incluso sin conectividad.",
    "Convertir reportes dispersos en puntos críticos mediante agrupamiento espacial y priorizarlos por severidad.",
    "Sugerir el tipo de residuo desde la fotografía para estandarizar el dato.",
    "Notificar de inmediato ante residuos peligrosos o severidad alta.",
    "Exponer indicadores operativos para el seguimiento de la entidad.",
  ];
  objs.forEach((t, i) => {
    const y = 3.42 + i * 0.6;
    iconCircle(s, { x: M, y: y + 0.02, d: 0.34, glyph: String(i + 1), bg: C.moss, fg: C.deep });
    s.addText(t, {
      x: M + 0.52, y, w: 6.7, h: 0.5,
      fontFace: BODY, fontSize: 12.5, color: C.ink, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });

  card(s, { x: 7.9, y: 2.95, w: CW - 7.2, h: 3.3 });
  s.addText("ALCANCE DE LA ENTREGA", {
    x: 8.2, y: 3.18, w: 4.5, h: 0.25,
    fontFace: BODY, fontSize: 10, bold: true, color: C.moss, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  const scope = [
    ["Actor primario", "Ciudadano residente"],
    ["Actor secundario", "Operador de aseo"],
    ["Territorio piloto", "Una localidad urbana"],
    ["Flujo cubierto", "Reporte → clasificación → agrupamiento → priorización → cierre"],
    ["Fuera de alcance", "Facturación, despacho de vehículos, comparendo ambiental"],
  ];
  scope.forEach(([k, v], i) => {
    const y = 3.55 + i * 0.55;
    s.addText(k, {
      x: 8.2, y, w: 4.4, h: 0.24,
      fontFace: BODY, fontSize: 10.5, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(v, {
      x: 8.2, y: y + 0.22, w: 4.4, h: 0.3,
      fontFace: BODY, fontSize: 11, color: C.ink, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });
  footer(s, 3);
  s.addNotes(
    "DELIMITACION (60 s). Lea la pregunta de investigacion completa y en voz alta: es lo que convierte el trabajo en algo evaluable y es lo que el jurado de semillero espera oir. De los cinco objetivos mencione solo el 1 y el 2; el resto esta en pantalla.",
  );
}

/* ---------- 4 · la solución ---------- */
{
  const s = lightSlide("De una foto en la calle a una cuadrilla en ruta", "La solución");

  s.addText(
    "El ciudadano toma una foto, la app resuelve la ubicación y envía el reporte en menos de un minuto. " +
    "En la nube el reporte se clasifica, se agrupa con sus vecinos y se prioriza.",
    {
      x: M, y: 1.5, w: CW, h: 0.5,
      fontFace: BODY, fontSize: 14, color: C.ink, lineSpacing: 20, isTextBox: true, margin: 0,
    },
  );

  const steps = [
    ["Reporta", "Foto, GPS y categoría\nen menos de 60 s"],
    ["Clasifica", "Visión por computador\nsugiere el tipo de residuo"],
    ["Agrupa", "Reportes cercanos forman\nun punto crítico"],
    ["Prioriza", "Severidad acumulada\nordena la intervención"],
    ["Interviene", "El operador cierra\nel ciclo"],
  ];
  const sw = (CW - 4 * 0.28) / 5;
  steps.forEach(([t, d], i) => {
    const x = M + i * (sw + 0.28);
    const last = i === steps.length - 1;
    card(s, { x, y: 2.3, w: sw, h: 2.25, fill: last ? C.deep : C.cream });
    iconCircle(s, {
      x: x + sw / 2 - 0.25, y: 2.55, d: 0.5, glyph: String(i + 1),
      bg: last ? C.moss : C.forest, fg: last ? C.deep : C.white,
    });
    s.addText(t, {
      x: x + 0.15, y: 3.18, w: sw - 0.3, h: 0.32, align: "center",
      fontFace: HEAD, fontSize: 15, bold: true, color: last ? C.white : C.forest,
      isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: x + 0.15, y: 3.55, w: sw - 0.3, h: 0.85, align: "center",
      fontFace: BODY, fontSize: 11, color: last ? C.cream : C.ink,
      lineSpacing: 15, isTextBox: true, margin: 0,
    });
    if (!last) {
      s.addText("›", {
        x: x + sw + 0.02, y: 3.05, w: 0.24, h: 0.4, align: "center",
        fontFace: BODY, fontSize: 22, bold: true, color: C.moss, isTextBox: true, margin: 0,
      });
    }
  });

  statCard(s, { x: M, y: 4.85, w: (CW - 0.6) / 3, value: "< 60 s", label: "Para emitir un reporte", note: "Foto, ubicación y categoría, con cola local si no hay señal" });
  statCard(s, { x: M + (CW - 0.6) / 3 + 0.3, y: 4.85, w: (CW - 0.6) / 3, value: "120 m", label: "Radio de agrupamiento", note: "Configurable entre 30 y 1000 m según el territorio" });
  statCard(s, { x: M + 2 * ((CW - 0.6) / 3 + 0.3), y: 4.85, w: (CW - 0.6) / 3, value: "3", label: "Reportes mínimos", note: "Umbral para que un grupo se considere punto crítico" });
  footer(s, 4);
  s.addNotes(
    "SOLUCION (60 s). Recorra los cinco pasos, una frase cada uno. AQUI VA LA DEMOSTRACION EN VIVO: tome una foto con el celular, envie el reporte, muestre el mapa. Remate: 'lo que acaban de ver son treinta segundos; si reportar cuesta mas que ignorar el problema, nadie reporta'.",
  );
}

/* ---------- 5 · arquitectura ---------- */
{
  const s = lightSlide("Arquitectura serverless en AWS", "Diseño técnico");

  const bands = [
    { y: 1.55, h: 0.95, label: "CLIENTE", items: [["App Flutter", "Android · iOS"]] },
    { y: 2.62, h: 0.95, label: "BORDE", items: [["Cognito", "auth + grupos"], ["API Gateway HTTP", "JWT · throttling"]] },
    { y: 3.69, h: 0.95, label: "CÓMPUTO", items: [["Lambda × 8", "Python 3.12 · arm64"], ["Un rol IAM por función", "mínimo privilegio"]] },
    { y: 4.76, h: 0.95, label: "DATOS", items: [["DynamoDB", "single-table · 3 GSI"], ["S3 + KMS", "evidencias cifradas"]] },
    { y: 5.83, h: 0.95, label: "ASÍNCRONO", items: [["EventBridge + SNS", "alertas prioritarias"], ["Rekognition", "clasificación asistida"], ["SQS DLQ", "nada se pierde"]] },
  ];

  bands.forEach((b) => {
    s.addText(b.label, {
      x: M, y: b.y + 0.3, w: 1.35, h: 0.3,
      fontFace: BODY, fontSize: 10, bold: true, color: C.moss, charSpacing: 1.5,
      isTextBox: true, margin: 0,
    });
    const areaX = M + 1.45;
    const areaW = CW - 1.45;
    const n = b.items.length;
    const iw = (areaW - (n - 1) * 0.25) / n;
    b.items.forEach(([t, d], i) => {
      const x = areaX + i * (iw + 0.25);
      card(s, { x, y: b.y, w: iw, h: b.h });
      s.addText(t, {
        x: x + 0.25, y: b.y + 0.16, w: iw - 0.5, h: 0.3,
        fontFace: HEAD, fontSize: 14, bold: true, color: C.forest, isTextBox: true, margin: 0,
      });
      s.addText(d, {
        x: x + 0.25, y: b.y + 0.5, w: iw - 0.5, h: 0.3,
        fontFace: BODY, fontSize: 11, color: C.muted, isTextBox: true, margin: 0,
      });
    });
  });
  footer(s, 5);
  s.addNotes(
    "ARQUITECTURA (2 min). La diapositiva mas importante para la nota. No enumere servicios: explique decisiones. Borde: la validacion del token la hace API Gateway, no mi codigo. Computo: ocho funciones para tener minimo privilegio real. Datos: una sola tabla y ninguna operacion usa Scan. La flecha gruesa: la foto no atraviesa el computo, la app sube directo a S3 con URL prefirmada, lo que evita el limite de 6 MB de Lambda.",
  );
}

/* ---------- 6 · justificación ---------- */
{
  const s = lightSlide("Cada servicio responde a un rasgo del problema", "Justificación tecnológica");

  const rows = [
    ["Demanda muy irregular: picos tras lluvias, casi nula de madrugada", "Lambda + API Gateway", "Escala a cero; sin capacidad ociosa"],
    ["Consultas siempre por zona o por estado, nunca analíticas", "DynamoDB single-table", "Todo es Query por clave; nunca Scan"],
    ["La evidencia pesa mucho más que el resto del reporte", "S3 + URL prefirmada", "La foto no pasa por el cómputo"],
    ["Clasificar residuos sin dataset propio inicial", "Rekognition", "Línea base inmediata y reemplazable"],
    ["Nuevos consumidores del evento a futuro", "EventBridge", "El productor no conoce a sus consumidores"],
    ["Datos personales implícitos: ubicación y foto", "KMS + IAM + TTL", "Cifrado, mínimo privilegio, retención acotada"],
  ];

  const hy = 1.52;
  ["Rasgo del problema", "Servicio elegido", "Por qué"].forEach((h, i) => {
    const x = M + [0, 5.6, 8.6][i];
    s.addText(h.toUpperCase(), {
      x, y: hy, w: [5.4, 2.8, 3.3][i], h: 0.28,
      fontFace: BODY, fontSize: 10, bold: true, color: C.moss, charSpacing: 1.5,
      isTextBox: true, margin: 0,
    });
  });

  rows.forEach((r, i) => {
    const y = 1.95 + i * 0.78;
    if (i % 2 === 0) {
      s.addShape(pres.ShapeType.rect, {
        x: M - 0.15, y: y - 0.08, w: CW + 0.3, h: 0.72,
        fill: { color: C.cream }, line: { color: C.cream },
      });
    }
    s.addText(r[0], {
      x: M, y, w: 5.4, h: 0.58,
      fontFace: BODY, fontSize: 11.5, color: C.ink, lineSpacing: 15, isTextBox: true, margin: 0,
    });
    s.addText(r[1], {
      x: M + 5.6, y, w: 2.8, h: 0.58,
      fontFace: BODY, fontSize: 11.5, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(r[2], {
      x: M + 8.6, y, w: 3.3, h: 0.58,
      fontFace: BODY, fontSize: 11.5, color: C.muted, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });

  s.addText(
    "Descartados con razón documentada: contenedores en ECS/EKS (costo base injustificado), " +
    "PostgreSQL + PostGIS (instancia siempre encendida y VPC innecesaria), Firebase (menor ejercicio de arquitectura).",
    {
      x: M, y: 6.5, w: CW, h: 0.42,
      fontFace: BODY, fontSize: 10.5, italic: true, color: C.muted,
      lineSpacing: 14, isTextBox: true, margin: 0,
    },
  );
  footer(s, 6);
  s.addNotes(
    "JUSTIFICACION (90 s, recortable). No lea las seis filas: elija dos y explíquelas bien. Luego mencione lo descartado, que es lo que demuestra criterio: 'consideré PostgreSQL con PostGIS; lo descarté porque mis consultas son de proximidad, que el geohash resuelve a costo constante, y PostGIS obligaba a una instancia siempre encendida en una VPC que costaria mas que toda la solucion'.",
  );
}

/* ---------- 7 · modelo de datos ---------- */
{
  const s = lightSlide("Una sola tabla, cuatro preguntas, ningún Scan", "Modelo de datos");

  s.addText(
    "En DynamoDB el modelo se diseña desde las consultas, no desde las entidades. " +
    "Hay exactamente cuatro consultas en el producto y cada una tiene su clave.",
    {
      x: M, y: 1.5, w: CW, h: 0.5,
      fontFace: BODY, fontSize: 13.5, color: C.ink, lineSpacing: 19, isTextBox: true, margin: 0,
    },
  );

  const q = [
    ["Detalle de un reporte", "Tabla principal", "REPORT#<uuid>"],
    ["¿Qué hay cerca de aquí?", "GSI1 · geohash", "GEO#<geohash6>"],
    ["¿Qué está pendiente?", "GSI2 · estado", "STATUS#<estado>"],
    ["¿De quién es esta foto?", "GSI3 · disperso", "EVID#<clave>"],
  ];
  const qw = (CW - 0.75) / 4;
  q.forEach(([a, b, c], i) => {
    const x = M + i * (qw + 0.25);
    card(s, { x, y: 2.15, w: qw, h: 1.7 });
    s.addText(a, {
      x: x + 0.22, y: 2.35, w: qw - 0.44, h: 0.55,
      fontFace: HEAD, fontSize: 14, bold: true, color: C.forest,
      lineSpacing: 18, isTextBox: true, margin: 0,
    });
    s.addText(b, {
      x: x + 0.22, y: 2.98, w: qw - 0.44, h: 0.26,
      fontFace: BODY, fontSize: 11, color: C.muted, isTextBox: true, margin: 0,
    });
    s.addText(c, {
      x: x + 0.22, y: 3.3, w: qw - 0.44, h: 0.3,
      fontFace: "Courier New", fontSize: 10.5, bold: true, color: C.ink,
      isTextBox: true, margin: 0,
    });
  });

  const notes = [
    ["Geohash a dos precisiones", "Se guarda con precisión 7 (~153 m) pero se particiona por los 6 primeros caracteres (~1,2 km): un barrio completo en una sola consulta, sin partición caliente."],
    ["Índice disperso", "GSI3 solo indexa reportes con evidencia, con proyección KEYS_ONLY. Sin él, cada foto subida costaría un Scan de la tabla entera."],
    ["TTL de 540 días", "Es a la vez decisión de privacidad y de costo: el reporte y su evidencia en S3 caducan juntos."],
  ];
  const nw = (CW - 0.6) / 3;
  notes.forEach(([t, d], i) => {
    const x = M + i * (nw + 0.3);
    s.addText(t, {
      x, y: 4.2, w: nw, h: 0.3,
      fontFace: HEAD, fontSize: 14, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x, y: 4.55, w: nw, h: 1.3,
      fontFace: BODY, fontSize: 11.5, color: C.ink, lineSpacing: 17, isTextBox: true, margin: 0,
    });
  });
  footer(s, 7);
  s.addNotes(
    "MODELO DE DATOS (90 s, recortable). Frase clave: 'en DynamoDB uno no disena desde las entidades sino desde las consultas; tengo exactamente cuatro y cada una tiene su clave'. Si hay tiempo explique el geohash a dos precisiones (se guarda con 7, se particiona por 6) para que las particiones no sean ni diminutas ni calientes.",
  );
}

/* ---------- 8 · algoritmo ---------- */
{
  const s = lightSlide("De reportes sueltos a puntos críticos priorizados", "Algoritmo");

  const steps = [
    ["Prefiltrado por geohash", "Se consultan la celda del punto y sus vecinas en GSI1. Acota el conjunto a decenas de reportes sin escanear la tabla."],
    ["Agrupamiento por densidad", "Variante de DBSCAN sobre distancia de Haversine: cada reporte no asignado abre un grupo y absorbe a los que estén dentro del radio."],
    ["Umbral de existencia", "Un grupo es punto crítico solo con 3 o más reportes. Evita que una queja aislada movilice una cuadrilla."],
    ["Priorización", "Severidad acumulada ordena los grupos; la categoría dominante define el protocolo de manejo."],
  ];
  steps.forEach(([t, d], i) => {
    const y = 1.55 + i * 1.12;
    iconCircle(s, { x: M, y: y + 0.06, d: 0.42, glyph: String(i + 1) });
    s.addText(t, {
      x: M + 0.62, y, w: 6.6, h: 0.3,
      fontFace: HEAD, fontSize: 16, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: M + 0.62, y: y + 0.34, w: 6.6, h: 0.7,
      fontFace: BODY, fontSize: 12, color: C.ink, lineSpacing: 16, isTextBox: true, margin: 0,
    });
  });

  card(s, { x: 8.4, y: 1.55, w: CW - 7.7, h: 4.5, fill: C.deep });
  s.addText("COMPORTAMIENTO VERIFICADO", {
    x: 8.75, y: 1.8, w: 4.0, h: 0.26,
    fontFace: BODY, fontSize: 10, bold: true, color: C.moss, charSpacing: 1.5,
    isTextBox: true, margin: 0,
  });
  const cases = [
    ["4 reportes en 8 m", "1 punto crítico · severidad 15 · prioridad Alta"],
    ["Los mismos, ya atendidos", "0 puntos: lo cerrado sale del análisis"],
    ["Solo 2 reportes cercanos", "0 puntos: no alcanza el umbral"],
    ["3 cercanos + 3 a 4 km", "2 puntos independientes"],
    ["Radio pedido: 99.999 m", "Se acota a 1000 m en el servidor"],
  ];
  cases.forEach(([k, v], i) => {
    const y = 2.2 + i * 0.76;
    s.addText(k, {
      x: 8.75, y, w: 4.0, h: 0.26,
      fontFace: BODY, fontSize: 11.5, bold: true, color: C.white, isTextBox: true, margin: 0,
    });
    s.addText(v, {
      x: 8.75, y: y + 0.25, w: 4.0, h: 0.44,
      fontFace: BODY, fontSize: 11, color: C.moss, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });
  footer(s, 8);
  s.addNotes(
    "ALGORITMO (2 min). Aqui se gana el criterio de rigor tecnico: es lo unico verdaderamente propio del proyecto. Explique los cuatro pasos y sea explicito con el umbral: 'un grupo solo es punto critico con tres o mas reportes; sin ese umbral una queja aislada movilizaria una cuadrilla'. Senale el panel derecho: no son casos ilustrativos, son pruebas que corren en cada push.",
  );
}

/* ---------- 9 · seguridad ---------- */
{
  const s = lightSlide("Seguridad y privacidad por diseño", "Ingeniería");

  const left = [
    ["Autenticación en el borde", "API Gateway valida el JWT antes de invocar código propio. Una petición sin credenciales nunca ejecuta una Lambda."],
    ["Mínimo privilegio real", "Ocho roles IAM, uno por función. get_report solo lee; presign_evidence solo firma en un prefijo del bucket."],
    ["Cifrado extremo a extremo", "TLS obligatorio por política de bucket; KMS con rotación anual en DynamoDB, S3, logs, SNS y SQS."],
  ];
  const right = [
    ["Minimización de datos", "No se pide nombre, cédula ni teléfono. La única identidad es el sub opaco de Cognito."],
    ["Seudonimización en logs", "Se registra sha256(user_id) truncado: suficiente para correlacionar, insuficiente para identificar."],
    ["Sin fuga en los errores", "Un fallo interno devuelve 500 genérico con request_id. Hay una prueba que lo verifica."],
  ];

  [left, right].forEach((col, ci) => {
    col.forEach(([t, d], i) => {
      const x = M + ci * (CW / 2 + 0.2);
      const y = 1.55 + i * 1.45;
      const w = CW / 2 - 0.2;
      card(s, { x, y, w, h: 1.25 });
      s.addText(t, {
        x: x + 0.28, y: y + 0.18, w: w - 0.56, h: 0.3,
        fontFace: HEAD, fontSize: 15, bold: true, color: C.forest, isTextBox: true, margin: 0,
      });
      s.addText(d, {
        x: x + 0.28, y: y + 0.52, w: w - 0.56, h: 0.62,
        fontFace: BODY, fontSize: 11.5, color: C.ink, lineSpacing: 16, isTextBox: true, margin: 0,
      });
    });
  });

  card(s, { x: M, y: 5.95, w: CW, h: 0.85, fill: C.cream });
  s.addText(
    "Deuda reconocida: sin verificación anti-fraude por EXIF, sin WAF, sin desenfoque automático de rostros " +
    "y sin reproceso automático de la DLQ. Documentarlo es parte del rigor.",
    {
      x: M + 0.35, y: 6.14, w: CW - 0.7, h: 0.5,
      fontFace: BODY, fontSize: 11.5, italic: true, color: C.ink,
      lineSpacing: 16, isTextBox: true, margin: 0,
    },
  );
  footer(s, 9);
  s.addNotes(
    "SEGURIDAD (90 s). Elija dos tarjetas, no las seis: minimo privilegio real y seudonimizacion en logs. Luego LEA LA DEUDA RECONOCIDA: 'no verifico que la foto se tomo donde dice, no hay WAF y no desenfoco rostros; lo documente porque un analisis de seguridad que solo lista lo que si hice no es un analisis de seguridad'. Si no lo dice usted, se lo preguntan igual.",
  );
}

/* ---------- 10 · calidad ---------- */
{
  const s = lightSlide("Prácticas de ingeniería que sostienen el resultado", "Calidad");

  statCard(s, { x: M, y: 1.5, w: (CW - 0.9) / 4, value: "112", label: "Pruebas automatizadas", note: "Corren sin credenciales de AWS y sin red" });
  statCard(s, { x: M + ((CW - 0.9) / 4 + 0.3), y: 1.5, w: (CW - 0.9) / 4, value: "82 %", label: "Cobertura total", note: "Dominio y servicios al 100 %" });
  statCard(s, { x: M + 2 * ((CW - 0.9) / 4 + 0.3), y: 1.5, w: (CW - 0.9) / 4, value: "8", label: "Roles IAM", note: "Uno por función, permisos declarados" });
  statCard(s, { x: M + 3 * ((CW - 0.9) / 4 + 0.3), y: 1.5, w: (CW - 0.9) / 4, value: "0", label: "Recursos creados a mano", note: "Toda la infraestructura en Terraform" });

  s.addChart(
    pres.ChartType.bar,
    [{
      name: "Cobertura",
      labels: ["Geo", "Servicios", "Handlers API", "HTTP", "Modelos"],
      values: [100, 100, 99, 98, 98],
    }],
    {
      x: M, y: 3.75, w: 6.3, h: 2.6,
      barDir: "col",
      chartColors: [C.forest],
      showTitle: true,
      title: "Cobertura por módulo del dominio (%)",
      titleFontFace: HEAD, titleFontSize: 13, titleColor: C.forest,
      showValue: true, dataLabelPosition: "outEnd",
      dataLabelFontFace: BODY, dataLabelFontSize: 10, dataLabelColor: C.ink,
      valAxisMaxVal: 104, valAxisHidden: true,
      catAxisLabelFontFace: BODY, catAxisLabelFontSize: 10, catAxisLabelColor: C.muted,
      catGridLine: { style: "none" }, valGridLine: { style: "none" },
      showLegend: false,
      plotArea: { fill: { color: C.white } },
    },
  );

  const practices = [
    ["Dependencias hacia el dominio", "Handlers delgados sobre una capa de servicios que no conoce HTTP ni AWS."],
    ["Repositorio intercambiable", "Un doble en memoria con la misma semántica permite probar sin nube."],
    ["CI en cada push", "ruff, bandit, pytest con umbral de cobertura y terraform validate."],
    ["Despliegue con OIDC", "GitHub asume un rol de AWS: cero llaves de larga vida almacenadas."],
  ];
  practices.forEach(([t, d], i) => {
    const y = 3.62 + i * 0.72;
    s.addText(t, {
      x: 7.4, y, w: CW - 6.7, h: 0.26,
      fontFace: HEAD, fontSize: 13.5, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: 7.4, y: y + 0.26, w: CW - 6.7, h: 0.42,
      fontFace: BODY, fontSize: 11, color: C.ink, lineSpacing: 14, isTextBox: true, margin: 0,
    });
  });
  footer(s, 10);
  s.addNotes(
    "CALIDAD (60 s). Los cuatro numeros y una historia concreta que vale mas que todos ellos: una prueba fallo la primera vez que la corri porque la API devolvia el identificador del usuario junto con el reporte. Es una fuga de datos personales que no se ve leyendo el codigo, solo se ve cuando alguien la prueba.",
  );
}

/* ---------- 11 · costos ---------- */
{
  const s = lightSlide("Demostrarla no cuesta nada; operarla, cinco dólares", "Costo de operación");

  s.addText(
    "Operación real de una localidad: 3.000 reportes y 30.000 consultas de mapa al mes, con foto promedio de 400 KB.",
    {
      x: M, y: 1.5, w: CW, h: 0.35,
      fontFace: BODY, fontSize: 13.5, color: C.ink, isTextBox: true, margin: 0,
    },
  );

  s.addChart(
    pres.ChartType.doughnut,
    [{
      name: "Costo mensual (USD)",
      labels: ["Rekognition", "KMS", "EventBridge · SNS · CloudWatch", "DynamoDB", "S3", "Lambda", "API Gateway"],
      values: [3.0, 1.0, 0.6, 0.1, 0.05, 0.05, 0.04],
    }],
    {
      x: M, y: 2.0, w: 6.2, h: 4.2,
      chartColors: [C.forest, C.moss, "5A8F5B", "7FA85C", "B8CFA0", "D4E2C4", C.line],
      holeSize: 55,
      showLegend: true, legendPos: "b",
      legendFontFace: BODY, legendFontSize: 10, legendColor: C.ink,
      showTitle: false,
      showValue: false,
      dataBorder: { pt: 2, color: C.white },
    },
  );

  card(s, { x: 7.2, y: 2.0, w: CW - 6.5, h: 1.55, fill: C.deep });
  s.addText("0 USD", {
    x: 7.55, y: 2.22, w: 5.2, h: 0.55,
    fontFace: HEAD, fontSize: 34, bold: true, color: C.white, isTextBox: true, margin: 0,
  });
  s.addText("La demostración cabe en la capa gratuita de AWS", {
    x: 7.55, y: 2.82, w: 5.2, h: 0.3,
    fontFace: BODY, fontSize: 12, color: C.moss, isTextBox: true, margin: 0,
  });
  s.addText("Operación real de una localidad: ≈ 4,85 USD / mes", {
    x: 7.55, y: 3.1, w: 5.2, h: 0.3,
    fontFace: BODY, fontSize: 11.5, color: C.cream, isTextBox: true, margin: 0,
  });

  const notes = [
    ["El 62 % del costo es Rekognition", "Un clasificador propio en el dispositivo eliminaría ese renglón: es el argumento económico de la investigación."],
    ["El resto escala a cero", "Sin tráfico no hay factura: no hay instancias, ni NAT Gateway, ni capacidad reservada."],
    ["La clave KMS es opcional", "Único cargo fijo del diseño (1 USD/mes). Desactivada por defecto; el dato sigue cifrado con claves de AWS."],
  ];
  notes.forEach(([t, d], i) => {
    const y = 3.85 + i * 0.85;
    s.addText(t, {
      x: 7.2, y, w: CW - 6.5, h: 0.28,
      fontFace: HEAD, fontSize: 14, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: 7.2, y: y + 0.28, w: CW - 6.5, h: 0.5,
      fontFace: BODY, fontSize: 11.5, color: C.ink, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });
  footer(s, 11);
  s.addNotes(
    "COSTOS (60 s, recortable). 'La demostracion cabe en la capa gratuita; la operacion real de una localidad cuesta menos de cinco dolares al mes. Pero el dato interesante es la composicion: el 62 % es el servicio de vision por computador.' Ese puente hacia la investigacion es el mejor momento de la presentacion: uselo para pasar a la siguiente diapositiva.",
  );
}

/* ---------- 12 · proyección investigativa ---------- */
{
  const s = lightSlide("De taller de curso a línea de investigación", "Semillero");

  s.addText(
    "Existe literatura sobre crowdsourcing ambiental y sobre clasificación automática de residuos, " +
    "pero es escasa la evidencia sobre su combinación en contextos urbanos latinoamericanos.",
    {
      x: M, y: 1.5, w: CW, h: 0.5,
      fontFace: BODY, fontSize: 13.5, color: C.ink, lineSpacing: 19, isTextBox: true, margin: 0,
    },
  );

  const phases = [
    ["Fase 1", "Validación concurrente", "Contrastar los puntos críticos derivados de reportes ciudadanos con el inventario oficial: precisión, exhaustividad y F1, con barrido de parámetros de agrupamiento."],
    ["Fase 2", "Clasificador propio", "Corpus anonimizado y etiquetado por doble anotador; MobileNetV3 ajustado frente a la línea base, medido en F1, latencia y costo."],
    ["Fase 3", "Modelo predictivo", "Rejilla de geohash y modelo de conteo para estimar reaparición a 7 días: pasar de recolección reactiva a preventiva."],
  ];
  const pw = (CW - 0.6) / 3;
  phases.forEach(([n, t, d], i) => {
    const x = M + i * (pw + 0.3);
    card(s, { x, y: 2.15, w: pw, h: 2.6 });
    s.addText(n.toUpperCase(), {
      x: x + 0.28, y: 2.38, w: pw - 0.56, h: 0.24,
      fontFace: BODY, fontSize: 10, bold: true, color: C.moss, charSpacing: 2,
      isTextBox: true, margin: 0,
    });
    s.addText(t, {
      x: x + 0.28, y: 2.66, w: pw - 0.56, h: 0.36,
      fontFace: HEAD, fontSize: 16, bold: true, color: C.forest, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: x + 0.28, y: 3.08, w: pw - 0.56, h: 1.5,
      fontFace: BODY, fontSize: 11.5, color: C.ink, lineSpacing: 16, isTextBox: true, margin: 0,
    });
  });

  s.addText("La arquitectura actual ya habilita la investigación", {
    x: M, y: 5.0, w: CW, h: 0.32,
    fontFace: HEAD, fontSize: 17, bold: true, color: C.forest, isTextBox: true, margin: 0,
  });
  const enablers = [
    "Evidencias en S3 con etiquetas de IA almacenadas: corpus en formación desde el primer reporte",
    "geohash + created_at indexados: la serie espacio-temporal ya existe",
    "Parámetros de agrupamiento configurables: los experimentos son reproducibles",
    "Publicación en EventBridge: agregar un consumidor de datos no toca el código que funciona",
  ];
  enablers.forEach((t, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = M + col * (CW / 2 + 0.1);
    const y = 5.45 + row * 0.6;
    iconCircle(s, { x, y: y + 0.02, d: 0.3, glyph: "✓", bg: C.moss, fg: C.deep });
    s.addText(t, {
      x: x + 0.45, y, w: CW / 2 - 0.55, h: 0.5,
      fontFace: BODY, fontSize: 11.5, color: C.ink, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });
  footer(s, 12);
  s.addNotes(
    "SEMILLERO (2 min). Si le interesa la convocatoria, esta es la diapositiva por la que vino. Nombre el vacio: hay literatura sobre reporte ciudadano y sobre clasificacion de residuos, poca sobre las dos juntas en ciudades latinoamericanas. Explique la Fase 1 con concrecion: comparar contra el inventario oficial publicado como dato abierto y medir precision y exhaustividad. Es un experimento ejecutable, no una intencion.",
  );
}

/* ---------- 13 · entregables ---------- */
{
  const s = lightSlide("Qué se entrega", "Repositorio");

  const blocks = [
    ["mobile/", "App Flutter", "Modelos, servicios (API, auth, ubicación, cola sin conexión), pantallas de reporte y mapa, tema accesible Material 3 y pruebas."],
    ["backend/", "API en Python 3.12", "Ocho handlers, capa de dominio y servicios, repositorios intercambiables, 112 pruebas y peticiones listas en api.http."],
    ["infra/", "Terraform", "DynamoDB, S3, Cognito, Lambda con roles de mínimo privilegio, API Gateway, EventBridge, SNS, DLQ, alarmas y tablero."],
    ["docs/", "Documentación técnica", "Diez documentos: análisis, arquitectura, modelo de datos, seguridad, ADR, pruebas, proyección, despliegue, API y guion de sustentación."],
  ];
  const bw = (CW - 0.9) / 4;
  blocks.forEach(([p, t, d], i) => {
    const x = M + i * (bw + 0.3);
    card(s, { x, y: 1.6, w: bw, h: 3.0 });
    s.addText(p, {
      x: x + 0.25, y: 1.82, w: bw - 0.5, h: 0.3,
      fontFace: "Courier New", fontSize: 13, bold: true, color: C.moss, isTextBox: true, margin: 0,
    });
    s.addText(t, {
      x: x + 0.25, y: 2.18, w: bw - 0.5, h: 0.5,
      fontFace: HEAD, fontSize: 15, bold: true, color: C.forest,
      lineSpacing: 19, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: x + 0.25, y: 2.75, w: bw - 0.5, h: 1.6,
      fontFace: BODY, fontSize: 11, color: C.ink, lineSpacing: 15, isTextBox: true, margin: 0,
    });
  });

  card(s, { x: M, y: 4.9, w: CW, h: 1.5, fill: C.deep });
  s.addText("Repositorio público en GitHub", {
    x: M + 0.45, y: 5.12, w: CW - 0.9, h: 0.35,
    fontFace: HEAD, fontSize: 19, bold: true, color: C.white, isTextBox: true, margin: 0,
  });
  s.addText("github.com/DiegoGamba/ecoruta", {
    x: M + 0.45, y: 5.5, w: CW - 0.9, h: 0.35,
    fontFace: "Courier New", fontSize: 16, bold: true, color: C.moss, isTextBox: true, margin: 0,
  });
  s.addText(
    "README con diagramas y guía de despliegue · CI con pruebas, análisis de seguridad y validación de infraestructura · Licencia MIT",
    {
      x: M + 0.45, y: 5.92, w: CW - 0.9, h: 0.32,
      fontFace: BODY, fontSize: 11.5, color: C.cream, isTextBox: true, margin: 0,
    },
  );
  footer(s, 13);
  s.addNotes(
    "ENTREGABLES (30 s). Muestre el repositorio en vivo, no la diapositiva: baje por el README, abra un ADR, abra la carpeta de evidencias. Diez segundos de repositorio real valen mas que un minuto describiendolo.",
  );
}

/* ---------- 14 · cierre ---------- */
{
  const s = darkSlide();
  s.addShape(pres.ShapeType.ellipse, {
    x: -1.8, y: 3.4, w: 5.2, h: 5.2,
    fill: { color: C.forest, transparency: 50 }, line: { color: C.forest, transparency: 100 },
  });

  s.addText("EN RESUMEN", {
    x: M, y: 1.3, w: 8, h: 0.3,
    fontFace: BODY, fontSize: 12, bold: true, color: C.moss, charSpacing: 3,
    isTextBox: true, margin: 0,
  });
  s.addText(
    "El conocimiento local del vecino,\nconvertido en un inventario vivo y priorizado.",
    {
      x: M, y: 1.7, w: 11.4, h: 1.5,
      fontFace: HEAD, fontSize: 31, bold: true, color: C.white,
      lineSpacing: 44, isTextBox: true, margin: 0,
    },
  );

  const closing = [
    ["Problema real y delimitado", "Puntos críticos dinámicos que los inventarios manuales no alcanzan"],
    ["Arquitectura justificada", "Cada servicio responde a un rasgo del problema, con alternativas descartadas por escrito"],
    ["Ingeniería verificable", "112 pruebas, roles de mínimo privilegio, infraestructura como código y CI"],
    ["Camino investigativo abierto", "Validación concurrente, corpus abierto y clasificador propio en el dispositivo"],
  ];
  closing.forEach(([t, d], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = M + col * (CW / 2 + 0.15);
    const y = 3.75 + row * 1.2;
    s.addText(t, {
      x, y, w: CW / 2 - 0.3, h: 0.3,
      fontFace: HEAD, fontSize: 16, bold: true, color: C.moss, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x, y: y + 0.34, w: CW / 2 - 0.3, h: 0.6,
      fontFace: BODY, fontSize: 12, color: C.cream, lineSpacing: 16, isTextBox: true, margin: 0,
    });
  });

  s.addText("Diego Gamba · Mariana Diez  ·  github.com/DiegoGamba/ecoruta", {
    x: M, y: 6.35, w: 9, h: 0.32,
    fontFace: BODY, fontSize: 12, color: C.moss, isTextBox: true, margin: 0,
  });
  s.addNotes("Gracias. Quedo atento a preguntas sobre la arquitectura, el algoritmo de agrupamiento o la proyección investigativa.");
}

pres.writeFile({ fileName: "EcoRuta-presentacion.pptx" }).then(() => {
  console.log("Deck generado: EcoRuta-presentacion.pptx");
});
