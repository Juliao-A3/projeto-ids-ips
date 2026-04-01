import io
import random
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── Paleta 
C_BG = colors.HexColor('#F7F9FC')
C_WHITE = colors.HexColor('#FFFFFF')
C_PRIMARY = colors.HexColor('#1A56DB')
C_TEXT = colors.HexColor('#1E293B')
C_MUTED = colors.HexColor('#64748B')
C_BORDER = colors.HexColor('#E2E8F0')
C_CRITICA = colors.HexColor('#DC2626')
C_ALTA = colors.HexColor('#D97706')
C_MEDIA = colors.HexColor('#2563EB')
C_SUCCESS = colors.HexColor('#16A34A')
C_WARNING = colors.HexColor('#D97706')
C_CRITICA_BG = colors.HexColor('#FEE2E2')
C_ALTA_BG = colors.HexColor('#FEF3C7')
C_MEDIA_BG = colors.HexColor('#DBEAFE')
C_WARNING_BG = colors.HexColor('#FFFBEB')


# ── Helpers 
def draw_rounded_rect(c, x, y, w, h, r=4, fill=None, stroke=None, stroke_width=0.5):
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    if fill:   c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke); c.setLineWidth(stroke_width)
    c.drawPath(p, fill=1 if fill else 0, stroke=1 if stroke else 0)


def draw_severity_badge(c, x, y, text):
    t = (text or 'N/A').upper()
    if t in ('CRITICA', 'CRITICA'):  bg, fg = C_CRITICA_BG, C_CRITICA
    elif t == 'ALTA':                bg, fg = C_ALTA_BG,    C_ALTA
    elif t in ('MEDIA', 'MEDIA'):    bg, fg = C_MEDIA_BG,   C_MEDIA
    else:                            bg, fg = colors.HexColor('#F1F5F9'), C_MUTED
    bw = 52
    draw_rounded_rect(c, x - bw/2, y - 7, bw, 14, r=3, fill=bg)
    c.setFillColor(fg)
    c.setFont('Helvetica-Bold', 6.5)
    c.drawCentredString(x, y - 1, t)


def grafico_picos(logs) -> io.BytesIO:
    volume = {}
    for log in logs:
        if log.timestamp:
            hora = log.timestamp.strftime('%H:%M')
            volume[hora] = volume.get(hora, 0) + 1
    if not volume:
        horas, ataques = [f'{h:02d}:00' for h in [0, 4, 8, 12, 16, 20]], [0]*6
    else:
        horas, ataques = list(volume.keys()), list(volume.values())

    fig, ax = plt.subplots(figsize=(3.8, 1.8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    bars = ax.bar(range(len(horas)), ataques, color='#1A56DB', width=0.6, zorder=3)
    if ataques:
        mx = max(ataques)
        for bar, v in zip(bars, ataques):
            bar.set_alpha(0.4 + 0.6 * (v / mx if mx else 1))
    ax.set_xticks(range(len(horas)))
    ax.set_xticklabels(horas, rotation=45, ha='right', fontsize=6, color='#64748B')
    ax.tick_params(axis='y', labelsize=6, colors='#64748B')
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.yaxis.grid(True, color='#F1F5F9', zorder=0)
    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


def draw_page_footer(c, W, margin, cw, page_num, total_pages,
                     truncado, limite_aplicado, total_real, tipo_label):
    fy = margin + 0.9*cm
    c.setStrokeColor(C_BORDER); c.setLineWidth(0.5)
    c.line(margin, fy, margin + cw, fy)
    if truncado:
        c.setFillColor(C_WARNING); c.setFont('Helvetica', 5.5)
        c.drawCentredString(W/2, fy - 0.22*cm,
            f'* Relatorio {tipo_label} -- {limite_aplicado} de {total_real:,} alertas mostrados')
    c.setFillColor(C_MUTED); c.setFont('Helvetica', 5.5)
    c.drawString(margin, fy - 0.45*cm, 'GERADO AUTOMATICAMENTE PELO SISTEMA IDS/IPS IA -- AEGIS v4.0.2')
    c.drawRightString(margin + cw, fy - 0.45*cm, f'PAGINA {page_num:02d} DE {total_pages:02d}')


def draw_table_header(c, margin, y, cw, cols, col_widths):
    th = 0.65*cm
    draw_rounded_rect(c, margin, y - th, cw, th, r=4, fill=C_PRIMARY)
    cx = margin
    for col, cw2 in zip(cols, col_widths):
        c.setFillColor(C_WHITE); c.setFont('Helvetica-Bold', 6.5)
        c.drawCentredString(cx + cw2/2, y - th + (th - 7)/2, col)
        cx += cw2
    return y - th


def draw_log_row(c, margin, y, log, row_idx, TABLE_CWS, ROW_H):
    row_fill = C_WHITE if row_idx % 2 == 0 else C_BG
    draw_rounded_rect(c, margin, y - ROW_H, sum(TABLE_CWS), ROW_H, r=0,
                      fill=row_fill, stroke=C_BORDER, stroke_width=0.3)

    ts   = log.timestamp.strftime('%H:%M:%S') if log.timestamp else '-'
    sev  = log.severidade.value if log.severidade else '-'
    acao = ('Bloqueado' if log.status and log.status.value == 'mitigado' else
            'Pendente'  if log.status and log.status.value == 'pendente'  else 'Ignorado')

    row_data = [ts, log.src_ip or '-', log.dest_ip or '-',
                log.protocolo or '-', sev, acao]
    cx = margin
    for j, (val, cw2) in enumerate(zip(row_data, TABLE_CWS)):
        cy2 = y - ROW_H + (ROW_H - 7)/2
        if j == 4:
            draw_severity_badge(c, cx + cw2/2, cy2 + 1, val)
        else:
            col_text = (C_SUCCESS if val == 'Bloqueado' else
                        C_CRITICA if val == 'Pendente'  else C_MUTED)
            c.setFillColor(col_text if j == 5 else C_TEXT)
            c.setFont('Helvetica-Bold' if j == 5 else 'Helvetica', 6.5)
            c.drawCentredString(cx + cw2/2, cy2, val)
        cx += cw2


# ─ PDF PRINCIPAL
def gerar_pdf(logs, summary, period, tipo: str = "detalhado") -> io.BytesIO:
    from backend.models import Severidade, Status

    buf  = io.BytesIO()
    W, H = A4
    c    = canvas.Canvas(buf, pagesize=A4)

    now_str   = datetime.now(timezone.utc).strftime('%d de %B, %Y -- %H:%M:%S')
    report_id = f'#IDS-{datetime.now(timezone.utc).strftime("%Y-%m-%d")}-X11'

    total      = summary.get('total_eventos', 0)
    criticos   = summary.get('criticos', 0)
    altos      = summary.get('altos', 0)
    medios     = summary.get('medios', 0)
    bloqueados = summary.get('bloqueados', 0)
    total_ips  = summary.get('total_ips_bloqueados', 0)

    truncado        = summary.get('truncado', False)
    total_real      = summary.get('total_real', total)
    limite_aplicado = summary.get('limite_aplicado', len(logs))
    tipo_label      = 'DETALHADO' if tipo == 'detalhado' else 'RESUMIDO'

    mitigados_pct = f'{(bloqueados/total*100):.1f}%' if total else '0%'
    nivel_risco   = 'CRITICO'  if criticos > 0 else ('ALTO' if altos > 0 else 'MEDIO')
    nivel_cor     = C_CRITICA  if criticos > 0 else (C_ALTA if altos > 0 else C_MEDIA)

    margin    = 1.8 * cm
    cw        = W - 2 * margin
    footer_h  = 1.6 * cm
    ROW_H     = 0.58 * cm
    TH_H      = 0.65 * cm

    TABLE_COLS = ['HORARIO', 'ORIGEM (IP)', 'DESTINO', 'PROTOCOLO', 'SEVERIDADE', 'ESTADO']
    TABLE_CWS  = [2.2*cm, 3.0*cm, 3.0*cm, 2.2*cm, 2.8*cm, 2.6*cm]

    # seleciona logs para a tabela
    if tipo == 'resumido':
        tabela_logs = [l for l in logs if l.severidade and l.severidade.value in ('critica', 'alta')]
        if not tabela_logs: tabela_logs = logs
    else:
        tabela_logs = logs

    # pré-calcula total de páginas
    # estimativa de linhas que cabem na pág 1 (conservadora)
    ROWS_PG1 = 7
    ROWS_PGN = int((H - 2*margin - footer_h - TH_H - 1.5*cm) / ROW_H)
    n_extra  = max(0, len(tabela_logs) - ROWS_PG1)
    extra_pg = -(-n_extra // ROWS_PGN) if n_extra > 0 else 0
    total_pages = 1 + extra_pg

    # PÁGINA 1
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - margin

    # header
    hh = 2.1*cm
    draw_rounded_rect(c, margin, y - hh, cw, hh, r=6, fill=C_WHITE, stroke=C_BORDER)
    ix = margin + 0.5*cm
    iy = y - hh + (hh - 0.9*cm)/2
    draw_rounded_rect(c, ix, iy, 0.9*cm, 0.9*cm, r=5, fill=C_PRIMARY)
    c.setFillColor(C_WHITE); c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(ix + 0.45*cm, iy + 0.22*cm, 'A')
    tx = ix + 1.1*cm
    c.setFillColor(C_TEXT); c.setFont('Helvetica-Bold', 11)
    c.drawString(tx, y - hh + hh*0.62, 'SISTEMA IDS/IPS IA')
    c.setFillColor(C_MUTED); c.setFont('Helvetica', 7.5)
    c.drawString(tx, y - hh + hh*0.32, f'Relatorio Tecnico de Incidentes  --  {tipo_label}  --  {period}')
    rx = margin + cw - 0.4*cm
    c.setFillColor(C_MUTED); c.setFont('Helvetica', 6.5)
    c.drawRightString(rx, y - hh + hh*0.72, 'REPORT ID')
    c.setFillColor(C_TEXT); c.setFont('Helvetica-Bold', 7.5)
    c.drawRightString(rx, y - hh + hh*0.50, report_id)
    c.setFillColor(C_MUTED); c.setFont('Helvetica', 6.5)
    c.drawRightString(rx, y - hh + hh*0.28, f'GERADO EM  {now_str}')
    y -= hh + 0.3*cm

    # aviso truncagem
    if truncado:
        ah = 0.62*cm
        draw_rounded_rect(c, margin, y - ah, cw, ah, r=4, fill=C_WARNING_BG, stroke=C_WARNING, stroke_width=0.8)
        c.setFillColor(C_WARNING); c.setFont('Helvetica-Bold', 7)
        c.drawString(margin + 0.35*cm, y - ah + 0.19*cm,
            f'A mostrar os {limite_aplicado} alertas mais recentes de {total_real:,} no total.')
        y -= ah + 0.25*cm

    # linha azul
    c.setStrokeColor(C_PRIMARY); c.setLineWidth(1.5)
    c.line(margin, y, margin + cw, y)
    y -= 0.38*cm

    # sumário
    c.setFillColor(C_TEXT); c.setFont('Helvetica-Bold', 8.5)
    c.drawString(margin, y, 'SUMARIO EXECUTIVO')
    y -= 0.28*cm

    card_w = (cw - 0.4*cm) / 3
    card_h = 1.6*cm
    cards = [
        ('TOTAL DE ALERTAS',  f'{total:,}', C_PRIMARY, None),
        ('AMEACAS MITIGADAS', mitigados_pct, C_SUCCESS, None),
        ('NIVEL DE RISCO',    nivel_risco,   nivel_cor, nivel_cor),
    ]
    for i, (label, value, vc, border_c) in enumerate(cards):
        cx = margin + i * (card_w + 0.2*cm)
        draw_rounded_rect(c, cx, y - card_h, card_w, card_h, r=5, fill=C_WHITE,
                          stroke=border_c or C_BORDER, stroke_width=0.8 if border_c else 0.5)
        c.setFillColor(C_MUTED); c.setFont('Helvetica', 6.5)
        c.drawString(cx + 0.3*cm, y - 0.4*cm, label)
        c.setFillColor(vc); c.setFont('Helvetica-Bold', 17)
        c.drawString(cx + 0.3*cm, y - 1.15*cm, value)
    y -= card_h + 0.3*cm

    # 4 métricas
    mw = (cw - 0.9*cm) / 4
    mh = 1.0*cm
    for i, (lbl, val, col) in enumerate([
        ('CRITICOS', str(criticos), C_CRITICA),
        ('ALTOS',    str(altos),    C_ALTA),
        ('MEDIOS',   str(medios),   C_MEDIA),
        ('IPs BLOQ', str(total_ips),C_SUCCESS),
    ]):
        mx = margin + i * (mw + 0.3*cm)
        draw_rounded_rect(c, mx, y - mh, mw, mh, r=4, fill=C_WHITE, stroke=col, stroke_width=0.6)
        draw_rounded_rect(c, mx, y - mh, mw, 0.05*cm, r=0, fill=col)
        c.setFillColor(col); c.setFont('Helvetica-Bold', 13)
        c.drawCentredString(mx + mw/2, y - 0.65*cm, val)
        c.setFillColor(C_MUTED); c.setFont('Helvetica', 6)
        c.drawCentredString(mx + mw/2, y - mh + 0.12*cm, lbl)
    y -= mh + 0.3*cm

    # gráfico + protocolos
    col_w = (cw - 0.4*cm) / 2
    col_h = 3.0*cm

    draw_rounded_rect(c, margin, y - col_h, col_w, col_h, r=5, fill=C_WHITE, stroke=C_BORDER)
    c.setFillColor(C_MUTED); c.setFont('Helvetica-Bold', 6.5)
    c.drawString(margin + 0.35*cm, y - 0.38*cm, 'TOP PROTOCOLOS AFETADOS')

    proto_count = {}
    for log in logs:
        if log.protocolo:
            p = f'{log.protocolo.upper()} ({log.dest_port})' if log.dest_port else log.protocolo.upper()
            proto_count[p] = proto_count.get(p, 0) + 1
    top_protos = sorted(proto_count.items(), key=lambda x: x[1], reverse=True)[:3]
    if not top_protos:
        top_protos = [('HTTPS (443)', 65), ('SSH (22)', 22), ('DNS (53)', 13)]
    else:
        tp = sum(v for _, v in top_protos) or 1
        top_protos = [(k, int(v/tp*100)) for k, v in top_protos]

    bmw = col_w - 2.0*cm
    py = y - 0.85*cm
    for proto, pct in top_protos:
        c.setFillColor(C_TEXT); c.setFont('Helvetica', 6.5)
        c.drawString(margin + 0.35*cm, py, proto)
        bx, by, bh = margin + 0.35*cm, py - 0.22*cm, 0.15*cm
        draw_rounded_rect(c, bx, by, bmw, bh, r=2, fill=C_BORDER)
        draw_rounded_rect(c, bx, by, bmw * pct/100, bh, r=2, fill=C_PRIMARY)
        c.setFillColor(C_MUTED); c.setFont('Helvetica', 6)
        c.drawRightString(margin + col_w - 0.3*cm, py, f'{pct}%')
        py -= 0.68*cm

    gx = margin + col_w + 0.4*cm
    draw_rounded_rect(c, gx, y - col_h, col_w, col_h, r=5, fill=C_WHITE, stroke=C_BORDER)
    c.setFillColor(C_MUTED); c.setFont('Helvetica-Bold', 6.5)
    c.drawString(gx + 0.35*cm, y - 0.38*cm, 'PICOS DE ATAQUE')
    c.drawImage(ImageReader(grafico_picos(logs)), gx + 0.2*cm, y - col_h + 0.15*cm,
                width=col_w - 0.4*cm, height=col_h - 0.6*cm,
                preserveAspectRatio=True, mask='auto')
    y -= col_h + 0.35*cm

    # título tabela
    lbl_tabela = 'INCIDENTES CRITICOS' if tipo == 'resumido' else 'TODOS OS INCIDENTES'
    c.setFillColor(C_TEXT); c.setFont('Helvetica-Bold', 8)
    c.drawString(margin, y, f'{lbl_tabela}  ({len(tabela_logs)} registos)')
    y -= 0.3*cm

    y = draw_table_header(c, margin, y, cw, TABLE_COLS, TABLE_CWS)

    # linhas pág 1
    log_idx    = 0
    row_idx    = 0
    y_lim      = margin + footer_h + 0.2*cm

    while log_idx < len(tabela_logs) and (y - ROW_H) >= y_lim:
        draw_log_row(c, margin, y, tabela_logs[log_idx], row_idx, TABLE_CWS, ROW_H)
        y -= ROW_H; row_idx += 1; log_idx += 1

    draw_page_footer(c, W, margin, cw, 1, total_pages,
                     truncado, limite_aplicado, total_real, tipo_label)
    c.showPage()

    # PÁGINAS EXTRA
    page_num = 2
    while log_idx < len(tabela_logs):
        c.setFillColor(C_BG); c.rect(0, 0, W, H, fill=1, stroke=0)

        # mini header
        c.setFillColor(C_PRIMARY); c.setFont('Helvetica-Bold', 8)
        c.drawString(margin, H - margin - 0.3*cm,
                     f'AEGIS IDS/IPS IA  --  {tipo_label}  --  {period}  --  {lbl_tabela} (cont.)')
        c.setFillColor(C_MUTED); c.setFont('Helvetica', 7)
        c.drawRightString(margin + cw, H - margin - 0.3*cm, report_id)
        c.setStrokeColor(C_BORDER); c.setLineWidth(0.5)
        c.line(margin, H - margin - 0.55*cm, margin + cw, H - margin - 0.55*cm)

        y = H - margin - 1.0*cm
        y = draw_table_header(c, margin, y, cw, TABLE_COLS, TABLE_CWS)

        row_idx_page = 0
        while log_idx < len(tabela_logs) and (y - ROW_H) >= y_lim:
            draw_log_row(c, margin, y, tabela_logs[log_idx], row_idx_page, TABLE_CWS, ROW_H)
            y -= ROW_H; row_idx_page += 1; log_idx += 1

        draw_page_footer(c, W, margin, cw, page_num, total_pages,
                         truncado, limite_aplicado, total_real, tipo_label)
        c.showPage()
        page_num += 1

    c.save()
    buf.seek(0)
    return buf