import flet as ft
import random
import asyncio
import os

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
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#1e1e2f"
    page.padding = 20

    # Estado
    estado = {"pontos": 0, "rodada": 0, "tempo": 10, "vivo": False, "doc": None}

    # UI Elements
    lbl_rodada = ft.Text("RODADA 0/5", size=14, color="#a2a2ba", weight="bold")
    lbl_pontos = ft.Text("PONTOS: 0", size=22, color="#00ffcc", weight="bold")
    lbl_timer = ft.Text("10s", size=18, color="#ff7675", weight="bold")
    prog_bar = ft.ProgressBar(width=300, value=1, color="#00cec9", bgcolor="#444")
    
    lbl_nome_doc = ft.Text("", size=22, weight="bold", color="white", text_align="center")
    
    rg_setor = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="RH", label="RH"),
        ft.Radio(value="Financeiro", label="Financeiro"),
        ft.Radio(value="Administrativo", label="Administrativo"),
        ft.Radio(value="Jurídico", label="Jurídico")
    ], spacing=0))

    rg_ciclo = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="Corrente", label="Corrente"),
        ft.Radio(value="Intermediario", label="Intermediário"),
        ft.Radio(value="Permanente", label="Permanente")
    ], spacing=0))

    # Funções de Lógica
    async def iniciar_rodada():
        if estado["rodada"] >= 5:
            await finalizar_jogo()
            return
        
        estado["rodada"] += 1
        estado["tempo"] = 10
        estado["vivo"] = True
        estado["doc"] = random.choice(documentos)
        
        lbl_rodada.value = f"RODADA {estado['rodada']}/5"
        lbl_nome_doc.value = estado["doc"]["nome"]
        rg_setor.value = None
        rg_ciclo.value = None
        prog_bar.value = 1
        page.update()
        
        while estado["tempo"] > 0 and estado["vivo"]:
            await asyncio.sleep(1)
            estado["tempo"] -= 1
            lbl_timer.value = f"{estado['tempo']}s"
            prog_bar.value = estado["tempo"] / 10
            page.update()
        
        if estado["tempo"] == 0 and estado["vivo"]:
            await validar_resposta(timeout=True)

    async def validar_resposta(timeout=False):
        if not estado["vivo"] and not timeout: return
        estado["vivo"] = False
        
        pontos_da_vez = 0
        if not timeout:
            if rg_setor.value == estado["doc"]["setor"]: pontos_da_vez += 1
            if rg_ciclo.value == estado["doc"]["ciclo"]: pontos_da_vez += 1
        
        estado["pontos"] += pontos_da_vez
        lbl_pontos.value = f"PONTOS: {estado['pontos']}"
        
        # Feedback Visual
        cor = "green" if pontos_da_vez == 2 else "orange" if pontos_da_vez == 1 else "red"
        msg = "Tempo Esgotado!" if timeout else f"Você ganhou {pontos_da_vez} pontos!"
        
        snack = ft.SnackBar(ft.Text(f"{msg} Gabarito: {estado['doc']['setor']} | {estado['doc']['ciclo']}"), bgcolor=cor)
        page.snack_bar = snack
        snack.open = True
        page.update()
        
        await asyncio.sleep(2.5) # Tempo para ler o resultado
        await iniciar_rodada()

    async def finalizar_jogo():
        lbl_nome_doc.value = "FIM DE JOGO!"
        btn_confirmar.visible = False
        page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text("Partida Finalizada!"),
            content=ft.Text(f"Sua pontuação final foi: {estado['pontos']}"),
            actions=[ft.TextButton("Jogar Novamente", on_click=lambda _: page.reload())]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    btn_confirmar = ft.ElevatedButton(
        "CONFIRMAR RESPOSTA",
        on_click=lambda _: page.run_task(validar_resposta),
        bgcolor="#00b894",
        color="white",
        width=300,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # Layout em Cartão
    card_jogo = ft.Container(
        content=ft.Column([
            lbl_rodada,
            lbl_pontos,
            ft.Row([lbl_timer, prog_bar], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color="transparent"),
            ft.Container(
                content=lbl_nome_doc,
                padding=20,
                bgcolor="#2d2d44",
                border_radius=15,
                border=ft.border.all(1, "#444")
            ),
            ft.Text("QUAL O SETOR?", size=12, weight="bold", color="#a2a2ba"),
            rg_setor,
            ft.Text("QUAL O CICLO?", size=12, weight="bold", color="#a2a2ba"),
            rg_ciclo,
            ft.Divider(height=10, color="transparent"),
            btn_confirmar
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30,
        bgcolor="#252538",
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=20, color="#10000000"),
        width=400
    )

    page.add(card_jogo)
    page.run_task(iniciar_rodada)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
