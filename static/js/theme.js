(() => {
    const CHAVE_TEMA = "agendamedica-tema";
    const temasDisponiveis = ["light", "dark"];
    const raiz = document.documentElement;
    const botao = document.getElementById("alternarTema");
    const icone = document.getElementById("iconeTema");
    const texto = document.getElementById("textoTema");

    function aplicarTema(tema) {
        const temaValido = temasDisponiveis.includes(tema) ? tema : "light";
        raiz.setAttribute("data-bs-theme", temaValido);
        localStorage.setItem(CHAVE_TEMA, temaValido);
        if (icone && texto) {
            icone.textContent = temaValido === "dark" ? "☀" : "☾";
            texto.textContent = temaValido === "dark" ? "Tema claro" : "Tema escuro";
        }
    }

    aplicarTema(localStorage.getItem(CHAVE_TEMA) || "light");
    if (botao) {
        botao.addEventListener("click", () => {
            const atual = raiz.getAttribute("data-bs-theme") || "light";
            const proximo = temasDisponiveis[(temasDisponiveis.indexOf(atual) + 1) % temasDisponiveis.length];
            aplicarTema(proximo);
        });
    }
})();
