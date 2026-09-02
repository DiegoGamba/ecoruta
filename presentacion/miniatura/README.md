# Miniatura del video de sustentación

`miniatura-youtube.png` — 1280 × 720 px (16:9), lista para cargar en YouTube.

Cumple los requisitos del taller: retrato del estudiante, título del proyecto, temas
principales y herramientas utilizadas, todo legible a tamaño reducido.

## Falta incrustar el retrato

La miniatura tiene un marcador circular en la mitad izquierda. Para reemplazarlo:

1. Guarde su foto o avatar como `avatar.png` en esta carpeta (recórtela cuadrada).
2. En `miniatura.html`, sustituya el bloque `<div class="marcador">…</div>` por:

   ```html
   <img src="avatar.png" alt="Diego Gamba">
   ```

3. Vuelva a generar la imagen: abra `miniatura.html` en el navegador, ajuste la ventana a
   1280 × 720 y capture; o pídale a quien tenga la herramienta que la re-renderice.

El instructivo admite un avatar en estilo caricatura o anime generado a partir de la foto.

## Contenido de la miniatura

| Elemento | Valor |
|---|---|
| Título del proyecto | EcoRuta |
| Bajada | App móvil para el reporte y la priorización de puntos críticos de residuos sólidos |
| Temas | Arquitectura Cloud · Apps multiplataforma · Geolocalización |
| Herramientas | Flutter · AWS Lambda · DynamoDB · Terraform · Python |
| Autor | Diego Gamba — Diseño de Aplicaciones Móviles |
