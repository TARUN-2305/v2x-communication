import os
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT

W, H = A3   # 841.9 x 1190.6 pt
M    = 11*mm
GAP  = 4*mm
COL  = (W - 2*M - GAP) / 2

# ── Exact color palette ───────────────────────────────────────────────────────
WHITE   = colors.white
BG      = colors.HexColor('#FFFFFF')        # page background
CARD    = colors.HexColor('#F7F7F7')        # section card bg
CARDBRD = colors.HexColor('#E0E0E0')        # card border
HDR_BG  = colors.white                      # header background
ORANGE  = colors.HexColor('#E65C00')        # primary accent
ORANGE2 = colors.HexColor('#F97316')        # lighter orange
DARK    = colors.HexColor('#1A1A1A')        # body text
MID     = colors.HexColor('#555555')        # secondary text
LIGHT_T = colors.HexColor('#888888')        # tertiary text

# KPI box colors matching sample poster
KPI1_BG = colors.HexColor('#1A6B3A')        # deep green
KPI2_BG = colors.HexColor('#0E7490')        # teal
KPI3_BG = colors.HexColor('#92400E')        # amber/brown
KPI4_BG = colors.HexColor('#1D4ED8')        # blue

UL      = ORANGE
TBL_HDR = colors.HexColor('#E65C00')
TBL_ROW1= colors.HexColor('#FFF7ED')
TBL_ROW2= colors.HexColor('#FFFFFF')
TBL_GRN = colors.HexColor('#F0FDF4')
TBL_GRN_T=colors.HexColor('#166534')

def mk(name, size=7, lead=9, color=DARK, align=TA_JUSTIFY, bold=False, indent=0, fi=0):
    fn = 'Helvetica-Bold' if bold else 'Helvetica'
    return ParagraphStyle(name, fontName=fn, fontSize=size, leading=lead,
                          textColor=color, alignment=align,
                          leftIndent=indent, firstLineIndent=fi)

S_BODY  = mk('body',  6.8, 8.8, DARK, TA_JUSTIFY)
S_BUL   = mk('bul',   6.8, 9.0, DARK, TA_JUSTIFY, indent=7, fi=-7)
S_REF   = mk('ref',   5.8, 7.5, MID,  TA_LEFT)
S_SM    = mk('sm',    5.3, 6.5, MID,  TA_CENTER)
S_SMWH  = mk('smwh',  5.3, 6.5, colors.white, TA_CENTER)

def fr(cv, items, x, y, w, h):
    f = Frame(x, y, w, h, showBoundary=0,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    f.addFromList(list(items), cv)

def card(cv, x, y, w, h):
    cv.setFillColor(CARD)
    cv.setStrokeColor(CARDBRD)
    cv.setLineWidth(0.5)
    cv.roundRect(x, y-h, w, h, 2.5*mm, fill=1, stroke=1)

def sec(cv, x, y, w, txt):
    """Section header: bold dark text + orange underline"""
    cv.setFont('Helvetica-Bold', 8.5)
    cv.setFillColor(DARK)
    cv.drawCentredString(x + w/2, y, txt)
    cv.setStrokeColor(UL)
    cv.setLineWidth(1.8)
    cv.line(x, y-2, x+w, y-2)
    return y - 4*mm

def kpi_box(cv, x, y, w, h, big, sub, bg, tc=colors.white):
    cv.setFillColor(bg)
    cv.setStrokeColor(colors.HexColor('#CCCCCC'))
    cv.setLineWidth(0.3)
    cv.roundRect(x, y, w, h, 2*mm, fill=1, stroke=0)
    cv.setFont('Helvetica-Bold', 13)
    cv.setFillColor(tc)
    cv.drawCentredString(x+w/2, y+h/2+2.5, big)
    cv.setFont('Helvetica', 5.5)
    cv.setFillColor(colors.HexColor('#FFFFFF99'))
    cv.drawCentredString(x+w/2, y+h/2-7, sub)

def draw_poster():
    out_pdf = 'EcoSync_A3_Poster_Light.pdf'
    cv = canvas.Canvas(out_pdf, pagesize=A3)
    cv.setTitle('ECO-SYNC Transit AI — A3 Poster')

    # ── Page background ───────────────────────────────────────────────────────
    cv.setFillColor(BG)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    # ── HEADER ────────────────────────────────────────────────────────────────
    hh = 64*mm
    cv.setFillColor(HDR_BG)
    cv.setStrokeColor(CARDBRD)
    cv.setLineWidth(0.5)
    cv.roundRect(M, H-M-hh, W-2*M, hh, 3*mm, fill=1, stroke=1)
    
    # Orange top accent bar
    cv.setFillColor(ORANGE)
    cv.rect(M, H-M-3, W-2*M, 3, fill=1, stroke=0)
    
    # Thin orange bottom bar of header
    cv.setFillColor(ORANGE)
    cv.rect(M, H-M-hh, W-2*M, 1.5, fill=1, stroke=0)

    # RVCE Logo
    logo_path = 'Stuff/RV_Logo_Full.png'
    if os.path.exists(logo_path):
        cv.drawImage(logo_path,
                     M+4*mm, H-M-hh+7*mm,
                     width=36*mm, height=15*mm,
                     preserveAspectRatio=True, mask='auto')

    # "Go, change the world"
    cv.setFont('Helvetica-Oblique', 7.5)
    cv.setFillColor(LIGHT_T)
    cv.drawRightString(W-M-5*mm, H-M-9, 'Go, change the world')

    cx = W/2
    # Institution
    cv.setFont('Helvetica-Bold', 9.5)
    cv.setFillColor(DARK)
    cv.drawCentredString(cx, H-M-14, 'RV College of Engineering, Bengaluru – 560059')
    
    # Project title
    cv.setFont('Helvetica-Bold', 17)
    cv.setFillColor(ORANGE)
    cv.drawCentredString(cx, H-M-26, 'ECO-SYNC TRANSIT AI')
    
    # Subtitle
    cv.setFont('Helvetica-Oblique', 8)
    cv.setFillColor(MID)
    cv.drawCentredString(cx, H-M-36, 'Agentic AI for Economic Dispatch and Anti-Bunching in Urban Transit')
    
    # Students
    cv.setFont('Helvetica-Bold', 7.5)
    cv.setFillColor(DARK)
    cv.drawCentredString(cx, H-M-47,
        'Vikas K T (1RV23CS286)   |   Vishwas V (1RV23CS293)   |   Vijaykumar Y M (1RV24CS424)   |   Tarun R (1RV23CS271)')
    
    # Guide
    cv.setFont('Helvetica', 7)
    cv.setFillColor(MID)
    cv.drawCentredString(cx, H-M-56, 'Under the Guidance of: Dr. Sunil S, Department of Civil Engineering, RVCE')
    
    # Dept tag
    cv.setFont('Helvetica-Bold', 7)
    cv.setFillColor(ORANGE)
    cv.drawCentredString(cx, H-M-63, 'Department of Computer Science and Engineering   |   Academic Year 2025–2026')

    body_top = H - M - hh - 3.5*mm
    body_bot = 75*mm # Raised from 55mm to prevent overlap with bottom cards

    lx = M
    rx = M + COL + GAP
    y = body_top

    # ══════════════════════ LEFT COLUMN ═══════════════════════════════════════
    # Total available height = 341.5mm - 75mm = 266.5mm.
    # Distribute heights: 48mm, 50mm, 48mm, 72mm, 38mm = 256mm + 4*2.5mm gaps = 266mm.

    # ── Introduction ──────────────────────────────────────────────────────────
    sh = 48*mm
    card(cv, lx, y, COL, sh)
    sec(cv, lx+4*mm, y-5*mm, COL-8*mm, 'Introduction')
    txt = ("Public bus networks in Indian cities suffer from &lt;b&gt;bus bunching&lt;/b&gt; — a dynamic "
           "instability where a minor delay causes one bus to accumulate more passengers, slow "
           "further, and cluster with trailing buses. On &lt;b&gt;Bengaluru's Outer Ring Road (ORR)&lt;/b&gt;, "
           "this collapses headway spacing and doubles commuter wait times. &lt;b&gt;ECO-SYNC Transit AI&lt;/b&gt; "
           "replaces static timetables with an Agentic PPO Reinforcement Learning dispatcher "
           "that optimises a multi-dimensional &lt;b&gt;Economic Reward Function&lt;/b&gt;, integrating ticket "
           "revenue, passenger Value of Time (VoT), fuel costs, and bunching penalties — all "
           "explained in real-time by a &lt;b&gt;Groq Llama-3.1&lt;/b&gt; reasoning layer.")
    fr(cv, [Paragraph(txt, S_BODY)], lx+4*mm, y-sh+3*mm, COL-8*mm, sh-11*mm)
    y -= sh + 2.5*mm

    # ── Problem Definition ─────────────────────────────────────────────────────
    sh = 50*mm
    card(cv, lx, y, COL, sh)
    sec(cv, lx+4*mm, y-5*mm, COL-8*mm, 'Problem Definition')
    ps = [Paragraph(p, S_BUL) for p in [
        '1. Buses cluster, causing cascading service gaps exceeding 20 minutes on Bengaluru ORR.',
        '2. Static timetables cannot adapt to live congestion, signal failures, or passenger surges.',
        '3. Existing DRL controllers minimise headway variance but ignore economic costs of transit operations.',
        '4. Dispatch decisions are black-box, eroding driver and commuter trust in AI systems.',
        '5. No open-source system provides real-time dispatch &lt;i&gt;and&lt;/i&gt; explainability on a single route.',
    ]]
    fr(cv, ps, lx+4*mm, y-sh+3*mm, COL-8*mm, sh-11*mm)
    y -= sh + 2.5*mm

    # ── Objectives ────────────────────────────────────────────────────────────
    sh = 48*mm
    card(cv, lx, y, COL, sh)
    sec(cv, lx+4*mm, y-5*mm, COL-8*mm, 'Objectives')
    os_ = [Paragraph(p, S_BUL) for p in [
        '1. Build a high-fidelity Gymnasium simulation environment: 30-stop Bengaluru ORR circular route.',
        '2. Design Economic Reward: R = Revenue − Wait_Cost − Fuel_Cost − Bunching_Penalty.',
        '3. Train a PPO agent to issue PROCEED / HOLD / SKIP actions preventing bunching cascades.',
        '4. Integrate Groq Llama-3.1 to generate plain-language dispatch justifications in real-time.',
        '5. Deploy React.js + FastAPI dashboard with live Leaflet maps and WebSocket telemetry.',
    ]]
    fr(cv, os_, lx+4*mm, y-sh+3*mm, COL-8*mm, sh-11*mm)
    y -= sh + 2.5*mm

    # ── Methodology ──────────────────────────────────────────────────────────
    sh = 72*mm
    card(cv, lx, y, COL, sh)
    sec(cv, lx+4*mm, y-5*mm, COL-8*mm, 'Methodology')

    # 5-step flow boxes
    steps = [
        ('1','STATE\nEXTRACT','S=[gap_ahead, gap_behind, queue_len]'),
        ('2','ACTION\nSELECT', 'PPO outputs PROCEED / HOLD / SKIP'),
        ('3','ECON\nREWARD',  'R = Rev - WaitCost - Fuel - Penalty'),
        ('4','LLM\nREASON',   'Groq Llama-3.1 explains action live'),
        ('5','WS\nSTREAM',    'FastAPI 1Hz to React to Leaflet map'),
    ]
    n = len(steps)
    bw = (COL-8*mm)/n - 1.5*mm
    bh = 25*mm
    bx0= lx+4*mm
    by = y - sh + 29*mm  # Placed in [y-43, y-18] mm
    for i,(num,head,sub) in enumerate(steps):
        bx = bx0 + i*(bw+1.5*mm)
        box_bg = colors.HexColor('#FFF7ED') if i%2==0 else colors.HexColor('#FFFFFF')
        cv.setFillColor(box_bg)
        cv.setStrokeColor(ORANGE)
        cv.setLineWidth(0.8)
        cv.roundRect(bx, by, bw, bh, 2*mm, fill=1, stroke=1)
        
        # Number circle
        cv.setFillColor(ORANGE)
        cv.circle(bx+bw/2, by+bh-5*mm, 3.5*mm, fill=1, stroke=0)
        cv.setFont('Helvetica-Bold',7)
        cv.setFillColor(WHITE)
        cv.drawCentredString(bx+bw/2, by+bh-6.3*mm, num)
        
        # Head
        for li, ln in enumerate(head.split('\n')):
            cv.setFont('Helvetica-Bold',5.5)
            cv.setFillColor(ORANGE)
            cv.drawCentredString(bx+bw/2, by+bh-11.5*mm - li*5.5, ln)
        fr(cv,[Paragraph(sub, S_SM)], bx+1*mm, by+1*mm, bw-2*mm, 10*mm)
        
        # Arrow
        if i < n-1:
            ax_ = bx+bw+0.4*mm
            ay_ = by+bh/2
            cv.setStrokeColor(ORANGE)
            cv.setLineWidth(0.8)
            cv.line(ax_,ay_,ax_+1*mm,ay_)

    # Reward formula box (placed at [y-69.5, y-45.5] mm to prevent overlap with above boxes)
    cv.setFillColor(colors.HexColor('#FFF3E0'))
    cv.setStrokeColor(ORANGE)
    cv.setLineWidth(0.8)
    cv.roundRect(lx+4*mm, y-sh+2.5*mm, COL-8*mm, 24*mm, 2*mm, fill=1, stroke=1)
    
    cv.setFont('Helvetica-Bold',7.5)
    cv.setFillColor(ORANGE)
    cv.drawCentredString(lx+COL/2, y-sh+21.5*mm, 'Economic Reward Function')
    
    rows = [
        ('Helvetica-Bold',7.5,DARK,  'R  =  Revenue  -  Wait_Cost  -  Fuel_Cost  -  Bunching_Penalty'),
        ('Helvetica',6.5,  colors.HexColor('#166534'), 'Revenue  =  Rs.15 x boarded_passengers'),
        ('Helvetica',6.5,  colors.HexColor('#9B1C1C'), 'Wait_Cost  =  passengers x Rs.1.67/min x delay x 10'),
        ('Helvetica',6.5,  colors.HexColor('#92400E'), 'Fuel_Cost  =  Rs.0.83/min x idle_minutes'),
        ('Helvetica',6.5,  colors.HexColor('#7C3AED'), 'Bunching_Penalty  =  -250  if  gap_ahead <= 1.0 stop'),
    ]
    for i,(fn,fs,fc,txt) in enumerate(rows):
        cv.setFont(fn,fs)
        cv.setFillColor(fc)
        cv.drawCentredString(lx+COL/2, y-sh+16*mm - i*5.2, txt)
    y -= sh + 2.5*mm

    # ── Tools ─────────────────────────────────────────────────────────────────
    sh = 38*mm
    card(cv, lx, y, COL, sh)
    sec(cv, lx+4*mm, y-5*mm, COL-8*mm, 'Tools Used')
    tools = [
        ('Gymnasium / SB3','PPO training environment'),
        ('FastAPI + WebSocket','1Hz telemetry streaming'),
        ('React.js + Vite','Live dashboard frontend'),
        ('Leaflet / react-leaflet','Bengaluru ORR map layer'),
        ('Groq Llama-3.1','Real-time dispatch reasoning'),
        ('OSRM API','Real road coordinate routing'),
    ]
    tw = (COL-8*mm)/2 - 2*mm
    for i,(tn,td) in enumerate(tools):
        ci=i%2
        ri=i//2
        tx = lx+4*mm + ci*(tw+4*mm)
        ty_ = y - 12*mm - ri*7.2*mm
        cv.setFillColor(colors.HexColor('#FFF7ED'))
        cv.setStrokeColor(ORANGE)
        cv.setLineWidth(0.5)
        cv.roundRect(tx, ty_-4.5*mm, tw, 6*mm, 1.5*mm, fill=1, stroke=1)
        cv.setFont('Helvetica-Bold',6)
        cv.setFillColor(ORANGE)
        cv.drawString(tx+2*mm, ty_-0.5*mm, tn)
        cv.setFont('Helvetica',5.5)
        cv.setFillColor(MID)
        cv.drawString(tx+2*mm, ty_-3.8*mm, td)

    # ══════════════════════ RIGHT COLUMN ══════════════════════════════════════
    y = body_top

    # ── Dashboard screenshot ──────────────────────────────────────────────────
    # Increased height to 90mm to match the viewport's aspect ratio (1.6) without squeezing
    sh = 90*mm
    card(cv, rx, y, COL, sh)
    sec(cv, rx+4*mm, y-5*mm, COL-8*mm, 'Live Dashboard (Screenshot)')
    cv.drawImage('Stuff/map_screenshot.png',
                 rx+4*mm, y-sh+4*mm, width=COL-8*mm, height=sh-11*mm,
                 preserveAspectRatio=True, mask='auto')
    cv.setFont('Helvetica-Oblique',5.5)
    cv.setFillColor(LIGHT_T)
    cv.drawCentredString(rx+COL/2, y-sh+1.8*mm,
        'Fig 1: Real-time bus positions on Bengaluru ORR — Agentic AI Active, 5 buses live')
    y -= sh + 2.5*mm

    # ── KPI row ───────────────────────────────────────────────────────────────
    sh = 20*mm
    card(cv, rx, y, COL, sh)
    kpis = [('+100.4%','Net Efficiency Gain',KPI1_BG,WHITE),
            ('97.3%',  'Wait Cost Saved',    KPI2_BG,WHITE),
            ('0.22',   'Gini Equity Index',  KPI3_BG,WHITE),
            ('Rs.2,756','Net PPO Profit',    KPI4_BG,WHITE)]
    kw = (COL-8*mm)/4
    for i,(big,sub,bg_,tc) in enumerate(kpis):
        kpi_box(cv, rx+4*mm+i*kw+1, y-sh+2, kw-2, sh-4, big, sub, bg_, tc)
    y -= sh + 2.5*mm

    # ── Results & Discussion ──────────────────────────────────────────────────
    sh = 47*mm
    card(cv, rx, y, COL, sh)
    sec(cv, rx+4*mm, y-5*mm, COL-8*mm, 'Results & Discussion')
    hw = (COL-10*mm)*0.63
    ac = (COL-10*mm)*0.35
    ih = sh-11*mm
    cv.drawImage('Stuff/chart_headway_light.png',
                 rx+4*mm, y-sh+3*mm, width=hw, height=ih,
                 preserveAspectRatio=True, mask='auto')
    cv.drawImage('Stuff/chart_actions_light.png',
                 rx+4*mm+hw+2*mm, y-sh+3*mm, width=ac, height=ih,
                 preserveAspectRatio=True, mask='auto')
    y -= sh + 2.5*mm

    # ── Charts row 2 ──────────────────────────────────────────────────────────
    sh = 44*mm
    card(cv, rx, y, COL, sh)
    hw2 = (COL-10*mm)/2
    ih2 = sh-4*mm
    cv.drawImage('Stuff/chart_waitcost_light.png',
                 rx+4*mm, y-sh+2*mm, width=hw2, height=ih2,
                 preserveAspectRatio=True, mask='auto')
    cv.drawImage('Stuff/chart_economic_light.png',
                 rx+4*mm+hw2+2*mm, y-sh+2*mm, width=hw2, height=ih2,
                 preserveAspectRatio=True, mask='auto')
    y -= sh + 2.5*mm

    # ── Results table ─────────────────────────────────────────────────────────
    # Dynamically scale card height to fill down to body_bot (75mm)
    sh = y - body_bot - 2.5*mm
    card(cv, rx, y, COL, sh)
    sec(cv, rx+4*mm, y-5*mm, COL-8*mm, 'Key Numerical Results')

    data = [
        ['Metric','Static Timetable','Agentic PPO'],
        ['Net Economic Value','-Rs.7,10,981','+Rs.2,756'],
        ['Passenger Wait Cost','Rs.7,33,858','Rs.20,119 (-97.3%)'],
        ['Fleet Fuel Cost','Rs.372.78','Rs.374.85 (+0.55%)'],
        ['Ticket Revenue','Rs.23,250','Rs.23,250'],
        ['Gini Equity Index','1.16 (Unfair)','0.22 (Fair)'],
        ['Net Efficiency Gain','Baseline','+100.4%'],
    ]
    cws = [(COL-8*mm)*0.42, (COL-8*mm)*0.29, (COL-8*mm)*0.29]
    tbl = Table(data, colWidths=cws)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,0),  TBL_HDR),
        ('TEXTCOLOR',  (0,0),(-1,0),  colors.white),
        ('FONTNAME',   (0,0),(-1,0),  'Helvetica-Bold'),
        ('FONTNAME',   (0,1),(-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0),(-1,-1), 6.5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[TBL_ROW1, TBL_ROW2]),
        ('BACKGROUND', (2,1),(2,-1),  TBL_GRN),
        ('TEXTCOLOR',  (0,1),(1,-1),  DARK),
        ('TEXTCOLOR',  (2,1),(2,-1),  TBL_GRN_T),
        ('FONTNAME',   (2,1),(2,-1),  'Helvetica-Bold'),
        ('ALIGN',      (1,0),(-1,-1), 'CENTER'),
        ('ALIGN',      (0,0),(0,-1),  'LEFT'),
        ('LEFTPADDING', (0,0),(-1,-1), 4),
        ('RIGHTPADDING',(0,0),(-1,-1), 4),
        ('TOPPADDING',  (0,0),(-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('GRID',        (0,0),(-1,-1), 0.4, CARDBRD),
    ]))
    tw2,th2 = tbl.wrapOn(cv, COL-8*mm, sh)
    tbl.drawOn(cv, rx+4*mm, y-sh+sh-th2-7*mm)

    # ══════════════════════ BOTTOM 3-COL ══════════════════════════════════════
    # Positioned at [17mm, 69mm] to fit perfectly below the body columns (ending at 75mm)
    bot_y = 17*mm
    bot_h = 52*mm
    nc = 3
    cw3 = (W-2*M-(nc-1)*GAP)/nc
    sections = [
        ('Conclusions',
         ("ECO-SYNC Transit AI demonstrates that framing urban bus dispatch as an &lt;b&gt;economic "
          "optimisation problem&lt;/b&gt; leads to dramatically superior outcomes. The PPO agent "
          "learned to HOLD and SKIP stops strategically, delivering a &lt;b&gt;Rs.7,13,739 reduction&lt;/b&gt; "
          "in passenger wait costs and a &lt;b&gt;100.4% net efficiency gain&lt;/b&gt; over the static "
          "baseline. Groq Llama-3.1 provides fully explainable, rider-facing justifications for "
          "every decision. The Gini equity index fell from 1.16 to 0.22, confirming uniform, "
          "fair service across all 30 ORR stops.")),
        ('Outcome of the Work',
         ("A fully functional &lt;b&gt;Transit AI prototype&lt;/b&gt;: (1) Custom Gymnasium environment "
          "with 30-stop Bengaluru ORR, Poisson arrivals, stochastic delays; (2) Trained PPO "
          "agent achieving headway stability across 250 Monte Carlo episodes; (3) FastAPI "
          "WebSocket backend at 1Hz; (4) React.js dashboard with Leaflet maps, live economics "
          "charts, and LLM-generated explanations; (5) Research manuscript targeting "
          "&lt;b&gt;IEEE Trans. on Intelligent Transportation Systems&lt;/b&gt;.")),
        ('References',
         ("[1] Newell &amp; Potts (1964). Maintaining a bus schedule. ARRB.&lt;br/&gt;"
          "[2] Daganzo (2009). Headway control. Transportation Research Part B.&lt;br/&gt;"
          "[3] Schulman et al. (2017). Proximal Policy Optimization. arXiv:1707.06347.&lt;br/&gt;"
          "[4] Rafferty (2018). Valuing commuter time. JPT Vol. 21.&lt;br/&gt;"
          "[5] Boeing (2017). OSMnx: Street networks. CEUS Vol. 65.&lt;br/&gt;"
          "[6] Raffles &amp; Shan (2021). WebSocket for smart cities. IoT&amp;SS Vol. 12.")),
    ]
    for i,(title,body) in enumerate(sections):
        bx = M + i*(cw3+GAP)
        cv.setFillColor(CARD)
        cv.setStrokeColor(CARDBRD)
        cv.setLineWidth(0.5)
        cv.roundRect(bx, bot_y, cw3, bot_h, 2.5*mm, fill=1, stroke=1)
        sec(cv, bx+4*mm, bot_y+bot_h-5*mm, cw3-8*mm, title)
        sty_ = S_BODY if i<2 else S_REF
        fr(cv,[Paragraph(body, sty_)], bx+4*mm, bot_y+3*mm, cw3-8*mm, bot_h-12*mm)

    # ── Footer ────────────────────────────────────────────────────────────────
    # Positioned at [3.5mm, 15mm], completely clear of bottom cards
    cv.setFont('Helvetica-Bold',8.5)
    cv.setFillColor(ORANGE)
    cv.drawCentredString(W/2, 10.5*mm, 'Mentor')
    
    cv.setFont('Helvetica', 7.5)
    cv.setFillColor(DARK)
    cv.drawCentredString(W/2, 7*mm, 'Dr. Sunil S, Department of Civil Engineering, RVCE')
    
    cv.setFillColor(ORANGE)
    cv.rect(M, 3.5*mm, W-2*M, 1.8, fill=1, stroke=0)

    cv.save()
    print(f"Poster successfully saved to {out_pdf}")

if __name__ == "__main__":
    draw_poster()
