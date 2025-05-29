import requests

BASE_URL = 'http://127.0.0.1:5000'

print("=== PRUEBA DE CAJA GRIS ===")

# 1. Probar GET /productos (debería responder con lista)
print("Probando GET /productos")
response = requests.get(f'{BASE_URL}/productos')
assert response.status_code == 200, "Error al hacer GET /productos"
productos = response.json()
print(f"Productos encontrados: {len(productos)}")

# 2. Probar POST /productos
print("Probando POST /productos")
nuevo_producto = {
    "nombre": "Chevrolet Camaro",
    "precio": 45000,
    "descripcion": "Deportivo 2023"
}
response = requests.post(f'{BASE_URL}/productos', json=nuevo_producto)
assert response.status_code == 200, "Error al hacer POST /productos"
print(f"Producto creado: {response.json()['mensaje']}")

# 3. Verificar que el producto fue creado (GET de nuevo)
productos = requests.get(f'{BASE_URL}/productos').json()
ultimo = productos[-1]
print(f"Último producto creado: ID={ultimo['id']}, Nombre={ultimo['nombre']}")

# 4. Probar PUT /productos/<id>
print("Probando PUT /productos/<id>")
editar = {
    "nombre": "Chevrolet Camaro ZL1",
    "precio": 47000,
    "descripcion": "Actualizado"
}
response = requests.put(f"{BASE_URL}/productos/{ultimo['id']}", json=editar)
assert response.status_code == 200, "Error al hacer PUT"
print(f"Actualización exitosa: {response.json()['mensaje']}")

# 5. Verificar GET por ID
print("Probando GET /productos/<id>")
response = requests.get(f"{BASE_URL}/productos/{ultimo['id']}")
assert response.status_code == 200, "Error al hacer GET por ID"
data = response.json()
assert data['nombre'] == "Chevrolet Camaro ZL1", "El nombre no fue actualizado correctamente"
print("Producto actualizado correctamente")

# 6. Probar DELETE /productos/<id>
print("Probando DELETE /productos/<id>")
response = requests.delete(f"{BASE_URL}/productos/{ultimo['id']}")
assert response.status_code == 200, "Error al hacer DELETE"
print("Producto eliminado:", response.json()['mensaje'])

# 7. Confirmar que fue eliminado
print("Verificando eliminación")
response = requests.get(f"{BASE_URL}/productos/{ultimo['id']}")
assert response.status_code == 404, "El producto aún existe después del DELETE"
print("Eliminación confirmada")

print("=== TODAS LAS PRUEBAS DE CAJA GRIS PASARON ===")
