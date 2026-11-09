"""Funciones de cálculo financiero (sin dependencias de Streamlit, fáciles de probar)."""
import numpy as np
import pandas as pd

DIAS_ANIO = 252  # días de negociación por año


def retornos(precios: pd.DataFrame, log: bool = False) -> pd.DataFrame:
    """Retornos diarios simples (o logarítmicos)."""
    r = np.log(precios / precios.shift(1)) if log else precios.pct_change()
    return r.dropna(how="all")


def retorno_acumulado(precios: pd.DataFrame) -> pd.Series:
    return precios.iloc[-1] / precios.iloc[0] - 1


def retorno_anualizado(precios: pd.DataFrame) -> pd.Series:
    """Tasa compuesta anual (CAGR)."""
    anios = (precios.index[-1] - precios.index[0]).days / 365.25
    return (precios.iloc[-1] / precios.iloc[0]) ** (1 / anios) - 1


def volatilidad_anual(rets: pd.DataFrame) -> pd.Series:
    return rets.std() * np.sqrt(DIAS_ANIO)


def sharpe(rets: pd.DataFrame, rf: float = 0.0) -> pd.Series:
    """Sharpe = (retorno medio anual - tasa libre de riesgo) / volatilidad anual."""
    return (rets.mean() * DIAS_ANIO - rf) / volatilidad_anual(rets)


def drawdown(precios: pd.DataFrame) -> pd.DataFrame:
    """Caída porcentual desde el máximo histórico previo."""
    return precios / precios.cummax() - 1


def max_drawdown(precios: pd.DataFrame) -> pd.Series:
    return drawdown(precios).min()


def beta(rets: pd.DataFrame, benchmark: str) -> pd.Series:
    """Beta = Cov(activo, mercado) / Var(mercado)."""
    return rets.apply(lambda s: s.cov(rets[benchmark])) / rets[benchmark].var()


def base_100(precios: pd.DataFrame) -> pd.DataFrame:
    return precios / precios.iloc[0] * 100


def resumen(precios: pd.DataFrame, rets: pd.DataFrame, rf: float, benchmark: str) -> pd.DataFrame:
    """Tabla con todos los indicadores por activo."""
    return pd.DataFrame({
        "Retorno acumulado": retorno_acumulado(precios),
        "Retorno anualizado": retorno_anualizado(precios),
        "Volatilidad anual": volatilidad_anual(rets),
        "Sharpe": sharpe(rets, rf),
        "Máx. drawdown": max_drawdown(precios),
        f"Beta vs {benchmark}": beta(rets, benchmark),
    })


def limpiar_saltos(precios: pd.DataFrame, umbral: float = 0.15, tolerancia: float = 0.10):
    """Detecta precios sospechosos: un día con retorno extremo (|r| > umbral) que se
    revierte al día siguiente (el retorno acumulado de los 2 días es casi cero).
    Ese precio intermedio se reemplaza por el del día anterior.
    Devuelve (precios_limpios, tabla_con_lo_que_se_corrigio)."""
    p = precios.copy()
    r = precios.pct_change()
    detalle = []
    for col in p.columns:
        hoy = r[col]
        sig = hoy.shift(-1)
        mascara = (hoy.abs() > umbral) & (hoy * sig < 0) & (((1 + hoy) * (1 + sig) - 1).abs() < tolerancia)
        for fecha in hoy.index[mascara.fillna(False)]:
            i = p.index.get_loc(fecha)
            detalle.append({"Fecha": fecha.date(), "Activo": col,
                            "Precio reportado": float(precios.iloc[i][col]),
                            "Retorno del día": float(hoy.loc[fecha]),
                            "Retorno siguiente": float(sig.loc[fecha])})
            p.iloc[i, p.columns.get_loc(col)] = p.iloc[i - 1, p.columns.get_loc(col)]
    columnas = ["Fecha", "Activo", "Precio reportado", "Retorno del día", "Retorno siguiente"]
    tabla = pd.DataFrame(detalle, columns=columnas)
    if len(tabla):
        tabla = tabla.sort_values(["Fecha", "Activo"]).reset_index(drop=True)
    return p, tabla
