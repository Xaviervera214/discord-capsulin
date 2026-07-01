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

def alerta_valor_alto(df, top_n=10):
    productos = df[df["por_pedir"] > 0].copy()

    if productos.empty:
        return {
            "titulo": "Productos con mayor inversión por comprar",
            "prioridad": "Baja",
            "descripcion": "No hay productos con pedido sugerido.",
            "impacto": "Sin impacto económico detectado.",
            "criterio_utilizado": "Productos con pedido sugerido, ordenados por valor económico (valor_por_pedir).",
            "recomendacion": "No se requiere revisión por inversión.",
            "datos": productos
        }

    productos = productos.sort_values(
        by="valor_por_pedir",
        ascending=False
    )

    top_productos = productos.head(top_n)

    valor_total = productos["valor_por_pedir"].sum()
    valor_top = top_productos["valor_por_pedir"].sum()

    porcentaje = (valor_top / valor_total) * 100 if valor_total > 0 else 0

    return {
        "titulo": "Productos con mayor inversión por comprar",
        "prioridad": "Alta",
        "descripcion": f"Los {len(top_productos)} productos principales concentran ${valor_top:,.2f}, equivalente al {porcentaje:.2f}% del valor total por pedir.",
        "impacto": f"Los productos mostrados concentran ${valor_top:,.2f} de la inversión total por pedir.",
        "criterio_utilizado": "Productos con pedido sugerido, ordenados por mayor valor económico (valor_por_pedir).",
        "recomendacion": "Revise estos productos antes de autorizar la compra, porque concentran la mayor parte del dinero a invertir.",
        "datos": top_productos
    }

def alerta_existencia_critica(df):
    productos = df[
        (df["existencia"] <= 0) &
        (df["por_pedir"] > 0)
    ].copy()

    if productos.empty:
        return {
            "titulo": "Productos con existencia crítica",
            "prioridad": "Baja",
            "descripcion": "No se encontraron productos sin existencia y con pedido sugerido.",
            "impacto": "Sin riesgo de desabasto detectado.",
            "criterio_utilizado": "Productos con existencia menor o igual a cero y pedido sugerido mayor a cero.",
            "recomendacion": "No se requiere acción inmediata por desabasto.",
            "datos": productos
        }

    productos = productos.sort_values(
        by="por_pedir",
        ascending=False
    )

    cantidad_pareto = max(
        1,
        int(len(productos) * 0.20)
    )

    productos_pareto = productos.head(cantidad_pareto)
    productos_omitidos = len(productos) - len(productos_pareto)

    return {
        "titulo": "Productos con existencia crítica",
        "prioridad": "Alta",
        "descripcion": f"Se encontraron {len(productos)} productos sin existencia y con pedido sugerido. Se muestran los {len(productos_pareto)} más importantes según Pareto 20%. Quedan {productos_omitidos} productos fuera de este resumen.",
        "impacto": f"El grupo mostrado concentra {len(productos_pareto)} productos prioritarios de un total de {len(productos)} productos críticos.",
        "criterio_utilizado": "Productos con existencia menor o igual a cero, pedido sugerido mayor a cero, ordenados por mayor cantidad por pedir y filtrados con Pareto 20%.",
        "recomendacion": "Revise primero estos productos, porque representan el grupo prioritario para reducir el riesgo de desabasto.",
        "datos": productos_pareto
    }

def mostrar_hallazgo(hallazgo):
    print("\n" + "=" * 70)
    print(hallazgo["titulo"].upper())
    print("=" * 70)
    print(f"Prioridad: {hallazgo['prioridad']}")
    print(f"Descripción: {hallazgo['descripcion']}")
    print(f"Impacto: {hallazgo['impacto']}")
    print(f"Criterio utilizado: {hallazgo['criterio_utilizado']}")
    print(f"Recomendación: {hallazgo['recomendacion']}")

    datos = hallazgo["datos"]

    if not datos.empty:
        columnas = [
            "codigo",
            "articulo",
            "unidad",
            "existencia",
            "por_pedir",
            "ultimo_costo",
            "valor_por_pedir"
        ]

        print("\nProductos detectados:")
        print(datos[columnas].to_string(index=False))

def ejecutar_hallazgos():

    situacion = cargar_situacion()

    hallazgos = []

    hallazgos.append(
        alerta_valor_alto(situacion)
    )

    hallazgos.append(
        alerta_existencia_critica(situacion)
    )

    return hallazgos

def motor_alertas_inteligentes():

    alertas = alertas_rotacion_baja_por_pedir().copy()

    alertas["alerta_rotacion_baja"] = True
    alertas["prioridad"] = "MEDIA"

    alertas["motivo_alerta"] = (
        "Producto por pedir con rotación baja. "
        "Conviene revisar antes de incluirlo en el pedido."
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

motor_alertas = motor_alertas_inteligentes()

print("\nMotor de Alertas Inteligentes:")
print(motor_alertas[[
    "articulo",
    "existencia",
    "por_pedir",
    "rotacion",
    "prioridad",
    "motivo_alerta"
]].head(15))

hallazgos = ejecutar_hallazgos()

for hallazgo in hallazgos:
    mostrar_hallazgo(hallazgo)

