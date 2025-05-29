import requests
import threading
import time
import random

BASE_URL = 'http://127.0.0.1:5000/productos'

def crear_producto(i):
    data = {
        "nombre": f"Producto Test {i}",
        "precio": round(random.uniform(1, 100), 2),
        "descripcion": "Descripción de prueba"
    }
    response = requests.post(BASE_URL, json=data)
    print(f"Crear {i}: {response.status_code} - {response.json()}")

def editar_producto(id):
    data = {
        "nombre": f"Producto Editado {id}",
        "precio": round(random.uniform(1, 100), 2),
        "descripcion": "Descripción editada"
    }
    response = requests.put(f"{BASE_URL}/{id}", json=data)
    print(f"Editar {id}: {response.status_code} - {response.json()}")

def eliminar_producto(id):
    response = requests.delete(f"{BASE_URL}/{id}")
    print(f"Eliminar {id}: {response.status_code} - {response.json()}")

def listar_productos():
    response = requests.get(BASE_URL)
    productos = response.json()
    print(f"Listar: {len(productos)} productos")
    return productos

def prueba_estabilidad(num_iteraciones=20):
    # Crear productos
    for i in range(num_iteraciones):
        crear_producto(i)
        time.sleep(0.1)  # pequeña pausa

    # Listar productos para obtener ids
    productos = listar_productos()
    ids = [p['id'] for p in productos]

    # Editar los primeros 5 productos
    for id in ids[:5]:
        editar_producto(id)
        time.sleep(0.1)

    # Eliminar los últimos 5 productos
    for id in ids[-5:]:
        eliminar_producto(id)
        time.sleep(0.1)

    # Listar final
    listar_productos()

if __name__ == "__main__":
    prueba_estabilidad()
