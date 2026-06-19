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

productos = productos_por_pedir()
total = valor_total_por_pedir()

print("Productos por pedir:", len(productos))
print(f"Valor total por pedir: ${total:,.2f}")

print("\nTop productos críticos:")
print(top_productos_criticos())



print("\nTop valor por pedir:")
print(top_valor_por_pedir())
