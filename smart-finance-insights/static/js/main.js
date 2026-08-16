/* Smart Finance Insights - Main JavaScript */

// Toggle sidebar (mobile)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (sidebar) {
        sidebar.classList.toggle('active');
        if (overlay) overlay.classList.toggle('active');
    }
}

// Close sidebar when clicking overlay
document.addEventListener('DOMContentLoaded', function() {
    // Create sidebar overlay
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.onclick = toggleSidebar;
    document.body.appendChild(overlay);

    // Auto-dismiss flash messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(f => {
            f.style.opacity = '0';
            f.style.transform = 'translateY(-10px)';
            setTimeout(() => f.remove(), 300);
        });
    }, 5000);

    // Modal handling
    document.querySelectorAll('[data-modal-open]').forEach(btn => {
        btn.onclick = () => {
            const modal = document.getElementById(btn.dataset.modalOpen);
            if (modal) modal.classList.add('active');
        };
    });
    document.querySelectorAll('.modal-close, .modal-overlay').forEach(el => {
        el.onclick = (e) => {
            if (e.target === el) el.closest('.modal-overlay').classList.remove('active');
        };
    });

    // Edit transaction modal
    document.querySelectorAll('.edit-txn-btn').forEach(btn => {
        btn.onclick = async () => {
            const id = btn.dataset.id;
            const type = btn.dataset.type;
            const res = await fetch(`/api/transaction/${id}?type=${type}`);
            const data = await res.json();
            if (data.error) return alert('Error: ' + data.error);

            const form = document.getElementById('editTxnForm');
            form.action = `/expenses/edit/${id}`;
            form.querySelector('[name="type"]').value = type;
            form.querySelector('[name="category"]').value = data.category;
            form.querySelector('[name="description"]').value = data.description;
            form.querySelector('[name="amount"]').value = data.amount;
            form.querySelector('[name="date"]').value = data.date;
            document.getElementById('editTxnModal').classList.add('active');
        };
    });

    // Edit investment modal
    document.querySelectorAll('.edit-inv-btn').forEach(btn => {
        btn.onclick = async () => {
            const id = btn.dataset.id;
            const res = await fetch(`/api/investment/${id}`);
            const data = await res.json();
            if (data.error) return alert('Error: ' + data.error);

            const form = document.getElementById('editInvForm');
            form.action = `/investments/edit/${id}`;
            form.querySelector('[name="asset_type"]').value = data.asset_type;
            form.querySelector('[name="name"]').value = data.name;
            form.querySelector('[name="invested"]').value = data.invested;
            form.querySelector('[name="current"]').value = data.current;
            form.querySelector('[name="purchase_date"]').value = data.purchase_date;
            document.getElementById('editInvModal').classList.add('active');
        };
    });

    // Edit goal modal
    document.querySelectorAll('.edit-goal-btn').forEach(btn => {
        btn.onclick = async () => {
            const id = btn.dataset.id;
            const res = await fetch(`/api/goal/${id}`);
            const data = await res.json();
            if (data.error) return alert('Error: ' + data.error);

            const form = document.getElementById('editGoalForm');
            form.action = `/goals/edit/${id}`;
            form.querySelector('[name="name"]').value = data.name;
            form.querySelector('[name="target"]').value = data.target;
            form.querySelector('[name="saved"]').value = data.saved;
            form.querySelector('[name="target_date"]').value = data.target_date;
            form.querySelector('[name="category"]').value = data.category;
            document.getElementById('editGoalModal').classList.add('active');
        };
    });

    // Transaction type toggle in expense form
    const typeSelect = document.getElementById('txnType');
    if (typeSelect) {
        typeSelect.onchange = () => {
            const isIncome = typeSelect.value === 'income';
            const catSelect = document.getElementById('txnCategory');
            const sources = JSON.parse(catSelect.dataset.sources || '[]');
            const categories = JSON.parse(catSelect.dataset.categories || '[]');
            const options = isIncome ? sources : categories;
            catSelect.innerHTML = options.map(c => `<option value="${c}">${c}</option>`).join('');
        };
        typeSelect.onchange();
    }

    // Contribute to goal modal
    document.querySelectorAll('.contribute-btn').forEach(btn => {
        btn.onclick = () => {
            const form = document.getElementById('contributeForm');
            form.action = `/goals/contribute/${btn.dataset.id}`;
            form.querySelector('[name="amount"]').value = '';
            document.getElementById('contributeModal').classList.add('active');
        };
    });

    // Chart instances stored for cleanup
    window.chartInstances = window.chartInstances || [];

    // Destroy existing charts (prevents duplicate canvas errors)
    window.chartInstances.forEach(c => { try { c.destroy(); } catch(e){} });
    window.chartInstances = [];
});

// ============ Chart helpers ============
function createChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const chart = new Chart(canvas.getContext('2d'), config);
    window.chartInstances = window.chartInstances || [];
    window.chartInstances.push(chart);
    return chart;
}

// Format currency for display
function formatCurrency(amount) {
    return '₹' + Number(amount || 0).toLocaleString('en-IN');
}

// JARVIS Chat
function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const messages = document.getElementById('chatMessages');
    // Add user message
    messages.innerHTML += `
        <div class="chat-message user">
            <div class="chat-avatar user"><i class="bi bi-person"></i></div>
            <div class="chat-bubble">${escapeHtml(message)}</div>
        </div>`;
    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    messages.innerHTML += `
        <div class="chat-message assistant" id="${typingId}">
            <div class="chat-avatar jarvis"><i class="bi bi-robot"></i></div>
            <div class="chat-bubble"><i class="bi bi-three-dots"></i> JARVIS is typing...</div>
        </div>`;
    messages.scrollTop = messages.scrollHeight;

    // Send to server
    const formData = new FormData();
    formData.append('message', message);
    fetch('/jarvis/chat', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            const typing = document.getElementById(typingId);
            if (typing) typing.remove();
            if (data.error) {
                messages.innerHTML += `
                    <div class="chat-message assistant">
                        <div class="chat-avatar jarvis"><i class="bi bi-robot"></i></div>
                        <div class="chat-bubble">Sorry, I encountered an error. Please try again.</div>
                    </div>`;
            } else {
                messages.innerHTML += `
                    <div class="chat-message assistant">
                        <div class="chat-avatar jarvis"><i class="bi bi-robot"></i></div>
                        <div class="chat-bubble">${escapeHtml(data.response)}</div>
                    </div>`;
            }
            messages.scrollTop = messages.scrollHeight;
        })
        .catch(() => {
            const typing = document.getElementById(typingId);
            if (typing) typing.remove();
        });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Chat input - send on Enter
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
        chatInput.style.height = 'auto';
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    // Chat suggestion clicks
    document.querySelectorAll('.chat-suggestion').forEach(s => {
        s.onclick = () => {
            chatInput.value = s.textContent;
            sendChatMessage();
        };
    });

    // Scroll chat to bottom on load
    const messages = document.getElementById('chatMessages');
    if (messages) messages.scrollTop = messages.scrollHeight;
});

// Delete confirmation
function confirmDelete(event, message) {
    if (!confirm(message || 'Are you sure you want to delete this?')) {
        event.preventDefault();
        return false;
    }
    return true;
}
