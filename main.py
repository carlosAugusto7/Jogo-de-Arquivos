import flet as ft
import random
import asyncio

# =========================
# CONFIGURACOES E DADOS
# =========================
TEMPO_RODADA = 10
MAX_RODADAS = 5

documentos = [
    {"nome": "Contrato de Funcionario", "setor": "RH", "ciclo": "Permanente"},
    {"nome": "Folha de Pagamento 2023", "setor": "RH", "ciclo": "Intermediario"},
    {"nome": "Nota Fiscal 2022", "setor": "Financeiro", "ciclo": "Intermediario"},
    {"nome": "Ata de Reuniao", "setor": "Administrativo", "ciclo": "Permanente"},
    {"nome": "Processo Judicial", "setor": "Juridico", "ciclo": "Permanente"},
    {"nome": "Orcamento de Fornecedor", "setor": "Financeiro", "ciclo": "Corrente"},
    {"nome": "Curriculo Recebido", "setor": "RH", "ciclo": "Corrente"},
    {"nome": "Relatorio Anual", "setor": "Administrativo", "ciclo": "Permanente"},
]

def main(page: ft.Page):
    page.title = "Gestor de Arquivos"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 800

    # Variáveis de Estado
    estado = {
        "pontuacao": 0,
        "rodada": 0,
        "documento_atual": None,
        "tempo": TEMPO_RODADA,
        "correndo": False
    }

    # --- ELEMENTOS DA INTERFACE ---
    lbl_rodada = ft.Text("Rodada 0/0", size=16, color=ft.colors.GREY_400)
    lbl_score = ft.Text("Pontuação: 0", size=24, weight="bold", color=ft.colors.GREEN_ACCENT)
    lbl_doc = ft.Text("", size=22, weight="bold", text_align="center")
    
    barra_tempo = ft.ProgressBar(width=300, value=1, color=ft.colors.CYAN_ACCENT, bgcolor=ft.colors.GREY_800)
    lbl_timer = ft.Text(f"Tempo: {TEMPO_RODADA}s", color=ft.colors.RED_ACCENT)

    radio_setor = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="RH", label="RH"),
        ft.Radio(value="Financeiro", label="Financeiro"),
        ft.Radio(value="Administrativo", label="Administrativo"),
        ft.Radio(value="Juridico", label="Juridico"),
    ]))

    radio_ciclo = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="Corrente", label="Corrente"),
        ft.Radio(value="Intermediario", label="Intermediário"),
        ft.Radio(value="Permanente", label="Permanente"),
    ]))

    # --- LÓGICA DO JOGO ---
    async def contador_tempo():
        while estado["tempo"] > 0 and estado["correndo"]:
            await asyncio.sleep(1)
            estado["tempo"] -= 1
            lbl_timer.value = f"Tempo: {estado['tempo']}s"
            barra_tempo.value = estado["tempo"] / TEMPO_RODADA
            page.update()
        
        if estado["tempo"] <= 0 and estado["correndo"]:
            await finalizar_rodada(timeout=True)

    async def iniciar_rodada():
        if estado["rodada"] >= MAX_RODADAS:
            await mostrar_fim_jogo()
            return

        estado["rodada"] += 1
        estado["tempo"] = TEMPO_RODADA
        estado["correndo"] = True
        estado["documento_atual"] = random.choice(documentos)

        # Resetar UI
        lbl_rodada.value = f"Rodada {estado['rodada']}/{MAX_RODADAS}"
        lbl_doc.value = estado["documento_atual"]["nome"]
        radio_setor.value = None
        radio_ciclo.value = None
        barra_tempo.value = 1
        lbl_timer.value = f"Tempo: {TEMPO_RODADA}s"
        
        page.update()
        await contador_tempo()

    async def finalizar_rodada(timeout=False):
        estado["correndo"] = False
        doc = estado["documento_atual"]
        
        pontos_ganhos = 0
        if not timeout:
            if radio_setor.value == doc["setor"]: pontos_ganhos += 1
            if radio_ciclo.value == doc["ciclo"]: pontos_ganhos += 1
        
        estado["pontuacao"] += pontos_ganhos
        lbl_score.value = f"Pontuação: {estado['pontuacao']}"
        
        # Alerta de Resultado
        msg = f"Correto: {doc['setor']} | {doc['ciclo']}\nGanhou {pontos_ganhos} pontos!"
        titulo = "Tempo Esgotado!" if timeout else "Resultado"
        
        dlg = ft.AlertDialog(title=ft.Text(titulo), content=ft.Text(msg))
        page.dialog = dlg
        dlg.open = True
        page.update()
        
        await asyncio.sleep(2) # Espera 2 segundos para o usuário ver
        dlg.open = False
        page.update()
        await iniciar_rodada()

    async def mostrar_fim_jogo():
        lbl_doc.value = "FIM DE JOGO!"
        btn_confirmar.visible = False
        page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text("Parabéns!"),
            content=ft.Text(f"Pontuação Final: {estado['pontuacao']}"),
            actions=[ft.TextButton("Reiniciar", on_click=lambda _: page.reload())]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    async def validar_clique(e):
        if not radio_setor.value or not radio_ciclo.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione ambas as opções!"))
            page.snack_bar.open = True
            page.update()
            return
        await finalizar_rodada()

    btn_confirmar = ft.ElevatedButton("Confirmar Resposta", on_click=validar_clique, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)

    # --- MONTAGEM DA TELA ---
    page.add(
        ft.Column([
            lbl_rodada,
            lbl_score,
            lbl_timer,
            barra_tempo,
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            ft.Container(lbl_doc, padding=20, bgcolor=ft.colors.GREY_900, border_radius=10),
            ft.Text("Setor:", weight="bold"),
            radio_setor,
            ft.Text("Ciclo de Vida:", weight="bold"),
            radio_ciclo,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            btn_confirmar
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # Iniciar o jogo
    await iniciar_rodada()

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
