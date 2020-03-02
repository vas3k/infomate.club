function initializeThemeSwitcher() {
    const themeSwitch = document.querySelector('.theme-switcher input[type="checkbox"]');

    themeSwitch.addEventListener("change", function(e) {
        let theme = 'light';
        if (e.target.checked) {
            theme = 'dark';
        }
        switchTheme(theme);
    }, false);

    checkMacTheme();
    syncThemeSwitcher();
}

function checkMacTheme() {
    if (window.matchMedia) {
        const darkThemeMatch = window.matchMedia('(prefers-color-scheme: dark)');
        let theme = 'light';
        if (darkThemeMatch.matches) {
            theme = 'dark';
        }
        switchTheme(theme)
        darkThemeMatch.addListener((e) => {
            if (e.matches) {
                theme = 'dark';
            } else {
                theme = 'light';
            }
            switchTheme(theme);
            syncThemeSwitcher();
        })
    }
}

function switchTheme(theme) {
    document.documentElement.setAttribute('theme', theme);
    localStorage.setItem('theme', theme);
}

function syncThemeSwitcher() {
    const themeSwitch = document.querySelector('.theme-switcher input[type="checkbox"]');
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
