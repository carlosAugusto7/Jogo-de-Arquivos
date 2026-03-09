import flet as ft
import random
import asyncio

# Dados do jogo
documentos = [
    {"nome": "Contrato de Funcionário", "setor": "RH", "ciclo": "Permanente"},
    {"nome": "Folha de Pagamento 2023", "setor": "RH", "ciclo": "Intermediario"},
    {"nome": "Nota Fiscal 2022", "setor": "Financeiro", "ciclo": "Intermediario"},
    {"nome": "Ata de Reunião", "setor": "Administrativo", "ciclo": "Permanente"},
    {"nome": "Processo Judicial", "setor": "Jurídico", "ciclo": "Permanente"},
    {"nome": "Orçamento de Fornecedor", "setor": "Financeiro", "ciclo": "Corrente"},
    {"nome": "Currículo Recebido", "setor": "RH", "ciclo": "Corrente"},
    {"nome": "Relatório Anual", "setor": "Administrativo", "ciclo": "Permanente"},
]

async def main(page: ft.Page):
    page.title = "Gestor de Arquivos"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#1e1e2f"
    page.padding = 20

    # Estado do Jogo encapsulado
    class GameState:
        def __init__(self):
            self.pontos = 0
            self.rodada = 0
            self.tempo = 25
            self.vivo = False
            self.doc_atual = None

    st = GameState()

    # --- Elementos de UI ---
    lbl_rodada = ft.Text("RODADA 0/5", size=14, color="#a2a2ba", weight="bold")
    lbl_pontos = ft.Text("PONTOS: 0", size=24, color="#00ffcc", weight="bold")
    lbl_timer = ft.Text("25s", size=18, color="#ff7675", weight="bold")
    prog_bar = ft.ProgressBar(width=300, value=1, color="#00cec9", bgcolor="#333")
    lbl_nome_doc = ft.Text("", size=22, weight="bold", color="white", text_align="center")

    rg_setor = ft.RadioGroup(content=ft.Column([
        ft.Row([ft.Radio(value="RH", label="RH"), ft.Radio(value="Financeiro", label="Fin.")], alignment="center"),
        ft.Row([ft.Radio(value="Administrativo", label="Adm."), ft.Radio(value="Jurídico", label="Jur.")], alignment="center"),
    ]))

    rg_ciclo = ft.RadioGroup(content=ft.Row([
        ft.Radio(value="Corrente", label="Corr."),
        ft.Radio(value="Intermediario", label="Inter."),
        ft.Radio(value="Permanente", label="Perm."),
    ], alignment="center"))

    # --- Funções de Lógica ---
    async def iniciar_rodada():
        if st.rodada >= 5:
            await finalizar_jogo()
            return
        
        st.rodada += 1
        st.tempo = 25
        st.vivo = True
        st.doc_atual = random.choice(documentos)
        
        lbl_rodada.value = f"RODADA {st.rodada}/5"
        lbl_nome_doc.value = st.doc_atual["nome"]
        rg_setor.value = None
        rg_ciclo.value = None
        prog_bar.value = 1
        btn_confirmar.disabled = False
        page.update()
        
        while st.tempo > 0 and st.vivo:
            await asyncio.sleep(1)
            st.tempo -= 1
            lbl_timer.value = f"{st.tempo}s"
            prog_bar.value = st.tempo / 25
            page.update()
        
        if st.tempo == 0 and st.vivo:
            await validar_resposta(timeout=True)

    async def validar_resposta(timeout=False):
        if not st.vivo: return
        st.vivo = False
        btn_confirmar.disabled = True
        
        pontos_rodada = 0
        if not timeout:
            if rg_setor.value == st.doc_atual["setor"]: pontos_rodada += 1
            if rg_ciclo.value == st.doc_atual["ciclo"]: pontos_rodada += 1
        
        st.pontos += pontos_rodada
        lbl_pontos.value = f"PONTOS: {st.pontos}"
        
        cor = "green" if pontos_rodada == 2 else "orange" if pontos_rodada == 1 else "red"
        txt = f"Gabarito: {st.doc_atual['setor']} | {st.doc_atual['ciclo']}"
        
        snack = ft.SnackBar(ft.Text(f"{'Tempo Esgotado!' if timeout else 'OK!'} {txt}"), bgcolor=cor)
        page.overlay.append(snack)
        snack.open = True
        page.update()
        
        await asyncio.sleep(2)
        await iniciar_rodada()

    async def reset_game(e):
        dlg_fim.open = False
        st.pontos = 0
        st.rodada = 0
        lbl_pontos.value = "PONTOS: 0"
        page.update()
        await iniciar_rodada()

    async def finalizar_jogo():
        dlg_fim.content = ft.Text(f"Sua pontuação final foi: {st.pontos}")
        page.overlay.append(dlg_fim)
        dlg_fim.open = True
        page.update()

    dlg_fim = ft.AlertDialog(
        title=ft.Text("Partida Finalizada!"),
        actions=[ft.TextButton("Jogar Novamente", on_click=reset_game)]
    )

    btn_confirmar = ft.ElevatedButton(
        "CONFIRMAR",
        on_click=lambda _: asyncio.create_task(validar_resposta()),
        bgcolor="#00b894", color="white", width=250
    )

    # --- Conteúdo Principal ---
    container_principal = ft.Container(
        content=ft.Column([
            lbl_rodada,
            lbl_pontos,
            ft.Column([lbl_timer, prog_bar], horizontal_alignment="center", spacing=5),
            ft.Container(lbl_nome_doc, padding=20, bgcolor="#2d2d44", border_radius=10, width=350),
            ft.Text("SETOR", size=12, weight="bold", color="#a2a2ba"),
            rg_setor,
            ft.Text("CICLO", size=12, weight="bold", color="#a2a2ba"),
            rg_ciclo,
            btn_confirmar
        ], horizontal_alignment="center", spacing=15),
        bgcolor="#252538",
        padding=25,
        border_radius=20,
        width=400,
    )

    page.add(container_principal)
    await iniciar_rodada()

if __name__ == "__main__":
    ft.app(target=main)
