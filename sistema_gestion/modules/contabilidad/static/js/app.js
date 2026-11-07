// Aplicación JavaScript para el módulo de contabilidad

class ContabilidadApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCategorias();
        this.loadInitialData();
        this.loadMesesDisponibles();
        this.setupMesSelector();
    }

    setupEventListeners() {
        // Event listeners para los botones
        document.addEventListener('DOMContentLoaded', () => {
            // Listener para el formulario de transacción
            const tipoSelect = document.getElementById('tipo');
            if (tipoSelect) {
                tipoSelect.addEventListener('change', () => this.filterCategorias());
            }
            
            // Listener para el selector de mes
            const mesSelector = document.getElementById('mesSelector');
            if (mesSelector) {
                mesSelector.addEventListener('change', () => this.cargarIngresosSedes());
            }
        });
    }

    async loadCategorias() {
        try {
            const response = await fetch('/contabilidad/api/categorias');
            const categorias = await response.json();
            
            const categoriaSelect = document.getElementById('categoria');
            if (categoriaSelect) {
                categoriaSelect.innerHTML = '<option value="">Seleccionar...</option>';
                
                categorias.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.nombre;
                    option.textContent = cat.nombre;
                    option.dataset.tipo = cat.tipo;
                    categoriaSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error cargando categorías:', error);
        }
    }

    filterCategorias() {
        const tipo = document.getElementById('tipo').value;
        const categoriaSelect = document.getElementById('categoria');
        
        Array.from(categoriaSelect.options).forEach(option => {
            if (option.value === '') {
                option.style.display = 'block';
                return;
            }
            
            const optionTipo = option.dataset.tipo;
            option.style.display = (optionTipo === tipo) ? 'block' : 'none';
        });
    }

    async loadInitialData() {
        try {
            // Cargar resumen financiero
            const resumenResponse = await fetch('/contabilidad/api/resumen_financiero');
            const resumen = await resumenResponse.json();
            
            this.updateDashboard(resumen);
            
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
        }
    }

    updateDashboard(resumen) {
        // Actualizar tarjetas de resumen si existen
        const ingresosCard = document.querySelector('.bg-success h5');
        const egresosCard = document.querySelector('.bg-danger h5');
        const balanceCard = document.querySelector('.bg-primary h5, .bg-warning h5');
        
        if (ingresosCard) {
            ingresosCard.textContent = this.formatCurrency(resumen.totales.ingresos);
        }
        
        if (egresosCard) {
            egresosCard.textContent = this.formatCurrency(resumen.totales.egresos);
        }
        
        if (balanceCard) {
            balanceCard.textContent = this.formatCurrency(resumen.totales.balance);
        }
    }

    async guardarTransaccion() {
        try {
            const form = document.getElementById('transaccionForm');
            const formData = new FormData(form);
            
            const data = {
                tipo: formData.get('tipo'),
                categoria: formData.get('categoria'),
                descripcion: formData.get('descripcion'),
                monto: parseFloat(formData.get('monto')),
                fecha: formData.get('fecha')
            };
            
            // Validar datos
            if (!data.tipo || !data.categoria || !data.descripcion || !data.monto) {
                this.showToast('Por favor completa todos los campos', 'warning');
                return;
            }
            
            const response = await fetch('/contabilidad/api/transaccion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Transacción guardada correctamente', 'success');
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('nuevaTransaccionModal'));
                modal.hide();
                
                // Limpiar formulario
                form.reset();
                
                // Recargar datos
                this.loadInitialData();
                location.reload(); // Recargar página para actualizar tabla
                
            } else {
                this.showToast(result.error || 'Error al guardar transacción', 'error');
            }
            
        } catch (error) {
            console.error('Error guardando transacción:', error);
            this.showToast('Error al guardar transacción', 'error');
        }
    }

    async sincronizarExtracciones() {
        try {
            this.showLoading('Sincronizando extracciones...');
            
            const response = await fetch('/contabilidad/api/sincronizar_extracciones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast(result.message, 'success');
                location.reload(); // Recargar página para mostrar datos actualizados
            } else {
                this.showToast(result.error || 'Error al sincronizar', 'error');
            }
            
        } catch (error) {
            console.error('Error sincronizando extracciones:', error);
            this.showToast('Error al sincronizar extracciones', 'error');
        } finally {
            this.hideLoading();
        }
    }

    showAddTransaccionModal() {
        const modal = new bootstrap.Modal(document.getElementById('nuevaTransaccionModal'));
        modal.show();
        
        // Establecer fecha actual por defecto
        const fechaInput = document.getElementById('fecha');
        if (fechaInput) {
            fechaInput.value = new Date().toISOString().split('T')[0];
        }
    }

    showReportesModal() {
        // TODO: Implementar modal de reportes
        this.showToast('Módulo de reportes en desarrollo', 'info');
    }

    verTodasTransacciones() {
        // TODO: Implementar vista completa de transacciones
        this.showToast('Vista completa de transacciones en desarrollo', 'info');
    }

    refreshData() {
        location.reload();
    }

    async loadMesesDisponibles() {
        try {
            const response = await fetch('/contabilidad/api/meses_disponibles');
            const meses = await response.json();
            
            const mesSelector = document.getElementById('mesSelector');
            if (mesSelector) {
                mesSelector.innerHTML = '<option value="">Seleccionar mes...</option>';
                
                meses.forEach(mes => {
                    const option = document.createElement('option');
                    option.value = `${mes[1]}-${mes[0]}`; // mes-ano
                    option.textContent = `${mes[3]} ${mes[2]}`;
                    mesSelector.appendChild(option);
                });
                
                // Seleccionar el mes actual por defecto
                const ahora = new Date();
                const mesActual = `${String(ahora.getMonth() + 1).padStart(2, '0')}-${ahora.getFullYear()}`;
                mesSelector.value = mesActual;
            }
        } catch (error) {
            console.error('Error cargando meses:', error);
        }
    }

    setupMesSelector() {
        // Configurar el selector de mes
        const mesSelector = document.getElementById('mesSelector');
        if (mesSelector) {
            // Establecer el mes actual
            const ahora = new Date();
            const mesActual = `${String(ahora.getMonth() + 1).padStart(2, '0')}-${ahora.getFullYear()}`;
            mesSelector.value = mesActual;
        }
    }

    async cargarIngresosSedes() {
        try {
            const mesSelector = document.getElementById('mesSelector');
            if (!mesSelector.value) return;
            
            const [mes, ano] = mesSelector.value.split('-');
            
            const response = await fetch(`/contabilidad/api/ingresos_sedes?mes=${mes}&ano=${ano}`);
            const ingresos = await response.json();
            
            this.renderIngresosSedes(ingresos, false);
            this.actualizarTotalMes(ingresos);
            
        } catch (error) {
            console.error('Error cargando ingresos por sedes:', error);
            this.showToast('Error al cargar ingresos por sedes', 'error');
        }
    }

    actualizarTotalMes(ingresos) {
        const totalMes = document.getElementById('totalMes');
        if (!totalMes) return;
        
        let total = 0;
        Object.values(ingresos).forEach(ingreso => {
            total += ingreso.total || 0;
        });
        
        totalMes.textContent = this.formatCurrency(total);
    }

    renderIngresosSedes(ingresos, editable = false) {
        const container = document.getElementById('ingresosSedesContainer');
        if (!container) return;
        
        const sedes = [
            'Ventas BRISAS', 'Ventas CACHICAMO', 'Ventas CANO LAJAS', 'Ventas CANO PESCADO',
            'Ventas CERRITOS', 'Ventas MANANTIALES-1', 'Ventas MANANTIALES-2',
            'Ventas MIRAVALLE', 'Ventas SAN MIGUEL', 'Ventas LA TORTUGA', 'Ventas TROPEZON'
        ];
        
        let html = '<div class="row">';
        
        sedes.forEach(sede => {
            const datos = ingresos[sede] || { total: 0, cantidad: 0 };
            const nombreSede = sede.replace('Ventas ', '');
            
            if (editable) {
                html += `
                    <div class="col-md-4 col-sm-6 mb-3">
                        <div class="card border-primary">
                            <div class="card-body text-center">
                                <h6 class="card-title">${nombreSede}</h6>
                                <div class="input-group input-group-sm">
                                    <span class="input-group-text">$</span>
                                    <input type="number" class="form-control" 
                                           id="ingreso_${sede.replace(' ', '_')}" 
                                           value="${datos.total}" 
                                           step="1000" 
                                           min="0">
                                </div>
                                <small class="text-muted">${datos.cantidad} transacciones</small>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="col-md-4 col-sm-6 mb-3">
                        <div class="card border-primary">
                            <div class="card-body text-center">
                                <h6 class="card-title">${nombreSede}</h6>
                                <h5 class="text-primary">${this.formatCurrency(datos.total)}</h5>
                                <small class="text-muted">${datos.cantidad} transacciones</small>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        html += '</div>';
        container.innerHTML = html;
    }

    editarIngresosSedes() {
        const mesSelector = document.getElementById('mesSelector');
        if (!mesSelector.value) {
            this.showToast('Por favor selecciona un mes', 'warning');
            return;
        }
        
        this.renderIngresosSedes({}, true); // Renderizar campos vacíos primero
        
        // Cargar datos actuales y renderizar en modo edición
        this.cargarIngresosSedes().then(() => {
            this.renderIngresosSedes(window.ingresosActuales || {}, true);
            
            // Mostrar/ocultar botones
            document.getElementById('btnGuardar').style.display = 'inline-block';
            document.getElementById('btnCancelar').style.display = 'inline-block';
            document.querySelector('[onclick="editarIngresosSedes()"]').style.display = 'none';
        });
    }

    async guardarIngresosSedes() {
        try {
            const mesSelector = document.getElementById('mesSelector');
            const [mes, ano] = mesSelector.value.split('-');
            
            // Recopilar valores de todos los inputs
            const ingresos = {};
            const sedes = [
                'Ventas BRISAS', 'Ventas CACHICAMO', 'Ventas CANO LAJAS', 'Ventas CANO PESCADO',
                'Ventas CERRITOS', 'Ventas MANANTIALES-1', 'Ventas MANANTIALES-2',
                'Ventas MIRAVALLE', 'Ventas SAN MIGUEL', 'Ventas LA TORTUGA', 'Ventas TROPEZON'
            ];
            
            sedes.forEach(sede => {
                const input = document.getElementById(`ingreso_${sede.replace(' ', '_')}`);
                if (input) {
                    ingresos[sede] = {
                        total: parseFloat(input.value) || 0
                    };
                }
            });
            
            const response = await fetch('/contabilidad/api/ingresos_sedes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mes: mes,
                    ano: ano,
                    ingresos: ingresos
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Ingresos actualizados correctamente', 'success');
                this.cancelarEdicion();
                this.cargarIngresosSedes(); // Recargar en modo vista
            } else {
                this.showToast(result.error || 'Error al guardar ingresos', 'error');
            }
            
        } catch (error) {
            console.error('Error guardando ingresos:', error);
            this.showToast('Error al guardar ingresos', 'error');
        }
    }

    cancelarEdicion() {
        this.cargarIngresosSedes(); // Volver al modo vista
        
        // Ocultar/mostrar botones
        document.getElementById('btnGuardar').style.display = 'none';
        document.getElementById('btnCancelar').style.display = 'none';
        document.querySelector('[onclick="editarIngresosSedes()"]').style.display = 'inline-block';
    }

    async agregarNuevoIngreso() {
        try {
            const sede = document.getElementById('nuevaSede').value;
            const monto = parseFloat(document.getElementById('nuevoMonto').value) || 0;
            const fecha = document.getElementById('nuevaFecha').value;
            const descripcion = document.getElementById('nuevaDescripcion').value;
            
            if (!sede || monto <= 0 || !fecha) {
                this.showToast('Por favor completa todos los campos', 'warning');
                return;
            }
            
            const mesSelector = document.getElementById('mesSelector');
            if (!mesSelector.value) {
                this.showToast('Por favor selecciona un mes', 'warning');
                return;
            }
            
            const [mes, ano] = mesSelector.value.split('-');
            
            const response = await fetch('/contabilidad/api/transaccion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tipo: 'ingreso',
                    categoria: sede,
                    descripcion: descripcion || `Ingreso ${sede.replace('Ventas ', '')}`,
                    monto: monto,
                    fecha: fecha
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Ingreso agregado correctamente', 'success');
                
                // Limpiar formulario
                document.getElementById('nuevaSede').value = '';
                document.getElementById('nuevoMonto').value = '';
                document.getElementById('nuevaFecha').value = '';
                document.getElementById('nuevaDescripcion').value = '';
                
                // Recargar datos
                this.cargarIngresosSedes();
                
            } else {
                this.showToast(result.error || 'Error al agregar ingreso', 'error');
            }
            
        } catch (error) {
            console.error('Error agregando ingreso:', error);
            this.showToast('Error al agregar ingreso', 'error');
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    }

    showToast(message, type = 'info') {
        // Crear toast
        const toastContainer = this.getToastContainer();
        
        const toastId = `toast-${Date.now()}`;
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : type === 'success' ? 'success' : 'primary'} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    getToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    showLoading(message = 'Procesando...') {
        this.hideLoading();
        
        const modalHtml = `
            <div class="modal fade" id="loadingModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-sm modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-body text-center">
                            <div class="spinner-border text-success mb-3" role="status">
                                <span class="visually-hidden">Cargando...</span>
                            </div>
                            <p class="mb-0" id="loadingMessage">${message}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const loadingModal = document.getElementById('loadingModal');
        const modal = new bootstrap.Modal(loadingModal);
        modal.show();
    }

    hideLoading() {
        const loadingModal = document.getElementById('loadingModal');
        if (loadingModal) {
            const modal = bootstrap.Modal.getInstance(loadingModal);
            if (modal) {
                modal.hide();
            }
            setTimeout(() => {
                if (loadingModal && loadingModal.parentNode) {
                    loadingModal.remove();
                }
            }, 300);
        }
    }
}

// Hacer funciones globales para que puedan ser llamadas desde HTML
window.contabilidadApp = null;
window.showAddTransaccionModal = () => window.contabilidadApp.showAddTransaccionModal();
window.guardarTransaccion = () => window.contabilidadApp.guardarTransaccion();
window.sincronizarExtracciones = () => window.contabilidadApp.sincronizarExtracciones();
window.showReportesModal = () => window.contabilidadApp.showReportesModal();
window.verTodasTransacciones = () => window.contabilidadApp.verTodasTransacciones();
window.refreshData = () => window.contabilidadApp.refreshData();
window.editarIngresosSedes = () => window.contabilidadApp.editarIngresosSedes();


// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.contabilidadApp = new ContabilidadApp();
});