from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.lib.units import cm # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_LEFT # type: ignore
from sqlalchemy.orm import Session
from backend.models import LogEvento, IpsBloqueados, Severidade, Status
from datetime import datetime, timezone
import matplotlib # type: ignore
matplotlib.use('Agg')
import matplotlib.pyplot as plt # type: ignore
import io


def gerar_grafico_volume(logs: list) -> io.BytesIO:
    """Gera gráfico de volume de ataques por hora"""
    volume = {}
    for log in logs:
        if log.timestamp:
            hora = log.timestamp.strftime("%H:%M")
            volume[hora] = volume.get(hora, 0) + 1

    horas   = list(volume.keys())
    ataques = list(volume.values())

    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor('#0B0E14')
    ax.set_facecolor('#151921')
    ax.bar(horas, ataques, color='#00A3FF', width=0.6)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.spines['bottom'].set_color('#262C36')
    ax.spines['left'].set_color('#262C36')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('Volume de Ataques por Hora', color='#FFFFFF', fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def gerar_grafico_severidade(logs: list) -> io.BytesIO:
    """Gera gráfico de pizza por severidade"""
    contagem = {"CRÍTICA": 0, "ALTA": 0, "MÉDIA": 0, "BAIXA": 0}
    for log in logs:
        if log.severidade == Severidade.CRITICA:  contagem["CRÍTICA"] += 1
        elif log.severidade == Severidade.ALTA:   contagem["ALTA"]    += 1
        elif log.severidade == Severidade.MEDIA:  contagem["MÉDIA"]   += 1
        elif log.severidade == Severidade.BAIXA:  contagem["BAIXA"]   += 1

    labels = [k for k, v in contagem.items() if v > 0]
    values = [v for v in contagem.values() if v > 0]
    cores  = ['#ef4444', '#FFAB00', '#00A3FF', '#00C853'][:len(labels)]

    if not values:
        values = [1]
        labels = ["Sem dados"]
        cores  = ['#262C36']

    fig, ax = plt.subplots(figsize=(4, 3))
    fig.patch.set_facecolor('#0B0E14')
    ax.pie(values, labels=labels, colors=cores, autopct='%1.1f%%',
           textprops={'color': '#94A3B8', 'fontsize': 8})
    ax.set_title('Distribuição por Severidade', color='#FFFFFF', fontsize=10)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def gerar_pdf(logs: list, summary: dict, period: str) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # cores
    cor_primaria  = colors.HexColor('#00A3FF')
    cor_fundo     = colors.HexColor('#0B0E14')
    cor_surface   = colors.HexColor('#151921')
    cor_borda     = colors.HexColor('#262C36')
    cor_texto     = colors.HexColor('#FFFFFF')
    cor_secundario = colors.HexColor('#94A3B8')
    cor_critica   = colors.HexColor('#ef4444')
    cor_warning   = colors.HexColor('#FFAB00')
    cor_success   = colors.HexColor('#00C853')

    # estilos
    titulo_style = ParagraphStyle(
        'titulo', fontSize=20, textColor=cor_primaria,
        fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4
    )
    subtitulo_style = ParagraphStyle(
        'subtitulo', fontSize=10, textColor=cor_secundario,
        fontName='Helvetica', alignment=TA_CENTER, spaceAfter=2
    )
    secao_style = ParagraphStyle(
        'secao', fontSize=11, textColor=cor_primaria,
        fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6
    )

    # cabeçalho
    story.append(Paragraph("AEGIS IDS/IPS", titulo_style))
    story.append(Paragraph("RELATÓRIO DE SEGURANÇA — ANÁLISE DETALHADA", subtitulo_style))
    story.append(Paragraph(
        f"Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')} UTC  |  Período: {period}",
        subtitulo_style
    ))
    story.append(Spacer(1, 0.4*cm))

    # linha separadora
    story.append(Table([['']], colWidths=[17*cm],
        style=TableStyle([('LINEBELOW', (0,0), (-1,-1), 1, cor_primaria)])))
    story.append(Spacer(1, 0.3*cm))

    # resumo
    story.append(Paragraph("RESUMO EXECUTIVO", secao_style))
    resumo_data = [
        ['MÉTRICA', 'VALOR'],
        ['Total de Eventos',     str(summary.get('total_eventos', 0))],
        ['Severidade Crítica',   str(summary.get('criticos', 0))],
        ['Severidade Alta',      str(summary.get('altos', 0))],
        ['Severidade Média',     str(summary.get('medios', 0))],
        ['Eventos Mitigados',    str(summary.get('bloqueados', 0))],
        ['IPs Bloqueados',       str(summary.get('total_ips_bloqueados', 0))],
    ]
    resumo_table = Table(resumo_data, colWidths=[9*cm, 8*cm])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  cor_primaria),
        ('TEXTCOLOR',    (0,0), (-1,0),  cor_texto),
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('BACKGROUND',   (0,1), (-1,-1), cor_surface),
        ('TEXTCOLOR',    (0,1), (-1,-1), cor_secundario),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [cor_surface, cor_fundo]),
        ('GRID',         (0,0), (-1,-1), 0.5, cor_borda),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ]))
    story.append(resumo_table)
    story.append(Spacer(1, 0.4*cm))

    # gráficos
    story.append(Paragraph("ANÁLISE GRÁFICA", secao_style))
    grafico_volume     = gerar_grafico_volume(logs)
    grafico_severidade = gerar_grafico_severidade(logs)

    graficos_data = [[
        Image(grafico_volume,     width=11*cm, height=4*cm),
        Image(grafico_severidade, width=6*cm,  height=4*cm),
    ]]
    graficos_table = Table(graficos_data, colWidths=[11.5*cm, 6.5*cm])
    graficos_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), cor_surface),
        ('GRID',       (0,0), (-1,-1), 0.5, cor_borda),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(graficos_table)
    story.append(Spacer(1, 0.4*cm))

    # tabela detalhada
    story.append(Paragraph("REGISTO DETALHADO DE INCIDENTES", secao_style))
    tabela_data = [['TIMESTAMP', 'IP ORIGEM', 'IP DESTINO', 'PORTA', 'PROTOCOLO', 'EVENTO', 'SEV.', 'STATUS']]

    for log in logs:
        sev    = log.severidade.value.upper() if log.severidade else '-'
        status = log.status.value.upper()     if log.status     else '-'
        tabela_data.append([
            log.timestamp.strftime('%d/%m %H:%M') if log.timestamp else '-',
            log.src_ip   or '-',
            log.dest_ip  or '-',
            str(log.dest_port or '-'),
            log.protocolo or '-',
            (log.assinatura or '-')[:25],
            sev,
            status,
        ])

    tabela = Table(tabela_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 1.2*cm, 1.8*cm, 3.5*cm, 1.2*cm, 2*cm])
    
    # cores por severidade
    style_cmds = [
        ('BACKGROUND',   (0,0), (-1,0),  cor_primaria),
        ('TEXTCOLOR',    (0,0), (-1,0),  cor_texto),
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 7),
        ('BACKGROUND',   (0,1), (-1,-1), cor_surface),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [cor_surface, cor_fundo]),
        ('TEXTCOLOR',    (0,1), (-1,-1), cor_secundario),
        ('GRID',         (0,0), (-1,-1), 0.3, cor_borda),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ]

    # colore linhas por severidade
    for i, log in enumerate(logs, start=1):
        if log.severidade == Severidade.CRITICA:
            style_cmds.append(('TEXTCOLOR', (6,i), (6,i), cor_critica))
        elif log.severidade == Severidade.ALTA:
            style_cmds.append(('TEXTCOLOR', (6,i), (6,i), cor_warning))

    tabela.setStyle(TableStyle(style_cmds))
    story.append(tabela)

    # rodapé
    story.append(Spacer(1, 0.5*cm))
    story.append(Table([['']], colWidths=[17*cm],
        style=TableStyle([('LINEABOVE', (0,0), (-1,-1), 0.5, cor_borda)])))
    story.append(Paragraph(
        "© AEGIS IDS/IPS Security System — Relatório Confidencial",
        ParagraphStyle('rodape', fontSize=7, textColor=cor_secundario, alignment=TA_CENTER)
    ))

    doc.build(story)
    buf.seek(0)
    return buf