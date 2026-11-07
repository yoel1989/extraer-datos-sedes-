/**
 * Contabilidad Simple - Sistema de Gestión
 * Lógica simplificada para ingreso manual de datos históricos
 */

class ContabilidadSimple {
    constructor() {
        this.apiBase = '/contabilidad/api';
        this.periodoActual = { mes: '', ano: '' };
        this.ingresos = [];
        this.egresos = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.cargarAnos();
        this.establecerPeriodoActual();
    }

    setupEventListeners() {
        // Formularios
        document.getElementById('ingresosForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.agregarIngreso();
        });

        document.getElementById('egresosForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.agregarEgreso();
        });

        // Auto-calcular cuando cambian los montos
        document.getElementById('montoIngreso').addEventListener('input', () => this.calcularTotales());
        document.getElementById('montoEgreso').addEventListener('input', () => this.calcularTotales());
    }

    cargarAnos() {
        const anoSelector = document.getElementById('anoSelector');
        const anoActual = new Date().getFullYear();
        
        // Llenar con años desde 2020 hasta el actual + 1
        for (let ano = 2020; ano <= anoActual + 1; ano++) {
            const option = document.createElement('option');
            option.value = ano;
            option.textContent = ano;
            if (ano === anoActual) {
                option.selected = true;
            }
            anoSelector.appendChild(option);
        }
    }

    establecerPeriodoActual() {
        const ahora = new Date();
        const mes = String(ahora.getMonth() + 1).padStart(2, '0');
        const ano = ahora.getFullYear();
        
        document.getElementById('mesSelector').value = mes;
        document.getElementById('anoSelector').value = ano;
        
        this.periodoActual = { mes, ano };
        
        // Cargar datos del período actual
        setTimeout(() => this.cargarDatosPeriodo(), 500);
    }

    async cargarDatosPeriodo() {
        const mes = document.getElementById('mesSelector').value;
        const ano = document.getElementById('anoSelector').value;
        
        this.periodoActual = { mes, ano };
        
        try {
            this.mostrarCargando(true);
            
            const response = await fetch(`${this.apiBase}/datos_periodo?mes=${mes}&ano=${ano}`);
            const data = await response.json();
            
            if (data.success) {
                this.ingresos = data.ingresos || [];
                this.egresos = data.egresos || [];
                
                this.actualizarListas();
                this.calcularTotales();
                
                this.mostrarAlerta(`Datos cargados para ${this.getNombreMes(mes)} ${ano}`, 'success');
            } else {
                this.mostrarAlerta('Error cargando datos: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('Error de conexión: ' + error.message, 'danger');
        } finally {
            this.mostrarCargando(false);
        }
    }

    getNombreMes(mes) {
        const meses = {
            '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
            '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
            '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
        };
        return meses[mes] || mes;
    }

    agregarIngreso() {
        const concepto = document.getElementById('conceptoIngreso').value.trim();
        const monto = parseFloat(document.getElementById('montoIngreso').value) || 0;
        
        if (!concepto || monto <= 0) {
            this.mostrarAlerta('Por favor ingrese concepto y monto válidos', 'warning');
            return;
        }
        
        const ingreso = {
            id: Date.now(),
            concepto,
            monto,
            fecha: `${this.periodoActual.ano}-${this.periodoActual.mes}-01`
        };
        
        this.ingresos.push(ingreso);
        
        // Limpiar formulario
        document.getElementById('ingresosForm').reset();
        
        // Actualizar interfaz
        this.actualizarListas();
        this.calcularTotales();
        
        this.mostrarAlerta('Ingreso agregado correctamente', 'success');
    }

    agregarEgreso() {
        const concepto = document.getElementById('conceptoEgreso').value.trim();
        const monto = parseFloat(document.getElementById('montoEgreso').value) || 0;
        
        if (!concepto || monto <= 0) {
            this.mostrarAlerta('Por favor ingrese concepto y monto válidos', 'warning');
            return;
        }
        
        const egreso = {
            id: Date.now(),
            concepto,
            monto,
            fecha: `${this.periodoActual.ano}-${this.periodoActual.mes}-01`
        };
        
        this.egresos.push(egreso);
        
        // Limpiar formulario
        document.getElementById('egresosForm').reset();
        
        // Actualizar interfaz
        this.actualizarListas();
        this.calcularTotales();
        
        this.mostrarAlerta('Egreso agregado correctamente', 'success');
    }

    eliminarIngreso(id) {
        this.ingresos = this.ingresos.filter(ingreso => ingreso.id !== id);
        this.actualizarListas();
        this.calcularTotales();
        this.mostrarAlerta('Ingreso eliminado', 'info');
    }

    eliminarEgreso(id) {
        this.egresos = this.egresos.filter(egreso => egreso.id !== id);
        this.actualizarListas();
        this.calcularTotales();
        this.mostrarAlerta('Egreso eliminado', 'info');
    }

    actualizarListas() {
        // Actualizar lista de ingresos
        const listaIngresos = document.getElementById('listaIngresos');
        listaIngresos.innerHTML = '';
        
        if (this.ingresos.length === 0) {
            listaIngresos.innerHTML = '<div class="list-group-item text-muted">No hay ingresos registrados</div>';
        } else {
            this.ingresos.forEach(ingreso => {
                const item = document.createElement('div');
                item.className = 'list-group-item d-flex justify-content-between align-items-center';
                item.innerHTML = `
                    <div>
                        <strong>${ingreso.concepto}</strong>
                        <br>
                        <small class="text-muted">$${ingreso.monto.toLocaleString('es-CO')}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="contabilidadSimple.eliminarIngreso(${ingreso.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
                listaIngresos.appendChild(item);
            });
        }
        
        // Actualizar lista de egresos
        const listaEgresos = document.getElementById('listaEgresos');
        listaEgresos.innerHTML = '';
        
        if (this.egresos.length === 0) {
            listaEgresos.innerHTML = '<div class="list-group-item text-muted">No hay egresos registrados</div>';
        } else {
            this.egresos.forEach(egreso => {
                const item = document.createElement('div');
                item.className = 'list-group-item d-flex justify-content-between align-items-center';
                item.innerHTML = `
                    <div>
                        <strong>${egreso.concepto}</strong>
                        <br>
                        <small class="text-muted">$${egreso.monto.toLocaleString('es-CO')}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="contabilidadSimple.eliminarEgreso(${egreso.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
                listaEgresos.appendChild(item);
            });
        }
    }

    calcularTotales() {
        const totalIngresos = this.ingresos.reduce((sum, ingreso) => sum + ingreso.monto, 0);
        const totalEgresos = this.egresos.reduce((sum, egreso) => sum + egreso.monto, 0);
        const balance = totalIngresos - totalEgresos;
        
        document.getElementById('totalIngresos').textContent = totalIngresos.toLocaleString('es-CO');
        document.getElementById('totalEgresos').textContent = totalEgresos.toLocaleString('es-CO');
        document.getElementById('balance').textContent = balance.toLocaleString('es-CO');
        
        // Cambiar color del balance según resultado
        const balanceCard = document.getElementById('balance').closest('.card');
        balanceCard.className = balance >= 0 ? 'card bg-primary text-white' : 'card bg-warning text-white';
    }

    async guardarDatos() {
        if (this.ingresos.length === 0 && this.egresos.length === 0) {
            this.mostrarAlerta('No hay datos para guardar', 'warning');
            return;
        }
        
        if (!confirm(`¿Está seguro de guardar ${this.ingresos.length + this.egresos.length} registros para ${this.getNombreMes(this.periodoActual.mes)} ${this.periodoActual.ano}?`)) {
            return;
        }
        
        try {
            this.mostrarCargando(true);
            
            const datos = {
                mes: this.periodoActual.mes,
                ano: this.periodoActual.ano,
                ingresos: this.ingresos,
                egresos: this.egresos
            };
            
            const response = await fetch(`${this.apiBase}/guardar_periodo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.mostrarAlerta('✅ Datos guardados correctamente', 'success');
            } else {
                this.mostrarAlerta('❌ Error al guardar: ' + result.error, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('❌ Error de conexión: ' + error.message, 'danger');
        } finally {
            this.mostrarCargando(false);
        }
    }

    async exportarExcel() {
        await this.exportarDatos('excel');
    }

    async exportarPDF() {
        await this.exportarDatos('pdf');
    }

    async exportarDatos(formato) {
        try {
            this.mostrarCargando(true);
            
            const response = await fetch(`${this.apiBase}/exportar_periodo?mes=${this.periodoActual.mes}&ano=${this.periodoActual.ano}&formato=${formato}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `contabilidad_${this.periodoActual.ano}_${this.periodoActual.mes}.${formato}`;
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
}

// Funciones globales para compatibilidad con el HTML
let contabilidadSimple;

window.cargarDatosPeriodo = function() {
    contabilidadSimple.cargarDatosPeriodo();
};

window.guardarDatos = function() {
    contabilidadSimple.guardarDatos();
};

window.exportarExcel = function() {
    contabilidadSimple.exportarExcel();
};

window.exportarPDF = function() {
    contabilidadSimple.exportarPDF();
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    contabilidadSimple = new ContabilidadSimple();
});