document.addEventListener("DOMContentLoaded", () => {
    const scanForm = document.getElementById("scanForm");
    const urlInput = document.getElementById("urlInput");
    const scanBtn = document.getElementById("scanBtn");
    const errorMessage = document.getElementById("errorMessage");
    
    const resultsSection = document.getElementById("resultsSection");
    const riskBadge = document.getElementById("riskBadge");
    const analyzedUrl = document.getElementById("analyzedUrl");
    const predictionText = document.getElementById("predictionText");
    const riskScoreVal = document.getElementById("riskScoreVal");
    const phishingProbVal = document.getElementById("phishingProbVal");
    const progressFill = document.getElementById("progressFill");
    const explanationsList = document.getElementById("explanationsList");
    const historyTableBody = document.getElementById("historyTableBody");
    const totalScansCount = document.getElementById("totalScansCount");

    // Load Initial History & Stats
    fetchHistory();
    fetchStats();

    scanForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        showError("");
        setLoading(true);

        try {
            const response = await fetch("/api/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            if (!response.ok || data.status === "error") {
                showError(data.message || "Failed to analyze URL.");
                resultsSection.classList.add("hidden");
            } else {
                renderResults(data);
                fetchHistory();
                fetchStats();
            }
        } catch (err) {
            showError("Network error: Could not reach the scanning server.");
        } finally {
            setLoading(false);
        }
    });

    function renderResults(data) {
        resultsSection.classList.remove("hidden");
        analyzedUrl.textContent = data.url;
        predictionText.textContent = data.prediction;
        riskScoreVal.textContent = `${data.risk_score} / 100`;
        phishingProbVal.textContent = `${(data.phishing_probability * 100).toFixed(1)}%`;

        // Update Risk Badge
        riskBadge.textContent = data.risk_level;
        riskBadge.className = "badge " + getBadgeClass(data.risk_score);

        // Update Progress Bar
        progressFill.style.width = `${data.risk_score}%`;
        progressFill.style.backgroundColor = getProgressColor(data.risk_score);

        // Render Explanations
        explanationsList.innerHTML = "";
        if (data.explanations && data.explanations.length > 0) {
            data.explanations.forEach(exp => {
                const li = document.createElement("li");
                li.textContent = exp;
                explanationsList.appendChild(li);
            });
        } else {
            const li = document.createElement("li");
            li.textContent = "No specific threat flags triggered.";
            explanationsList.appendChild(li);
        }

        resultsSection.scrollIntoView({ behavior: "smooth" });
    }

    async function fetchHistory() {
        try {
            const res = await fetch("/api/history?limit=10");
            const data = await res.json();
            if (data.status === "success" && data.history) {
                renderHistoryTable(data.history);
            }
        } catch (err) {
            console.error("Failed to load scan history:", err);
        }
    }

    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.status === "success" && data.stats) {
                totalScansCount.textContent = data.stats.total_scans;
            }
        } catch (err) {
            console.error("Failed to load stats:", err);
        }
    }

    function renderHistoryTable(history) {
        if (!history || history.length === 0) {
            historyTableBody.innerHTML = '<tr><td colspan="5" class="empty-msg">No recent scan records found.</td></tr>';
            return;
        }

        historyTableBody.innerHTML = history.map(item => `
            <tr>
                <td>${formatDate(item.created_at)}</td>
                <td class="url-value">${escapeHtml(item.url)}</td>
                <td><strong>${item.prediction}</strong></td>
                <td>${item.risk_score} / 100</td>
                <td><span class="badge ${getBadgeClass(item.risk_score)}">${item.risk_level}</span></td>
            </tr>
        `).join("");
    }

    function getBadgeClass(score) {
        if (score < 30) return "safe";
        if (score < 60) return "suspicious";
        if (score < 85) return "high-risk";
        return "critical";
    }

    function getProgressColor(score) {
        if (score < 30) return "#22c55e";
        if (score < 60) return "#eab308";
        if (score < 85) return "#ef4444";
        return "#991b1b";
    }

    function setLoading(isLoading) {
        scanBtn.disabled = isLoading;
        scanBtn.querySelector(".btn-text").textContent = isLoading ? "Analyzing..." : "Scan URL";
    }

    function showError(msg) {
        if (msg) {
            errorMessage.textContent = msg;
            errorMessage.classList.remove("hidden");
        } else {
            errorMessage.textContent = "";
            errorMessage.classList.add("hidden");
        }
    }

    function formatDate(dateStr) {
        if (!dateStr) return "-";
        const d = new Date(dateStr);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }
});
