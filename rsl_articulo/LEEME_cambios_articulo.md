# Cambios del artículo (introducción → resultados)

Archivo principal: `RSL_introduccion_metodologia_resultados.tex` (plantilla Springer `sn-jnl`, estilo `sn-mathphys-num`, sin tocar `.cls` ni `.bst`). Compila con `latexmk -pdf`. `RSL_vista_previa.pdf` es la salida de prueba (39 páginas).

## Qué se hizo
1. Corpus actualizado a **35 estudios incluidos** (tablas, cifras y apéndice de 35 filas recalculados desde los datos codificados).
2. Se retiró del texto todo lenguaje de proceso interno: versiones de la sábana, hojas, códigos de incidencia y redacción de "agente". El manuscrito describe la RSL, no cómo se construyó el archivo de trabajo.
3. **Bibliometría reescrita** como un solo bloque (§Análisis bibliométrico en métodos y §4.3 en resultados), con AB1 (producción y tendencia), AB2 (estructura conceptual: red de co‑palabras y mapa temático) y AB3 (separación de las líneas facial y de clasificación). Los análisis se hacen sobre el corpus temático (141 registros); AB1 y AB2 se contrastan con los 35 estudios incluidos; AB3 no tiene contraste. Se eliminaron los gráficos antiguos de 343 registros (carpeta `bibliometria/` del repo original; no se copió aquí).
4. Resultados RQ1–RQ7 con tablas de síntesis; apéndices: cadenas de búsqueda, persistencia, tabla del corpus.
5. Referencias: se añadieron `aria2017bibliometrix`, `cobo2011science`, `callon1991coword`, `blondel2008fast`.

## Pendiente / a verificar por el equipo
- **Las 4 referencias nuevas están escritas de memoria**: verificar volumen, páginas y DOI antes de enviar.
- La definición del corpus temático y la asignación AB1–AB3 son **mi interpretación** de su tabla; confirmar.
- Las palabras clave cubren solo el 62 % del corpus temático; el texto lo declara y los análisis se presentan como exploratorios.
- `prisma_2020_RSL.png` es un **marcador de posición**: reemplazar con su figura.
- Discusión y conclusiones no están escritas (el trabajo llega hasta resultados).
- Hay comentarios `% NOTA PARA LOS AUTORES` en el `.tex` (p. ej. párrafo sobre uso de IA y ratificación): revisarlos y quitarlos antes de enviar.
- La ratificación de los 35 estudios queda aparte, como acordamos.
- `scripts_bibliometria/` reproduce las figuras y estadísticas (`prep.py` → `analisis.py` → `figuras.py`); requieren `recs.json` del corpus temático, que no se incluye aquí.
