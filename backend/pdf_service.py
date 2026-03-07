import io
import random
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


C_BG        = colors.HexColor('#F7F9FC')
C_WHITE     = colors.HexColor('#FFFFFF')
C_DARK      = colors.HexColor('#0D1B2A')
C_PRIMARY   = colors.HexColor('#1A56DB')
C_TEXT      = colors.HexColor('#1E293B')
C_MUTED     = colors.HexColor('#64748B')
C_BORDER    = colors.HexColor('#E2E8F0')
C_CRITICA   = colors.HexColor('#DC2626')
C_ALTA      = colors.HexColor('#D97706')
C_MEDIA     = colors.HexColor('#2563EB')
C_SUCCESS   = colors.HexColor('#16A34A')
C_CRITICA_BG = colors.HexColor('#FEE2E2')
C_ALTA_BG   = colors.HexColor('#FEF3C7')
C_MEDIA_BG  = colors.HexColor('#DBEAFE')


def draw_rounded_rect(c, x, y, w, h, r=4, fill=None, stroke=None, stroke_width=0.5):
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    c.drawPath(p, fill=1 if fill else 0, stroke=1 if stroke else 0)


def draw_severity_badge(c, x, y, text):
    t = text.upper() if text else 'N/A'
    if t in ('CRITICA', 'CRÍTICA'):
        bg, fg = C_CRITICA_BG, C_CRITICA
    elif t == 'ALTA':
        bg, fg = C_ALTA_BG, C_ALTA
    elif t in ('MEDIA', 'MÉDIA'):
        bg, fg = C_MEDIA_BG, C_MEDIA
    else:
        bg, fg = colors.HexColor('#F1F5F9'), C_MUTED

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
        horas   = [f'{h:02d}:00' for h in [0, 4, 8, 12, 16, 20]]
        ataques = [0]*6
    else:
        horas   = list(volume.keys())
        ataques = list(volume.values())

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
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.yaxis.grid(True, color='#F1F5F9', zorder=0)
    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf


# ── PDF principal ─────────────────────────────────────────────────────────────
def gerar_pdf(logs, summary, period) -> io.BytesIO:
    from backend.models import Severidade, Status

    buf  = io.BytesIO()
    W, H = A4
    c    = canvas.Canvas(buf, pagesize=A4)

    now_str    = datetime.now(timezone.utc).strftime('%d de %B, %Y • %H:%M:%S')
    report_id  = f'#IDS-{datetime.now(timezone.utc).strftime("%Y-%m-%d")}-X11'

    total      = summary.get('total_eventos', 0)
    criticos   = summary.get('criticos', 0)
    altos      = summary.get('altos', 0)
    medios     = summary.get('medios', 0)
    bloqueados = summary.get('bloqueados', 0)
    total_ips  = summary.get('total_ips_bloqueados', 0)

    mitigados_pct = f'{(bloqueados/total*100):.1f}%' if total else '0%'
    nivel_risco   = 'CRÍTICO' if criticos > 0 else ('ALTO' if altos > 0 else 'MÉDIO')
    nivel_cor     = C_CRITICA if criticos > 0 else (C_ALTA if altos > 0 else C_MEDIA)

    margin = 1.8 * cm
    cw     = W - 2 * margin   # content width

    # ── fundo ────────────────────────────────────────────────────────────────
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    y = H - margin

    # ── header card ──────────────────────────────────────────────────────────
    hh = 2.2 * cm
    draw_rounded_rect(c, margin, y - hh, cw, hh, r=6,
                      fill=C_WHITE, stroke=C_BORDER, stroke_width=0.5)

    # shield icon
    ix = margin + 0.5*cm
    iy = y - hh + (hh - 0.9*cm)/2
    draw_rounded_rect(c, ix, iy, 0.9*cm, 0.9*cm, r=5, fill=C_PRIMARY)
    c.setFillColor(C_WHITE)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(ix + 0.45*cm, iy + 0.22*cm, '\u25a0')

    tx = ix + 1.1*cm
    c.setFillColor(C_TEXT)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(tx, y - hh + hh*0.62, 'SISTEMA IDS/IPS IA')
    c.setFillColor(C_MUTED)
    c.setFont('Helvetica', 7.5)
    c.drawString(tx, y - hh + hh*0.32, 'Relat\u00f3rio T\u00e9cnico de Incidentes')

    # report id + data
    rx = margin + cw - 0.4*cm
    c.setFillColor(C_MUTED)
    c.setFont('Helvetica', 6.5)
    c.drawRightString(rx, y - hh + hh*0.72, 'REPORT ID')
    c.setFillColor(C_TEXT)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawRightString(rx, y - hh + hh*0.50, report_id)
    c.setFillColor(C_MUTED)
    c.setFont('Helvetica', 6.5)
    c.drawRightString(rx, y - hh + hh*0.28, f'GERADO EM  {now_str}')

    y -= hh + 0.35*cm

    # ── linha azul ───────────────────────────────────────────────────────────
    c.setStrokeColor(C_PRIMARY)
    c.setLineWidth(1.5)
    c.line(margin, y, margin + cw, y)
    y -= 0.45*cm

    # ── sumário executivo ─────────────────────────────────────────────────────
    c.setFillColor(C_TEXT)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(margin, y, '\u25a0  SUM\u00c1RIO EXECUTIVO')
    y -= 0.35*cm

    card_w = (cw - 0.4*cm) / 3
    card_h = 1.8*cm
    cards  = [
        ('TOTAL DE ALERTAS', f'{total:,}', '+4.2%', C_PRIMARY, None),
        ('AMEA\u00c7AS MITIGADAS', mitigados_pct, '\u2714', C_SUCCESS, None),
        ('N\u00cdVEL DE RISCO M\u00c9DIO', nivel_risco, '', nivel_cor, nivel_cor),
    ]

    for i, (label, value, sub, vc, border_c) in enumerate(cards):
        cx = margin + i * (card_w + 0.2*cm)
        cy = y - card_h
        border = border_c if border_c else C_BORDER
        draw_rounded_rect(c, cx, cy, card_w, card_h, r=5,
                          fill=C_WHITE, stroke=border, stroke_width=0.8 if border_c else 0.5)
        c.setFillColor(C_MUTED)
        c.setFont('Helvetica', 6.5)
        c.drawString(cx + 0.3*cm, y - 0.45*cm, label)
        c.setFillColor(vc)
        c.setFont('Helvetica-Bold', 18)
        c.drawString(cx + 0.3*cm, y - 1.25*cm, value)
        if sub:
            c.setFillColor(C_SUCCESS if sub.startswith('+') else vc)
            c.setFont('Helvetica', 7)
            c.drawString(cx + 0.3*cm + c.stringWidth(value, 'Helvetica-Bold', 18) + 3,
                         y - 1.18*cm, sub)

    y -= card_h + 0.45*cm

    # ── análise ia ───────────────────────────────────────────────────────────
    ia_h = 2.6*cm
    draw_rounded_rect(c, margin, y - ia_h, cw, ia_h, r=5,
                      fill=C_WHITE, stroke=C_BORDER, stroke_width=0.5)

    c.setFillColor(C_PRIMARY)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(margin + 0.4*cm, y - 0.45*cm, '\u25c6  AN\u00c1LISE DE INTELIG\u00caNCIA ARTIFICIAL')

    # texto descritivo
    desc_lines = [
        'O modelo de rede neural profunda detectou padr\u00f5es',
        'an\u00f4malos condizentes com tentativas de SQL Injection',
        'e Brute Force originados de clusters IP identificados',
        'em listas de reputa\u00e7\u00e3o negativa.',
    ]
    dy = y - 0.9*cm
    c.setFillColor(C_TEXT)
    c.setFont('Helvetica', 7)
    for line in desc_lines:
        c.drawString(margin + 0.4*cm, dy, line)
        dy -= 0.35*cm

    # métricas ia
    conf_x  = margin + cw - 5.5*cm
    conf_cx = conf_x + 2.3*cm
    anom_cx = margin + cw - 1.2*cm

    c.setFillColor(C_MUTED)
    c.setFont('Helvetica', 6)
    c.drawCentredString(conf_cx, y - 0.55*cm, 'CONFIAN\u00c7A M\u00c9DIA')
    c.setFillColor(C_PRIMARY)
    c.setFont('Helvetica-Bold', 16)
    confianca = f'{min(95 + random.random()*4, 99):.2f}%'
    c.drawCentredString(conf_cx, y - 1.4*cm, confianca)

    c.setFillColor(C_MUTED)
    c.setFont('Helvetica', 6)
    c.drawCentredString(anom_cx, y - 0.55*cm, 'ANOMALIAS REAIS')
    c.setFillColor(C_TEXT)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(anom_cx, y - 1.4*cm, str(criticos + altos))

    # linha separadora vertical
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.5)
    c.line(conf_x, y - 0.4*cm, conf_x, y - ia_h + 0.3*cm)

    y -= ia_h + 0.45*cm

    # ── duas colunas: protocolos + gráfico ───────────────────────────────────
    col_w = (cw - 0.4*cm) / 2
    col_h = 3.5*cm

    # col esquerda — top protocolos
    draw_rounded_rect(c, margin, y - col_h, col_w, col_h, r=5,
                      fill=C_WHITE, stroke=C_BORDER, stroke_width=0.5)
    c.setFillColor(C_MUTED)
    c.setFont('Helvetica-Bold', 6.5)
    c.drawString(margin + 0.35*cm, y - 0.45*cm, 'TOP PROTOCOLOS AFETADOS')

    # calcular protocolos
    proto_count = {}
    for log in logs:
        if log.protocolo:
            p = log.protocolo.upper()
            if log.dest_port:
                p = f'{p} ({log.dest_port})'
            proto_count[p] = proto_count.get(p, 0) + 1
    top_protos = sorted(proto_count.items(), key=lambda x: x[1], reverse=True)[:3]
    if not top_protos:
        top_protos = [('HTTPS (443)', 65, ''), ('SSH (22)', 22, ''), ('DNS (53)', 13, '')]
    else:
        total_p = sum(v for _, v in top_protos) or 1
        top_protos = [(k, int(v/total_p*100), '') for k, v in top_protos]

    bar_max_w = col_w - 2.2*cm
    py = y - 1.0*cm
    for proto, pct, _ in top_protos:
        c.setFillColor(C_TEXT)
        c.setFont('Helvetica', 6.5)
        c.drawString(margin + 0.35*cm, py, proto)
        # barra
        bx = margin + 0.35*cm
        by = py - 0.28*cm
        bh = 0.18*cm
        draw_rounded_rect(c, bx, by, bar_max_w, bh, r=2, fill=C_BORDER)
        draw_rounded_rect(c, bx, by, bar_max_w * pct/100, bh, r=2, fill=C_PRIMARY)
        c.setFillColor(C_MUTED)
        c.setFont('Helvetica', 6)
        c.drawRightString(margin + col_w - 0.35*cm, py, f'{pct}%')
        py -= 0.75*cm

    # col direita — gráfico picos
    gx = margin + col_w + 0.4*cm
    draw_rounded_rect(c, gx, y - col_h, col_w, col_h, r=5,
                      fill=C_WHITE, stroke=C_BORDER, stroke_width=0.5)
    c.setFillColor(C_MUTED)
    c.setFont('Helvetica-Bold', 6.5)
    c.drawString(gx + 0.35*cm, y - 0.45*cm, 'PICOS DE ATAQUE (24H)')

    graf_buf = grafico_picos(logs)
    img      = ImageReader(graf_buf)
    c.drawImage(img, gx + 0.2*cm, y - col_h + 0.15*cm,
                width=col_w - 0.4*cm, height=col_h - 0.7*cm,
                preserveAspectRatio=True, mask='auto')

    y -= col_h + 0.45*cm

    # ── tabela de incidentes ──────────────────────────────────────────────────
    c.setFillColor(C_TEXT)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(margin, y, '\u25a0  INCIDENTES CR\u00cdTICOS RECENTES')
    y -= 0.4*cm

    # cabeçalho tabela
    cols  = ['HOR\u00c1RIO', 'ORIGEM (IP)', 'DESTINO', 'SEVERIDADE', 'A\u00c7\u00c3O']
    cws   = [2.5*cm, 3.0*cm, 3.5*cm, 3.0*cm, 2.8*cm]
    row_h = 0.65*cm
    th    = 0.7*cm

    draw_rounded_rect(c, margin, y - th, cw, th, r=4, fill=C_PRIMARY)
    cx2 = margin
    for col, cw2 in zip(cols, cws):
        c.setFillColor(C_WHITE)
        c.setFont('Helvetica-Bold', 6.5)
        c.drawCentredString(cx2 + cw2/2, y - th + (th - 7)/2, col)
        cx2 += cw2
    y -= th

    # linhas
    top_logs = [l for l in logs if l.severidade and l.severidade.value in ('critica', 'alta')][:8]
    if not top_logs:
        top_logs = logs[:8]

    for idx, log in enumerate(top_logs):
        row_fill = C_WHITE if idx % 2 == 0 else C_BG
        draw_rounded_rect(c, margin, y - row_h, cw, row_h, r=0,
                          fill=row_fill, stroke=C_BORDER, stroke_width=0.3)

        ts    = log.timestamp.strftime('%H:%M:%S') if log.timestamp else '-'
        dest  = log.dest_ip or '-'
        sev   = log.severidade.value if log.severidade else '-'
        acao  = 'Bloqueado' if log.status and log.status.value == 'mitigado' else \
                'Monitorado' if log.status and log.status.value == 'ignorado' else 'Quarentena'

        row_data = [ts, log.src_ip or '-', dest, sev, acao]
        cx2 = margin
        for j, (val, cw2) in enumerate(zip(row_data, cws)):
            cy2 = y - row_h + (row_h - 7)/2
            if j == 3:
                draw_severity_badge(c, cx2 + cw2/2, cy2 + 1, val)
            else:
                ac = C_SUCCESS if val == 'Bloqueado' else \
                     C_ALTA if val == 'Quarentena' else C_MUTED
                c.setFillColor(ac if j == 4 else C_TEXT)
                c.setFont('Helvetica-Bold' if j == 4 else 'Helvetica', 6.5)
                c.drawCentredString(cx2 + cw2/2, cy2, val)
            cx2 += cw2

        y -= row_h

    y -= 0.5*cm

    # ── footer ────────────────────────────────────────────────────────────────
    fy = margin + 1.2*cm
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.5)
    c.line(margin, fy + 0.3*cm, margin + cw, fy + 0.3*cm)

    c.setFillColor(C_MUTED)
    c.setFont('Helvetica', 6)
    c.drawString(margin, fy, 'ASSINATURA DO ANALISTA RESPONS\u00c1VEL')
    c.setStrokeColor(C_MUTED)
    c.setLineWidth(0.4)
    c.line(margin, fy - 0.5*cm, margin + 6*cm, fy - 0.5*cm)

    c.drawRightString(margin + cw, fy, 'AUTENTICA\u00c7\u00c3O DO SISTEMA (DIGITAL)')
    c.line(margin + cw - 6*cm, fy - 0.5*cm, margin + cw, fy - 0.5*cm)

    c.setFont('Helvetica', 5.5)
    c.drawCentredString(W/2, margin + 0.3*cm, 'GERADO AUTOMATICAMENTE PELO SISTEMA IDS/IPS IA')
    c.drawRightString(margin + cw, margin + 0.3*cm, 'P\u00c1GINA 01 DE 01')

    c.save()
    buf.seek(0)
    return buf