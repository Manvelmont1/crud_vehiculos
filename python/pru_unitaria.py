import unittest
import json
import tempfile
import os
import sqlite3
from backend import app

class TestBackend(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        app.config['TESTING'] = True
        self.app = app.test_client()

        # Crear base de datos temporal (Windows compatible)
        fd, self.temp_db_name = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        # Cambiar la base de datos en el backend
        import backend
        self.original_database = backend.DATABASE
        backend.DATABASE = self.temp_db_name

        # Crear la tabla
        db = sqlite3.connect(self.temp_db_name)
        db.execute('''CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT)''')
        db.commit()
        db.close()

    def tearDown(self):
        """Limpieza después de cada prueba"""
        import backend
        backend.DATABASE = self.original_database
        if os.path.exists(self.temp_db_name):
            os.unlink(self.temp_db_name)

    def insert_test_product(self, nombre="Producto Test", precio=10.99, descripcion="Descripción test"):
        """Helper para insertar un producto de prueba"""
        db = sqlite3.connect(self.temp_db.name)
        cursor = db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                          [nombre, precio, descripcion])
        product_id = cursor.lastrowid
        db.commit()
        db.close()
        return product_id

    def test_home_route(self):
        """Prueba la ruta principal"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_productos_empty(self):
        """Prueba obtener productos cuando la base está vacía"""
        response = self.app.get('/productos')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_post_producto(self):
        """Prueba crear un nuevo producto"""
        producto_data = {
            'nombre': 'Laptop',
            'precio': 999.99,
            'descripcion': 'Laptop gaming'
        }
        
        response = self.app.post('/productos',
                               data=json.dumps(producto_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mensaje'], 'Producto guardado correctamente')
        
        # Verificar que el producto se guardó en la base de datos
        db = sqlite3.connect(self.temp_db.name)
        cursor = db.execute('SELECT * FROM productos WHERE nombre = ?', ['Laptop'])
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], 'Laptop')
        self.assertEqual(row[2], 999.99)
        self.assertEqual(row[3], 'Laptop gaming')
        db.close()

    def test_get_productos_with_data(self):
        """Prueba obtener productos cuando hay datos"""
        # Insertar algunos productos de prueba
        self.insert_test_product("Producto 1", 10.0, "Descripción 1")
        self.insert_test_product("Producto 2", 20.0, "Descripción 2")
        
        response = self.app.get('/productos')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['nombre'], 'Producto 1')
        self.assertEqual(data[1]['nombre'], 'Producto 2')

    def test_get_producto_by_id_exists(self):
        """Prueba obtener un producto específico que existe"""
        product_id = self.insert_test_product("Producto Específico", 25.50, "Descripción específica")
        
        response = self.app.get(f'/productos/{product_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['id'], product_id)
        self.assertEqual(data['nombre'], 'Producto Específico')
        self.assertEqual(data['precio'], 25.50)
        self.assertEqual(data['descripcion'], 'Descripción específica')

    def test_get_producto_by_id_not_exists(self):
        """Prueba obtener un producto que no existe"""
        response = self.app.get('/productos/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Producto no encontrado')

    def test_put_producto_exists(self):
        """Prueba actualizar un producto existente"""
        product_id = self.insert_test_product("Producto Original", 15.0, "Descripción original")
        
        updated_data = {
            'nombre': 'Producto Actualizado',
            'precio': 30.0,
            'descripcion': 'Descripción actualizada'
        }
        
        response = self.app.put(f'/productos/{product_id}',
                              data=json.dumps(updated_data),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mensaje'], 'Producto actualizado')
        
        # Verificar que el producto se actualizó en la base de datos
        db = sqlite3.connect(self.temp_db.name)
        cursor = db.execute('SELECT * FROM productos WHERE id = ?', [product_id])
        row = cursor.fetchone()
        self.assertEqual(row[1], 'Producto Actualizado')
        self.assertEqual(row[2], 30.0)
        self.assertEqual(row[3], 'Descripción actualizada')
        db.close()

    def test_delete_producto_exists(self):
        """Prueba eliminar un producto existente"""
        product_id = self.insert_test_product("Producto a Eliminar", 5.0, "Para eliminar")
        
        response = self.app.delete(f'/productos/{product_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mensaje'], 'Producto eliminado')
        
        # Verificar que el producto fue eliminado de la base de datos
        db = sqlite3.connect(self.temp_db.name)
        cursor = db.execute('SELECT * FROM productos WHERE id = ?', [product_id])
        row = cursor.fetchone()
        self.assertIsNone(row)
        db.close()

    def test_crud_workflow_complete(self):
        """Prueba completa del flujo CRUD"""
        # CREATE
        producto_data = {
            'nombre': 'Producto CRUD',
            'precio': 45.99,
            'descripcion': 'Prueba CRUD completa'
        }
        
        response = self.app.post('/productos',
                               data=json.dumps(producto_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # READ - obtener todos los productos
        response = self.app.get('/productos')
        data = json.loads(response.data)
        product_id = data[0]['id']
        
        # READ - obtener producto específico
        response = self.app.get(f'/productos/{product_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['nombre'], 'Producto CRUD')
        
        # UPDATE
        updated_data = {
            'nombre': 'Producto CRUD Actualizado',
            'precio': 55.99,
            'descripcion': 'Descripción actualizada'
        }
        
        response = self.app.put(f'/productos/{product_id}',
                              data=json.dumps(updated_data),
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verificar actualización
        response = self.app.get(f'/productos/{product_id}')
        data = json.loads(response.data)
        self.assertEqual(data['nombre'], 'Producto CRUD Actualizado')
        
        # DELETE
        response = self.app.delete(f'/productos/{product_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verificar eliminación
        response = self.app.get(f'/productos/{product_id}')
        self.assertEqual(response.status_code, 404)

    def test_json_invalid_format(self):
        """Prueba con JSON malformado"""
        response = self.app.post('/productos',
                               data='{"nombre": "Test", "precio":}',  # JSON inválido
                               content_type='application/json')
        
        # Debería devolver error 400
        self.assertEqual(response.status_code, 400)

    def test_missing_required_fields(self):
        """Prueba con campos requeridos faltantes"""
        incomplete_data = {
            'nombre': 'Producto Incompleto'
            # Falta precio y descripcion
        }
        
        response = self.app.post('/productos',
                               data=json.dumps(incomplete_data),
                               content_type='application/json')
        
        # Debería generar un error porque falta el precio
        self.assertEqual(response.status_code, 500)


def run_all_tests():
    """Función para ejecutar todas las pruebas"""
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBackend)
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print(f"\n{'='*60}")
    print(f"RESUMEN DE PRUEBAS UNITARIAS")
    print(f"{'='*60}")
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.errors:
        print(f"\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}")
            print(f"  {error}")
    
    if result.failures:
        print(f"\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}")
            print(f"  {failure}")
    
    if result.wasSuccessful():
        print(f"\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    else:
        print(f"\n❌ ALGUNAS PRUEBAS FALLARON")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Ejecutar todas las pruebas
    success = run_all_tests()
    
    # Salir con código apropiado
    exit(0 if success else 1)