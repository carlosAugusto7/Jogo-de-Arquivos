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
    page.title = "Gestor de Arquivos v2"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#1e1e2f"
    page.padding = 10 # Melhor para mobile

    # Estado do Jogo
    class GameState:
        def __init__(self):
            self.pontos = 0
            self.rodada = 0
            self.tempo = 20 # Tempo aumentado
            self.vivo = False
            self.doc_atual = None
            self.timer_task = None

    st = GameState()

    # --- Elementos de UI ---
    lbl_rodada = ft.Text("RODADA 0/5", size=14, color="#a2a2ba", weight="bold")
    lbl_pontos = ft.Text("PONTOS: 0", size=26, color="#00ffcc", weight="extrabold")
    lbl_timer = ft.Text("20s", size=18, color="#ff7675", weight="bold")
    prog_bar = ft.ProgressBar(width=300, value=1, color="#00cec9", bgcolor="#444")
    lbl_nome_doc = ft.Text("", size=20, weight="bold", color="white", text_align="center")

    # Radio Groups com layout melhorado
    rg_setor = ft.RadioGroup(content=ft.Row([
        ft.Radio(value="RH", label="RH"),
        ft.Radio(value="Financeiro", label="Fin."),
        ft.Radio(value="Administrativo", label="Adm."),
        ft.Radio(value="Jurídico", label="Jur."),
    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True))

    rg_ciclo = ft.RadioGroup(content=ft.Row([
        ft.Radio(value="Corrente", label="Corrente"),
        ft.Radio(value="Intermediario", label="Interm."),
        ft.Radio(value="Permanente", label="Perm."),
    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True))

    async def fechar_dialogo(e):
        dlg_fim.open = False
        await reiniciar_jogo()

    dlg_fim = ft.AlertDialog(
        title=ft.Text("Fim de Jogo!"),
        actions=[ft.TextButton("Jogar Novamente", on_click=fechar_dialogo)]
    )

    # --- Funções Principais ---

    async def timer_count():
        try:
            while st.tempo > 0 and st.vivo:
                await asyncio.sleep(1)
                st.tempo -= 1
                lbl_timer.value = f"{st.tempo}s"
                prog_bar.value = st.tempo / 20
                page.update()
            
            if st.tempo == 0 and st.vivo:
                await validar_resposta(timeout=True)
        except asyncio.CancelledError:
            pass

    async def iniciar_rodada():
        if st.rodada >= 5:
            await finalizar_jogo()
            return

        st.rodada += 1
        st.tempo = 20
        st.vivo = True
        st.doc_atual = random.choice(documentos)
        
        # Reset UI
        lbl_rodada.value = f"RODADA {st.rodada}/5"
        lbl_nome_doc.value = st.doc_atual["nome"]
        rg_setor.value = None
        rg_ciclo.value = None
        prog_bar.value = 1
        btn_confirmar.disabled = False
        btn_confirmar.visible = True
        
        page.update()
        
        # Inicia o timer
        st.timer_task = asyncio.create_task(timer_count())

    async def validar_resposta(timeout=False):
        if not st.vivo: return
        st.vivo = False
        btn_confirmar.disabled = True # Evita múltiplos cliques
        
        if st.timer_task:
            st.timer_task.cancel()

        ganhou_pontos = 0
        if not timeout:
            if rg_setor.value == st.doc_atual["setor"]: ganhou_pontos += 1
            if rg_ciclo.value == st.doc_atual["ciclo"]: ganhou_pontos += 1
        
        st.pontos += ganhou_pontos
        lbl_pontos.value = f"PONTOS: {st.pontos}"
        
        # Cores e Feedback
        cor = "green" if ganhou_pontos == 2 else "orange" if ganhou_pontos == 1 else "red"
        msg = "Tempo Esgotado!" if timeout else f"+{ganhou_pontos} Pontos!"
        
        snack = ft.SnackBar(
            ft.Text(f"{msg} Gabarito: {st.doc_atual['setor']} | {st.doc_atual['ciclo']}"),
            bgcolor=cor,
            duration=2000
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()
        
        await asyncio.sleep(2)
        await iniciar_rodada()

    async def finalizar_jogo():
        st.vivo = False
        dlg_fim.content = ft.Text(f"Sua pontuação final: {st.pontos} de 10 possíveis!")
        page.dialog = dlg_fim
        dlg_fim.open = True
        page.update()

    async def reiniciar_jogo():
        st.pontos = 0
        st.rodada = 0
        lbl_pontos.value = "PONTOS: 0"
        await iniciar_rodada()

    btn_confirmar = ft.ElevatedButton(
        "CONFIRMAR RESPOSTA",
        on_click=lambda _: asyncio.create_task(validar_resposta()),
        bgcolor="#00b894",
        color="white",
        height=50,
        expand=True
    )

    # --- Layout Responsivo ---
    card_jogo = ft.Container(
        content=ft.Column([
            lbl_rodada,
            lbl_pontos,
            ft.Row([lbl_timer, prog_bar], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ft.Divider(height=10, color="transparent"),
            ft.Container(
                content=lbl_nome_doc,
                padding=20,
                bgcolor="#2d2d44",
                border_radius=15,
                border=ft.border.all(1, "#444"),
                alignment=ft.alignment.center
            ),
            ft.Text("SETOR RESPONSÁVEL:", size=12, weight="bold", color="#a2a2ba"),
            rg_setor,
            ft.Text("FASE DO CICLO VITAL:", size=12, weight="bold", color="#a2a2ba"),
            rg_ciclo,
            ft.Row([btn_confirmar])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=25,
        bgcolor="#252538",
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=30, color="#1a000000"),
        width=450, # Largura máxima
        margin=10
    )

    page.add(ft.SafeControlAncestor(ft.Column([card_jogo], horizontal_alignment=ft.CrossAxisAlignment.CENTER)))
    
    # Início do Jogo
    await iniciar_rodada()

if __name__ == "__main__":
    ft.app(target=main)
