import csv
import random
from datetime import datetime, timedelta

random.seed(42)
N = 200000

CATEGORIAS = ["Electronica", "Hogar", "Moda", "Deportes", "Belleza"]
MEDIOS_PAGO = ["tarjeta", "PSE", "contraentrega"]
CIUDADES = ["Cali", "Bogota", "Medellin", "Barranquilla", "Bucaramanga"]

inicio = datetime(2025, 1, 1)
segundos_anio = 365 * 24 * 3600 - 1

escritas = 0
with open("ventas_ecommerce.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["order_id", "customer_id", "category", "quantity",
                "unit_price", "payment_method", "city", "order_date"])
    for i in range(1, N + 1):
        fecha = inicio + timedelta(seconds=random.randint(0, segundos_anio))
        fila = [
            i,
            random.randint(1, 5000),
            random.choice(CATEGORIAS),
            random.randint(1, 5),
            random.randint(10, 500) * 1000,
            random.choice(MEDIOS_PAGO),
            random.choice(CIUDADES),
            fecha.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        r = random.random()
        if r < 0.02:
            fila[2] = ""
        elif r < 0.04:
            fila[3] = -1
        elif r < 0.05:
            fila[7] = ""
        w.writerow(fila)
        escritas += 1
        if random.random() < 0.01:
            w.writerow(fila)
            escritas += 1

print("Filas de datos escritas:", escritas)
