const tabs = document.querySelectorAll(".tab");
const underline = document.getElementById("tab-underline");

function setActiveTab(tab) {
    tabs.forEach((t) => {
        t.classList.remove("text-gray-500");
        t.classList.add("text-gray-300/75");
    });
    tab.classList.remove("text-gray-300/75");
    tab.classList.add("text-gray-500");

    underline.style.left = tab.offsetLeft + "px";
    underline.style.width = tab.offsetWidth + "px";
}

tabs.forEach((tab) => {
    tab.addEventListener("click", () => setActiveTab(tab));
});

setActiveTab(document.getElementById("tab-monthly"));
