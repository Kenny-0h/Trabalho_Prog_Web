(() => {
    const STORAGE_KEY = "agendamedica-tema";
    const DEFAULT_THEME = "light";

    // Registro extensível de temas: adicionar um novo tema aqui habilita o ciclo automaticamente
    const THEMES = {
        light: {
            next: "dark",
            icon: "☾",
            buttonLabel: "Tema escuro",
        },
        dark: {
            next: "light",
            icon: "☀",
            buttonLabel: "Tema claro",
        },
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
            iconEl.textContent = THEMES[theme].icon;
            textEl.textContent = THEMES[theme].buttonLabel;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        applyTheme(getSavedTheme());

        const toggleBtn = document.getElementById("alternarTema");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                const current = getSavedTheme();
                const nextTheme = THEMES[current].next;
                applyTheme(nextTheme);
            });
        }
    });
})();