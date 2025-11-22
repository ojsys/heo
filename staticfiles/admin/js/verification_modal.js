/* Verification Modal JavaScript for Admin List View */

(function() {
    'use strict';

    // Create modal element for list view
    function createListViewModal() {
        if (document.getElementById('listViewModal')) return;

        const modal = document.createElement('div');
        modal.id = 'listViewModal';
        modal.innerHTML = `
            <span class="close-btn" onclick="closeListViewModal()">&times;</span>
            <div class="modal-content">
                <div class="modal-title" id="listModalTitle"></div>
                <img id="listModalImage" src="" alt="Document Preview">
            </div>
        `;
        document.body.appendChild(modal);

        // Close on click outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeListViewModal();
            }
        });
    }

    // Open modal
    window.openListViewModal = function(url, title) {
        createListViewModal();
        document.getElementById('listModalImage').src = url;
        document.getElementById('listModalTitle').textContent = title;
        document.getElementById('listViewModal').style.display = 'block';
    };

    // Close modal
    window.closeListViewModal = function() {
        const modal = document.getElementById('listViewModal');
        if (modal) {
            modal.style.display = 'none';
        }
    };

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Add click handlers to all document view buttons
        document.querySelectorAll('.view-doc-btn').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('data-url');
                const title = this.getAttribute('data-title');
                openListViewModal(url, title);
            });
        });

        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeListViewModal();
            }
        });
    });
})();
