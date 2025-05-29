// Simulación básica del DOM
const document = {
    inputs: {
        nombre: '',
        precio: '',
        descripcion: ''
    },
    getElementById(id) {
        return {
            get value() {
                return document.inputs[id];
            },
            set value(val) {
                document.inputs[id] = val;
            },
            textContent: ''
        };
    },
    getElementByIdText(id) {
        return {
            textContent: ''
        };
    },
};

// Simulación de variables globales
let productoEditandoId = null;

// Funciones desde script.js
function limpiarFormulario() {
    document.getElementById('nombre').value = '';
    document.getElementById('precio').value = '';
    document.getElementById('descripcion').value = '';
    productoEditandoId = null;
}

function guardarProductoSimulado() {
    const producto = {
        nombre: document.getElementById('nombre').value,
        precio: parseFloat(document.getElementById('precio').value),
        descripcion: document.getElementById('descripcion').value
    };

    const url = productoEditandoId ? `/productos/${productoEditandoId}` : '/productos';
    const method = productoEditandoId ? 'PUT' : 'POST';

    console.log("Producto a guardar:", producto);
    console.log("URL:", url);
    console.log("Método:", method);

    return { url, method, producto };
}

// === CASOS DE PRUEBA DE CAJA BLANCA ===

console.log("==== PRUEBA 1: limpiarFormulario ====");
document.inputs.nombre = 'Producto X';
document.inputs.precio = '99.9';
document.inputs.descripcion = 'Descripción';
productoEditandoId = 5;
limpiarFormulario();
console.assert(document.inputs.nombre === '', 'Nombre debería estar vacío');
console.assert(document.inputs.precio === '', 'Precio debería estar vacío');
console.assert(document.inputs.descripcion === '', 'Descripción debería estar vacía');
console.assert(productoEditandoId === null, 'productoEditandoId debe ser null');

console.log("==== PRUEBA 2: guardarProducto (POST) ====");
document.inputs.nombre = 'Nuevo';
document.inputs.precio = '15.5';
document.inputs.descripcion = 'Nuevo producto';
productoEditandoId = null;
const postResult = guardarProductoSimulado();
console.assert(postResult.url === '/productos', 'URL debe ser POST /productos');
console.assert(postResult.method === 'POST', 'Debe usar método POST');
console.assert(postResult.producto.precio === 15.5, 'Precio debe convertirse a número');

console.log("==== PRUEBA 3: guardarProducto (PUT) ====");
document.inputs.nombre = 'Editado';
document.inputs.precio = '77';
document.inputs.descripcion = 'Actualización';
productoEditandoId = 3;
const putResult = guardarProductoSimulado();
console.assert(putResult.url === '/productos/3', 'URL debe ser PUT /productos/3');
console.assert(putResult.method === 'PUT', 'Debe usar método PUT');
console.assert(putResult.producto.nombre === 'Editado', 'Nombre debe ser Editado');

console.log("==== Todas las pruebas pasaron correctamente ====");
