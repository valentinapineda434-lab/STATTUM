from datetime import date, timedelta

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

import metricas as m

st.set_page_config(page_title="Stattum | Riesgo y rendimiento", page_icon="📈", layout="wide")

CATALOGO = {
    "EXITO.CL": "Almacenes Éxito (retail, COP)",
    "ECOPETROL.CL": "Ecopetrol (energía, COP)",
    "PFCIBEST.CL": "Grupo Cibest pref. (banca, COP)",
    "ICOLCAP.CL": "iShares COLCAP (ETF, COP)",
}
DEFECTO = ["EXITO.CL", "ECOPETROL.CL", "PFCIBEST.CL", "ICOLCAP.CL"]

# Colores por activo (elegidos para que se distingan en todos los gráficos)
COLORES = {
    "EXITO.CL": "#E8B400",
    "ECOPETROL.CL": "#1B8A3D",
    "PFCIBEST.CL": "#1F4E9C",
    "ICOLCAP.CL": "#6B7280",
}
# Logos opcionales: si subes estos archivos a la carpeta assets/ del repositorio, se muestran solos
LOGOS = {
    "EXITO.CL": "assets/exito.png",
    "ECOPETROL.CL": "assets/ecopetrol.png",
    "PFCIBEST.CL": "assets/cibest.png",
    "ICOLCAP.CL": "assets/icolcap.png",
}

# ---------------- Barra lateral ----------------
st.sidebar.title("⚙️ Parámetros")
seleccion = st.sidebar.multiselect(
    "Activos", list(CATALOGO), default=DEFECTO, format_func=lambda t: f"{t} · {CATALOGO[t]}"
)
extras = st.sidebar.text_input("Otros tickers (separados por coma)", "",
                               help="Ej.: acciones de otras bolsas. Confirma el símbolo en Yahoo Finance.")
for t in [x.strip().upper() for x in extras.split(",") if x.strip()]:
    if t not in seleccion:
        seleccion.append(t)
limpiar = st.sidebar.checkbox("Corregir precios que se revierten al día siguiente", value=True,
                              help="Detecta saltos de más de 15 % que se deshacen al día siguiente (posibles errores de la fuente) y los corrige.")
rellenar = st.sidebar.checkbox("Rellenar huecos de hasta 5 días", value=True,
                               help="Útil para acciones poco líquidas con días sin negociación.")

# Periodo fijo por defecto para que los resultados coincidan con el README
inicio = st.sidebar.date_input("Fecha inicial", date(2021, 11, 9))
fin = st.sidebar.date_input("Fecha final", date(2026, 11, 6))
rf = st.sidebar.slider("Tasa libre de riesgo anual (%)", 0.0, 20.0, 4.0, 0.25) / 100
ventana = st.sidebar.slider("Ventana de volatilidad móvil (días)", 20, 120, 60)

st.markdown(
    "<style>h1{color:#0B5FA5;border-bottom:3px solid #E8B400;padding-bottom:6px;}</style>",
    unsafe_allow_html=True,
)
st.title("📈 Riesgo y rendimiento de activos financieros")
st.caption("Stattum · Los resultados históricos no garantizan rendimientos futuros.")

# Tarjetas de los activos seleccionados (con logo si existe el archivo)
if seleccion:
    columnas = st.columns(min(len(seleccion), 6))
    for col, t in zip(columnas, seleccion):
        color = COLORES.get(t, "#0B5FA5")
        with col:
            ruta = LOGOS.get(t)
            if ruta and Path(ruta).exists():
                st.image(ruta, width=90)
            st.markdown(
                f"<div style='border-left:6px solid {color};padding:6px 10px;"
                f"background:#F7F9FB;border-radius:6px;'><b>{t}</b><br>"
                f"<span style='font-size:0.8em;color:#4B5563'>{CATALOGO.get(t, 'Activo adicional')}</span></div>",
                unsafe_allow_html=True,
            )

if len(seleccion) < 2:
    st.info("Selecciona al menos 2 activos para comparar.")
    st.stop()
if inicio >= fin:
    st.error("La fecha inicial debe ser anterior a la final.")
    st.stop()

benchmark = st.sidebar.selectbox(
    "Referencia de mercado (para beta)", seleccion,
    index=seleccion.index("ICOLCAP.CL") if "ICOLCAP.CL" in seleccion else 0,
)


# ---------------- Datos ----------------
@st.cache_data(ttl=3600, show_spinner="Descargando datos de Yahoo Finance...")
def cargar_precios(tickers: tuple, inicio: str, fin: str) -> pd.DataFrame:
    df = yf.download(list(tickers), start=inicio, end=fin, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(tickers[0])
    return df


try:
    # En yfinance la fecha final es exclusiva; se suma 1 día para incluirla
    crudo = cargar_precios(tuple(seleccion), str(inicio), str(fin + timedelta(days=1)))
except Exception as e:
    st.error(f"No se pudieron descargar los datos: {e}")
    st.stop()

sin_datos = [t for t in seleccion if t not in crudo.columns or crudo[t].dropna().empty]
if sin_datos:
    st.warning(f"Sin datos para: {', '.join(sin_datos)}. Se excluyen del análisis.")
precios = crudo.drop(columns=sin_datos, errors="ignore")

if rellenar:
    precios = precios.ffill(limit=5)

# Se conservan solo las fechas comunes a todos los activos (p. ej. días bursátiles)
precios = precios.dropna()
if precios.shape[1] < 2 or len(precios) < 30:
    st.error("No hay suficientes datos comunes para analizar. Amplía el periodo o cambia los activos.")
    st.stop()
if benchmark not in precios.columns:
    benchmark = precios.columns[0]

saltos = pd.DataFrame()
if limpiar:
    precios, saltos = m.limpiar_saltos(precios)
    if len(saltos):
        st.info(f"Se corrigieron {len(saltos)} precios sospechosos (saltos que se revierten al día siguiente).")
        with st.expander("Ver precios corregidos"):
            st.dataframe(saltos.style.format({"Precio reportado": "{:,.0f}", "Retorno del día": "{:.1%}",
                                              "Retorno siguiente": "{:.1%}"}), width="stretch")

rets = m.retornos(precios)
tabla = m.resumen(precios, rets, rf, benchmark)

# ---------------- Pestañas ----------------
t1, t2, t3, t4, t5 = st.tabs(["Resumen", "Precios", "Riesgo", "Correlación", "Conclusiones"])

with t1:
    st.subheader("Indicadores por activo")
    fmt = {c: "{:.2%}" for c in ["Retorno acumulado", "Retorno anualizado", "Volatilidad anual", "Máx. drawdown"]}
    fmt.update({"Sharpe": "{:.2f}", f"Beta vs {benchmark}": "{:.2f}"})
    st.dataframe(tabla.style.format(fmt), width="stretch")

    st.subheader("Mapa riesgo-retorno")
    dfp = tabla.reset_index().rename(columns={"index": "Activo", "Ticker": "Activo"})
    dfp.columns = ["Activo"] + list(dfp.columns[1:])
    fig = px.scatter(dfp, x="Volatilidad anual", y="Retorno anualizado", text="Activo",
                     color="Activo", color_discrete_map=COLORES,
                     hover_data={"Sharpe": ":.2f", "Activo": False})
    fig.update_traces(marker=dict(size=16), textposition="top center")
    fig.update_layout(xaxis_tickformat=".0%", yaxis_tickformat=".0%", height=450)
    st.plotly_chart(fig, width="stretch")
    st.caption("Más a la izquierda y arriba = menos riesgo y más retorno.")

with t2:
    st.subheader("Crecimiento de una inversión de 100")
    fig = px.line(m.base_100(precios), color_discrete_map=COLORES)
    fig.update_layout(yaxis_title="Valor (base 100)", xaxis_title="", legend_title="", height=450)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Tendencia con medias móviles")
    activo = st.selectbox("Activo", precios.columns)
    c1, c2 = st.columns(2)
    corta = c1.slider("Media corta (días)", 5, 50, 20)
    larga = c2.slider("Media larga (días)", 50, 200, 100)
    serie = precios[activo]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=serie.index, y=serie, name="Precio", line=dict(color=COLORES.get(activo))))
    fig.add_trace(go.Scatter(x=serie.index, y=serie.rolling(corta).mean(), name=f"MA {corta}"))
    fig.add_trace(go.Scatter(x=serie.index, y=serie.rolling(larga).mean(), name=f"MA {larga}"))
    fig.update_layout(height=400)
    st.plotly_chart(fig, width="stretch")

with t3:
    st.subheader("Drawdown (caída desde el máximo)")
    fig = px.line(m.drawdown(precios), color_discrete_map=COLORES)
    fig.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="", legend_title="", height=400)
    st.plotly_chart(fig, width="stretch")

    st.subheader(f"Volatilidad móvil anualizada ({ventana} días)")
    vol_m = rets.rolling(ventana).std() * (m.DIAS_ANIO ** 0.5)
    fig = px.line(vol_m.dropna(), color_discrete_map=COLORES)
    fig.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="", legend_title="", height=400)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Distribución de retornos diarios")
    largo = rets.melt(var_name="Activo", value_name="Retorno")
    fig = px.histogram(largo, x="Retorno", color="Activo", nbins=80, barmode="overlay", opacity=0.6,
                       color_discrete_map=COLORES)
    fig.update_layout(xaxis_tickformat=".0%", height=400)
    st.plotly_chart(fig, width="stretch")

with t4:
    st.subheader("Correlación de retornos diarios")
    fig = px.imshow(rets.corr(), text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    fig.update_layout(height=450)
    st.plotly_chart(fig, width="stretch")
    st.caption("Correlación baja o negativa entre activos ayuda a diversificar el riesgo.")

with t5:
    st.subheader("Lectura automática de los resultados")
    mejor_sh = tabla["Sharpe"].idxmax()
    mas_vol = tabla["Volatilidad anual"].idxmax()
    menos_vol = tabla["Volatilidad anual"].idxmin()
    mejor_ret = tabla["Retorno anualizado"].idxmax()
    peor_dd = tabla["Máx. drawdown"].idxmin()

    corr = rets.corr()
    pares = [(a, b, corr.loc[a, b]) for i, a in enumerate(corr.columns) for b in corr.columns[i + 1:]]
    a, b, c = min(pares, key=lambda p: p[2])

    st.markdown(f"""
- **Mayor retorno anualizado:** {mejor_ret} ({tabla.loc[mejor_ret, 'Retorno anualizado']:.1%}).
- **Mejor relación retorno/riesgo (Sharpe):** {mejor_sh} ({tabla.loc[mejor_sh, 'Sharpe']:.2f}).
- **Más volátil:** {mas_vol} ({tabla.loc[mas_vol, 'Volatilidad anual']:.1%}); **menos volátil:** {menos_vol} ({tabla.loc[menos_vol, 'Volatilidad anual']:.1%}).
- **Mayor caída desde un máximo:** {peor_dd} ({tabla.loc[peor_dd, 'Máx. drawdown']:.1%}).
- **Par con menor correlación (mejor diversificador):** {a} y {b} ({c:.2f}).
""")
    st.warning(
        "Limitaciones: el análisis es descriptivo y usa solo el pasado; no predice precios futuros ni "
        "constituye una recomendación de inversión. Solo se usan fechas comunes a todos los activos."
    )
    st.download_button("⬇️ Descargar indicadores (CSV)", tabla.to_csv().encode("utf-8"),
                       "indicadores.csv", "text/csv")
