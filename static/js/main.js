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

let body = document.querySelector('body');
body.addEventListener('keyup', checkKeyPress);


initializeThemeSwitcher();
hideTooltipOnAnyClick();
