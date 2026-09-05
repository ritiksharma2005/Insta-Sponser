import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sponsor_engine.db"
LEADS_JSON_PATH = BASE_DIR / "data" / "leads.json"

def get_all_clients():
    """Fetches all client records from SQLite DB or leads.json fallback."""
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads ORDER BY lead_score DESC")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                return [dict(r) for r in rows]
        except Exception as e:
            print("SQLite Error:", e)

    if LEADS_JSON_PATH.exists():
        try:
            with open(LEADS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("JSON Error:", e)
    return []

def update_client_in_db(lead_id, status, notes=""):
    """Updates status and notes for a client."""
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leads SET status = ?, notes = ? WHERE lead_id = ?",
                (status, notes, lead_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("Update DB error:", e)

    # Sync leads.json
    if LEADS_JSON_PATH.exists():
        try:
            with open(LEADS_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                if item.get("lead_id") == lead_id:
                    item["status"] = status
                    if notes:
                        item["notes"] = notes
            with open(LEADS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Sync JSON error:", e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News NIT IIT - Automated Client DM & Pipeline Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#f0f9ff',
                            500: '#0284c7',
                            600: '#0284c7',
                            900: '#0c4a6e',
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Header -->
        <header class="flex flex-col md:flex-row md:items-center md:justify-between pb-8 border-b border-slate-800">
            <div>
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-sky-500/10 text-sky-400 rounded-xl border border-sky-500/20">
                        <i class="fa-solid fa-paper-plane text-2xl"></i>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold text-white tracking-tight">News NIT IIT – Sponsor CRM</h1>
                        <p class="text-sm text-slate-400">Automated Daily DM Engine & Client History Tracker</p>
                    </div>
                </div>
            </div>
            <div class="mt-4 md:mt-0 flex items-center gap-3">
                <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    GitHub Actions Daily Cron Active
                </span>
            </div>
        </header>

        <!-- Metric Cards -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 my-8">
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm">
                <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Discovered</div>
                <div class="text-3xl font-bold text-sky-400 mt-2" id="metric-total">0</div>
            </div>
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm">
                <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">🔥 Hot Prospects</div>
                <div class="text-3xl font-bold text-rose-400 mt-2" id="metric-hot">0</div>
            </div>
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm">
                <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Auto DMs Sent</div>
                <div class="text-3xl font-bold text-emerald-400 mt-2" id="metric-contacted">0</div>
            </div>
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm">
                <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Follow-Ups Active</div>
                <div class="text-3xl font-bold text-amber-400 mt-2" id="metric-followup">0</div>
            </div>
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm col-span-2 md:col-span-1">
                <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Converted Clients</div>
                <div class="text-3xl font-bold text-indigo-400 mt-2" id="metric-converted">0</div>
            </div>
        </div>

        <!-- Filters & Search -->
        <div class="flex flex-col sm:flex-row gap-4 mb-8 justify-between items-center bg-slate-900/40 p-4 rounded-2xl border border-slate-800">
            <div class="w-full sm:w-72 relative">
                <i class="fa-solid fa-search absolute left-3.5 top-3.5 text-slate-500"></i>
                <input type="text" id="search-input" onkeyup="filterClients()" placeholder="Search business or city..." 
                       class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500">
            </div>

            <div class="flex gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
                <button onclick="setFilter('ALL')" class="filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-sky-500 text-white" data-status="ALL">All Clients</button>
                <button onclick="setFilter('CONTACTED')" class="filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700" data-status="CONTACTED">Auto DMs Sent</button>
                <button onclick="setFilter('REPLIED')" class="filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700" data-status="REPLIED">Replied</button>
                <button onclick="setFilter('FOLLOWED_UP')" class="filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700" data-status="FOLLOWED_UP">Follow-Up Sent</button>
                <button onclick="setFilter('CONVERTED')" class="filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700" data-status="CONVERTED">Converted</button>
            </div>
        </div>

        <!-- Client List -->
        <div id="clients-container" class="space-y-6">
            <!-- Dynamic Client Cards Rendered via JS -->
        </div>
    </div>

    <script>
        let rawClients = {{ clients_json|safe }};
        let currentFilter = 'ALL';

        function renderClients() {
            const container = document.getElementById('clients-container');
            const searchVal = document.getElementById('search-input').value.toLowerCase();

            let filtered = rawClients.filter(c => {
                const matchesStatus = currentFilter === 'ALL' || c.status === currentFilter;
                const matchesSearch = c.business_name.toLowerCase().includes(searchVal) || 
                                      c.city.toLowerCase().includes(searchVal) ||
                                      c.category.toLowerCase().includes(searchVal);
                return matchesStatus && matchesSearch;
            });

            // Update Metrics
            document.getElementById('metric-total').innerText = rawClients.length;
            document.getElementById('metric-hot').innerText = rawClients.filter(c => c.lead_tier === 'HOT').length;
            document.getElementById('metric-contacted').innerText = rawClients.filter(c => c.status === 'CONTACTED' || c.status === 'APPROVED').length;
            document.getElementById('metric-followup').innerText = rawClients.filter(c => c.status === 'FOLLOWED_UP' || c.status === 'REPLIED').length;
            document.getElementById('metric-converted').innerText = rawClients.filter(c => c.status === 'CONVERTED').length;

            if (filtered.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-16 bg-slate-900/30 rounded-2xl border border-slate-800">
                        <i class="fa-solid fa-folder-open text-4xl text-slate-600 mb-3"></i>
                        <p class="text-slate-400 font-medium">No client records matching current filter.</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = filtered.map(client => {
                const cleanHandle = (client.instagram || '').replace('@', '').trim();
                const igUrl = cleanHandle ? `https://ig.me/m/${cleanHandle}` : '#';
                
                let statusBadgeClass = 'bg-sky-500/10 text-sky-400 border-sky-500/20';
                if (client.status === 'CONVERTED') statusBadgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
                if (client.status === 'REPLIED' || client.status === 'INTERESTED') statusBadgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
                if (client.status === 'FOLLOWED_UP') statusBadgeClass = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';

                return `
                    <div class="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 shadow-xl hover:border-slate-700 transition">
                        <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-4 pb-4 border-b border-slate-800/60">
                            <div>
                                <div class="flex items-center gap-3">
                                    <h3 class="text-xl font-bold text-white">${client.business_name}</h3>
                                    <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">${client.lead_tier} (${client.lead_score}/100)</span>
                                </div>
                                <p class="text-xs text-slate-400 mt-1">
                                    <i class="fa-solid fa-tag text-slate-500 mr-1"></i>${client.category} &nbsp;|&nbsp;
                                    <i class="fa-solid fa-location-dot text-slate-500 mr-1"></i>${client.city}, ${client.state} &nbsp;|&nbsp;
                                    <i class="fa-brands fa-instagram text-slate-500 mr-1"></i>${client.instagram}
                                </p>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="px-3 py-1 rounded-full text-xs font-semibold border ${statusBadgeClass}">${client.status}</span>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 my-4">
                            <div class="lg:col-span-2">
                                <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Customized AI DM Message Sent:</label>
                                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 text-sm text-slate-300 font-mono whitespace-pre-wrap">${client.personalized_message}</div>
                            </div>

                            <div class="flex flex-col justify-between space-y-4">
                                <div>
                                    <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Follow-Up & Status Actions:</label>
                                    <div class="grid grid-cols-2 gap-2">
                                        <button onclick="updateStatus('${client.lead_id}', 'REPLIED')" class="px-3 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-amber-300 transition text-left">💬 Mark Replied</button>
                                        <button onclick="updateStatus('${client.lead_id}', 'FOLLOWED_UP')" class="px-3 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-indigo-300 transition text-left">🔄 Sent Follow-Up</button>
                                        <button onclick="updateStatus('${client.lead_id}', 'INTERESTED')" class="px-3 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-sky-300 transition text-left">⭐ Interested</button>
                                        <button onclick="updateStatus('${client.lead_id}', 'CONVERTED')" class="px-3 py-2 rounded-xl text-xs font-medium bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 transition text-left">🎉 Converted!</button>
                                    </div>
                                </div>

                                <a href="${igUrl}" target="_blank" class="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold text-xs tracking-wide shadow-lg transition">
                                    <i class="fa-brands fa-instagram text-base"></i> Open Direct Instagram Chat
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function setFilter(status) {
            currentFilter = status;
            document.querySelectorAll('.filter-btn').forEach(btn => {
                if (btn.dataset.status === status) {
                    btn.className = 'filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-sky-500 text-white';
                } else {
                    btn.className = 'filter-btn px-4 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700';
                }
            });
            renderClients();
        }

        function filterClients() {
            renderClients();
        }

        function updateStatus(leadId, newStatus) {
            fetch('/api/update-client', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lead_id: leadId, status: newStatus})
            })
            .then(res => res.json())
            .then(data => {
                const client = rawClients.find(c => c.lead_id === leadId);
                if (client) client.status = newStatus;
                renderClients();
            });
        }

        renderClients();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    clients = get_all_clients()
    return render_template_string(HTML_TEMPLATE, clients_json=json.dumps(clients))

@app.route("/api/clients")
def api_clients():
    return jsonify(get_all_clients())

@app.route("/api/update-client", methods=["POST"])
def api_update_client():
    data = request.get_json() or {}
    lead_id = data.get("lead_id")
    status = data.get("status")
    notes = data.get("notes", "")
    if lead_id and status:
        update_client_in_db(lead_id, status, notes)
        return jsonify({"success": True, "lead_id": lead_id, "status": status})
    return jsonify({"success": False, "error": "Invalid parameters"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
