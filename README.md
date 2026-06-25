# Tesouro EOP UI Library 🎨

**Biblioteca genérica de interface gráfica para aplicações CustomTkinter.**

Desenvolvida para padronizar e acelerar a criação de ferramentas e automações. A `eop_ui` encapsula toda a lógica repetitiva de UI (configuração de janela, gerenciamento de fontes, telas de login, logs de execução, barras de progresso e modais de mensagem), permitindo que você foque inteiramente na lógica de negócio da sua aplicação.

---

## ✨ Funcionalidades

* ⚙️ **Configuração Centralizada:** Toda a parametrização visual e de comportamento é feita através de um único objeto (`AppConfig`).
* 🔐 **Tela de Login Integrada:** Validação automática de campos, suporte a subtítulos de aviso e callbacks simplificados.
* 💻 **Tela de Execução:** Interface pronta para rotinas longas, com log de texto em tempo real (com timestamps) e barra de progresso determinada.
* 🧭 **Navegação e Menus:** Botão de voltar embutido, menu superior nativo (com atalhos para *Sobre* e *Manual de Uso*) e fácil expansão.
* 🎨 **Design Padronizado:** Cores, tipografia e espaçamentos consistentes, baseados no tema *dark-blue* do CustomTkinter em modo *Light*.

---

## 📦 Instalação e Dependências

Certifique-se de ter o Python 3.8+ instalado. Para instalar as dependências necessárias, execute:

```bash
pip install -r requirements.txt
```

**Dependências principais:**
* `customtkinter`
* `Pillow` (para renderização de logos e ícones)

---

## 🚀 Uso Rápido (Quick Start)

Para utilizar a biblioteca, basta importar as classes base, configurar seus parâmetros através do `AppConfig` e herdar o comportamento no seu app com `BaseApp`.

```python
from eop_ui import AppConfig, BaseApp

class MeuApp(BaseApp):
    def __init__(self):
        # 1. Defina as configurações da sua aplicação
        cfg = AppConfig(
            app_name="Extrator de Relatórios SIAFE",
            developer_info="EOP / SUPCONC - Tesouro Estadual",
            login_subtitle="⚠️ Use suas credenciais de rede"
        )
        
        # 2. Inicialize a classe base com a configuração
        super().__init__(cfg)
        
        # 3. Chame a tela inicial desejada
        self.show_login_frame(on_success=self.iniciar_processamento)

    def iniciar_processamento(self, usuario, senha):
        # Transição para a tela de execução após o login
        self.show_execution_frame(initial_msg=">>> Autenticado com sucesso. Iniciando rotina...")
        
        # Exemplo de uso do log e progresso
        self.log(f"Usuário logado: {usuario}")
        self.update_progress(0.5, "Baixando dados... (50%)")
        
        # Finalização
        self.finalize_progress(
            label="Concluído!", 
            title="Sucesso", 
            message="Os relatórios foram extraídos com sucesso."
        )

if __name__ == "__main__":
    app = MeuApp()
    # Garante o encerramento seguro (encerra processos em background se houver)
    app.protocol("WM_DELETE_WINDOW", app.safe_exit)
    app.mainloop()
```

---

## 🏗️ Estrutura Principal

### `AppConfig`
Um `dataclass` que concentra os parâmetros da sua interface. Ao invés de espalhar `self.geometry`, `self.title` ou caminhos de arquivos pelo código, você define tudo aqui. 
* **Identidade:** `app_name`, `app_version`, `developer_info`.
* **Caminhos:** `icon_filename`, `image_filename`, `manual_filename`. Os caminhos são resolvidos automaticamente com base no diretório de execução.
* **Login:** Controle granular sobre a tela de acesso (ex: `user_digits_only=True`, `user_max_length=11`).

### `BaseApp`
A janela principal (herda de `ctk.CTk`). Implementa métodos facilitadores:
* **Telas:** `show_login_frame()`, `show_execution_frame()`, `clear_frame()`.
* **Feedback Visual:** `update_progress()`, `log()`, `reset_progress()`, `finalize_progress()`.
* **Modais:** `messagebox_info()`, `messagebox_warning()`, `messagebox_error()`, `messagebox_question()`.
* **Componentes:** `make_primary_button()`, `make_success_button()`, `make_header_label()`.

---

## 📂 Padrão de Diretórios Esperado

Por padrão (caso você não altere os caminhos no `AppConfig`), a biblioteca espera a seguinte estrutura no diretório do seu script principal:

```text
meu_projeto/
├── main.py                # Seu script executável
├── Manual de Uso.pdf      # Manual aberto pela tecla F2
└── img/
    ├── icon.ico           # Ícone da janela
    ├── tesouro.png        # Logo exibido na tela de login
    └── voltar.png         # Ícone do botão de voltar
```

> **Dica:** Se os arquivos de imagem ou o manual não forem encontrados, a UI simplesmente se adapta e os oculta de forma silenciosa, sem quebrar a aplicação.
