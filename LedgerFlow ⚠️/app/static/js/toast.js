// Toast notification helper
export function toast(msg, type = 'success') {
    const d = document.createElement('div');
    d.className = `toast ${type}`;
    d.textContent = msg;
    document.body.append(d);
    setTimeout(() => d.remove(), 3000);
} 