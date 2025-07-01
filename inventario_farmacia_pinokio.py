import gradio as gr
import pandas as pd
import os
from datetime import datetime

# Archivos base
PRODUCTOS_CSV = "productos.csv"
MOVIMIENTOS_CSV = "movimientos.csv"

# Inicializar CSV si no existen
def inicializar_csv():
    if not os.path.exists(PRODUCTOS_CSV):
        df = pd.DataFrame(columns=["SKU", "Nombre", "Categoría", "Unidad"])
        df.to_csv(PRODUCTOS_CSV, index=False)
    if not os.path.exists(MOVIMIENTOS_CSV):
        df = pd.DataFrame(columns=["Fecha/Hora", "Tipo", "SKU", "Cantidad", "Observaciones"])
        df.to_csv(MOVIMIENTOS_CSV, index=False)

# Cargar data
def cargar_datos():
    productos = pd.read_csv(PRODUCTOS_CSV)
    movimientos = pd.read_csv(MOVIMIENTOS_CSV)
    return productos, movimientos

# Guardar movimiento y actualizar stock
def registrar_movimiento(tipo, sku, cantidad, observaciones):
    productos, movimientos = cargar_datos()

    if sku not in productos.SKU.values:
        return f"SKU {sku} no encontrado. Agrega el producto primero."

    # Agregar movimiento
    nuevo = pd.DataFrame([{
        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Tipo": tipo,
        "SKU": sku,
        "Cantidad": cantidad,
        "Observaciones": observaciones
    }])
    movimientos = pd.concat([movimientos, nuevo], ignore_index=True)
    movimientos.to_csv(MOVIMIENTOS_CSV, index=False)
    return f"Movimiento registrado: {tipo} de {cantidad} unidades para SKU {sku}."

# Agregar nuevo producto
def agregar_producto(sku, nombre, categoria, unidad):
    productos, _ = cargar_datos()
    if sku in productos.SKU.values:
        return f"El SKU {sku} ya existe."
    nuevo = pd.DataFrame([[sku, nombre, categoria, unidad]], columns=productos.columns)
    productos = pd.concat([productos, nuevo], ignore_index=True)
    productos.to_csv(PRODUCTOS_CSV, index=False)
    return f"Producto agregado: {nombre} (SKU: {sku})"

# Ver stock actual
def ver_stock():
    productos, movimientos = cargar_datos()
    productos["Stock"] = productos["SKU"].apply(lambda sku: calcular_stock(sku, movimientos))
    return productos[["SKU", "Nombre", "Categoría", "Unidad", "Stock"]]

def calcular_stock(sku, movimientos):
    entradas = movimientos[(movimientos.SKU == sku) & (movimientos.Tipo == "Entrada")]["Cantidad"].sum()
    salidas = movimientos[(movimientos.SKU == sku) & (movimientos.Tipo == "Salida")]["Cantidad"].sum()
    return entradas - salidas

# Inicializar archivos CSV
inicializar_csv()

# Interfaz Gradio
def interfaz():
    with gr.Blocks() as demo:
        gr.Markdown("# Inventario de Farmacia | Modo escáner código de barras")

        with gr.Tab("Registrar Movimiento"):
            tipo = gr.Dropdown(["Entrada", "Salida"], label="Tipo de Movimiento")
            sku = gr.Textbox(label="SKU (Escanea o escribe)")
            cantidad = gr.Number(label="Cantidad", value=1)
            observaciones = gr.Textbox(label="Observaciones", lines=1)
            btn_registrar = gr.Button("Registrar")
            salida_mov = gr.Textbox(label="Resultado", interactive=False)

            btn_registrar.click(fn=registrar_movimiento, inputs=[tipo, sku, cantidad, observaciones], outputs=salida_mov)

        with gr.Tab("Agregar Producto"):
            new_sku = gr.Textbox(label="Nuevo SKU")
            nombre = gr.Textbox(label="Nombre del Producto")
            categoria = gr.Textbox(label="Categoría")
            unidad = gr.Textbox(label="Unidad")
            btn_agregar = gr.Button("Agregar Producto")
            salida_prod = gr.Textbox(label="Resultado", interactive=False)

            btn_agregar.click(fn=agregar_producto, inputs=[new_sku, nombre, categoria, unidad], outputs=salida_prod)

        with gr.Tab("Ver Stock"):
            btn_ver = gr.Button("Actualizar Stock")
            tabla = gr.Dataframe(label="Stock Actual")
            btn_ver.click(fn=ver_stock, outputs=tabla)

    return demo

interfaz().launch()
