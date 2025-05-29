// Prueba simple para llamar repetidamente las funciones del script.js

async function pruebaEstabilidadFrontend(iteraciones = 20) {
    for (let i = 0; i < iteraciones; i++) {
        console.log(`Iteración ${i+1}`);

        // Crear producto
        document.getElementById('nombre').value = `Producto Test ${i}`;
        document.getElementById('precio').value = (Math.random() * 100).toFixed(2);
        document.getElementById('descripcion').value = 'Descripción de prueba';
        
        await guardarProducto();  // Asumiendo guardarProducto devuelve Promise

        // Cargar productos para actualizar tabla
        await new Promise(resolve => setTimeout(resolve, 200));

        // Editar primer producto (simulamos editar el primer id que aparece en la tabla)
        const primerFila = document.querySelector('#tabla-productos tbody tr');
        if (primerFila) {
            const id = parseInt(primerFila.cells[0].textContent);
            if (!isNaN(id)) {
                await editarProducto(id);
                
                // Modificar formulario y guardar para editar
                document.getElementById('nombre').value += ' Editado';
                await guardarProducto();
            }
        }

        // Esperar y luego eliminar el último producto (para simular ciclo completo)
        await new Promise(resolve => setTimeout(resolve, 200));
        const filas = document.querySelectorAll('#tabla-productos tbody tr');
        if (filas.length > 0) {
            const ultimoId = parseInt(filas[filas.length - 1].cells[0].textContent);
            if (!isNaN(ultimoId)) {
                eliminarProducto(ultimoId);
            }
        }

        // Esperar antes de la siguiente iteración
        await new Promise(resolve => setTimeout(resolve, 500));
    }
}
pruebaEstabilidadFrontend();
