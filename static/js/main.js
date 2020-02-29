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
        visibleTooltips[i].style.visibility = null;
    }
}

function hideTooltipOnAnyClick() {
    document.body.addEventListener("click", function(e) {
        hideTooltip();
    }, true);
}

function addWeirdLogicThatSomeGeeksWillUseOnceAndForget() {
    let body = document.querySelector('body');
    body.addEventListener('keyup', function(e) {
        let tooltip;

        if (e.keyCode == 81) {
            tooltip = document.activeElement.parentNode.parentNode.querySelector('.article-tooltip');
            if (tooltip.style.visibility == "visible") {
                tooltip.style.visibility = null;
            } else {
                tooltip.style.visibility = "visible";
            }
        }


        if (e.keyCode == 9) {
            hideTooltip();
        }
    });
}

function useSmartTooltipPositioning() {
    // This handler is trying to keep the tooltip card on the screen
    // so that it doesn't go beyond its borders if it's enough space nearby
    const preservedMargin = 20; // px
    const defaultTop = -100; // px
    const screenWidth = (window.innerWidth || screen.width);
    const screenHeight = (window.innerHeight || screen.height || document.documentElement.clientHeight);

    if (screenWidth <= 750) return; // disable on small screens

    let articles = document.querySelectorAll(".article");
    for (let i = 0; i < articles.length; i++) {
        articles[i].addEventListener("mouseover", smartPosition);
    }

    function smartPosition(e) {
        let tooltip = document.querySelector(".article:hover .article-tooltip");
        let bounding = tooltip.getBoundingClientRect();
        let topDelta = 0;

        if (bounding.bottom > screenHeight) {
            // card's bottom is below the screen border
            if (bounding.height <= screenHeight) {
                topDelta = screenHeight - bounding.bottom - preservedMargin;
            } else {
                // card is too long to fit the screen, just stick it to the top
                topDelta = preservedMargin - bounding.top;
            }
        }

        if (bounding.top < 0) {
            // card's top is above the screen border
            topDelta = preservedMargin - bounding.top;
        }

        if (topDelta !== 0) {
            // compensate position by adding delta to the current 'top' value
            let currentTop = parseInt(tooltip.style.top || defaultTop, 10);
            tooltip.style.top = (currentTop + topDelta) + "px";
        }
    }
}


initializeThemeSwitcher();
hideTooltipOnAnyClick();
useSmartTooltipPositioning();
addWeirdLogicThatSomeGeeksWillUseOnceAndForget();
