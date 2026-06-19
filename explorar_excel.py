import pandas as pd

archivo = "data/VENTAS POR ARTICULO.xlsx"

df = pd.read_excel(archivo, header=None)

print(df.iloc[0:15, 0:25].to_string())