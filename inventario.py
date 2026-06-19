import pandas as pd

ARCHIVO_SITUACION = "data/SITUACION DE INVENTARIO.xlsx"


def cargar_situacion():

    df = pd.read_excel(
        ARCHIVO_SITUACION,
        header=None
    )

    datos = df.iloc[6:].copy()

    situacion = pd.DataFrame({
        "codigo": datos.iloc[:, 0],
"articulo": datos.iloc[:, 2],
        "unidad": datos.iloc[:, 7],
        "existencia": datos.iloc[:, 10],
        "por_pedir": datos.iloc[:, 12],
        "ultimo_costo": datos.iloc[:, 14],
        "valor_por_pedir": datos.iloc[:, 17]
    })

    situacion = situacion.dropna(subset=["articulo"])

    return situacion