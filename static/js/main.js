const today = new Date().toLocaleDateString("en-CA");
const datePicker = document.getElementById("date-picker");
const tbody = document.getElementById("session-tbody");

datePicker.value = today;

async function fetchSessions(date) {
    try {
        const response = await fetch(`/api/sessions?date=${date}`);
        const sessions = await response.json();
        renderTable(sessions);
    } catch (e) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center py-4">Failed to load sessions.</td>
            </tr>`;
    }
}

function renderTable(sessions) {
    tbody.innerHTML = "";

    if (sessions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center align-middle py-6 italic">
                    No games played on this date.
                </td>
            </tr>`;
        return;
    }

    const grouped = {};
    sessions.forEach((session) => {
        if (!grouped[session.game_name]) {
            grouped[session.game_name] = [];
        }
        grouped[session.game_name].push(session);
    });

    Object.entries(grouped).forEach(([gameName, sessions]) => {
        sessions.forEach((session) => {
            const start = new Date(session.start_time).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
            });
            const end = new Date(session.end_time).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
            });

            const row = document.createElement("tr");
            row.innerHTML = `
                <td class="text-center align-middle px-6 py-3">${gameName}</td>
                <td class="text-center align-middle px-6 py-3">${start} - ${end}</td>
                <td class="text-center align-middle px-6 py-3">${session.duration_minutes} min</td>
            `;
            tbody.appendChild(row);
        });
    });
}

datePicker.addEventListener("change", (e) => fetchSessions(e.target.value));

document.getElementById("reset-btn").addEventListener("click", () => {
    datePicker.value = today;
    fetchSessions(today);
});

fetchSessions(today);
