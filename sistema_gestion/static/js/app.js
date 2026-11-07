// JavaScript principal para el Sistema de Gestión

// Función para inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-ocultar alertas después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Animación de entrada para las tarjetas
    animateCards();
});

// Función para animar las tarjetas del dashboard
function animateCards() {
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        setTimeout(function() {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

// Función para mostrar loading
function showLoading(element) {
    if (element) {
        element.disabled = true;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
    }
}

// Función para ocultar loading
function hideLoading(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}

// Función para confirmar acciones
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Función para formatear números
function formatNumber(num) {
    return new Intl.NumberFormat('es-CO').format(num);
}

// Función para formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
    }).format(amount);
}

// Función para formatear fechas
function formatDate(date) {
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Función para copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('¡Copiado al portapapeles!', 'success');
    }).catch(function(err) {
        console.error('Error al copiar: ', err);
        showNotification('Error al copiar al portapapeles', 'error');
    });
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    var notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Agregar al body
    document.body.appendChild(notification);

    // Auto-eliminar después de 5 segundos
    setTimeout(function() {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Función para manejar errores de AJAX
function handleAjaxError(xhr, status, error) {
    console.error('AJAX Error:', error);
    var message = 'Ocurrió un error inesperado';
    
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    } else if (xhr.status === 401) {
        message = 'No autorizado. Por favor inicia sesión.';
    } else if (xhr.status === 403) {
        message = 'Acceso denegado.';
    } else if (xhr.status === 404) {
        message = 'Recurso no encontrado.';
    } else if (xhr.status === 500) {
        message = 'Error del servidor.';
    }
    
    showNotification(message, 'error');
}

// Función para validar formularios
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return false;

    var inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    var isValid = true;

    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Función para limpiar formularios
function clearForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return;

    form.reset();
    var inputs = form.querySelectorAll('.is-invalid');
    inputs.forEach(function(input) {
        input.classList.remove('is-invalid');
    });
}

// Función para exportar datos a CSV
function exportToCSV(data, filename) {
    var csv = [];
    var headers = Object.keys(data[0]);
    csv.push(headers.join(','));

    data.forEach(function(row) {
        var values = headers.map(function(header) {
            return '"' + row[header] + '"';
        });
        csv.push(values.join(','));
    });

    var csvContent = csv.join('\n');
    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    var link = document.createElement('a');
    
    if (link.download !== undefined) {
        var url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Función para imprimir contenido
function printContent(elementId) {
    var element = document.getElementById(elementId);
    if (!element) return;

    var printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Imprimir</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Función para manejar responsive sidebar (si se implementa en el futuro)
function toggleSidebar() {
    var sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// Exportar funciones globalmente
window.SistemaGestion = {
    showLoading: showLoading,
    hideLoading: hideLoading,
    confirmAction: confirmAction,
    formatNumber: formatNumber,
    formatCurrency: formatCurrency,
    formatDate: formatDate,
    copyToClipboard: copyToClipboard,
    showNotification: showNotification,
    handleAjaxError: handleAjaxError,
    validateForm: validateForm,
    clearForm: clearForm,
    exportToCSV: exportToCSV,
    printContent: printContent,
    toggleSidebar: toggleSidebar
};