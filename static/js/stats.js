const COLORS = [
    "rgb(86, 69, 146)",
    "rgb(114, 76, 249)",
    "rgb(202, 125, 249)",
    "rgb(248, 150, 216)",
    "rgb(237, 246, 125)",
];

const MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];
const MONTH_SHORT = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
];

const tabs = document.querySelectorAll(".tab");
const underline = document.getElementById("tab-underline");
const monthlyView = document.getElementById("monthly-view");
const yearlyView = document.getElementById("yearly-view");

function showView(view) {
    view.classList.remove("hidden");
    requestAnimationFrame(() => {
        view.style.opacity = "1";
    });
}

function hideView(view) {
    view.style.opacity = "0";
    setTimeout(() => view.classList.add("hidden"), 250);
}

function setActiveTab(tab) {
    tabs.forEach((t) => {
        t.classList.remove("text-white");
        t.classList.add("text-gray-300/75");
    });
    tab.classList.remove("text-gray-300/75");
    tab.classList.add("text-white");
    underline.style.left = tab.offsetLeft + "px";
    underline.style.width = tab.offsetWidth + "px";

    if (tab.id === "tab-monthly") {
        hideView(yearlyView);
        showView(monthlyView);
    } else {
        hideView(monthlyView);
        showView(yearlyView);
        if (!yearlyChartInstance) loadYearlyChart();
    }
}

tabs.forEach((tab) => tab.addEventListener("click", () => setActiveTab(tab)));
setActiveTab(document.getElementById("tab-monthly"));

const now = new Date();
const TODAY_YEAR = now.getFullYear();
const TODAY_MONTH = now.getMonth();

// Monthly view state
let mYear = TODAY_YEAR;
let mMonth = TODAY_MONTH;

// Yearly view state
let yYear = TODAY_YEAR;

const monthDisplay = document.getElementById("month-display");
const prevMonthBtn = document.getElementById("prev-month");
const nextMonthBtn = document.getElementById("next-month");
const monthPickerPopover = document.getElementById("month-picker-popover");

function updateMonthDisplay() {
    monthDisplay.textContent = `${MONTH_NAMES[mMonth]} ${mYear}`;
    const atMax = mYear === TODAY_YEAR && mMonth === TODAY_MONTH;
    nextMonthBtn.classList.toggle("opacity-30", atMax);
    nextMonthBtn.classList.toggle("pointer-events-none", atMax);
}

prevMonthBtn.addEventListener("click", () => {
    if (mMonth === 0) {
        mMonth = 11;
        mYear--;
    } else {
        mMonth--;
    }
    updateMonthDisplay();
    loadMonthlyChart();
});

nextMonthBtn.addEventListener("click", () => {
    if (mYear === TODAY_YEAR && mMonth === TODAY_MONTH) return;
    if (mMonth === 11) {
        mMonth = 0;
        mYear++;
    } else {
        mMonth++;
    }
    updateMonthDisplay();
    loadMonthlyChart();
});

monthDisplay.addEventListener("click", () => {
    monthPickerPopover.classList.toggle("hidden");
    if (!monthPickerPopover.classList.contains("hidden")) renderMonthPopover();
});

function renderMonthPopover() {
    monthPickerPopover.innerHTML = `
        <div class="flex items-center justify-between mb-3 font-bold">
            <button id="mp-prev-year" class="px-2 hover:text-white transition-colors">&#8592;</button>
            <span id="mp-year">${mYear}</span>
            <button id="mp-next-year" class="px-2 transition-colors ${mYear >= TODAY_YEAR ? "opacity-30 pointer-events-none" : "hover:text-white"}">&#8594;</button>
        </div>
        <div class="grid grid-cols-3 gap-2">
            ${MONTH_SHORT.map((m, i) => {
                const isFuture = mYear === TODAY_YEAR && i > TODAY_MONTH;
                return `<button
                    class="mp-month px-2 py-1 rounded text-sm transition-colors
                        ${isFuture ? "opacity-30 pointer-events-none cursor-default" : "hover:bg-white/20"}
                        ${i === mMonth ? "bg-white/25 font-bold" : ""}"
                    data-month="${i}"
                >${m}</button>`;
            }).join("")}
        </div>
    `;

    document.getElementById("mp-prev-year").addEventListener("click", (e) => {
        e.stopPropagation();
        mYear--;
        renderMonthPopover();
    });
    document.getElementById("mp-next-year").addEventListener("click", (e) => {
        e.stopPropagation();
        if (mYear >= TODAY_YEAR) return;
        mYear++;
        renderMonthPopover();
    });
    monthPickerPopover.querySelectorAll(".mp-month").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            mMonth = parseInt(btn.dataset.month);
            monthPickerPopover.classList.add("hidden");
            updateMonthDisplay();
            loadMonthlyChart();
        });
    });
}

document.addEventListener("click", (e) => {
    if (!monthPickerPopover.contains(e.target) && e.target !== monthDisplay) {
        monthPickerPopover.classList.add("hidden");
    }
});

updateMonthDisplay();

const yearDisplay = document.getElementById("year-display");
const prevYearBtn = document.getElementById("prev-year");
const nextYearBtn = document.getElementById("next-year");
const yearPickerPopover = document.getElementById("year-picker-popover");

function updateYearDisplay() {
    yearDisplay.textContent = yYear;
    const atMax = yYear >= TODAY_YEAR;
    nextYearBtn.classList.toggle("opacity-30", atMax);
    nextYearBtn.classList.toggle("pointer-events-none", atMax);
}

prevYearBtn.addEventListener("click", () => {
    yYear--;
    updateYearDisplay();
    loadYearlyChart();
});

nextYearBtn.addEventListener("click", () => {
    if (yYear >= TODAY_YEAR) return;
    yYear++;
    updateYearDisplay();
    loadYearlyChart();
});

yearDisplay.addEventListener("click", () => {
    yearPickerPopover.classList.toggle("hidden");
    if (!yearPickerPopover.classList.contains("hidden")) renderYearPopover();
});

function renderYearPopover() {
    const start = yYear - 4;
    const years = Array.from({ length: 9 }, (_, i) => start + i).filter(
        (y) => y <= TODAY_YEAR,
    );
    const atMax = yYear >= TODAY_YEAR;
    yearPickerPopover.innerHTML = `
        <div class="flex items-center justify-between mb-3 font-bold">
            <button id="yp-prev" class="px-2 hover:text-white transition-colors">&#8592;</button>
            <span>${years[0]} – ${years[years.length - 1]}</span>
            <button id="yp-next" class="px-2 transition-colors ${atMax ? "opacity-30 pointer-events-none" : "hover:text-white"}">&#8594;</button>
        </div>
        <div class="grid grid-cols-3 gap-2">
            ${years
                .map(
                    (y) => `
                <button
                    class="yp-year px-2 py-1 rounded text-sm transition-colors hover:bg-white/20 ${y === yYear ? "bg-white/25 font-bold" : ""}"
                    data-year="${y}"
                >${y}</button>
            `,
                )
                .join("")}
        </div>
    `;

    document.getElementById("yp-prev").addEventListener("click", (e) => {
        e.stopPropagation();
        yYear -= 9;
        renderYearPopover();
    });
    document.getElementById("yp-next").addEventListener("click", (e) => {
        e.stopPropagation();
        if (yYear >= TODAY_YEAR) return;
        yYear = Math.min(yYear + 9, TODAY_YEAR);
        renderYearPopover();
    });
    yearPickerPopover.querySelectorAll(".yp-year").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            yYear = parseInt(btn.dataset.year);
            yearPickerPopover.classList.add("hidden");
            updateYearDisplay();
            loadYearlyChart();
        });
    });
}

document.addEventListener("click", (e) => {
    if (!yearPickerPopover.contains(e.target) && e.target !== yearDisplay) {
        yearPickerPopover.classList.add("hidden");
    }
});

updateYearDisplay();

const sharedScaleOptions = (xTitle) => ({
    x: {
        ticks: { color: "white" },
        grid: { color: "rgba(255,255,255,0.1)" },
        title: { display: true, text: xTitle, color: "white" },
    },
    y: {
        beginAtZero: true,
        ticks: { color: "white" },
        grid: { color: "rgba(255,255,255,0.1)" },
        title: { display: true, text: "Minutes", color: "white" },
    },
});

let monthlyChartInstance = null;
let monthlyReqId = 0;

async function loadMonthlyChart() {
    const reqId = ++monthlyReqId;
    const month = `${mYear}-${String(mMonth + 1).padStart(2, "0")}`;
    const response = await fetch(`/api/playtime/daily?month=${month}`);
    if (reqId !== monthlyReqId) return;
    const data = await response.json();
    if (reqId !== monthlyReqId) return;

    const daysInMonth = new Date(mYear, mMonth + 1, 0).getDate();
    const labels = Array.from({ length: daysInMonth }, (_, i) => i + 1);

    // Build { gameName: { dayNumber: minutes } }
    const gameMap = {};
    data.forEach((row) => {
        const day = parseInt(row.play_date.split("-")[2]);
        if (!gameMap[row.game_name]) gameMap[row.game_name] = {};
        gameMap[row.game_name][day] =
            (gameMap[row.game_name][day] || 0) + row.game_minutes;
    });

    // Top 3 by total minutes this month
    const top3 = Object.entries(gameMap)
        .map(([name, days]) => ({
            name,
            total: Object.values(days).reduce((a, b) => a + b, 0),
        }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 3)
        .map((g) => g.name);

    const datasets = top3.map((name, i) => ({
        label: name,
        data: labels.map((day) => gameMap[name][day] || 0),
        backgroundColor: COLORS[i],
        borderRadius: 4,
    }));

    if (monthlyChartInstance) {
        monthlyChartInstance.destroy();
        monthlyChartInstance = null;
    }
    monthlyChartInstance = new Chart(document.getElementById("monthlyChart"), {
        type: "bar",
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: "white" } } },
            scales: sharedScaleOptions("Day"),
        },
    });
}

let yearlyChartInstance = null;
let yearlyReqId = 0;

async function loadYearlyChart() {
    const reqId = ++yearlyReqId;
    const response = await fetch(`/api/playtime/monthly?year=${yYear}`);
    if (reqId !== yearlyReqId) return;
    const data = await response.json();
    if (reqId !== yearlyReqId) return;

    // Build { gameName: { monthIndex: minutes } }
    const gameMap = {};
    data.forEach((row) => {
        const month = parseInt(row.play_month.split("-")[1]) - 1;
        if (!gameMap[row.game_name]) gameMap[row.game_name] = {};
        gameMap[row.game_name][month] =
            (gameMap[row.game_name][month] || 0) + row.game_minutes;
    });

    // Top 5 by total minutes this year
    const top5 = Object.entries(gameMap)
        .map(([name, months]) => ({
            name,
            total: Object.values(months).reduce((a, b) => a + b, 0),
        }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 5)
        .map((g) => g.name);

    const datasets = top5.map((name, i) => ({
        label: name,
        data: Array.from({ length: 12 }, (_, m) => gameMap[name][m] || 0),
        backgroundColor: COLORS[i],
        borderRadius: 4,
    }));

    if (yearlyChartInstance) {
        yearlyChartInstance.destroy();
        yearlyChartInstance = null;
    }
    yearlyChartInstance = new Chart(document.getElementById("yearlyChart"), {
        type: "bar",
        data: { labels: MONTH_SHORT, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: "white" } } },
            scales: sharedScaleOptions("Month"),
        },
    });
}

loadMonthlyChart();
