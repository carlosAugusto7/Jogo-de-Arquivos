import flet as ft
import random
import asyncio
import os

# Dados do jogo
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

async def main(page: ft.Page):
    page.title = "Gestor de Arquivos"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # Estado do jogo
    pontuacao = 0
    rodada = 0
    tempo = 10
    correndo = False
    doc_atual = None

    # UI
    lbl_rodada = ft.Text("Rodada 0/5", size=16)
    lbl_score = ft.Text("Pontuação: 0", size=24, color="green")
    lbl_doc = ft.Text("Documento", size=20, weight="bold")
    lbl_timer = ft.Text("Tempo: 10s", color="red")
    
    rg_setor = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="RH", label="RH"),
        ft.Radio(value="Financeiro", label="Financeiro"),
        ft.Radio(value="Administrativo", label="Administrativo"),
        ft.Radio(value="Juridico", label="Juridico")
    ]))

    rg_ciclo = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="Corrente", label="Corrente"),
        ft.Radio(value="Intermediario", label="Intermediário"),
        ft.Radio(value="Permanente", label="Permanente")
    ]))

    async def iniciar_rodada():
        nonlocal rodada, tempo, correndo, doc_atual
        if rodada >= 5:
            lbl_doc.value = f"FIM! Pontos: {pontuacao}"
            btn_conf.visible = False
            page.update()
            return
        
        rodada += 1
        tempo = 10
        correndo = True
        doc_atual = random.choice(documentos)
        
        lbl_rodada.value = f"Rodada {rodada}/5"
        lbl_doc.value = doc_atual["nome"]
        rg_setor.value = None
        rg_ciclo.value = None
        page.update()
        
        while tempo > 0 and correndo:
            await asyncio.sleep(1)
            tempo -= 1
            lbl_timer.value = f"Tempo: {tempo}s"
            page.update()
        
        if tempo == 0 and correndo:
            await finalizar(True)

    async def finalizar(timeout=False):
        nonlocal pontuacao, correndo
        correndo = False
        ganhou = 0
        if not timeout:
            if rg_setor.value == doc_atual["setor"]: ganhou += 1
            if rg_ciclo.value == doc_atual["ciclo"]: ganhou += 1
        
        pontuacao += ganhou
        lbl_score.value = f"Pontuação: {pontuacao}"
        
        dlg = ft.AlertDialog(title=ft.Text("Resultado"), content=ft.Text(f"Correto: {doc_atual['setor']} | {doc_atual['ciclo']}"))
        page.dialog = dlg
        dlg.open = True
        page.update()
        await asyncio.sleep(2)
        dlg.open = False
        await iniciar_rodada()

    btn_conf = ft.ElevatedButton("Confirmar", on_click=lambda _: page.run_task(finalizar))

    page.add(lbl_rodada, lbl_score, lbl_timer, lbl_doc, rg_setor, rg_ciclo, btn_conf)
    
    # Inicia o jogo
    page.run_task(iniciar_rodada)

# ESSA LINHA É O SEGREDO PARA O RENDER
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
