"""
UI_main.py
================
Biblioteca genérica de interface gráfica para aplicações CustomTkinter.

Encapsula toda a lógica de UI repetitiva: configuração de janela, fontes,
tela de login, tela de execução com log e barra de progresso, mensagens e
botão de voltar. Cada aplicação passa suas configurações via `AppConfig` e
herda de `BaseApp`, implementando apenas a lógica de negócio.

Exemplo mínimo de uso:
    from eop_ui import AppConfig, BaseApp

    class MeuApp(BaseApp):
        def __init__(self):
            cfg = AppConfig(app_name="Meu Programa", developer_info="Minha Equipe")
            super().__init__(cfg)
            self.show_login_frame()

    if __name__ == "__main__":
        app = MeuApp()
        app.protocol("WM_DELETE_WINDOW", app.safe_exit)
        app.mainloop()
"""
from __future__ import annotations

from typing import Callable, Optional
from tkinter import Menu, messagebox
from dataclasses import dataclass
import customtkinter as ctk
from pathlib import Path
from PIL import Image
import time
import sys
import os

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue")

# ===========================================================================
# AppConfig — toda a parametrização em um único objeto
# ===========================================================================

@dataclass
class AppConfig:
    """
    Configuração centralizada da aplicação. Todos os atributos possuem
    valores-padrão razoáveis e podem ser sobrescritos conforme necessário.

    Parâmetros de identidade
    ------------------------
    app_name       : Nome exibido na barra de título e nas telas.
    app_version    : Versão usada no diálogo "Sobre".
    developer_info : Texto exibido no rodapé de todas as telas.
    about_text     : Conteúdo completo do diálogo "Sobre" (gerado
                     automaticamente a partir dos campos acima se omitido).

    Parâmetros de janela
    --------------------
    window_width / window_height : Dimensões em pixels.
    resizable        : Tupla (horizontal, vertical) booleanos.
    bg_color         : Cor de fundo da janela raiz.

    Parâmetros de caminhos
    ----------------------
    base_path           : Diretório base do projeto (padrão: pasta do script).
    icon_filename       : Caminho relativo ao ícone (.ico).
    image_filename      : Caminho relativo à imagem/logo principal.
    back_button_filename: Caminho relativo ao ícone de "voltar".
    manual_filename     : Caminho relativo ao PDF do manual.

    Parâmetros da tela de login
    ---------------------------
    login_subtitle      : Aviso exibido abaixo do título (ex: "⚠️ Use dados do SIAFE").
    login_user_label    : Rótulo do campo de usuário.
    login_pass_label    : Rótulo do campo de senha.
    login_button_text   : Texto do botão de login.
    user_max_length     : Número máximo de caracteres aceitos no campo de usuário.
    user_digits_only    : Se True, o campo de usuário aceita apenas dígitos.
    user_exact_length   : Se True, exige exatamente `user_max_length` dígitos para
                          habilitar o botão. Se False, qualquer texto não vazio basta.

    Parâmetros visuais
    ------------------
    font_family           : Família de fontes usada em toda a aplicação.
    font_header_size      : Tamanho da fonte de cabeçalho.
    font_body_size        : Tamanho da fonte de corpo/rótulos.
    color_primary         : Cor do botão principal.
    color_primary_hover   : Cor de hover do botão principal.
    color_success         : Cor do botão de ação/sucesso.
    color_success_hover   : Cor de hover do botão de ação/sucesso.
    color_disabled        : Cor de botões desabilitados.
    color_footer          : Cor do texto do rodapé.
    color_warning_text    : Cor do texto de aviso na tela de login.
    logo_size             : Tupla (largura, altura) para redimensionar o logo.
    """

    # Identidade
    app_name: str = "Biblioteca de UI CustomTkinter"
    app_version: str = "1.0.0"
    developer_info: str = "EOP / SUPCONC - Tesouro Estadual"
    about_text: str = ""

    # Janela
    window_width: int = 500
    window_height: int = 650
    resizable: tuple = (False, False)
    bg_color: str = "white"

    # Caminhos (relativos ao base_path)
    base_path: Optional[Path] = None
    icon_filename: str = "img/icon.ico"
    image_filename: str = "img/tesouro.png"
    back_button_filename: str = "img/voltar.png"
    manual_filename: str = "Manual de Uso.pdf"

    # Tela de login
    login_subtitle: str = ""
    login_user_label: str = "Usuário:"
    login_pass_label: str = "Senha:"
    login_button_text: str = "ENTRAR"
    user_max_length: int = 0           # 0 = sem limite
    user_digits_only: bool = False
    user_exact_length: bool = False    # exigir exatamente user_max_length dígitos

    # Fontes
    font_family: str = "Roboto"
    font_header_size: int = 24
    font_body_size: int = 14

    # Cores
    color_primary: str = "#1f6aa5"
    color_primary_hover: str = "#144d7a"
    color_success: str = "#4CAF50"
    color_success_hover: str = "#45a049"
    color_disabled: str = "#555555"
    color_footer: str = "gray"
    color_warning_text: str = "red"

    # Logo
    logo_size: tuple = (105, 105)

    def __post_init__(self):
        # Resolve o caminho base automaticamente se não fornecido
        if self.base_path is None:
            self.base_path = Path(sys.argv[0]).resolve().parent

        # Gera o texto "Sobre" padrão se não foi fornecido
        if not self.about_text:
            self.about_text = (
                f"{self.app_name}\n"
                f"Versão: {self.app_version}\n"
                f"{self.developer_info}"
            )

    # ------------------------------------------------------------------
    # Propriedades de conveniência para os caminhos resolvidos
    # ------------------------------------------------------------------
    @property
    def icon_path(self) -> Path:
        return self.base_path / self.icon_filename

    @property
    def image_path(self) -> Path:
        return self.base_path / self.image_filename

    @property
    def back_button_path(self) -> Path:
        return self.base_path / self.back_button_filename

    @property
    def manual_path(self) -> Path:
        return self.base_path / self.manual_filename


# ===========================================================================
# BaseApp — classe base com toda a infraestrutura de UI
# ===========================================================================

class BaseApp(ctk.CTk):
    """
    Classe base para aplicações CustomTkinter padronizadas.
    """

    def __init__(self, config: AppConfig):
        super().__init__()
        self.cfg = config

        # ------------------------------------------------------------------
        # Configuração da janela principal
        # ------------------------------------------------------------------
        self.title(self.cfg.app_name)
        self.resizable(*self.cfg.resizable)
        self.configure(fg_color=self.cfg.bg_color)
        self._center_window(self.cfg.window_width, self.cfg.window_height)

        if self.cfg.icon_path.exists():
            self.iconbitmap(self.cfg.icon_path)

        # ------------------------------------------------------------------
        # Fontes padronizadas
        # ------------------------------------------------------------------
        f = self.cfg.font_family
        self.font_header = ctk.CTkFont(family=f, size=self.cfg.font_header_size, weight="bold")
        self.font_bold   = ctk.CTkFont(family=f, size=self.cfg.font_body_size,   weight="bold")
        self.font_label  = ctk.CTkFont(family=f, size=self.cfg.font_body_size,   weight="normal")

        # ------------------------------------------------------------------
        # Container principal
        # ------------------------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ------------------------------------------------------------------
        # Estado interno compartilhado
        # ------------------------------------------------------------------
        self._usuario: str = ""
        self._senha:   str = ""
        self._login_callback: Optional[Callable] = None

    # =======================================================================
    # GERENCIAMENTO DE JANELA
    # =======================================================================

    def _center_window(self, width: int, height: int):
        """Centraliza a janela na tela."""
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws / 2) - (width / 2))
        y = int((hs / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def clear_frame(self):
        """Remove todos os widgets do container principal."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def safe_exit(self, cleanup_fn: Optional[Callable] = None):
        """
        Encerra a aplicação de forma segura.

        cleanup_fn: função opcional chamada antes de destruir a janela
                    (ex: fechar driver Selenium, salvar estado).
        """
        if cleanup_fn:
            try:
                cleanup_fn()
            except Exception:
                pass
        self._usuario = ""
        self._senha   = ""
        self.destroy()
        sys.exit()

    # =======================================================================
    # COMPONENTES REUTILIZÁVEIS
    # =======================================================================

    def _add_logo(self, size: Optional[tuple] = None):
        """
        Insere o logo/imagem principal no topo do container.
        Silencioso se o arquivo não existir.
        """
        size = size or self.cfg.logo_size
        if self.cfg.image_path.exists():
            try:
                pil_img = Image.open(self.cfg.image_path)
                ctk_img = ctk.CTkImage(pil_img, size=size)
                ctk.CTkLabel(self.main_container, text="", image=ctk_img).pack(pady=(10, 5))
            except Exception:
                pass

    def _add_footer(self):
        """Adiciona o rodapé padrão fixo na parte inferior."""
        ctk.CTkLabel(
            self.main_container,
            text=self.cfg.developer_info,
            font=(self.cfg.font_family, 10),
            text_color=self.cfg.color_footer,
        ).pack(side="bottom", pady=10)

    def add_back_button(self, command: Callable):
        """
        Adiciona o botão de voltar no canto superior esquerdo do container.
        Silencioso se a imagem não existir.
        """
        if self.cfg.back_button_path.exists():
            img = ctk.CTkImage(Image.open(self.cfg.back_button_path), size=(30, 30))
            ctk.CTkButton(
                self.main_container,
                image=img, text="", width=10,
                fg_color="#ffffff", hover_color="#eeeeee",
                command=command,
            ).place(x=0, y=0)

    def create_menu(self, extra_items: Optional[list] = None):
        """
        Cria a barra de menu padrão com Sobre (F1) e Manual (F2).

        extra_items: lista de tuplas (label, comando, atalho_teclado).
                     atalho_teclado pode ser None.
                     Exemplo: [("Configurações (F3)", self.abrir_config, "<F3>")]
        """
        bar = Menu(self.main_container)
        self.configure(menu=bar)

        bar.add_cascade(label="Sobre (F1)", command=self._show_about)
        self.bind("<F1>", lambda _: self._show_about())

        bar.add_cascade(label="Manual de Uso (F2)", command=self._open_manual)
        self.bind("<F2>", lambda _: self._open_manual())

        if extra_items:
            for label, cmd, hotkey in extra_items:
                bar.add_cascade(label=label, command=cmd)
                if hotkey:
                    self.bind(hotkey, lambda _, c=cmd: c())

    def _show_about(self):
        self.messagebox_info("Sobre", self.cfg.about_text)

    def _open_manual(self):
        try:
            os.startfile(self.cfg.manual_path)
        except Exception:
            self.messagebox_error("Erro", "Manual não encontrado.")

    # =======================================================================
    # WIDGETS
    # =======================================================================

    def make_primary_button(
        self,
        parent,
        text: str,
        command: Callable,
        width: int = 250,
        height: int = 40,
        **kwargs,
    ) -> ctk.CTkButton:
        """Cria um botão com a cor primária configurada."""
        return ctk.CTkButton(
            parent, text=text, width=width, height=height,
            font=self.font_bold,
            fg_color=self.cfg.color_primary,
            hover_color=self.cfg.color_primary_hover,
            command=command,
            **kwargs,
        )

    def make_success_button(
        self,
        parent,
        text: str,
        command: Callable,
        width: int = 250,
        height: int = 50,
        **kwargs,
    ) -> ctk.CTkButton:
        """Cria um botão com a cor de sucesso/ação configurada."""
        return ctk.CTkButton(
            parent, text=text, width=width, height=height,
            font=self.font_bold,
            fg_color=self.cfg.color_success,
            hover_color=self.cfg.color_success_hover,
            command=command,
            **kwargs,
        )

    def make_section_frame(self, fill: str = "x", pady: int = 10) -> ctk.CTkFrame:
        """Cria e empacota um CTkFrame transparente de seção."""
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(fill=fill, pady=pady)
        return frame

    def make_header_label(self, text: str, pady: tuple = (20, 5)) -> ctk.CTkLabel:
        """Cria e empacota um label de cabeçalho (fonte grande)."""
        lbl = ctk.CTkLabel(self.main_container, text=text, font=self.font_header)
        lbl.pack(pady=pady)
        return lbl

    def make_subtitle_label(self, text: str, pady: tuple = (0, 20)) -> ctk.CTkLabel:
        """Cria e empacota um label de subtítulo (fonte normal)."""
        lbl = ctk.CTkLabel(self.main_container, text=text, font=self.font_label)
        lbl.pack(pady=pady)
        return lbl

    # =======================================================================
    # TELA DE LOGIN
    # =======================================================================

    def show_login_frame(
        self,
        on_success: Optional[Callable[[str, str], None]] = None,
        menu_items: Optional[list] = None,
    ):
        """
        Exibe a tela de login padrão.

        Parâmetros
        ----------
        on_success  : Callback chamado com (usuario, senha) após o clique no
                      botão de login.
        menu_items  : Itens extras para a barra de menu (mesmo formato de
                      `create_menu(extra_items=...)`).

        Validação automática:
            - Campo de senha não pode estar vazio.
            - Campo de usuário: se `user_digits_only=True`, aceita só dígitos.
              Se `user_exact_length=True`, exige exatamente `user_max_length`
              caracteres para habilitar o botão.
        """
        self._login_callback = on_success
        self.clear_frame()
        self.create_menu(menu_items)
        self._add_logo()

        ctk.CTkLabel(
            self.main_container,
            text=self.cfg.app_name,
            font=self.font_header,
        ).pack(pady=(5, 5))

        if self.cfg.login_subtitle:
            ctk.CTkLabel(
                self.main_container,
                text=self.cfg.login_subtitle,
                text_color=self.cfg.color_warning_text,
                font=(self.cfg.font_family, 14),
            ).pack(pady=(0, 20))

        # Campo de usuário
        ctk.CTkLabel(
            self.main_container,
            text=self.cfg.login_user_label,
            font=self.font_label,
        ).pack(pady=(5, 0))

        user_kwargs: dict = {"width": 300, "height": 40}
        if self.cfg.user_digits_only:
            val_cmd = self.register(self._validate_user_input)
            user_kwargs.update({"validate": "key", "validatecommand": (val_cmd, "%P")})

        self._entry_user = ctk.CTkEntry(self.main_container, **user_kwargs)
        self._entry_user.pack(pady=(2, 10))

        # Campo de senha
        ctk.CTkLabel(
            self.main_container,
            text=self.cfg.login_pass_label,
            font=self.font_label,
        ).pack(pady=(5, 0))

        self._entry_pass = ctk.CTkEntry(self.main_container, width=300, height=40, show="*")
        self._entry_pass.pack(pady=(2, 20))

        # Botão de login (desabilitado por padrão)
        self._btn_login = ctk.CTkButton(
            self.main_container,
            text=self.cfg.login_button_text,
            width=300, height=45,
            state="disabled",
            fg_color=self.cfg.color_disabled,
            command=self._process_login,
        )
        self._btn_login.pack(pady=20)

        self._add_footer()

        # Binds para atualização em tempo real e Enter
        self._entry_user.bind("<KeyRelease>", lambda _: self._check_login_fields())
        self._entry_pass.bind("<KeyRelease>", lambda _: self._check_login_fields())
        self.bind("<Return>", lambda _: self._process_login())

    def _validate_user_input(self, value: str) -> bool:
        """
        Validador de tecla para o campo de usuário quando `user_digits_only=True`.
        Permite: vazio, ou somente dígitos respeitando o limite configurado.
        """
        max_len = self.cfg.user_max_length
        if value == "":
            return True
        if not value.isdigit():
            return False
        if max_len > 0 and len(value) > max_len:
            return False
        return True

    def _check_login_fields(self):
        """Habilita/desabilita o botão de login com base no preenchimento dos campos."""
        user = self._entry_user.get()
        pwd  = self._entry_pass.get()

        if self.cfg.user_exact_length and self.cfg.user_max_length > 0:
            user_ok = len(user) == self.cfg.user_max_length
        elif self.cfg.user_max_length > 0:
            user_ok = 0 < len(user) <= self.cfg.user_max_length
        else:
            user_ok = bool(user.strip())

        all_ok = user_ok and bool(pwd.strip())

        if all_ok:
            self._btn_login.configure(state="normal", fg_color=self.cfg.color_primary)
        else:
            self._btn_login.configure(state="disabled", fg_color=self.cfg.color_disabled)

    def _process_login(self):
        if self._btn_login.cget("state") == "disabled":
            return
        
        self._usuario = self._entry_user.get()
        self._senha   = self._entry_pass.get()
        self.unbind("<Return>")

        if self._login_callback:
            self._login_callback(self._usuario, self._senha)

    # =======================================================================
    # TELA DE EXECUÇÃO (LOG + PROGRESSO)
    # =======================================================================

    def show_execution_frame(
        self,
        on_cancel: Optional[Callable] = None,
        initial_msg: str = ">>> Iniciando processamento...",
        menu_items: Optional[list] = None,
    ):
        """
        Exibe a tela de execução com barra de progresso e área de log.

        Parâmetros
        ----------
        on_cancel   : Callback chamado ao clicar no botão de voltar/cancelar.
                      Se None, o botão de voltar não é exibido.
        initial_msg : Primeira linha exibida na área de log.
        menu_items  : Itens extras para a barra de menu.

        Após chamar este método, use:
            self.log("mensagem")                        — para adicionar linhas ao log
            self.update_progress(0.5, "50% concluído") — para atualizar a barra
            self.finalize_progress(...)                 — ao terminar o processamento
        """
        self.clear_frame()
        self.create_menu(menu_items)

        if on_cancel:
            self.add_back_button(on_cancel)

        self._progress_label = ctk.StringVar(value="Processando... (0%)")

        ctk.CTkLabel(
            self.main_container,
            textvariable=self._progress_label,
            font=self.font_header,
        ).pack(pady=10)

        self._progress_bar = ctk.CTkProgressBar(self.main_container, width=400, mode="determinate")
        self._progress_bar.pack(pady=10)
        self._progress_bar.set(0)

        self._log_box = ctk.CTkTextbox(self.main_container, width=450, height=350)
        self._log_box.pack(pady=10)
        self._log_box.insert("0.0", f"{initial_msg}\n")

        self._add_footer()

    def log(self, msg: str):
        """
        Adiciona uma linha ao log com timestamp no formato [HH:MM:SS].

        Thread-safe: pode ser chamado de qualquer thread.
        """
        if not self.winfo_exists() or not hasattr(self, "_log_box"):
            return

        formatted = f"[{time.strftime('%H:%M:%S')}] {msg}\n"

        def _insert():
            if hasattr(self, "_log_box") and self._log_box.winfo_exists():
                try:
                    self._log_box.insert("end", formatted)
                    self._log_box.see("end")
                except Exception:
                    pass

        self.after(0, _insert)

    def update_progress(self, value: float, label: Optional[str] = None):
        """
        Atualiza a barra de progresso e o label. Thread-safe.

        Parâmetros
        ----------
        value : Float entre 0.0 e 1.0.
        label : Texto do label. Se None, exibe "Processando... (XX%)".
        """
        def _update():
            if not hasattr(self, "_progress_bar") or not self._progress_bar.winfo_exists():
                return
            self._progress_bar.set(max(0.0, min(1.0, value)))
            text = label if label else f"Processando... ({int(value * 100)}%)"
            self._progress_label.set(text)

        self.after(0, _update)

    def finalize_progress(
        self,
        label: str = "Concluído (100%)",
        title: Optional[str] = None,
        message: Optional[str] = None,
        msg_type: str = "info",
    ):
        """
        Finaliza a barra de progresso (100%) e exibe mensagem opcional. Thread-safe.

        Parâmetros
        ----------
        label    : Texto final do label de progresso.
        title    : Título da mensagem (None = sem mensagem).
        message  : Corpo da mensagem.
        msg_type : "info", "warning" ou "error".
        """
        def _finalize():
            if hasattr(self, "_progress_bar") and self._progress_bar.winfo_exists():
                self._progress_bar.set(1.0)
                self._progress_label.set(label)

            if title and message:
                dispatch = {
                    "info":    self.messagebox_info,
                    "warning": self.messagebox_warning,
                    "error":   self.messagebox_error,
                }
                dispatch.get(msg_type, self.messagebox_info)(title, message)

        self.after(0, _finalize)

    def reset_progress(self):
        """Reinicia a barra de progresso para 0% em modo determinado. Thread-safe."""
        def _reset():
            if hasattr(self, "_progress_bar") and self._progress_bar.winfo_exists():
                self._progress_bar.set(0.0)
                self._progress_label.set("Processando... (0%)")
        self.after(0, _reset)

    # =======================================================================
    # MENSAGENS — sempre com topmost para não ficar atrás da janela principal
    # =======================================================================

    def messagebox_info(self, title: str, message: str):
        """Exibe um diálogo de informação."""
        self.attributes("-topmost", True)
        messagebox.showinfo(title, message)
        self.attributes("-topmost", False)

    def messagebox_warning(self, title: str, message: str):
        """Exibe um diálogo de aviso."""
        self.attributes("-topmost", True)
        messagebox.showwarning(title, message)
        self.attributes("-topmost", False)

    def messagebox_error(self, title: str, message: str):
        """Exibe um diálogo de erro."""
        self.attributes("-topmost", True)
        messagebox.showerror(title, message)
        self.attributes("-topmost", False)

    def messagebox_question(self, title: str, message: str) -> bool:
        """Exibe um diálogo Sim/Não. Retorna True se o usuário clicar 'Sim'."""
        self.attributes("-topmost", True)
        result = messagebox.askyesno(title, message)
        self.attributes("-topmost", False)
        return result