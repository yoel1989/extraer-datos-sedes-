/**
 * Módulo de Contabilidad - Sistema de Gestión
 * Archivo JavaScript principal para funcionalidades del frontend
 */

class ContabilidadManager {
    constructor() {
        this.apiBase = '/contabilidad/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.calcularTotales();
        this.cargarDatosIniciales();
    }

    setupEventListeners() {
        // Event listeners para inputs numéricos
        document.addEventListener('input', (e) => {
            if (e.target.type === 'number') {
                this.calcularTotales();
            }
        });

        // Prevenir envío de formularios por defecto
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
            });
        });
    }

    async cargarDatosIniciales() {
        try {
            const response = await fetch(`${this.apiBase}/resumen_financiero`);
            const data = await response.json();
            this.actualizarResumenFinanciero(data);
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
        }
    }

    actualizarResumenFinanciero(data) {
        if (data.totales) {
            document.getElementById('totalIngresos').textContent = 
                '$' + data.totales.ingresos.toLocaleString('es-CO');
            document.getElementById('totalEgresos').textContent = 
                '$' + data.totales.egresos.toLocaleString('es-CO');
            
            const balance = data.totales.balance;
            const balanceElement = document.getElementById('balance');
            balanceElement.textContent = '$' + balance.toLocaleString('es-CO');
            balanceElement.className = balance >= 0 ? 'text-warning' : 'text-danger';
        }
    }

    calcularTotales() {
        let totalIngresos = 0;
        let totalEgresos = 0;

        // Sumar ingresos por sedes
        document.querySelectorAll('#ingresosSedesContainer input[type="number"]').forEach(input => {
            totalIngresos += parseFloat(input.value) || 0;
        });

        // Sumar ingresos por clientes
        document.querySelectorAll('#ingresosClientesContainer input[type="number"]').forEach(input => {
            totalIngresos += parseFloat(input.value) || 0;
        });

        // Sumar ingresos TV
        document.querySelectorAll('#ingresosTVContainer input[type="number"]').forEach(input => {
            totalIngresos += parseFloat(input.value) || 0;
        });

        // Sumar ingresos extras
        document.querySelectorAll('#ingresosExtrasContainer input[type="number"]').forEach(input => {
            totalIngresos += parseFloat(input.value) || 0;
        });

        // Sumar egresos
        document.querySelectorAll('#egresosContainer input[type="number"]').forEach(input => {
            totalEgresos += parseFloat(input.value) || 0;
        });

        // Actualizar display
        document.getElementById('totalIngresos').textContent = '$' + totalIngresos.toLocaleString('es-CO');
        document.getElementById('totalEgresos').textContent = '$' + totalEgresos.toLocaleString('es-CO');

        const balance = totalIngresos - totalEgresos;
        const balanceElement = document.getElementById('balance');
        balanceElement.textContent = '$' + balance.toLocaleString('es-CO');
        balanceElement.className = balance >= 0 ? 'text-warning' : 'text-danger';
    }

    agregarFila(tipo) {
        const tbody = event.target.closest('.card').querySelector('tbody');
        const newRow = document.createElement('tr');
        
        let placeholderTexto = '';
        switch(tipo) {
            case 'sedes': placeholderTexto = 'Nombre de la sede'; break;
            case 'clientes': placeholderTexto = 'Nombre del cliente'; break;
            case 'tv': placeholderTexto = 'Servicio TV'; break;
            case 'extras': placeholderTexto = 'Concepto extra'; break;
            case 'egresos': placeholderTexto = 'Concepto de egreso'; break;
        }
        
        newRow.innerHTML = `
            <td class="small">
                <div class="input-group input-group-sm">
                    <input type="text" class="form-control form-control-sm" placeholder="${placeholderTexto}" style="height: 28px;">
                    <button class="btn btn-sm btn-outline-danger" onclick="contabilidadManager.eliminarFila(this)" style="height: 28px; padding: 0.2rem 0.4rem;">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </td>
            <td class="text-end small">
                <div class="input-group input-group-sm">
                    <span class="input-group-text" style="font-size: 0.7rem; padding: 0.2rem 0.4rem;">$</span>
                    <input type="number" class="form-control form-control-sm text-end" value="0" step="1000" min="0" style="height: 28px;">
                </div>
            </td>
        `;
        tbody.appendChild(newRow);
        
        // Recalcular totales después de agregar
        this.calcularTotales();
    }

    eliminarFila(boton) {
        const fila = boton.closest('tr');
        const tbody = fila.closest('tbody');
        if (tbody.children.length > 1) {
            fila.remove();
            this.calcularTotales();
        } else {
            this.mostrarAlerta('Debe haber al menos una fila en la tabla', 'warning');
        }
    }

    obtenerDatosTabla(tipo) {
        const botonAgregar = document.querySelector(`[onclick*="agregarFila('${tipo}')"]`);
        if (!botonAgregar) return [];
        
        const tabla = botonAgregar.closest('.card').querySelector('tbody');
        if (!tabla) return [];
        
        const filas = tabla.querySelectorAll('tr');
        const datos = [];
        
        filas.forEach(fila => {
            const nombreInput = fila.querySelector('input[type="text"]');
            const montoInput = fila.querySelector('input[type="number"]');
            
            if (nombreInput && montoInput) {
                const nombre = nombreInput.value || '';
                const monto = parseFloat(montoInput.value) || 0;
                
                if (nombre && monto > 0) {
                    datos.push({ nombre, monto });
                }
            }
        });
        
        return datos;
    }

    async guardarSeccion(seccion) {
        try {
            const datos = {};
            datos[seccion] = this.obtenerDatosTabla(seccion);
            
            if (datos[seccion].length === 0) {
                this.mostrarAlerta('No hay datos válidos para guardar en esta sección', 'warning');
                return;
            }
            
            this.mostrarCargando(true);
            
            const response = await fetch(`${this.apiBase}/guardar_datos_contables`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.mostrarAlerta('✅ Cambios guardados correctamente', 'success');
                await this.cargarDatosIniciales(); // Recargar datos
            } else {
                this.mostrarAlerta('❌ Error: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('❌ Error de conexión: ' + error.message, 'danger');
        } finally {
            this.mostrarCargando(false);
        }
    }

    async guardarTodosLosCambios() {
        try {
            const datos = {
                sedes: this.obtenerDatosTabla('sedes'),
                clientes: this.obtenerDatosTabla('clientes'),
                tv: this.obtenerDatosTabla('tv'),
                extras: this.obtenerDatosTabla('extras'),
                egresos: this.obtenerDatosTabla('egresos')
            };
            
            const totalItems = Object.values(datos).reduce((sum, arr) => sum + arr.length, 0);
            if (totalItems === 0) {
                this.mostrarAlerta('No hay datos para guardar', 'warning');
                return;
            }
            
            if (!confirm(`¿Está seguro de guardar ${totalItems} ítems?`)) {
                return;
            }
            
            this.mostrarCargando(true);
            
            const response = await fetch(`${this.apiBase}/guardar_datos_contables`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos),
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.mostrarAlerta('✅ Todos los cambios guardados correctamente', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                this.mostrarAlerta('❌ Error al guardar: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('❌ Error al guardar: ' + error.message, 'danger');
        } finally {
            this.mostrarCargando(false);
        }
    }

    descartarSeccion(seccion) {
        if (confirm(`¿Está seguro de descartar los cambios de esta sección?`)) {
            location.reload();
        }
    }

    descartarCambios() {
        if (confirm('¿Está seguro de descartar todos los cambios no guardados?')) {
            location.reload();
        }
    }

    mostrarAlerta(mensaje, tipo = 'info') {
        // Crear alerta si no existe un contenedor
        let alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alertContainer';
            alertContainer.style.position = 'fixed';
            alertContainer.style.top = '20px';
            alertContainer.style.right = '20px';
            alertContainer.style.zIndex = '9999';
            alertContainer.style.width = '300px';
            document.body.appendChild(alertContainer);
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${tipo} alert-dismissible fade show`;
        alert.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    mostrarCargando(mostrar) {
        let loadingOverlay = document.getElementById('loadingOverlay');
        
        if (mostrar) {
            if (!loadingOverlay) {
                loadingOverlay = document.createElement('div');
                loadingOverlay.id = 'loadingOverlay';
                loadingOverlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
                loadingOverlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
                loadingOverlay.style.zIndex = '9998';
                loadingOverlay.innerHTML = `
                    <div class="spinner-border text-light" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                `;
                document.body.appendChild(loadingOverlay);
            }
            loadingOverlay.style.display = 'flex';
        } else {
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        }
    }

    async exportarDatos(formato) {
        try {
            this.mostrarCargando(true);
            
            const response = await fetch(`${this.apiBase}/exportar?formato=${formato}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `contabilidad_${new Date().toISOString().split('T')[0]}.${formato}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.mostrarAlerta(`✅ Datos exportados correctamente en formato ${formato.toUpperCase()}`, 'success');
            } else {
                throw new Error('Error al exportar datos');
            }
        } catch (error) {
            console.error('Error exportando:', error);
            this.mostrarAlerta('❌ Error al exportar datos: ' + error.message, 'danger');
        } finally {
            this.mostrarCargando(false);
        }
    }
}

// Funciones globales para compatibilidad con el HTML existente
let contabilidadManager;

window.agregarFila = function(tipo) {
    contabilidadManager.agregarFila(tipo);
};

window.eliminarFila = function(boton) {
    contabilidadManager.eliminarFila(boton);
};

window.guardarSeccion = function(seccion) {
    contabilidadManager.guardarSeccion(seccion);
};

window.guardarTodosLosCambios = function() {
    contabilidadManager.guardarTodosLosCambios();
};

window.descartarSeccion = function(seccion) {
    contabilidadManager.descartarSeccion(seccion);
};

window.descartarCambios = function() {
    contabilidadManager.descartarCambios();
};

window.exportarDatos = function(formato) {
    contabilidadManager.exportarDatos(formato);
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    contabilidadManager = new ContabilidadManager();
});