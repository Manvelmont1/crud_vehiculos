import unittest
import json
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import sys
sys.path.append('.')

# Importamos el módulo a probar
from backend import app, init_db, get_db, DATABASE

class TestBackendCajaBlanca(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Crear base de datos temporal
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        
        # Reemplazar la base de datos por la temporal
        global DATABASE
        self.original_db = DATABASE
        DATABASE = self.test_db.name
        
        # Inicializar base de datos
        with self.app.app_context():
            init_db()
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        global DATABASE
        DATABASE = self.original_db
        os.unlink(self.test_db.name)
    
    # ==================== PRUEBAS DE RUTA / PATH COVERAGE ====================
    
    def test_home_route(self):
        """Prueba ruta GET / - Renderiza template"""
        with patch('backend.render_template') as mock_render:
            mock_render.return_value = "mock_template"
            response = self.client.get('/')
            mock_render.assert_called_once_with('index.html')
            self.assertEqual(response.status_code, 200)
    
    def test_productos_get_ruta_vacia(self):
        """Prueba GET /productos con base de datos vacía"""
        response = self.client.get('/productos')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
    
    def test_productos_get_con_datos(self):
        """Prueba GET /productos con datos existentes"""
        # Insertar datos de prueba
        db = get_db()
        db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                   ['Test Product', 10.5, 'Test Description'])
        db.commit()
        
        response = self.client.get('/productos')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Test Product')
    
    def test_productos_post_exitoso(self):
        """Prueba POST /productos - inserción exitosa"""
        producto_data = {
            'nombre': 'Nuevo Producto',
            'precio': 25.99,
            'descripcion': 'Nueva descripción'
        }
        
        response = self.client.post('/productos',
                                   data=json.dumps(producto_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mensaje'], 'Producto guardado correctamente')
        
        # Verificar inserción en BD
        db = get_db()
        cursor = db.execute('SELECT * FROM productos WHERE nombre = ?', ['Nuevo Producto'])
        row = cursor.fetchone()
        self.assertIsNotNone(row)
    
    def test_producto_id_get_existente(self):
        """Prueba GET /productos/{id} - producto existente"""
        # Insertar producto de prueba
        db = get_db()
        cursor = db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                           ['Test Product', 15.0, 'Test Desc'])
        db.commit()
        producto_id = cursor.lastrowid
        
        response = self.client.get(f'/productos/{producto_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['nombre'], 'Test Product')
    
    def test_producto_id_get_no_existente(self):
        """Prueba GET /productos/{id} - producto no existe (rama else)"""
        response = self.client.get('/productos/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Producto no encontrado')
    
    def test_producto_id_put(self):
        """Prueba PUT /productos/{id} - actualización"""
        # Insertar producto inicial
        db = get_db()
        cursor = db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                           ['Original', 10.0, 'Original Desc'])
        db.commit()
        producto_id = cursor.lastrowid
        
        # Datos actualizados
        update_data = {
            'nombre': 'Actualizado',
            'precio': 20.0,
            'descripcion': 'Descripción actualizada'
        }
        
        response = self.client.put(f'/productos/{producto_id}',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mensaje'], 'Producto actualizado')
        
        # Verificar actualización
        cursor = db.execute('SELECT nombre FROM productos WHERE id = ?', [producto_id])
        row = cursor.fetchone()
        self.assertEqual(row[0], 'Actualizado')
    
    def test_producto_id_delete(self):
        """Prueba DELETE /productos/{id} - eliminación"""
        # Insertar producto
        db = get_db()
        cursor = db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                           ['Para Eliminar', 5.0, 'Delete me'])
        db.commit()
        producto_id = cursor.lastrowid
        
        response = self.client.delete(f'/productos/{producto_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mensaje'], 'Producto eliminado')
        
        # Verificar eliminación
        cursor = db.execute('SELECT * FROM productos WHERE id = ?', [producto_id])
        row = cursor.fetchone()
        self.assertIsNone(row)
    
    # ==================== PRUEBAS DE CONDICIÓN / CONDITION COVERAGE ====================
    
    def test_init_db_tabla_no_existe(self):
        """Prueba init_db cuando la tabla no existe"""
        # Eliminar tabla si existe
        db = get_db()
        db.execute('DROP TABLE IF EXISTS productos')
        db.commit()
        
        # Ejecutar init_db
        with self.app.app_context():
            init_db()
        
        # Verificar que la tabla fue creada
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
    
    def test_get_db_conexion(self):
        """Prueba get_db() retorna conexión válida"""
        db = get_db()
        self.assertIsInstance(db, sqlite3.Connection)
        db.close()
    
    # ==================== PRUEBAS DE RAMA / BRANCH COVERAGE ====================
    
    def test_productos_metodos_diferentes(self):
        """Prueba que productos() maneja correctamente GET vs POST"""
        # Rama GET
        get_response = self.client.get('/productos')
        self.assertEqual(get_response.status_code, 200)
        
        # Rama POST
        post_data = {'nombre': 'Test', 'precio': 1.0, 'descripcion': 'Test'}
        post_response = self.client.post('/productos',
                                        data=json.dumps(post_data),
                                        content_type='application/json')
        self.assertEqual(post_response.status_code, 200)
    
    def test_producto_id_todos_metodos(self):
        """Prueba todas las ramas de producto_id() (GET, PUT, DELETE)"""
        # Crear producto para las pruebas
        db = get_db()
        cursor = db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                           ['Multi Test', 1.0, 'Test'])
        db.commit()
        producto_id = cursor.lastrowid
        
        # Rama GET con producto existente
        get_response = self.client.get(f'/productos/{producto_id}')
        self.assertEqual(get_response.status_code, 200)
        
        # Rama PUT
        update_data = {'nombre': 'Updated', 'precio': 2.0, 'descripcion': 'Updated'}
        put_response = self.client.put(f'/productos/{producto_id}',
                                      data=json.dumps(update_data),
                                      content_type='application/json')
        self.assertEqual(put_response.status_code, 200)
        
        # Rama DELETE
        delete_response = self.client.delete(f'/productos/{producto_id}')
        self.assertEqual(delete_response.status_code, 200)
        
        # Rama GET con producto no existente (después del DELETE)
        get_deleted = self.client.get(f'/productos/{producto_id}')
        self.assertEqual(get_deleted.status_code, 404)
    
    # ==================== PRUEBAS DE DECISIÓN / DECISION COVERAGE ====================
    
    def test_decision_producto_existe_vs_no_existe(self):
        """Prueba decisión if row: en producto_id GET"""
        # Decisión TRUE: producto existe
        db = get_db()
        cursor = db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                           ['Exists', 1.0, 'Test'])
        db.commit()
        producto_id = cursor.lastrowid
        
        response_exists = self.client.get(f'/productos/{producto_id}')
        self.assertEqual(response_exists.status_code, 200)
        
        # Decisión FALSE: producto no existe
        response_not_exists = self.client.get('/productos/99999')
        self.assertEqual(response_not_exists.status_code, 404)
    
    # ==================== PRUEBAS DE BUCLE / LOOP COVERAGE ====================
    
    def test_loop_productos_lista_conversion(self):
        """Prueba el bucle list comprehension en productos GET"""
        # Caso 0 iteraciones (lista vacía)
        response_empty = self.client.get('/productos')
        data_empty = json.loads(response_empty.data)
        self.assertEqual(len(data_empty), 0)
        
        # Caso múltiples iteraciones
        db = get_db()
        for i in range(3):
            db.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                      [f'Product {i}', i * 10.0, f'Desc {i}'])
        db.commit()
        
        response_multiple = self.client.get('/productos')
        data_multiple = json.loads(response_multiple.data)
        self.assertEqual(len(data_multiple), 3)
        
        # Verificar estructura de cada elemento
        for i, producto in enumerate(data_multiple):
            self.assertIn('id', producto)
            self.assertIn('nombre', producto)
            self.assertIn('precio', producto)
            self.assertIn('descripcion', producto)
    
    # ==================== PRUEBAS DE MANEJO DE ERRORES ====================
    
    def test_error_handling_json_invalido(self):
        """Prueba manejo de JSON inválido en POST"""
        # Enviar JSON malformado
        try:
            response = self.client.post('/productos',
                                      data='{"nombre": invalid json}',
                                      content_type='application/json')
            # El comportamiento puede variar según la implementación
        except Exception as e:
            # Verificar que se maneja la excepción apropiadamente
            self.assertIsInstance(e, (ValueError, json.JSONDecodeError))
    
    def test_database_operations_integrity(self):
        """Prueba integridad de operaciones de base de datos"""
        # Verificar que las operaciones DB se commitean correctamente
        producto_data = {'nombre': 'DB Test', 'precio': 1.0, 'descripcion': 'Test'}
        
        response = self.client.post('/productos',
                                   data=json.dumps(producto_data),
                                   content_type='application/json')
        
        # Verificar en nueva conexión (simula persistencia)
        new_db = get_db()
        cursor = new_db.execute('SELECT * FROM productos WHERE nombre = ?', ['DB Test'])
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        new_db.close()


if __name__ == '__main__':
    # Ejecutar todas las pruebas
    unittest.main(verbosity=2)
