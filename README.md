# Proyecto de analítica financiera | IX Concurso ITM 2026

**Curso:** Lenguajes de Programación · Ingeniería Financiera  
**Concurso:** 12 de noviembre de 2026  
**Simulacro:** 10 de noviembre de 2026  
**Tecnología:** Python + Streamlit

## 1. Identificación del proyecto

- **Nombre de la aplicación:** Stattum
- **Equipo e integrantes:** Isabella Hincapie - Manuela Bohorquez - Yuliana Pineda
- **Enlace a la aplicación:** [Pendiente: URL de Streamlit Community Cloud]
- **Repositorio del proyecto:** [https://github.com/isahincapiecontacto-netizen/Stattum](https://github.com/isahincapiecontacto-netizen/Stattum)
- **Última actualización:** 2026-11-08

## 2. ¿Qué queremos investigar? · S25

- **Situación o fenómeno de interés:** Los inversionistas en Colombia pueden elegir empresas de sectores muy distintos (comercio, energía, banca), y cada una implica un nivel de riesgo diferente. Queremos entender cómo se comportaron en la práctica en la Bolsa de Valores de Colombia (BVC).
- **Pregunta principal:** *¿Cómo se comportaron el rendimiento y el riesgo de Almacenes Éxito (EXITO.CL), Ecopetrol (ECOPETROL.CL) y Grupo Cibest (PFCIBEST.CL) frente al mercado colombiano (ICOLCAP.CL) durante los últimos cinco años (nov 2021 – nov 2026) y cuál ofreció la mejor relación rendimiento-riesgo?*
- **Objetivo del análisis:** Comparar retorno, volatilidad, caídas máximas y correlación entre los cuatro activos, usando datos históricos diarios.
- **Importancia financiera:** Medir el rendimiento sin medir el riesgo conduce a malas decisiones. Comparar ambos y la correlación entre activos permite evaluar su aporte a la diversificación de un portafolio.
- **Preguntas complementarias:**
  - ¿Qué activo sufrió la mayor caída desde un máximo (drawdown)?
  - ¿Qué par de activos ofrece mejor diversificación (menor correlación)?
  - ¿Qué tan sensible es cada activo al mercado (beta frente al mercado colombiano, ICOLCAP)?

**Qué puede y qué no puede responderse:** con datos históricos podemos describir rendimientos, volatilidad, correlaciones y caídas pasadas. **No** podemos predecir precios futuros, ni garantizar que el comportamiento pasado se repita, ni explicar las causas de cada movimiento.

## 3. Activos, datos y alcance · S25

| Activo | Ticker | Tipo | Razón para incluirlo |
|---|---|---|---|
| Almacenes Éxito | EXITO.CL | Acción (comercio minorista) | Principal cadena de tiendas que cotiza en la BVC; representa el consumo y el sector retail |
| Ecopetrol | ECOPETROL.CL | Acción (energía) | Mayor empresa del país; su precio depende del petróleo y de factores políticos |
| Grupo Cibest (Bancolombia) | PFCIBEST.CL | Acción preferencial (banca) | Mayor grupo bancario colombiano; representa el sector financiero |
| iShares COLCAP | ICOLCAP.CL | ETF | Replica el índice COLCAP; sirve de referencia del mercado (benchmark y base para la beta) |

- **Fuente de datos:** Yahoo Finance mediante la librería [yfinance](https://ranaroussi.github.io/yfinance/)
- **Período:** 2021-11-09 – 2026-11-06 (fijo para que los resultados sean reproducibles; ajustable en la app)
- **Frecuencia:** Diaria
- **Variables disponibles:** Fecha, apertura, máximo, mínimo, cierre ajustado, volumen. Usamos el **cierre ajustado** (`auto_adjust=True`).
- **Limitaciones de los datos:**
  - Las acciones colombianas tienen menor liquidez: hay días sin negociación. Usamos únicamente **fechas comunes** a todos los activos y, si hace falta, rellenamos huecos de hasta 5 días.
  - Los precios están en **pesos colombianos (COP)**; no se considera el efecto de la tasa de cambio.
  - Cibest cambió de nombre y de ticker (antes Bancolombia, PFBCOLOM). En la corrida del notebook (datos hasta 2026-11-06), `PFCIBEST.CL` sí tuvo datos para todo el periodo analizado, desde 2021-11-09.
  - Éxito tuvo cambios de control accionario y tiene poca liquidez: su historial puede mostrar saltos.
  - La tasa libre de riesgo de la app (4 % por defecto) debe ajustarse a una referencia colombiana, por ejemplo TES, y citar la fuente.
  - Los símbolos `.CL` deben confirmarse en Yahoo Finance antes de usarse.
  - Yahoo Finance es una fuente gratuita, no oficial, y puede tener faltantes o correcciones.

**Primera prueba:** [Enlace al notebook o archivo; anota qué funcionó y qué no al descargar con `yf.download`]

## 4. Metodología de análisis · S25–S26

| Indicador / técnica | ¿Qué mide? | ¿Por qué lo necesitamos? | Implementación |
|---|---|---|---|
| Retorno diario | `r_t = P_t / P_{t-1} − 1` | Base de todos los cálculos de riesgo | `metricas.retornos` |
| Retorno acumulado | `P_final / P_inicial − 1` | Ganancia total en el período | `metricas.retorno_acumulado` |
| Retorno anualizado (CAGR) | `(P_final / P_inicial)^(1/años) − 1` | Comparar activos en una misma escala anual | `metricas.retorno_anualizado` |
| Volatilidad anual | `σ_diaria × √252` | Mide el riesgo (dispersión de retornos) | `metricas.volatilidad_anual` |
| Ratio de Sharpe | `(μ_anual − r_f) / σ_anual` | Retorno obtenido por unidad de riesgo; responde la pregunta principal | `metricas.sharpe` |
| Drawdown máximo | Mayor caída desde un máximo previo | Riesgo de pérdida real que sufriría un inversionista | `metricas.max_drawdown` |
| Beta | `Cov(activo, mercado) / Var(mercado)` | Sensibilidad frente al mercado colombiano (ICOLCAP) | `metricas.beta` |
| Correlación | Relación lineal entre retornos | Potencial de diversificación | `app.py` (pestaña Correlación) |
| Medias móviles | Promedio de precios de 20 y 100 días | Identificar tendencia | `app.py` (pestaña Precios) |

Seleccionamos estos indicadores porque cubren las dos caras de la pregunta (rendimiento y riesgo) y su combinación (Sharpe). Un Sharpe alto indica mejor retorno por unidad de riesgo, pero asume retornos aproximadamente normales, algo que no se cumple bien en cripto.

### Visualizaciones previstas

| Gráfico | Pregunta que ayuda a responder | Variables | Interpretación esperada |
|---|---|---|---|
| Base 100 (líneas) | ¿Cuánto habría crecido una inversión de 100? | Precio normalizado | Comparar trayectorias y momentos de caída |
| Mapa riesgo-retorno (dispersión) | ¿Qué activo da más retorno por riesgo? | Volatilidad vs. retorno anualizado | Mejor posición: arriba a la izquierda |
| Drawdown (líneas) | ¿Qué tan profundas fueron las caídas? | Caída desde el máximo | Duración y severidad de las pérdidas |
| Volatilidad móvil | ¿El riesgo cambió con el tiempo? | Desv. estándar móvil anualizada | Periodos de calma vs. estrés |
| Histograma de retornos | ¿Cómo se distribuyen los retornos diarios? | Retorno diario | Colas gruesas, dispersión por activo |
| Mapa de calor de correlación | ¿Qué activos diversifican? | Correlación de retornos | Correlaciones bajas = mejor diversificación |

**Primer resultado verificable:** 
| Ticker | Retorno acumulado | Retorno anualizado | Volatilidad anual | Sharpe | Máx. drawdown | Beta vs ICOLCAP.CL |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ECOPETROL.CL** | 73.86% | 11.72% | 37.65% | 0.37 | -37.99% | 0.82 |
| **EXITO.CL** | 41.61% | 7.22% | 44.56% | 0.28 | -66.59% | 0.43 |
| **ICOLCAP.CL** | 118.76% | 16.98% | 18.02% | 0.72 | -30.22% | 1.00 |
| **PFCIBEST.CL** | 267.24% | 29.78% | 31.98% | 0.83 | -32.58% | 0.93 |

**Qué estamos analizando:** comparamos cuatro activos de la BVC desde cinco dimensiones: **rentabilidad** (retorno acumulado y anualizado), **riesgo** (volatilidad y drawdown), **eficiencia** (Sharpe: retorno obtenido por cada unidad de riesgo), **sensibilidad al mercado** (beta frente al ICOLCAP) y **diversificación** (correlación entre activos). Ningún indicador responde la pregunta por sí solo: hay que leerlos juntos.

**Lectura inicial:** Cibest tuvo el mayor retorno (30,22 % anual) y el mejor Sharpe (0,84), por encima del mercado (ICOLCAP: 17,21 % y 0,73). Su retorno fue 1,76 veces el del mercado y su volatilidad 1,78 veces, por lo que su ventaja en Sharpe es real pero moderada: ganó más, pero asumiendo proporcionalmente más riesgo. Ecopetrol y Éxito rindieron menos que el mercado con una volatilidad de más del doble (37,80 % y 44,56 % frente a 18,00 %).

## 5. Diseño de la aplicación · S25

- **Usuarios previstos:** Estudiantes, inversionistas principiantes y docentes que quieran comparar riesgo y rendimiento entre activos.
- **Entradas y filtros:** Selección de activos (más un ticker libre), rango de fechas, tasa libre de riesgo, ventana de volatilidad móvil y referencia de mercado.
- **Secciones de la interfaz:** Resumen · Precios · Riesgo · Correlación · Conclusiones.
- **Resultados visibles:** Tabla de indicadores, mapa riesgo-retorno, gráficos de precio, drawdown, volatilidad, histograma, mapa de calor, lectura automática de resultados y descarga en CSV.
- **Interacción principal:** Al cambiar activos, fechas o parámetros, la app vuelve a descargar los datos (con caché de 1 hora), recalcula todos los indicadores y actualiza gráficos y conclusiones.

**Flujo previsto:**  
Selección de activos y parámetros → Descarga con yfinance → Alineación de fechas y cálculo de retornos → Indicadores y gráficos → Lectura automática e interpretación.

**Boceto o esquema:** 

**Decisión técnica:** Python por su ecosistema financiero (`pandas`, `numpy`) y acceso directo a datos con `yfinance`. Streamlit permite construir una interfaz interactiva sin programar frontend. Separamos los cálculos en `metricas.py` para poder probarlos de forma independiente.

## 6. Construcción y pruebas · S26 (5 de noviembre)

- **Componentes implementados:** Código escrito para todas las secciones descritas arriba. **[Actualiza este punto con lo que verifiques que funciona en el laboratorio.]**
- **Cómo ejecutar la aplicación:**
  ```bash
  pip install -r requirements.txt
  streamlit run app.py
  ```
- **Dependencias:** `requirements.txt` (streamlit, yfinance, pandas, numpy, plotly)
- **Pruebas realizadas:**

| Caso | Resultado esperado | Resultado obtenido |
|---|---|---|
| Beta del benchmark contra sí mismo (datos sintéticos) | 1.00 | 1.00 ✅ |
| Drawdown siempre ≤ 0 (datos sintéticos) | Verdadero | Verdadero ✅ |
| Base 100 inicia en 100 (datos sintéticos) | 100 en todos los activos | 100 ✅ |
| Descarga real con EXITO.CL, ECOPETROL.CL, PFCIBEST.CL, ICOLCAP.CL | Tabla con 4 filas | [Pendiente de probar] |
| Ticker inválido | Aviso y exclusión del activo | [Pendiente de probar] |
| Fecha inicial posterior a la final | Mensaje de error | [Pendiente de probar] |

- **Errores conocidos y cómo se resolvieron:** [Completa durante el laboratorio]
- **Pendientes antes del simulacro:** Desplegar en Streamlit Community Cloud, probar con datos reales, completar el boceto e integrantes.

## 7. Hallazgos e interpretación · S26–S28

*Completa con los resultados reales de la app. Plantilla para cada hallazgo:*

1. **Evidencia:**
   Hallazgo 1: Cibest ofreció la mejor relación rendimiento-riesgo
**Evidencia:** tabla de indicadores (sección 4) y mapa riesgo-retorno. 
<img width="1226" height="447" alt="image" src="https://github.com/user-attachments/assets/ed0f05ae-ed77-4c14-8dca-3e4a813c0719" />
**Qué muestra:** `PFCIBEST.CL` tuvo el mayor retorno anualizado (30,22 %) y el Sharpe más alto (0,84), por encima del mercado (ICOLCAP: 17,21 % y 0,73), con una volatilidad mayor (31,97 % frente a 18,00 %).
**Interpretación financiera:** el retorno adicional compensó con creces el riesgo adicional: una inversión de 100 habría llegado a 373,6.
**Limitaciones:** el Sharpe usa una tasa libre de riesgo de 4 %, que no es una referencia colombiana; con tasas más altas los valores bajan. Un periodo de cinco años no garantiza que el resultado se repita.

### Hallazgo 2: Éxito fue el más riesgoso y rindió menos que el mercado
**Evidencia:** volatilidad de 44,56 %, drawdown máximo de −66,59 % y Sharpe de 0,30. 
<img width="1242" height="415" alt="image" src="https://github.com/user-attachments/assets/ac06f929-228b-4d6d-a991-52e1a8aec155" />
**Qué muestra:** su precio cayó desde el máximo del 25 de marzo de 2022 hasta el mínimo del 11 de abril de 2025 (−66,6 %). Después se recuperó hasta cerrar en 147,8 (base 100).
**Interpretación financiera:** rindió menos que el mercado (8,14 % frente a 17,21 % anual) con más del doble de volatilidad, así que su riesgo no fue compensado. La fuerte recuperación posterior merece explicarse con una fuente verificada, por ejemplo el cambio de control accionario. 
**Limitaciones:** acción de baja liquidez y con cambios corporativos, que pueden generar saltos en el historial.

### Hallazgo 3: Éxito es el mejor diversificador
**Evidencia:** mapa de calor de correlación. 
<img width="1254" height="455" alt="image" src="https://github.com/user-attachments/assets/97c939b5-548f-439b-9eb5-62cff8988e17" />
**Qué muestra:** Éxito tiene correlaciones bajas con todos los demás (0,15 con Ecopetrol, 0,17 con ICOLCAP y 0,19 con Cibest), mientras que Cibest e ICOLCAP están más relacionados (0,53) y Ecopetrol con Cibest (0,47). Su beta es de 0,43.
**Interpretación financiera:** Éxito se movió de forma casi independiente del resto, por lo que combinarlo con Ecopetrol u otras acciones reduciría el riesgo conjunto, aunque por sí solo tuvo el peor Sharpe del grupo.
**Limitaciones:** la correlación se calculó con retornos diarios y puede cambiar en crisis. El ICOLCAP incluye a estas mismas empresas, por lo que sus correlaciones y betas pueden estar sesgados al alza.

### Hallazgo 4: Ecopetrol rindió menos que el mercado con el doble de riesgo
**Evidencia:** tabla de indicadores y gráfico de crecimiento base 100.
<img width="1239" height="463" alt="image" src="https://github.com/user-attachments/assets/08561dac-b4be-4dab-b5bf-f93af2bc1e2c" />
**Qué muestra:** retorno anualizado de 13,33 % frente a 17,21 % del ICOLCAP, volatilidad de 37,80 % (más del doble) y Sharpe de 0,41. Ecopetrol y Cibest tocaron su mínimo el mismo día, el 26 de septiembre de 2022 (−38,0 % y −32,6 %); el ICOLCAP lo hizo el 23 de marzo de 2023 (−30,2 %).
**Interpretación financiera:** su desempeño dependió más de factores propios del sector petrolero que del mercado en general (beta de 0,82).
**Limitaciones:** el análisis es descriptivo y no explica las causas de cada movimiento.

**Conclusión:** entre Éxito, Ecopetrol y Cibest, **Cibest (`PFCIBEST.CL`) ofreció la mejor relación rendimiento-riesgo** (Sharpe de 0,84), superando incluso al mercado colombiano (ICOLCAP, 0,73). Ecopetrol (0,41) y Éxito (0,30) rindieron menos que el mercado con mucho más riesgo. Éxito fue el más volátil (44,56 %) y el de mayor caída (−66,59 %), pero también el mejor diversificador (correlación de 0,15 con Ecopetrol).

> Los resultados históricos no garantizan rendimientos futuros.


## 8. Simulacro · S27 (10 de noviembre)

**Guion de sustentación (3–5 minutos):**
1. **Problema (30 s):** comparar riesgo y rendimiento de Éxito, Ecopetrol, Cibest y el mercado colombiano (COLCAP).
2. **Datos y metodología (45 s):** Yahoo Finance, 5 años diarios; retorno, volatilidad, Sharpe, drawdown, beta y correlación.
3. **Demostración (90 s):** cambiar activos y fechas, mostrar mapa riesgo-retorno y drawdown.
4. **Hallazgos (60 s):** activo con mejor Sharpe, más volátil y mejor diversificador.
5. **Conclusión y limitaciones (30 s):** análisis descriptivo, no predictivo.

**Retroalimentación recibida:** [Observaciones del docente o compañeros]

| Ajuste necesario | Responsable | Estado |
|---|---|---|
| [Ajuste] | [Integrante] | [Pendiente] |

## 9. Presentación final · S28 (12 de noviembre)

- **Enlace funcional de la aplicación:** [URL]
- **Versión final / commit:** [Enlace]
- **Evidencia de presentación:** [Enlace autorizado]
- **Conclusiones finales:** [Síntesis]
- **Limitaciones y posibles mejoras:** Solo se usan fechas comunes; no se modelan costos de transacción ni impuestos; mejoras posibles: optimización de portafolio (frontera eficiente).

## 10. Bitácora de trabajo y aportes

| Fecha | Integrante(s) | Investigación o decisión | Avance técnico / evidencia | Próximo paso |
|---|---|---|---|---|
| 2026-11-03 | Isabella Hincapie Manuela Bohorquez - Yuliana Pineda | Nombre del equipo (STATTUM), pregunta y activos | Decisión de como se iba a trabajar, preguntas a resolver y objetivos | Elegir tickers a analizar |
| 2026-11-05 | Isabella Hincapie Manuela Bohorquez - Yuliana Pineda | Codigo base  | Se ejecutó el notebook en Google Colab con datos reales de Yahoo Finance: la descarga funcionó para los 4 activos y se obtuvo la tabla de indicadores. Primer resultado: Cibest con el mejor Sharpe y Éxito con la mayor caída (−66,59 %). |Verificar los símbolos `.CL` en Yahoo Finance, fijar el período del análisis, preparar las capturas y publicar la app en Streamlit. |
| 2026-11-10 | [Nombre] | [Retroalimentación] | [Cambio] | [Acción] |

## Fundamento en los recursos de consulta

| Recurso | Qué tomamos de él | Dónde se usa |
|---|---|---|
| [yfinance](https://ranaroussi.github.io/yfinance/) | `yf.download` con varios tickers a la vez. La fecha `start` es inclusiva y `end` es exclusiva, por eso la app suma un día a la fecha final. Se fija `auto_adjust=True` para usar precios ajustados. Con varios tickers devuelve columnas multinivel; la app toma `["Close"]`. | `app.py` → `cargar_precios` |
| [pandas](https://pandas.pydata.org/docs/) | `pct_change` (retornos), `rolling` (medias y volatilidad móvil), `cummax` (drawdown), `corr` y `cov` | `metricas.py` y `app.py` |
| [Streamlit](https://docs.streamlit.io/) | `st.sidebar`, `st.multiselect`, `st.slider`, `st.tabs`, `st.cache_data` (caché de descargas) y `st.download_button` | `app.py` |
| [Shiny para R](https://shiny.posit.co/r/) | Descartado: el proyecto se implementa en Python + Streamlit. Se conserva como alternativa equivalente. | Decisión técnica (sección 5) |

**Extensión opcional con empresas colombianas:** la app permite agregar tickers propios (por ejemplo, acciones de la BVC). Se debe verificar cada símbolo en Yahoo Finance y declarar que sus precios están en pesos colombianos y que son menos líquidos, lo que genera días sin datos (hay una opción para rellenar huecos de hasta 5 días).

## Recursos de consulta

- [Libro de programación y analítica financiera del curso](https://github.com/vyolete/proyecto_analitica_financiera)
- [Documentación de yfinance](https://ranaroussi.github.io/yfinance/)
- [Documentación de pandas](https://pandas.pydata.org/docs/)
- [Documentación de Streamlit](https://docs.streamlit.io/)
