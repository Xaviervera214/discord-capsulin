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

def cargar_rotacion():
    archivo = "data/ROTACION DE INVENTARIO.xlsx"
    rotacion = pd.read_excel(archivo, header=None)
    return rotacion

def productos_por_pedir():
    situacion = cargar_situacion()
    productos = situacion[situacion["por_pedir"] > 0].copy()
    return productos

def valor_total_por_pedir():
    productos = productos_por_pedir()
    total = productos["valor_por_pedir"].sum()
    return total

def top_productos_criticos():
    
    productos = productos_por_pedir()
    top = productos.sort_values(by="por_pedir", ascending=False)
    return top.head(10)

def top_valor_por_pedir():

    productos = productos_por_pedir()
    top = productos.sort_values(by="valor_por_pedir", ascending=False)
    return top.head(10)


def resumen_ejecutivo():

    productos = productos_por_pedir()

    total_productos = len(productos)
    valor_total = valor_total_por_pedir()

    producto_critico = top_productos_criticos().iloc[0]
    producto_valor = top_valor_por_pedir().iloc[0]

    resumen = f"""
RESUMEN CAPSULIN
----------------------------------------
Productos por pedir: {total_productos}
Valor total por pedir: ${valor_total:,.2f}

Mayor urgencia:
{producto_critico["articulo"]}
Por pedir: {producto_critico["por_pedir"]}

Mayor inversión:
{producto_valor["articulo"]}
Valor por pedir: ${producto_valor["valor_por_pedir"]:,.2f}
"""

    return resumen

productos = productos_por_pedir()
total = valor_total_por_pedir()

print("Productos por pedir:", len(productos))
print(f"Valor total por pedir: ${total:,.2f}")

print("\nTop productos críticos:")
print(top_productos_criticos())



print("\nTop valor por pedir:")
print(top_valor_por_pedir())

print("\nResumen ejecutivo:")
print(resumen_ejecutivo())

situacion = cargar_situacion()
print(situacion.columns)

rotacion = cargar_rotacion()

def rotacion_limpia():

    df = cargar_rotacion()

    datos = df.iloc[6:].copy()

    rotacion = pd.DataFrame({
        "articulo": datos.iloc[:, 0],
        "unidad": datos.iloc[:, 9],
        "salidas": datos.iloc[:, 13],
        "inventario_promedio": datos.iloc[:, 16],
        "rotacion": datos.iloc[:, 18]
    })

    rotacion = rotacion.dropna(subset=["articulo"])

    rotacion["salidas"] = pd.to_numeric(
        rotacion["salidas"],
        errors="coerce"
    )

    rotacion["inventario_promedio"] = pd.to_numeric(
        rotacion["inventario_promedio"],
        errors="coerce"
    )

    rotacion["rotacion"] = pd.to_numeric(
        rotacion["rotacion"],
        errors="coerce"
    )

    return rotacion

def productos_rotacion_baja():

    rotacion = rotacion_limpia()

    productos = rotacion[
        rotacion["rotacion"] < 0.5
    ].copy()

    return productos


def productos_sin_salidas():

    rotacion = rotacion_limpia()

    productos = rotacion[
        rotacion["salidas"] == 0
    ].copy()

    return productos

def productos_por_pedir_sin_salidas():

    productos = productos_por_pedir()
    sin_salidas = productos_sin_salidas()

    resultado = productos.merge(
        sin_salidas,
        on="articulo",
        how="inner",
        suffixes=("_situacion", "_rotacion")
    )

    return resultado

def alertas_rotacion_baja_por_pedir():

    productos = productos_por_pedir()
    rotacion_baja = productos_rotacion_baja()

    alertas = productos.merge(
        rotacion_baja,
        on="articulo",
        how="inner",
        suffixes=("_situacion", "_rotacion")
    )

    return alertas

rotacion_baja = productos_rotacion_baja()

print("\nProductos con rotación baja:")
print(len(rotacion_baja))

sin_salidas = productos_sin_salidas()

print("\nProductos sin salidas:")
print(len(sin_salidas))
sospechosos = productos_por_pedir_sin_salidas()

print("\nProductos por pedir sin salidas:")
print(len(sospechosos))

print("\nSospechosos:")
print(sospechosos[[
    "articulo",
    "por_pedir",
    "existencia"
]])

alertas = alertas_rotacion_baja_por_pedir()

print("\nAlertas: productos por pedir con rotación baja:")
print(len(alertas))

print(alertas[[
    "articulo",
    "existencia",
    "por_pedir",
    "rotacion"
]].head(15))