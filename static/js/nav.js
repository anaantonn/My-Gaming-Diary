function getCurrentPage() {
    if (document.getElementById("homepage")) {
        const navElement = document.getElementById("navhome");
        navElement.classList.remove("group", "hover:text-blue-800");
        navElement.classList.add(
            "text-blue-800",
            "pointer-events-none",
            "cursor-default",
        );

        const underline = navElement.querySelector("span");
        if (underline) {
            underline.classList.remove(
                "max-w-0",
                "group-hover:max-w-full",
                "transition-all",
                "duration-500",
            );
            underline.classList.add("max-w-full");
        }
    } else if (document.getElementById("statspage")) {
        const navElement = document.getElementById("navstats");
        navElement.classList.remove("group", "hover:text-blue-800");
        navElement.classList.add(
            "text-blue-800",
            "pointer-events-none",
            "cursor-default",
        );

        const underline = navElement.querySelector("span");
        if (underline) {
            underline.classList.remove(
                "max-w-0",
                "group-hover:max-w-full",
                "transition-all",
                "duration-500",
            );
            underline.classList.add("max-w-full");
        }
    }
}

getCurrentPage();
