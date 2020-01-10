function initializeThemeSwitcher() {
    const themeSwitch = document.querySelector('.theme-switcher input[type="checkbox"]');

    themeSwitch.addEventListener("change", function(e) {
        if (e.target.checked) {
            document.body.className = "dark-theme";
            localStorage.setItem("theme", "dark");
        } else {
            document.body.className = "light-theme";
            localStorage.setItem("theme", "light");
        }
    }, false);

    const isDarkOS = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = localStorage.getItem("theme");
    if (theme === "dark" || isDarkOS) {
        document.body.className = "dark-theme";
        themeSwitch.checked = true;
    }
}

function hideTooltip() {
    let visibleTooltips = document.querySelectorAll(".article-tooltip");
    for (let i = 0; i < visibleTooltips.length; i++) {
        if (visibleTooltips[i].style.display !== "none") {
            visibleTooltips[i].style.display = null;
        }
    }
}

function hideTooltipOnAnyClick() {
    document.body.addEventListener("click", function(e) {
        hideTooltip();
    }, true);
}

function checkKeyPress(e) {

    let tooltip;

    if (e.keyCode == 81) {
        tooltip = document.activeElement.parentNode.parentNode.querySelector('.article-tooltip');
        if (tooltip.style.display == "block") {
            tooltip.style.display = null;
        } else {
            tooltip.style.display = "block";
        }
    }

    if (e.keyCode == 9) {
        hideTooltip();
    }
}

var body = document.querySelector('body');
body.addEventListener('keyup', checkKeyPress);


initializeThemeSwitcher();
hideTooltipOnAnyClick();
