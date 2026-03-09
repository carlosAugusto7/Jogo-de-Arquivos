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
    # Centralização garantida
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#1e1e2f"
    page.padding = 20

    # Variáveis de controle (Estado)
    class Game:
        pontos = 0
        rodada = 0
        tempo = 25
        vivo = False
        doc_atual = None
        task = None

    g = Game()

    # --- UI Elements ---
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

    # --- Lógica ---
    async def iniciar_rodada():
        if g.rodada >= 5:
            await finalizar_jogo()
            return
        
        g.rodada += 1
        g.tempo = 25
        g.vivo = True
        g.doc_atual = random.choice(documentos)
        
        lbl_rodada.value = f"RODADA {g.rodada}/5"
        lbl_nome_doc.value = g.doc_atual["nome"]
        rg_setor.value = None
        rg_ciclo.value = None
        prog_bar.value = 1
        btn_confirmar.disabled = False
        page.update()
        
        # Timer simplificado
        while g.tempo > 0 and g.vivo:
            await asyncio.sleep(1)
            g.tempo -= 1
            lbl_timer.value = f"{g.tempo}s"
            prog_bar.value = g.tempo / 25
            page.update()
        
        if g.tempo == 0 and g.vivo:
            await validar_resposta(timeout=True)

    async def validar_resposta(timeout=False):
        if not g.vivo: return
        g.vivo = False
        btn_confirmar.disabled = True
        
        p = 0
        if not timeout:
            if rg_setor.value == g.doc_atual["setor"]: p += 1
            if rg_ciclo.value == g.doc_atual["ciclo"]: p += 1
        
        g.pontos += p
        lbl_pontos.value = f"PONTOS: {g.pontos}"
        
        cor = "green" if p == 2 else "orange" if p == 1 else "red"
        txt = f"Gabarito: {g.doc_atual['setor']} | {g.doc_atual['ciclo']}"
        
        snack = ft.SnackBar(ft.Text(f"{'Tempo Esgotado!' if timeout else 'Respondido!'} {txt}"), bgcolor=cor)
        page.overlay.append(snack)
        snack.open = True
        page.update()
        
        await asyncio.sleep(2)
        await iniciar_rodada()

    async def finalizar_jogo():
        def restart(e):
            page.clean() # Limpa a tela antes de reiniciar
            asyncio.run_coroutine_threadsafe(main(page), asyncio.get_running_loop())

        dlg = ft.AlertDialog(
            title=ft.Text("Fim de Jogo!"),
            content=ft.Text(f"Sua pontuação: {g.pontos}"),
            actions=[ft.TextButton("Reiniciar", on_click=lambda _: page.reload())]
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    btn_confirmar = ft.ElevatedButton(
        "CONFIRMAR",
        on_click=lambda _: asyncio.create_task(validar_resposta()),
        bgcolor="#00b894", color="white", width=250
    )

    # --- Layout Responsivo ---
    # Usamos um Container com largura adaptável (max_width)
    conteudo = ft.Container(
        content=ft.Column([
            lbl_rodada,
            lbl_pontos,
            ft.Column([lbl_timer, prog_bar], horizontal_alignment="center", spacing=5),
            ft.Container(lbl_nome_doc, padding=20, bgcolor="#2d2d44", border_radius=10),
            ft.Text("SETOR", size=12, weight="bold"),
            rg_setor,
            ft.Text("CICLO", size=12, weight="bold"),
            rg_ciclo,
            btn_confirmar
        ], horizontal_alignment="center", spacing=15),
        bgcolor="#252538",
        padding=20,
        border_radius=20,
        width=400, # Largura fixa para PC, mas Flet ajusta no mobile se a tela for menor
    )

    page.add(conteudo)
    asyncio.create_task(iniciar_rodada())

if __name__ == "__main__":
    ft.app(target=main)
