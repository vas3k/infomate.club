function initializeThemeSwitcher() {
    const toggleSwitch = document.querySelector('.theme-switcher input[type="checkbox"]');

    function switchTheme(e) {
        if (e.target.checked) {
            document.body.className = "dark-theme";
            localStorage.setItem("theme", "dark");
        } else {
            document.body.className = "light-theme";
            localStorage.setItem("theme", "light");
        }
    }

    toggleSwitch.addEventListener("change", switchTheme, false);

    const theme = localStorage.getItem("theme");
    if (theme === "dark") {
        document.body.className = "dark-theme";
        toggleSwitch.checked = true;
    }
}

initializeThemeSwitcher();
