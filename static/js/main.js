function initializeThemeSwitcher() {
    const themeSwitch = document.querySelector('.theme-switcher input[type="checkbox"]');

    themeSwitch.addEventListener("change", function(e) {
        let theme = 'light';
        if (e.target.checked) {
            theme = 'dark';
        }

        document.documentElement.setAttribute('theme', theme);
        localStorage.setItem('theme', theme);
    }, false);

    const theme = localStorage.getItem('theme');
    if (theme !== null) {
        themeSwitch.checked = (theme === 'dark');
        document.documentElement.setAttribute('theme', theme);
    }
}

function hideTooltipOnAnyClick() {
    document.body.addEventListener("click", function(e) {
        const visibleTooltips = document.querySelectorAll(".article-tooltip");
        for (let i = 0; i < visibleTooltips.length; i++) {
            if (visibleTooltips[i].style.display !== "none") {
                visibleTooltips[i].style.display = "none";
            }
        }
    }, true);
}

initializeThemeSwitcher();
// hideTooltipOnAnyClick();
