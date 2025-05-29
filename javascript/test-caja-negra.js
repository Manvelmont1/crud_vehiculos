// test-caja-negra.js

console.log("=== PRUEBA DE CAJA NEGRA - INICIANDO ===");

// 1. Verificar estructura básica de la interfaz
console.assert(document.querySelector('h1')?.textContent.includes('Añadir'), '❌ Título principal no encontrado');
console.assert(document.querySelector('#nombre'), '❌ Campo "nombre" no existe');
console.assert(document.querySelector('#precio'), '❌ Campo "precio" no existe');
console.assert(document.querySelector('#descripcion'), '❌ Campo "descripcion" no existe');
console.assert(document.querySelector('button'), '❌ Botón "Guardar" no encontrado');
console.assert(document.querySelector('#tabla-productos'), '❌ Tabla de productos no encontrada');

console.log("✅ Estructura básica verificada");

// 2. Simular entrada en el formulario y clic en "Guardar"
document.getElementById('nombre').value = "Mazda 3";
document.getElementById('precio').value = "30000";
document.getElementById('descripcion').value = "Modelo 2024";

console.log("🔄 Simulando clic en 'Guardar'");
document.querySelector('button').click();

// Esperar a que fetch simulado (backend real) responda
setTimeout(() => {
    const mensaje = document.getElementById('message').textContent;
    console.assert(mensaje !== '', '❌ No se mostró mensaje tras guardar');
    console.log("✅ Mensaje mostrado:", mensaje);

    const filas = document.querySelectorAll('#tabla-productos tbody tr');
    console.assert(filas.length > 0, '❌ La tabla no fue actualizada tras guardar');
    console.log(`✅ La tabla contiene ${filas.length} fila(s)`);

    // 3. Simular clic en editar
    const btnEditar = filas[0].querySelector('button');
    if (btnEditar) {
        console.log("🔄 Simulando clic en 'Editar'");
        btnEditar.click();

        setTimeout(() => {
            const nombre = document.getElementById('nombre').value;
            console.assert(nombre !== '', '❌ No se llenó el formulario al editar');
            console.log("✅ Formulario editado con nombre:", nombre);

            // 4. Simular clic en eliminar
            const btnEliminar = filas[0].querySelectorAll('button')[1];
            if (btnEliminar) {
                window.confirm = () => true; // Forzar confirmación para test
                console.log("🔄 Simulando clic en 'Eliminar'");
                btnEliminar.click();

                setTimeout(() => {
                    const nuevoMensaje = document.getElementById('message').textContent;
                    console.assert(nuevoMensaje.includes('eliminado') || nuevoMensaje !== '', '❌ No se mostró mensaje tras eliminar');
                    console.log("✅ Mensaje tras eliminar:", nuevoMensaje);
                    console.log("=== FIN DE PRUEBAS ===");
                }, 800);
            }
        }, 800);
    }

}, 800);
