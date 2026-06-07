const COLORS = [
    "rgba(139, 92, 246, 0.85)",
    "rgba(6, 182, 212, 0.85)",
    "rgba(16, 185, 129, 0.85)",
    "rgba(245, 158, 11, 0.85)",
    "rgba(239, 68, 68, 0.85)",
    "rgba(236, 72, 153, 0.85)",
    "rgba(59, 130, 246, 0.85)",
    "rgba(234, 179, 8, 0.85)",
    "rgba(168, 85, 247, 0.85)",
    "rgba(20, 184, 166, 0.85)",
    "rgba(156, 163, 175, 0.6)",
];

const sharedOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: "bottom",
            labels: { color: "white", padding: 14 },
        },
        tooltip: {
            callbacks: {
                label: (ctx) => {
                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                    const pct = ((ctx.parsed / total) * 100).toFixed(1);
                    return ` ${ctx.label}: ${ctx.parsed} min (${pct}%)`;
                },
            },
        },
    },
};

async function loadGameTotalsChart() {
    const response = await fetch("/api/game-totals");
    const data = await response.json();

    const TOP_N = 8;
    const top = data.slice(0, TOP_N);
    const rest = data.slice(TOP_N);

    const labels = top.map((g) => g.game_name);
    const values = top.map((g) => g.total_duration_minutes);

    if (rest.length > 0) {
        labels.push("Others");
        values.push(rest.reduce((sum, g) => sum + g.total_duration_minutes, 0));
    }

    new Chart(document.getElementById("gameTotalsChart"), {
        type: "doughnut",
        data: {
            labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: COLORS.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: "rgba(0,0,0,0.2)",
                },
            ],
        },
        options: sharedOptions,
    });
}

async function loadYearlyChart() {
    const response = await fetch("/api/playtime/yearly");
    const data = await response.json();

    // year_total_minutes is the same on every row for a given year —
    // deduplicate by taking one value per year
    const yearMap = {};
    data.forEach((row) => {
        const year = row.play_year.split("-")[0];
        yearMap[year] = row.year_total_minutes;
    });

    const years = Object.keys(yearMap).sort();
    const values = years.map((y) => yearMap[y]);

    new Chart(document.getElementById("yearlyChart"), {
        type: "doughnut",
        data: {
            labels: years,
            datasets: [
                {
                    data: values,
                    backgroundColor: COLORS.slice(0, years.length),
                    borderWidth: 2,
                    borderColor: "rgba(0,0,0,0.2)",
                },
            ],
        },
        options: sharedOptions,
    });
}

loadGameTotalsChart();
loadYearlyChart();

async function loadGenreChart() {
    const response = await fetch("/api/playtime/by-genre");
    const data = await response.json();

    const labels = data.map((g) => g.genre);
    const values = data.map((g) => g.total_minutes);

    // More genres than hardcoded colours — cycle through the palette
    const bgColors = labels.map((_, i) => COLORS[i % COLORS.length]);

    new Chart(document.getElementById("genreChart"), {
        type: "doughnut",
        data: {
            labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: bgColors,
                    borderWidth: 2,
                    borderColor: "rgba(0,0,0,0.2)",
                },
            ],
        },
        options: sharedOptions,
    });
}

loadGenreChart();
