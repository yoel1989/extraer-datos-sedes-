// Aplicación JavaScript para el Sistema de Extracción

class ExtractionApp {
    constructor() {
        this.currentExtractions = new Map();
        this.init();
    }

    init() {
        this.cleanupModals(); // Limpiar cualquier modal residual al iniciar
        this.setupEventListeners();
        this.setDefaultDates();
        this.loadHistory();
        this.loadStats();
        this.startPolling();
    }

    setupEventListeners() {
        // Botón Extraer Todo
        document.getElementById('extractAllBtn').addEventListener('click', () => {
            this.extractAll();
        });

        // Botones de sitios individuales
        document.querySelectorAll('.extract-site-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.currentTarget;
                const sitio = target.dataset.sitio;
                const name = target.dataset.name;
                this.extractSite(sitio, name);
            });
        });

        // Botón refrescar
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadHistory();
            this.showToast('Historial actualizado', 'info');
        });

        // Botón refrescar historial
        document.getElementById('refreshHistoryBtn').addEventListener('click', () => {
            this.loadHistory();
            this.loadStats();
        });

        // Botones de limpiar base de datos
        const cleanButtons = document.querySelectorAll('[data-clean]');
        cleanButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const cleanType = e.target.closest('[data-clean]').dataset.clean;
                if (cleanType) {
                    this.cleanDatabase(cleanType);
                }
            });
        });

        // Botones de descarga de PDFs
        const generateBtn = document.getElementById('generateAndDownloadAll');
        if (generateBtn) {
            generateBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.generateAndDownloadAll();
            });
        }

        const downloadAllBtn = document.getElementById('downloadAllPdfs');
        if (downloadAllBtn) {
            downloadAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.downloadAllPdfs();
            });
        }

        const listPdfsBtn = document.getElementById('listPdfs');
        if (listPdfsBtn) {
            listPdfsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showPdfsModal();
            });
        }

        const downloadSelectedBtn = document.getElementById('downloadSelectedPdfs');
        if (downloadSelectedBtn) {
            downloadSelectedBtn.addEventListener('click', () => {
                this.downloadSelectedPdfs();
            });
        }

        // Validación de fechas
        document.getElementById('fechaInicio').addEventListener('change', () => {
            this.validateDates();
        });

        document.getElementById('fechaFin').addEventListener('change', () => {
            this.validateDates();
        });
        

    }

    setDefaultDates() {
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
        
        document.getElementById('fechaFin').value = today.toISOString().split('T')[0];
        document.getElementById('fechaInicio').value = thirtyDaysAgo.toISOString().split('T')[0];
    }

    validateDates() {
        const fechaInicio = new Date(document.getElementById('fechaInicio').value);
        const fechaFin = new Date(document.getElementById('fechaFin').value);
        
        if (fechaInicio > fechaFin) {
            document.getElementById('fechaFin').value = document.getElementById('fechaInicio').value;
        }
    }

    async extractAll() {
        if (!this.validateForm()) return;

        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        try {
            this.showProgress();
            this.disableButtons(true);

            const response = await fetch('/extraccion/api/extract_all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fecha_inicio: fechaInicio,
                    fecha_fin: fechaFin
                })
            });

            const result = await response.json();

            if (result.success) {
                this.currentExtractions.set(result.extraction_id, {
                    type: 'all',
                    fecha_inicio: fechaInicio,
                    fecha_fin: fechaFin
                });

                this.showToast('Extracción de todos los sitios iniciada', 'success');
                this.updateAllSiteStatus('processing');
            } else {
                this.showToast('Error al iniciar extracción', 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error de conexión', 'error');
        } finally {
            this.disableButtons(false);
        }
    }

    async extractSite(sitioKey, sitioName) {
        if (!this.validateForm()) return;

        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        try {
            this.showProgress();
            this.updateSiteStatus(sitioKey, 'processing');

            const response = await fetch(`/extraccion/api/extract_site/${sitioKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fecha_inicio: fechaInicio,
                    fecha_fin: fechaFin
                })
            });

            const result = await response.json();

            if (result.success) {
                this.currentExtractions.set(result.extraction_id, {
                    type: 'site',
                    sitio: sitioKey,
                    sitio_name: sitioName,
                    fecha_inicio: fechaInicio,
                    fecha_fin: fechaFin
                });

                this.showToast(`Extracción de ${sitioName} iniciada`, 'success');
            } else {
                this.updateSiteStatus(sitioKey, 'error');
                this.showToast(`Error al extraer ${sitioName}`, 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            this.updateSiteStatus(sitioKey, 'error');
            this.showToast('Error de conexión', 'error');
        }
    }

    validateForm() {
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        if (!fechaInicio || !fechaFin) {
            this.showToast('Por favor selecciona ambas fechas', 'warning');
            return false;
        }

        return true;
    }

    showProgress() {
        document.getElementById('progressSection').style.display = 'block';
    }

    updateSiteStatus(sitioKey, status) {
        const card = document.querySelector(`[data-sitio="${sitioKey}"]`);
        if (!card) return;

        const badge = card.querySelector('.badge');
        const btn = card.querySelector('.extract-site-btn');

        // Remover clases de estado anteriores
        card.classList.remove('processing', 'completed', 'error');
        badge.classList.remove('bg-secondary', 'bg-primary', 'bg-success', 'bg-danger');

        switch (status) {
            case 'processing':
                card.classList.add('processing');
                badge.classList.add('bg-primary');
                badge.textContent = 'Procesando';
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Procesando';
                break;
            case 'completed':
                card.classList.add('completed');
                badge.classList.add('bg-success');
                badge.textContent = 'Completado';
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check me-1"></i>Completado';
                break;
            case 'error':
                card.classList.add('error');
                badge.classList.add('bg-danger');
                badge.textContent = 'Error';
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Reintentar';
                break;
            default:
                badge.classList.add('bg-secondary');
                badge.textContent = 'Listo';
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-download me-1"></i>Extraer';
        }
    }

    updateAllSiteStatus(status) {
        document.querySelectorAll('.site-card').forEach(card => {
            const sitioKey = card.dataset.sitio;
            this.updateSiteStatus(sitioKey, status);
        });
    }

    async loadHistory() {
        try {
            const response = await fetch('/extraccion/api/extractions');
            const extractions = await response.json();

            this.renderHistoryTable(extractions);

        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/extraccion/api/database_stats');
            const stats = await response.json();

            this.renderStats(stats);

        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderStats(stats) {
        document.getElementById('totalExtractions').textContent = stats.total_extractions || 0;
        document.getElementById('completedExtractions').textContent = stats.estado_stats?.completado || 0;
        document.getElementById('processingExtractions').textContent = stats.estado_stats?.procesando || 0;
        document.getElementById('totalLogs').textContent = stats.total_logs || 0;
    }

    async cleanDatabase(cleanType) {
        const typeNames = {
            'logs_only': 'solo los logs',
            'completed_only': 'las extracciones completadas',
            'all': 'TODOS los registros'
        };

        const confirmed = confirm(`¿Estás seguro de que quieres eliminar ${typeNames[cleanType]}? Esta acción no se puede deshacer.`);
        
        if (!confirmed) return;

        try {
            this.showLoading('Limpiando base de datos...');

            const response = await fetch('/extraccion/api/clean_database', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: cleanType
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(result.message, 'success');
                this.loadHistory();
                this.loadStats();
            } else {
                this.showToast(result.message, 'error');
            }

        } catch (error) {
            console.error('Error cleaning database:', error);
            this.showToast('Error al limpiar la base de datos', 'error');
        } finally {
            this.hideLoading();
            this.cleanupModals(); // Limpiar cualquier dropdown residual
        }
    }

    showLoading(message = 'Procesando...') {
        // Eliminar cualquier modal existente primero
        this.hideLoading();
        
        // Crear nuevo modal de carga
        const modalHtml = `
            <div class="modal fade" id="loadingModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-sm modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-body text-center">
                            <div class="spinner-border text-primary mb-3" role="status">
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
        document.getElementById('loadingMessage').textContent = message;
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
            // Forzar eliminación después de un pequeño timeout
            setTimeout(() => {
                if (loadingModal && loadingModal.parentNode) {
                    loadingModal.remove();
                }
            }, 300);
        }
    }

    async generateAndDownloadAll() {
        if (!this.validateForm()) return;

        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        try {
            this.showLoading('Generando y descargando todos los PDFs...');

            const response = await fetch('/extraccion/api/generate_and_download_all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fecha_inicio: fechaInicio,
                    fecha_fin: fechaFin
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('Extracción masiva iniciada. Se generará un ZIP con todos los PDFs.', 'success');
                
                // Monitorear el progreso
                this.monitorExtraction(result.extraction_id);
            } else {
                this.showToast(result.message || 'Error al iniciar extracción masiva', 'error');
            }

        } catch (error) {
            console.error('Error en generate and download all:', error);
            this.showToast('Error al iniciar extracción masiva', 'error');
        } finally {
            this.hideLoading();
            this.cleanupModals(); // Limpiar cualquier dropdown residual
        }
    }

    async monitorExtraction(extractionId) {
        const checkStatus = async () => {
            try {
                const response = await fetch('/extraccion/api/extractions');
                const extractions = await response.json();
                
                const extraction = extractions.find(e => e.id === extractionId);
                if (extraction) {
                    if (extraction.estado === 'completado' && extraction.archivo_pdf && extraction.archivo_pdf.endsWith('.zip')) {
                        // Descargar el ZIP generado
                        const link = document.createElement('a');
                        link.href = `/extraccion/reports/${extraction.archivo_pdf}`;
                        link.download = extraction.archivo_pdf;
                        link.target = '_blank';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        this.showToast('ZIP generado y descargado exitosamente', 'success');
                        this.loadHistory();
                        return;
                    } else if (extraction.estado === 'error') {
                        this.showToast('Error en la extracción masiva', 'error');
                        return;
                    }
                }
                
                // Continuar monitoreando
                setTimeout(checkStatus, 3000);
            } catch (error) {
                console.error('Error monitoring extraction:', error);
            }
        };
        
        setTimeout(checkStatus, 2000); // Empezar a monitorear después de 2 segundos
    }

    async downloadAllPdfs() {
        try {
            this.showLoading('Preparando descarga de todos los PDFs...');

            const response = await fetch('/extraccion/api/download_all_pdfs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Crear un blob y descargar
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `reportes_completos_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.showToast('Descarga de todos los PDFs iniciada', 'success');
            } else {
                const error = await response.json();
                this.showToast(error.message || 'Error al descargar PDFs', 'error');
            }

        } catch (error) {
            console.error('Error downloading PDFs:', error);
            this.showToast('Error al descargar PDFs', 'error');
        } finally {
            this.hideLoading();
            this.cleanupModals(); // Limpiar cualquier dropdown residual
        }
    }

    async showPdfsModal() {
        try {
            this.showLoading('Cargando lista de PDFs...');

            const response = await fetch('/extraccion/api/list_pdfs');
            const result = await response.json();

            if (result.success) {
                this.renderPdfsList(result.pdfs);
                
                // Pequeña pausa para asegurar que el DOM esté listo
                setTimeout(() => {
                    const modalElement = document.getElementById('pdfsModal');
                    if (modalElement) {
                        // Limpiar cualquier instancia anterior del modal
                        const existingModal = bootstrap.Modal.getInstance(modalElement);
                        if (existingModal) {
                            existingModal.dispose();
                        }
                        
                        const modal = new bootstrap.Modal(modalElement);
                        modal.show();
                        
                        // Asegurar que el modal se pueda cerrar correctamente
                        modalElement.addEventListener('hidden.bs.modal', () => {
                            // Limpiar cualquier backdrop residual
                            const backdrops = document.querySelectorAll('.modal-backdrop');
                            backdrops.forEach(backdrop => backdrop.remove());
                            document.body.classList.remove('modal-open');
                        }, { once: true });
                    }
                }, 100);
            } else {
                this.showToast(result.message || 'Error al cargar PDFs', 'error');
            }

        } catch (error) {
            console.error('Error loading PDFs:', error);
            this.showToast('Error al cargar PDFs', 'error');
        } finally {
            this.hideLoading();
        }
    }

    renderPdfsList(pdfs) {
        const container = document.getElementById('pdfsContainer');
        
        if (pdfs.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-file-pdf fa-3x mb-3"></i>
                    <h5>No hay PDFs disponibles</h5>
                    <p>Aún no se han generado reportes PDF</p>
                </div>
            `;
            
            // Auto-cerrar el modal después de 2 segundos si no hay PDFs
            setTimeout(() => {
                const modalElement = document.getElementById('pdfsModal');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                }
            }, 2000);
            
            return;
        }

        let html = `
            <div class="mb-3">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card bg-primary text-white">
                            <div class="card-body text-center">
                                <h5 class="card-title mb-0">${pdfs.length}</h5>
                                <small>Total PDFs</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-success text-white">
                            <div class="card-body text-center">
                                <h5 class="card-title mb-0">${pdfs.filter(p => p.exists).length}</h5>
                                <small>Disponibles</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-info text-white">
                            <div class="card-body text-center">
                                <h5 class="card-title mb-0">${this.formatFileSize(pdfs.reduce((sum, p) => sum + p.size, 0))}</h5>
                                <small>Tamaño Total</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th><input type="checkbox" id="selectAllPdfs" class="form-check-input"></th>
                            <th>Sitio</th>
                            <th>Período</th>
                            <th>Ventas</th>
                            <th>Total</th>
                            <th>Comisión</th>
                            <th>Total a Enviar</th>
                            <th>Tamaño</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        pdfs.forEach((pdf, index) => {
            const statusBadge = pdf.exists ? 
                '<span class="badge bg-success">Disponible</span>' : 
                '<span class="badge bg-danger">No encontrado</span>';

            const downloadBtn = pdf.exists ? 
                `<a href="/extraccion/reports/${pdf.archivo_pdf}" class="btn btn-sm btn-outline-primary" target="_blank">
                    <i class="fas fa-download"></i>
                </a>` : 
                '<button class="btn btn-sm btn-outline-secondary" disabled><i class="fas fa-download"></i></button>';

            const checkbox = pdf.exists ? 
                `<input type="checkbox" class="form-check-input pdf-checkbox" data-pdf="${pdf.archivo_pdf}">` : 
                '<input type="checkbox" class="form-check-input" disabled>';

            html += `
                <tr class="${pdf.exists ? '' : 'table-secondary'}">
                    <td>${checkbox}</td>
                    <td><strong>${pdf.sitio}</strong></td>
                    <td>${pdf.fecha_inicio} al ${pdf.fecha_fin}</td>
                    <td>${pdf.total_ventas || 0}</td>
                    <td>$ ${(pdf.total_valor || 0).toLocaleString('es-CO')}</td>
                    <td>$ ${(pdf.total_comision || 0).toLocaleString('es-CO')}</td>
                    <td>$ ${(pdf.total_enviar || 0).toLocaleString('es-CO')}</td>
                    <td>${this.formatFileSize(pdf.size)}</td>
                    <td>${statusBadge}</td>
                    <td>${downloadBtn}</td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;

        // Agregar event listeners
        document.getElementById('selectAllPdfs').addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.pdf-checkbox');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async downloadSelectedPdfs() {
        const selectedCheckboxes = document.querySelectorAll('.pdf-checkbox:checked');
        
        if (selectedCheckboxes.length === 0) {
            this.showToast('Por favor selecciona al menos un PDF', 'warning');
            return;
        }

        try {
            this.showLoading(`Descargando ${selectedCheckboxes.length} PDFs seleccionados...`);

            // Crear un ZIP temporal con los PDFs seleccionados
            const selectedPdfs = Array.from(selectedCheckboxes).map(cb => cb.dataset.pdf);
            
            // Para simplificar, descargaremos individualmente
            for (const pdf of selectedPdfs) {
                const link = document.createElement('a');
                link.href = `/extraccion/reports/${pdf}`;
                link.download = pdf;
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Pequeña pausa entre descargas
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            this.showToast(`${selectedCheckboxes.length} PDFs descargados exitosamente`, 'success');

        } catch (error) {
            console.error('Error downloading selected PDFs:', error);
            this.showToast('Error al descargar PDFs seleccionados', 'error');
        } finally {
            this.hideLoading();
        }
    }

    renderHistoryTable(extractions) {
        const tbody = document.getElementById('historyTableBody');
        tbody.innerHTML = '';

        extractions.forEach(extraction => {
            const row = document.createElement('tr');
            
            const estadoBadge = this.getEstadoBadge(extraction.estado);
            let pdfLink = '-';
            if (extraction.archivo_pdf) {
                if (extraction.archivo_pdf.endsWith('.zip')) {
                    pdfLink = `<a href="/extraccion/reports/${extraction.archivo_pdf}" class="btn btn-sm btn-success" target="_blank">
                        <i class="fas fa-file-archive"></i> Descargar ZIP
                    </a>`;
                } else {
                    pdfLink = `<a href="/extraccion/reports/${extraction.archivo_pdf}" class="btn btn-sm btn-outline-primary" target="_blank">
                        <i class="fas fa-file-pdf"></i> PDF
                    </a>`;
                }
            }

            // Convertir UTC a hora de Colombia (UTC-5)
            const utcDate = new Date(extraction.creado_en);
            const colombiaTime = new Date(utcDate.getTime() - (5 * 60 * 60 * 1000));
            
            const fecha = colombiaTime.toLocaleString('es-CO', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });

            row.innerHTML = `
                <td>${extraction.id}</td>
                <td>${extraction.sitio}</td>
                <td>${extraction.fecha_inicio} al ${extraction.fecha_fin}</td>
                <td>${estadoBadge}</td>
                <td>${extraction.total_ventas || 0}</td>
                <td>$ ${(extraction.total_valor || 0).toLocaleString('es-CO')}</td>
                <td>$ ${(extraction.total_comision || 0).toLocaleString('es-CO')}</td>
                <td>$ ${(extraction.total_enviar || 0).toLocaleString('es-CO')}</td>
                <td>${pdfLink}</td>
                <td>
                    <small class="text-muted">${fecha}</small>
                    <button class="btn btn-sm btn-outline-secondary ms-2" onclick="app.showLogs(${extraction.id})">
                        <i class="fas fa-list"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(row);
        });
    }

    getEstadoBadge(estado) {
        const badges = {
            'pendiente': '<span class="badge bg-secondary">Pendiente</span>',
            'procesando': '<span class="badge bg-primary">Procesando</span>',
            'completado': '<span class="badge bg-success">Completado</span>',
            'error': '<span class="badge bg-danger">Error</span>'
        };
        return badges[estado] || badges['pendiente'];
    }

    async showLogs(extractionId) {
        try {
            const response = await fetch(`/extraccion/api/extraction/${extractionId}/logs`);
            const logs = await response.json();

            this.renderLogs(logs);
            
            const modal = new bootstrap.Modal(document.getElementById('logsModal'));
            modal.show();

        } catch (error) {
            console.error('Error loading logs:', error);
            this.showToast('Error al cargar logs', 'error');
        }
    }

    renderLogs(logs) {
        const container = document.getElementById('logsContainer');
        container.innerHTML = '';

        if (logs.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay logs disponibles</p>';
            return;
        }

        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.tipo}`;
            
            // Convertir UTC a hora de Colombia (UTC-5)
            const utcLogTime = new Date(log.creado_en);
            const colombiaLogTime = new Date(utcLogTime.getTime() - (5 * 60 * 60 * 1000));
            const timestamp = colombiaLogTime.toLocaleTimeString('es-CO');
            
            logEntry.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div class="log-message">${log.mensaje}</div>
                    <small class="log-time text-muted">${timestamp}</small>
                </div>
            `;

            container.appendChild(logEntry);
        });

        // Scroll al final
        container.scrollTop = container.scrollHeight;
    }

    disableButtons(disabled) {
        document.getElementById('extractAllBtn').disabled = disabled;
        document.querySelectorAll('.extract-site-btn').forEach(btn => {
            btn.disabled = disabled;
        });
    }

    showToast(message, type = 'info') {
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
        // Aumentar el tiempo para notificaciones importantes
        const delay = type === 'success' && message.includes('ZIP disponible') ? 8000 : 3000;
        
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: delay
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

    cleanupModals() {
        // Limpiar cualquier backdrop residual de modales
        const modalBackdrops = document.querySelectorAll('.modal-backdrop');
        modalBackdrops.forEach(backdrop => backdrop.remove());
        
        // Limpiar cualquier backdrop residual de dropdowns
        const dropdownBackdrops = document.querySelectorAll('.dropdown-backdrop');
        dropdownBackdrops.forEach(backdrop => backdrop.remove());
        
        // Cerrar todos los dropdowns abiertos
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        
        // Remover clases y estilos del body
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
        
        // Limpiar cualquier atributo aria relacionado con modales/dropdowns
        document.body.removeAttribute('aria-modal');
        document.body.removeAttribute('role');
    }

    startPolling() {
        // Polling cada 5 segundos para actualizar estados
        setInterval(() => {
            this.checkExtractionStatus();
        }, 5000);
        
        // Limpieza automática cada 10 segundos para eliminar elementos residuales
        setInterval(() => {
            this.cleanupModals();
        }, 10000);
    }

    async checkExtractionStatus() {
        if (this.currentExtractions.size === 0) return;

        try {
            const response = await fetch('/extraccion/api/extractions');
            const extractions = await response.json();

            extractions.forEach(extraction => {
                if (this.currentExtractions.has(extraction.id)) {
                    const currentExtraction = this.currentExtractions.get(extraction.id);
                    
                    if (currentExtraction.type === 'site') {
                        this.updateSiteStatus(currentExtraction.sitio, extraction.estado);
                    }
                    
                    if (extraction.estado === 'completado' || extraction.estado === 'error') {
                        // Mostrar notificación especial si es una extracción TODOS completada con ZIP
                        if (currentExtraction.type === 'all' && extraction.estado === 'completado' && extraction.archivo_pdf && extraction.archivo_pdf.endsWith('.zip')) {
                            this.showToast(`¡Extracción completada! ZIP disponible para descargar con todos los reportes.`, 'success');
                            // Actualizar todos los sitios a completado
                            this.updateAllSiteStatus('completed');
                        } else if (currentExtraction.type === 'all') {
                            // Actualizar todos los sitios según el estado final
                            this.updateAllSiteStatus(extraction.estado === 'completado' ? 'completed' : 'error');
                        }
                        
                        this.currentExtractions.delete(extraction.id)
                        this.loadHistory(); // Refrescar historial
                        this.loadStats(); // Refrescar estadísticas
                        
                        // Ocultar sección de progreso si no hay extracciones activas
                        if (this.currentExtractions.size === 0) {
                            document.getElementById('progressSection').style.display = 'none';
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Error checking status:', error);
        }
    }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ExtractionApp();
});