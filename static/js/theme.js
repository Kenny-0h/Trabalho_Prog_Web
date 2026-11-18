(() => {
    const STORAGE_KEY = "agendamedica-tema";
    const DEFAULT_THEME = "light";
    const THEMES = {
        light: { next: "dark", buttonLabel: "Tema escuro", path: '<path d="M20.2 15.3A8.5 8.5 0 0 1 8.7 3.8 8.5 8.5 0 1 0 20.2 15.3Z"/>' },
        dark: { next: "light", buttonLabel: "Tema claro", path: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>' },
    };

    function getSavedTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        return THEMES[saved] ? saved : DEFAULT_THEME;
    }

    function applyTheme(themeName) {
        const theme = THEMES[themeName] ? themeName : DEFAULT_THEME;
        document.documentElement.setAttribute("data-bs-theme", theme);
        localStorage.setItem(STORAGE_KEY, theme);
        const iconEl = document.getElementById("iconeTema");
        const textEl = document.getElementById("textoTema");
        if (iconEl && textEl) {
            iconEl.innerHTML = THEMES[theme].path;
            textEl.textContent = THEMES[theme].buttonLabel;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        applyTheme(getSavedTheme());
        const toggleBtn = document.getElementById("alternarTema");
        if (toggleBtn) toggleBtn.addEventListener("click", () => applyTheme(THEMES[getSavedTheme()].next));
    });
})();
