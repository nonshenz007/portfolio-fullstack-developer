// Settings page handlers
import { toast } from './toast.js';

function openPasswordModal() {
    // TODO: Implement password change modal
    console.log('Password modal not implemented yet');
}

async function regenerateHash() {
    try {
        await fetch('/api/verichain/regenerate', { 
            method: 'POST',
            credentials: 'include'
        });
        toast('Hash-chain rebuilt');
    } catch (error) {
        toast('Failed to rebuild hash-chain', 'error');
    }
}

async function clearExports() {
    if (confirm('Delete all exported files?')) {
        try {
            await fetch('/api/exports/clear', { 
                method: 'DELETE',
                credentials: 'include'
            });
            toast('Exports cleared');
        } catch (error) {
            toast('Failed to clear exports', 'error');
        }
    }
}

// Debug toggle handler
document.addEventListener('DOMContentLoaded', function() {
    const debugToggle = document.getElementById('debug_toggle');
    if (debugToggle) {
        debugToggle.addEventListener('change', function(e) {
            fetch('/api/debug/' + (e.target.checked ? 'on' : 'off'), { 
                method: 'POST',
                credentials: 'include'
            });
        });
    }
});

// Export functions for use in other modules
window.openPasswordModal = openPasswordModal;
window.regenerateHash = regenerateHash;
window.clearExports = clearExports; 