# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Eletropostos Dashboard",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = ["#00C9A7","#0088FE","#FF6B6B","#FFD93D","#A855F7","#F97316","#06B6D4","#84CC16"]
DARK_BG = "#0D0F14"; CARD_BG = "#13161D"; CARD_BORDER = "#1E2330"
TEXT_PRIMARY = "#F0F2F8"; TEXT_MUTED = "#6B7280"; ACCENT = "#00C9A7"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="monospace", color=TEXT_PRIMARY, size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10),
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)

CSS = """
<style>
html, body { background-color: #0D0F14; color: #F0F2F8; }
#MainMenu, footer, header { display: none !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1600px; }
[data-testid="stSidebar"] { background-color: #0A0C10 !important; border-right: 1px solid #1E2330; }
.kpi-card { background:#13161D; border:1px solid #1E2330; border-radius:12px; padding:1.1rem 1.25rem; height:100%; position:relative; overflow:hidden; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:var(--accent,#00C9A7); border-radius:3px 0 0 3px; }
.kpi-label { font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; color:#6B7280; margin-bottom:0.3rem; }
.kpi-value { font-size:1.6rem; font-weight:500; color:#F0F2F8; line-height:1.1; }
.kpi-sub { font-size:0.65rem; color:#6B7280; margin-top:0.2rem; }
.section-hdr { font-size:0.7rem; letter-spacing:0.18em; text-transform:uppercase; color:#6B7280; padding-bottom:0.5rem; border-bottom:1px solid #1E2330; margin-bottom:1rem; margin-top:1.5rem; }
.alert-risk { background:rgba(255,107,107,0.08); border:1px solid rgba(255,107,107,0.25); border-radius:8px; padding:0.75rem 1rem; font-size:0.72rem; color:#FF6B6B; margin-bottom:1rem; }
.insight-card { background:#13161D; border:1px solid #1E2330; border-radius:10px; padding:0.9rem 1rem; font-size:0.72rem; line-height:1.6; height:100%; }
.insight-title { font-size:0.78rem; font-weight:700; color:#F0F2F8; margin-bottom:0.35rem; }
.page-title { font-size:2rem; font-weight:800; letter-spacing:-0.02em; line-height:1; }
.page-subtitle { font-size:0.72rem; color:#6B7280; margin-top:0.3rem; }
hr { border-color:#1E2330 !important; }
[data-testid="stDataFrame"] { border:1px solid #1E2330; border-radius:8px; }
#sf-toggle { position:fixed; top:14px; left:14px; z-index:999999; width:36px; height:36px; background:#13161D; border:1px solid #00C9A7; border-radius:8px; color:#00C9A7; font-size:20px; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 16px rgba(0,201,167,0.2); }
#sf-toggle:hover { background:#1E2330; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Injeta o botão de toggle diretamente no documento pai via components.html
# St.markdown roda dentro de um iframe e não consegue acessar a sidebar do pai
components.html("""
<script>
(function() {
    // Este script roda no iframe do Streamlit mas injeta o botão no documento PAI
    function inject() {
        var parentDoc = window.parent.document;

        // Evita duplicar o botão
        if (parentDoc.getElementById('sf-toggle')) return;

        // Cria e estiliza o botão no documento pai
        var btn = parentDoc.createElement('button');
        btn.id = 'sf-toggle';
        btn.innerHTML = '&#9776;';
        btn.title = 'Abrir/Fechar menu lateral';
        btn.style.cssText = [
            'position:fixed', 'top:14px', 'left:14px', 'z-index:999999',
            'width:36px', 'height:36px', 'background:#13161D',
            'border:1px solid #00C9A7', 'border-radius:8px',
            'color:#00C9A7', 'font-size:20px', 'cursor:pointer',
            'display:flex', 'align-items:center', 'justify-content:center',
            'box-shadow:0 2px 16px rgba(0,201,167,0.25)',
            'transition:background .15s', 'line-height:1', 'padding:0'
        ].join(';');

        btn.onmouseenter = function() { this.style.background = '#1E2330'; };
        btn.onmouseleave = function() { this.style.background = '#13161D'; };

        btn.onclick = function() {
            // Tenta clicar no botão nativo do Streamlit (todas as versões conhecidas)
            var sels = [
                '[data-testid="stSidebarCollapseButton"] button',
                '[data-testid="collapsedControl"] button',
                'button[aria-label="Close sidebar"]',
                'button[aria-label="Open sidebar"]',
                'button[aria-label="collapse sidebar"]',
                'button[aria-label="expand sidebar"]',
                '[data-testid="stSidebar"] > div > button',
            ];
            for (var i = 0; i < sels.length; i++) {
                var el = parentDoc.querySelector(sels[i]);
                if (el) { el.click(); updateBtn(); return; }
            }
            // Fallback: mostra/esconde a sidebar diretamente via CSS
            var sb = parentDoc.querySelector('[data-testid="stSidebar"]');
            if (sb) {
                var hidden = sb.style.display === 'none' || sb.offsetWidth < 30;
                sb.style.setProperty('display', hidden ? 'flex' : 'none', 'important');
                updateBtn();
            }
        };

        parentDoc.body.appendChild(btn);
        updateBtn();

        // Observa mudanças na sidebar para atualizar a opacidade do botão
        var sb = parentDoc.querySelector('[data-testid="stSidebar"]');
        if (sb) {
            var obs = new MutationObserver(updateBtn);
            obs.observe(sb, { attributes: true, attributeFilter: ['style', 'class'] });
        }
        // Também observa o body para pegar quando o Streamlit re-renderiza
        var bodyObs = new MutationObserver(function(muts) {
            // Re-verifica se o botão ainda existe no DOM
            if (!parentDoc.getElementById('sf-toggle')) inject();
            updateBtn();
        });
        bodyObs.observe(parentDoc.body, { childList: true, subtree: false });
    }

    function updateBtn() {
        var parentDoc = window.parent.document;
        var btn = parentDoc.getElementById('sf-toggle');
        if (!btn) return;
        var sb = parentDoc.querySelector('[data-testid="stSidebar"]');
        if (sb) {
            var collapsed = sb.offsetWidth < 50 || sb.style.display === 'none';
            btn.style.opacity = collapsed ? '1' : '0.4';
            btn.title = collapsed ? 'Abrir menu lateral' : 'Fechar menu lateral';
        }
    }

    // Tenta injetar imediatamente e também após o DOM estar pronto
    if (window.parent.document.body) {
        inject();
    } else {
        window.parent.document.addEventListener('DOMContentLoaded', inject);
    }
    // Retry por segurança (Streamlit pode demorar para renderizar)
    setTimeout(inject, 500);
    setTimeout(inject, 1500);
    setTimeout(updateBtn, 2000);
})();
</script>
""", height=0)


# ─── TOPBAR ───────────────────────────────────────────────────────────────────
components.html("""
<script>
(function() {
    var LOGO_URL = 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Logomarca_Intelbras_verde.png';

    function getSidebarWidth() {
        var pdoc = window.parent.document;
        // Tenta encontrar a sidebar do Streamlit pelo seletor padrão
        var sidebar = pdoc.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            var rect = sidebar.getBoundingClientRect();
            if (rect.width > 10) return rect.width;
        }
        return 0;
    }

    function buildTopbar() {
        var pdoc = window.parent.document;
        if (pdoc.getElementById('ib-topbar')) return;

        var style = pdoc.createElement('style');
        style.id = 'ib-topbar-style';
        style.textContent = [
            '#ib-topbar{position:fixed;top:0;left:0;right:0;z-index:99998;height:54px;',
            'background:#0A0C10;border-bottom:1px solid #1E2330;',
            'display:flex;align-items:center;padding:0 24px;font-family:monospace;}',
            '#ib-topbar-logo{height:39px;width:auto;object-fit:contain;margin-left:auto;}',
            '.block-container{padding-top:4.8rem !important;}'
        ].join('');
        pdoc.head.appendChild(style);

        var bar = pdoc.createElement('div');
        bar.id = 'ib-topbar';

        // ── Logo ──
        var logo = pdoc.createElement('img');
        logo.id = 'ib-topbar-logo'; logo.src = LOGO_URL; logo.alt = 'Intelbras';

        bar.appendChild(logo);
        pdoc.body.prepend(bar);

        adjustPadding();
        window.parent.addEventListener('resize', adjustPadding);
    }

    function adjustPadding() {
        var pdoc = window.parent.document;
        var bar = pdoc.getElementById('ib-topbar');
        if (!bar) return;
        var sw = getSidebarWidth();
        // Empurra o início da topbar para depois da sidebar
        bar.style.paddingLeft = (sw + 16) + 'px';
    }

    buildTopbar();
    setTimeout(adjustPadding, 800);

    var obs = new MutationObserver(function() {
        if (!window.parent.document.getElementById('ib-topbar')) buildTopbar();
        adjustPadding();
    });
    try { obs.observe(window.parent.document.body, { childList: true }); } catch(e) {}
})();
</script>
""", height=0)


def parse_start_date(s):
    if pd.isna(s): return pd.NaT
    s = str(s).strip()
    if ' - ' in s: s = s.split(' - ')[0].strip()
    for fmt in ('%d/%m/%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try: return pd.to_datetime(s, format=fmt)
        except: pass
    try: return pd.to_datetime(s, dayfirst=True)
    except: return pd.NaT

def parse_duration(d):
    if pd.isna(d): return 0
    parts = str(d).strip().split(':')
    try:
        if len(parts) == 3: return int(parts[0])*60 + int(parts[1]) + int(parts[2])/60
    except: return 0
    return 0

@st.cache_data(show_spinner=False)
def load_file(file_bytes, file_name):
    df = pd.read_excel(io.BytesIO(file_bytes))
    df['_source_file'] = file_name
    return df

def process_df(df):
    df = df.copy()
    df['data_inicio'] = df['Inicio - Fim'].apply(parse_start_date) if 'Inicio - Fim' in df.columns else df['Início - Fim'].apply(parse_start_date)
    df['data']        = df['data_inicio'].dt.date
    df['hora']        = df['data_inicio'].dt.hour
    df['dia_num']     = df['data_inicio'].dt.dayofweek
    df['semana']      = df['data_inicio'].dt.isocalendar().week
    df['duracao_min'] = df['Duração'].apply(parse_duration) if 'Duração' in df.columns else df.get('Duracao', pd.Series(0, index=df.index)).apply(parse_duration)
    df['is_weekend']  = df['dia_num'].isin([5, 6])
    df['dur_seg']     = pd.cut(df['duracao_min'], bins=[0,30,60,120,240,1e9],
                               labels=['<30min','30-60min','1-2h','2-4h','4h+'])
    for col in ['Receita(R$)', 'Energia(kWh)', 'Valor Ociosidade']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    df['paid']    = df['Pago?'] == 'sim'
    df['pending'] = df.get('Pagamento(Status)', pd.Series('', index=df.index)) == 'pending'
    return df

def compute_kpis(df):
    paid = df[df['paid']]
    energy = df[df['Energia(kWh)'] > 0]
    paid_e = paid[paid['Energia(kWh)'] > 0]
    attempts = df['Pago?'].isin(['sim','nao']).sum()
    days = df['data'].nunique() or 1
    total_rev = paid['Receita(R$)'].sum()
    pending_rev = df[df['pending']]['Receita(R$)'].sum()
    tag_col = 'Usuário(Tag)' if 'Usuário(Tag)' in df.columns else 'Usuário (ID)'
    user_counts = df.groupby(tag_col).size()
    kwh_total = energy['Energia(kWh)'].sum()
    rev_per_kwh = (paid_e['Receita(R$)'].sum() / paid_e['Energia(kWh)'].sum()
                   if paid_e['Energia(kWh)'].sum() > 0 else 0)
    power_rev = df[df[tag_col].isin(user_counts[user_counts>=5].index)]['Receita(R$)'].sum()
    return dict(
        total_sessions=len(df), paid_sessions=len(paid), revenue=total_rev,
        pending_rev=pending_rev, energy_kwh=kwh_total,
        avg_kwh=energy['Energia(kWh)'].mean() if len(energy) else 0,
        avg_ticket=paid['Receita(R$)'].mean() if len(paid) else 0,
        rev_per_kwh=rev_per_kwh, rev_per_day=total_rev/days,
        kwh_per_day=kwh_total/days,
        sessions_per_day=len(df)/days, days=days,
        conversion=len(paid)/attempts*100 if attempts else 0,
        approval=len(paid)/len(df)*100,
        rejection_rate=(df['Pago?'].eq('nao').sum()/max(attempts,1))*100,
        unique_users=user_counts.shape[0],
        one_time=(user_counts==1).sum(),
        power_users=(user_counts>=5).sum(),
        power_rev_pct=power_rev/total_rev*100 if total_rev else 0,
        idle_fee=df['Valor Ociosidade'].sum(),
        idle_sessions=(df['Valor Ociosidade']>0).sum(),
        proj_annual=total_rev/days*365,
        not_paid=df['Pago?'].eq('nao').sum(),
        tag_col=tag_col,
    )

# ─── CHARTS ───────────────────────────────────────────────────────────────────
def apply_axes(fig, xkw=None, ykw=None, show_legend=True):
    fig.update_layout(showlegend=show_legend)
    fig.update_xaxes(gridcolor="#1E2330", linecolor="#1E2330", tickfont=dict(size=10), **(xkw or {}))
    fig.update_yaxes(gridcolor="#1E2330", linecolor="#1E2330", tickfont=dict(size=10), **(ykw or {}))

def fig_daily(dfs):
    fig = go.Figure()
    for i, (name, sdf) in enumerate(dfs.items()):
        daily = (sdf[sdf['paid']]
                 .groupby('data')['Receita(R$)'].sum()
                 .reset_index()
                 .sort_values('data'))
        daily['data'] = pd.to_datetime(daily['data'])
        c = COLORS[i % len(COLORS)]
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        fig.add_trace(go.Scatter(
            x=daily['data'], y=daily['Receita(R$)'],
            name=name, mode='lines',
            line=dict(color=c, width=2),
            fill='tozeroy',
            fillcolor=f'rgba({r},{g},{b},0.07)',
        ))
    single = len(dfs) == 1
    fig.update_layout(**PLOTLY_LAYOUT, height=300)
    fig.update_layout(showlegend=not single)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330', tickformat='%d/%m/%Y')
    fig.update_yaxes(tickprefix='R$ ', tickformat=',.0f',
                     gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def fig_hourly(dfs):
    fig = go.Figure()
    for i, (name, sdf) in enumerate(dfs.items()):
        hourly = sdf[sdf['Energia(kWh)']>0].groupby('hora').size().reindex(range(24), fill_value=0)
        fig.add_trace(go.Bar(x=list(range(24)), y=hourly.values, name=name,
                             marker_color=COLORS[i%len(COLORS)], opacity=0.85))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', height=280)
    apply_axes(fig, xkw=dict(tickmode='linear', tick0=0, dtick=2, ticksuffix='h'))
    return fig

def fig_funnel(kpis):
    vals = [kpis['total_sessions'], kpis['paid_sessions']+kpis['not_paid'], kpis['paid_sessions']]
    labels = ['Total de sessões', 'Tentativa de pagamento', 'Pagas (aprovadas)']
    fig = go.Figure(go.Funnel(y=labels, x=vals, textinfo='value+percent previous',
        marker_color=[ACCENT, COLORS[1], COLORS[2]],
        connector=dict(line=dict(color=CARD_BORDER, width=1))))
    fig.update_layout(**PLOTLY_LAYOUT, height=220)
    fig.update_layout(showlegend=False)
    return fig

def fig_payment(df, color):
    paid = df[df['paid']]
    if 'Pagamento(Tipo)' not in paid.columns or len(paid) == 0:
        return go.Figure()
    counts = paid['Pagamento(Tipo)'].value_counts()
    labels = [l.replace('PAGBANK_CARD','PagBank').replace('WALLET','Wallet')
               .replace('VOUCHER','Voucher').replace('MANUAL','Manual') for l in counts.index]
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    pie_colors = [color, f'rgba({r},{g},{b},0.5)', '#2D3340','#3D4560','#4D5575']
    fig = go.Figure(go.Pie(labels=labels, values=counts.values, hole=0.62,
        marker=dict(colors=pie_colors[:len(labels)], line=dict(color=DARK_BG, width=2)),
        textinfo='percent', textfont_size=9))
    fig.update_layout(**PLOTLY_LAYOUT, height=240)
    fig.update_layout(showlegend=True,
        legend=dict(font=dict(size=9), orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.05))
    return fig

def fig_connectors(df):
    if 'Conector(Tipo)' not in df.columns: return go.Figure()
    conn = df.groupby('Conector(Tipo)').agg(sessions=('Receita(R$)','count'), revenue=('Receita(R$)','sum')).reset_index()
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Sessões','Receita (R$)'], horizontal_spacing=0.12)
    fig.add_trace(go.Bar(y=conn['Conector(Tipo)'], x=conn['sessions'], orientation='h',
                         marker_color=ACCENT, showlegend=False), row=1, col=1)
    fig.add_trace(go.Bar(y=conn['Conector(Tipo)'], x=conn['revenue'], orientation='h',
                         marker_color=COLORS[1], showlegend=False), row=1, col=2)
    fig.update_layout(**PLOTLY_LAYOUT, height=200)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(gridcolor=None, linecolor=None)
    return fig

def fig_duration(df, color):
    dur = df.groupby('dur_seg', observed=True).agg(
        count=('Receita(R$)','count'), avg_kwh=('Energia(kWh)','mean'), avg_rev=('Receita(R$)','mean')).reset_index()
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=dur['dur_seg'], y=dur['count'], name='Sessões',
                         marker_color=color, opacity=0.8), secondary_y=False)
    fig.add_trace(go.Scatter(x=dur['dur_seg'], y=dur['avg_rev'], name='Ticket Medio (R$)',
                             mode='lines+markers', line=dict(color=COLORS[2], width=2),
                             marker=dict(size=6)), secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT, height=270)
    fig.update_layout(showlegend=True)
    fig.update_yaxes(gridcolor='#1E2330', secondary_y=False)
    fig.update_yaxes(tickprefix='R$', gridcolor=None, secondary_y=True)
    return fig

def fig_weekly(df, color):
    weekly = df.groupby('semana').agg(revenue=('Receita(R$)','sum'), sessions=('Receita(R$)','count')).reset_index()
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=weekly['semana'].astype(str), y=weekly['revenue'],
                         name='Receita', marker_color=color, opacity=0.85), secondary_y=False)
    fig.add_trace(go.Scatter(x=weekly['semana'].astype(str), y=weekly['sessions'],
                             name='Sessões', mode='lines+markers',
                             line=dict(color=COLORS[2], width=2), marker=dict(size=6)), secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT, height=260)
    fig.update_layout(showlegend=True)
    fig.update_yaxes(tickprefix='R$', gridcolor='#1E2330', secondary_y=False)
    fig.update_yaxes(gridcolor=None, secondary_y=True)
    return fig

def fig_users(df, color, tag_col):
    uc = df.groupby(tag_col).agg(sessions=('Receita(R$)','count'), revenue=('Receita(R$)','sum'))
    segs = pd.cut(uc['sessions'], bins=[0,1,4,9,1e9], labels=['1 sessao','2-4','5-9','10+'])
    seg_cnt = uc.groupby(segs, observed=True).size()
    seg_rev = uc.groupby(segs, observed=True)['revenue'].sum()
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    alphas = [0.3,0.5,0.75,1.0]
    seg_colors = [f'rgba({r},{g},{b},{a})' for a in alphas]
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Usuários por segmento','Receita por segmento'],
                        horizontal_spacing=0.12)
    fig.add_trace(go.Bar(x=seg_cnt.index.tolist(), y=seg_cnt.values, marker_color=seg_colors, showlegend=False), row=1, col=1)
    fig.add_trace(go.Bar(x=seg_rev.index.tolist(), y=seg_rev.values, marker_color=seg_colors, showlegend=False), row=1, col=2)
    fig.update_layout(**PLOTLY_LAYOUT, height=240)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330', tickfont=dict(size=9))
    fig.update_yaxes(gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def fig_top_stations(df, top_n=15):
    col = 'Estação' if 'Estação' in df.columns else 'Estacao'
    if col not in df.columns: return go.Figure()
    paid = df[df['paid']]
    top = paid.groupby(col)['Receita(R$)'].sum().sort_values(ascending=True).tail(top_n)
    fig = go.Figure(go.Bar(
        y=top.index, x=top.values, orientation='h',
        marker=dict(color=top.values, colorscale=[[0,'#1E2330'],[1,ACCENT]], showscale=False)))
    fig.update_layout(**PLOTLY_LAYOUT, height=max(250, top_n*28))
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickprefix='R$ ', tickformat=',.0f', gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(tickfont=dict(size=9), gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def fig_top_stations_by_sessions(df, top_n=15):
    col = 'Estação' if 'Estação' in df.columns else 'Estacao'
    if col not in df.columns: return go.Figure()
    days = df['data'].nunique() or 1
    top = (df.groupby(col)
             .agg(sessions=('Receita(R$)','count'))
             .assign(sess_day=lambda x: x['sessions']/days)
             .sort_values('sess_day', ascending=True)
             .tail(top_n))
    fig = go.Figure(go.Bar(
        y=top.index, x=top['sess_day'], orientation='h',
        marker=dict(color=top['sess_day'], colorscale=[[0,'#1E2330'],[1,COLORS[1]]], showscale=False)))
    fig.update_layout(**PLOTLY_LAYOUT, height=max(250, top_n*28))
    fig.update_layout(showlegend=False)
    fig.update_xaxes(ticksuffix=' sess/dia', gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(tickfont=dict(size=9), gridcolor='#1E2330', linecolor='#1E2330')
    return fig



DIAS_SEMANA = ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo']

def fig_weekday_revenue(df, color):
    df2 = df[df['paid']].copy()
    df2['dow'] = df2['data_inicio'].dt.dayofweek
    rev = df2.groupby('dow')['Receita(R$)'].sum().reindex(range(7), fill_value=0)
    fig = go.Figure(go.Bar(
        x=DIAS_SEMANA, y=rev.values,
        marker=dict(color=rev.values, colorscale=[[0,'#1E2330'],[0.5,color],[1,'#0088FE']], showscale=False),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=280)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(tickprefix='R$ ', tickformat=',.0f', gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def fig_weekday_sessions(df, color):
    df2 = df.copy()
    df2['dow'] = df2['data_inicio'].dt.dayofweek
    sess = df2.groupby('dow').size().reindex(range(7), fill_value=0)
    paid = df2[df2['paid']].groupby('dow').size().reindex(range(7), fill_value=0)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=DIAS_SEMANA, y=sess.values, name='Total', marker_color=color, opacity=0.5))
    fig.add_trace(go.Bar(x=DIAS_SEMANA, y=paid.values, name='Pagas', marker_color='#0088FE', opacity=0.9))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='overlay', height=280)
    fig.update_layout(showlegend=True)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def fig_occupancy(df, top_n=15, horas_dia=24):
    col_est = 'Estacao' if 'Estacao' in df.columns else 'Estacao'
    for c in ['Estação', 'Estacao']:
        if c in df.columns:
            col_est = c
            break
    else:
        return go.Figure()
    days = df['data'].nunique() or 1
    minutos_disponiveis = days * horas_dia * 60
    occ = (df.groupby(col_est)
             .agg(sessions=('Receita(R$)','count'), total_min=('duracao_min','sum'))
             .assign(occupancy_pct=lambda x: (x['total_min'] / minutos_disponiveis * 100).clip(0, 100))
             .sort_values('occupancy_pct', ascending=True)
             .tail(top_n))
    bar_colors = ['#00C9A7' if v >= 80 else '#0088FE' if v >= 50 else '#FF6B6B' for v in occ['occupancy_pct']]
    fig = go.Figure(go.Bar(
        y=occ.index, x=occ['occupancy_pct'], orientation='h',
        marker_color=bar_colors,
        text=[f"{v:.1f}%" for v in occ['occupancy_pct']],
        textposition='outside', textfont=dict(size=9),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=max(250, top_n*28))
    fig.update_layout(showlegend=False,
                      title=dict(text=f'Base: {horas_dia}h/dia disponivel',
                                 font=dict(size=9, color='#6B7280'), x=1, xanchor='right') if horas_dia < 24 else {})
    fig.update_xaxes(ticksuffix='%', range=[0, 115], gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(tickfont=dict(size=9), gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def fig_revenue_cost_profit(df, custo_kwh, custo_pct):
    paid = df[df['paid']].copy()
    daily = paid.groupby('data').agg(
        receita=('Receita(R$)','sum'),
        kwh=('Energia(kWh)','sum'),
    ).reset_index().sort_values('data')
    daily['data'] = pd.to_datetime(daily['data'])
    daily['custo'] = daily['receita'] * (custo_pct/100) + daily['kwh'] * custo_kwh
    daily['lucro'] = daily['receita'] - daily['custo']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily['data'], y=daily['receita'], name='Receita',
        mode='lines', line=dict(color='#00C9A7', width=2),
        fill='tozeroy', fillcolor='rgba(0,201,167,0.07)'))
    fig.add_trace(go.Scatter(x=daily['data'], y=daily['custo'], name='Custo',
        mode='lines', line=dict(color='#FF6B6B', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=daily['data'], y=daily['lucro'], name='Lucro',
        mode='lines', line=dict(color='#0088FE', width=2),
        fill='tozeroy', fillcolor='rgba(0,136,254,0.07)'))
    fig.update_layout(**PLOTLY_LAYOUT, height=320)
    fig.update_layout(showlegend=True)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330', tickformat='%d/%m/%Y')
    fig.update_yaxes(tickprefix='R$ ', tickformat=',.0f', gridcolor='#1E2330', linecolor='#1E2330')
    return fig, daily





def _pl_decode(val):
    """Converte qualquer valor Plotly (ndarray, bdata dict, lista, None) → lista Python pura."""
    import numpy as np, base64 as b64
    if val is None: return []
    if isinstance(val, np.ndarray): return val.tolist()
    if isinstance(val, dict) and 'bdata' in val:
        dtype_map = {'f4':'float32','f8':'float64','i2':'int16','i4':'int32','i8':'int64','u1':'uint8'}
        dt = dtype_map.get(val.get('dtype','f8'), 'float64')
        try:
            raw = b64.b64decode(val['bdata'])
            sz  = __import__('numpy').dtype(dt).itemsize
            if len(raw) % sz != 0:
                for fb in ['float32','int16','uint8']:
                    if len(raw) % __import__('numpy').dtype(fb).itemsize == 0:
                        return __import__('numpy').frombuffer(raw, dtype=fb).tolist()
                return []
            return __import__('numpy').frombuffer(raw, dtype=dt).tolist()
        except Exception: return []
    if isinstance(val, (list, tuple)):
        out = []
        for v in val:
            if isinstance(v, (__import__('numpy').ndarray, dict)) and not isinstance(v, bool):
                out.extend(_pl_decode(v))
            else: out.append(v)
        return out
    if hasattr(val, '__iter__') and not isinstance(val, (str, bytes)): return list(val)
    return [val]

def _pl_floats(val):
    res = []
    for v in _pl_decode(val):
        try: res.append(float(v))
        except: res.append(0.0)
    return res

def _pl_strs(val):
    import datetime
    res = []
    for v in _pl_decode(val):
        if isinstance(v, (datetime.datetime, datetime.date)): res.append(v.strftime('%d/%m'))
        elif v is None: res.append('')
        else: res.append(str(v)[:16])
    return res

def _pl_color(mc, default='#888888'):
    import numpy as np
    if mc is None or isinstance(mc, (np.ndarray, bool, dict)): return default
    if isinstance(mc, str):
        if mc.startswith('#'): return mc
        if mc.startswith(('rgba','rgb')):
            try:
                inner = mc[mc.index('(')+1:mc.rindex(')')]
                p = inner.split(',')
                return f'#{int(float(p[0])):02x}{int(float(p[1])):02x}{int(float(p[2])):02x}'
            except: return default
        return default
    if isinstance(mc, (list, tuple)) and mc:
        return _pl_color(mc[0], default)
    return default

def _fig_to_img(fig, w=1100, h=420):
    """Converte figura Plotly → PNG via kaleido (requer Chrome instalado)."""
    import json as _json
    import plotly.graph_objects as _go
    fig_dict = _json.loads(fig.to_json())
    fig2 = _go.Figure(fig_dict)
    fig2.update_layout(
        paper_bgcolor='white', plot_bgcolor='#F8F9FA',
        font=dict(color='#1A1A18', size=12, family='Arial'),
        margin=dict(l=80, r=40, t=50, b=70),
    )
    fig2.update_xaxes(gridcolor='#E5E5E5', linecolor='#CCC', tickfont=dict(color='#333', size=11))
    fig2.update_yaxes(gridcolor='#E5E5E5', linecolor='#CCC', tickfont=dict(color='#333', size=11))
    return fig2.to_image(format='png', width=w, height=h, scale=4)



def generate_pdf(df, kpis, custo_kwh, custo_pct, dfs, color, title="Relatorio", horas_dia=24):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable,
                                         Image as RLImage, PageBreak, KeepTogether)
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        import datetime

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=1.8*cm, rightMargin=1.8*cm,
                                topMargin=2*cm, bottomMargin=1.8*cm)

        # ── Colours ──────────────────────────────────────────────────────────
        C_GREEN  = rl_colors.HexColor('#00C9A7')
        C_BLUE   = rl_colors.HexColor('#185FA5')
        C_GREY   = rl_colors.HexColor('#6B7280')
        C_BLACK  = rl_colors.HexColor('#1A1A18')
        C_BG     = rl_colors.HexColor('#F4F3F0')
        C_WHITE  = rl_colors.white
        C_BORD   = rl_colors.HexColor('#E0DFD9')
        C_HDR    = rl_colors.HexColor('#E5E4E0')
        W = 17.4*cm

        def S(size=9, bold=False, color=C_BLACK, align=TA_LEFT):
            return ParagraphStyle('s', fontSize=size, textColor=color,
                                  fontName='Helvetica-Bold' if bold else 'Helvetica',
                                  alignment=align, leading=size*1.45, spaceAfter=0)

        def section_hdr(text):
            return [
                Spacer(1, 10),
                Paragraph(text, S(7, bold=True, color=C_GREY)),
                HRFlowable(width=W, thickness=0.5, color=C_BORD, spaceAfter=4),
            ]

        def kv_table(rows, col_widths=None):
            """Tabela chave-valor 4 colunas."""
            cw = col_widths or [4.5*cm, 4*cm, 4.5*cm, 4*cm]
            data = [[Paragraph(c, S(8, bold=(j%2==0), color=C_GREY if j%2==0 else C_BLACK))
                     for j,c in enumerate(row)] for row in rows]
            t = Table(data, colWidths=cw)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,-1),C_BG),
                ('GRID',(0,0),(-1,-1),0.3,C_BORD),
                ('TOPPADDING',(0,0),(-1,-1),5),
                ('BOTTOMPADDING',(0,0),(-1,-1),5),
                ('LEFTPADDING',(0,0),(-1,-1),7),
                ('RIGHTPADDING',(0,0),(-1,-1),7),
                ('ROWBACKGROUNDS',(0,0),(-1,-1),[C_BG, C_WHITE]),
            ]))
            return t

        def chart(fig, w_cm=17.4, h_cm=6.5):
            """Converte figura para imagem PDF em largura total."""
            # Usa alta resolução para qualidade kaleido
            px_w = int(w_cm * 50)   # ~50px/cm → boa resolução
            px_h = int(h_cm * 50)
            png = _fig_to_img(fig, w=px_w, h=px_h)
            if png is None:
                return Paragraph('[Grafico indisponivel]', S(8, color=C_GREY))
            return RLImage(io.BytesIO(png), width=w_cm*cm, height=h_cm*cm)

        story = []

        # ── CAPA ─────────────────────────────────────────────────────────────
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph('RELATORIO FINANCEIRO', S(8, bold=True, color=C_GREY)))
        story.append(Spacer(1, 4))
        story.append(Paragraph('Eletropostos Dashboard', S(20, bold=True, color=C_BLACK)))
        story.append(Paragraph(title, S(12, bold=True, color=C_BLUE)))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f'Gerado em {datetime.date.today().strftime("%d/%m/%Y")}  |  '
            f'{kpis["days"]} dias de dados  |  '
            f'{kpis["total_sessions"]:,} sessões totais',
            S(8, color=C_GREY)))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width=W, thickness=2, color=C_GREEN))
        story.append(Spacer(1, 12))

        # ── KPIs PRINCIPAIS ───────────────────────────────────────────────────
        story += section_hdr('INDICADORES PRINCIPAIS')
        story.append(kv_table([
            ['Receita Confirmada', f"R$ {kpis['revenue']:,.2f}",
             'Sessões Pagas', f"{kpis['paid_sessions']:,}"],
            ['Energia Consumida', f"{kpis['energy_kwh']:,.1f} kWh",
             'R$/kWh Médio', f"R$ {kpis['rev_per_kwh']:.2f}"],
            ['Ticket Médio', f"R$ {kpis['avg_ticket']:.2f}",
             'Sessões/Dia', f"{kpis['sessions_per_day']:.1f}"],
            ['Receita/Dia', f"R$ {kpis['rev_per_day']:,.0f}",
             'kWh/Dia', f"{kpis['kwh_per_day']:.1f}"],
            ['Conversão', f"{kpis['conversion']:.1f}%",
             'Usuários Únicos', f"{kpis['unique_users']:,}"],
            ['Power Users (5+)', f"{kpis['power_users']}",
             'Receita Power Users', f"{kpis['power_rev_pct']:.1f}%"],
            ['Receita Pendente', f"R$ {kpis['pending_rev']:,.2f}",
             'Idle Fee Total', f"R$ {kpis['idle_fee']:,.2f}"],
            ['Projeção Anual', f"R$ {kpis['proj_annual']:,.0f}",
             'Taxa Reprovação', f"{kpis['rejection_rate']:.1f}%"],
        ]))
        story.append(Spacer(1, 10))

        # ── ANALISE DE CUSTOS ─────────────────────────────────────────────────
        paid_df = df[df['paid']].copy()
        daily_c = paid_df.groupby('data').agg(
            receita=('Receita(R$)','sum'), kwh=('Energia(kWh)','sum')).reset_index()
        daily_c['custo'] = daily_c['receita']*(custo_pct/100) + daily_c['kwh']*custo_kwh
        daily_c['lucro'] = daily_c['receita'] - daily_c['custo']
        total_r = daily_c['receita'].sum()
        total_c = daily_c['custo'].sum()
        total_l = daily_c['lucro'].sum()
        margem  = total_l/total_r*100 if total_r else 0

        story += section_hdr('ANALISE DE CUSTOS')
        story.append(kv_table([
            ['Custo energia (R$/kWh)', f"R$ {custo_kwh:.2f}",
             'Custo operacional (%)', f"{custo_pct:.1f}%"],
            ['Receita total', f"R$ {total_r:,.2f}",
             'Custo total', f"R$ {total_c:,.2f}"],
            ['Lucro total', f"R$ {total_l:,.2f}",
             'Margem liquida', f"{margem:.1f}%"],
        ]))
        story.append(Spacer(1, 8))

        # ── GRAFICOS — cada um em linha própria ───────────────────────────────
        story.append(PageBreak())
        story += section_hdr('RECEITA DIÁRIA')
        story.append(chart(fig_daily(dfs), h_cm=6))
        story.append(Spacer(1, 10))

        story += section_hdr('RECEITA vs CUSTO vs LUCRO')
        fig_rcl, _ = fig_revenue_cost_profit(df, custo_kwh, custo_pct)
        story.append(chart(fig_rcl, h_cm=6))
        story.append(Spacer(1, 10))

        story.append(PageBreak())
        story += section_hdr('DISTRIBUIÇÃO HORÁRIA DE SESSÕES')
        story.append(chart(fig_hourly(dfs), h_cm=6))
        story.append(Spacer(1, 10))

        story += section_hdr('FUNIL DE CONVERSÃO')
        story.append(chart(fig_funnel(kpis), h_cm=5))
        story.append(Spacer(1, 10))

        story.append(PageBreak())
        story += section_hdr('RECEITA POR DIA DA SEMANA')
        story.append(chart(fig_weekday_revenue(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        story += section_hdr('SESSÕES POR DIA DA SEMANA')
        story.append(chart(fig_weekday_sessions(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        story.append(PageBreak())
        story += section_hdr('MEIOS DE PAGAMENTO')
        story.append(chart(fig_payment(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        story += section_hdr('CONECTORES (SESSÕES E RECEITA)')
        story.append(chart(fig_connectors(df), h_cm=5))
        story.append(Spacer(1, 10))

        story.append(PageBreak())
        story += section_hdr('DURAÇÃO DAS SESSÕES COM TICKET MÉDIO')
        story.append(chart(fig_duration(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        story += section_hdr('EVOLUÇÃO SEMANAL (RECEITA E SESSÕES)')
        story.append(chart(fig_weekly(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        # Top estações
        col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
        n_st = min(df[col_est].nunique(), 15) if col_est in df.columns else 0
        if n_st > 0:
            h_st = max(5.5, n_st * 0.48)
            story.append(PageBreak())
            story += section_hdr('TOP 15 ESTAÇÕES POR RECEITA')
            story.append(chart(fig_top_stations(df, top_n=n_st), h_cm=h_st))
            story.append(Spacer(1, 10))

            story += section_hdr('TOP 15 ESTAÇÕES POR SESSÕES/DIA')
            story.append(chart(fig_top_stations_by_sessions(df, top_n=n_st), h_cm=h_st))
            story.append(Spacer(1, 10))

            story.append(PageBreak())
            story += section_hdr('TAXA DE OCUPAÇÃO — TOP 15 CARREGADORES')
            story.append(chart(fig_occupancy(df, top_n=n_st, horas_dia=horas_dia), h_cm=h_st))
            story.append(Spacer(1, 10))

        story += section_hdr('SEGMENTAÇÃO DE USUÁRIOS')
        story.append(chart(fig_users(df, color, kpis['tag_col']), h_cm=5.5))
        story.append(Spacer(1, 10))

        story += section_hdr('RECEITA POR ORIGEM')
        story.append(chart(fig_revenue_sources(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        story += section_hdr('RECEITA POR ORIGEM — EVOLUÇÃO SEMANAL')
        story.append(chart(fig_revenue_sources_bar(df, color), h_cm=5))
        story.append(Spacer(1, 10))

        # ── TABELAS ───────────────────────────────────────────────────────────
        story.append(PageBreak())

        col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
        if col_est in df.columns:
            story += section_hdr('TABELA — TOP 15 ESTACOES POR RECEITA')
            days_n = kpis['days'] or 1
            top = (df[df['paid']].groupby(col_est)
                   .agg(sessoes=('Receita(R$)','count'),
                        receita=('Receita(R$)','sum'),
                        kwh=('Energia(kWh)','sum'))
                   .assign(r_dia=lambda x: x['receita']/days_n)
                   .sort_values('receita', ascending=False).head(15).reset_index())
            hdr = [Paragraph(h, S(7, bold=True, color=C_GREY))
                   for h in ['Estação','Sessões','Receita (R$)','R$/Dia','kWh']]
            trows = [hdr]
            for _, row in top.iterrows():
                trows.append([
                    Paragraph(str(row[col_est])[:38], S(7)),
                    Paragraph(f"{row['sessoes']:,}", S(7)),
                    Paragraph(f"R$ {row['receita']:,.2f}", S(7)),
                    Paragraph(f"R$ {row['r_dia']:,.0f}", S(7)),
                    Paragraph(f"{row['kwh']:,.0f}", S(7)),
                ])
            ts = Table(trows, colWidths=[7*cm,2.2*cm,3*cm,2.3*cm,2.5*cm])
            ts.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),C_HDR),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_BG, C_WHITE]),
                ('GRID',(0,0),(-1,-1),0.3,C_BORD),
                ('TOPPADDING',(0,0),(-1,-1),4),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),
                ('LEFTPADDING',(0,0),(-1,-1),6),
                ('RIGHTPADDING',(0,0),(-1,-1),6),
            ]))
            story.append(ts)
            story.append(Spacer(1, 10))

        # Tabela dia da semana
        story += section_hdr('TABELA — DISTRIBUICAO POR DIA DA SEMANA')
        df2 = df.copy()
        df2['dow'] = df2['data_inicio'].dt.dayofweek
        wd_rev  = df2[df2['paid']].groupby('dow')['Receita(R$)'].sum().reindex(range(7), fill_value=0)
        wd_sess = df2.groupby('dow').size().reindex(range(7), fill_value=0)
        wd_hdr  = [Paragraph(h, S(7, bold=True, color=C_GREY))
                   for h in ['Dia','Sessões','Receita (R$)','Ticket Médio']]
        wd_rows = [wd_hdr]
        for i, dia in enumerate(DIAS_SEMANA):
            s = int(wd_sess.iloc[i]); r = float(wd_rev.iloc[i])
            wd_rows.append([
                Paragraph(dia, S(7)),
                Paragraph(f"{s:,}", S(7)),
                Paragraph(f"R$ {r:,.2f}", S(7)),
                Paragraph(f"R$ {r/s:.2f}" if s else "R$ 0,00", S(7)),
            ])
        tw = Table(wd_rows, colWidths=[4.5*cm,3*cm,5*cm,4.5*cm])
        tw.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),C_HDR),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_BG, C_WHITE]),
            ('GRID',(0,0),(-1,-1),0.3,C_BORD),
            ('TOPPADDING',(0,0),(-1,-1),4),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LEFTPADDING',(0,0),(-1,-1),6),
            ('RIGHTPADDING',(0,0),(-1,-1),6),
        ]))
        story.append(tw)

        # ── RODAPÉ ────────────────────────────────────────────────────────────
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width=W, thickness=0.5, color=C_BORD))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f'Eletropostos Dashboard  |  {datetime.date.today().strftime("%d/%m/%Y")}  |  '
            f'Relatorio gerado automaticamente',
            S(7, color=C_GREY, align=TA_CENTER)
        ))

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    except Exception as e:
        return str(e).encode()


# ─── UI HELPERS ───────────────────────────────────────────────────────────────
def kpi_card(label, value, sub='', accent='#00C9A7'):
    st.markdown(
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

def section(text):
    st.markdown(f'<div class="section-hdr">{text}</div>', unsafe_allow_html=True)

def generate_insights(kpis, df):
    insights = []
    if kpis['pending_rev'] > 0:
        insights.append(('Risco: Pagamentos Pendentes',
            f"R$ {kpis['pending_rev']:,.2f} em status pending. Revisar integração de gateway."))
    if kpis['power_rev_pct'] > 60:
        insights.append(('Concentração em Power Users',
            f"{kpis['power_users']} usuarios (5+ sessões) geram {kpis['power_rev_pct']:.1f}% da receita. "
            f"Programa de fidelidade pode reduzir risco de churn."))
    if kpis['unique_users'] > 0 and kpis['one_time'] / kpis['unique_users'] > 0.5:
        pct = kpis['one_time'] / kpis['unique_users'] * 100
        insights.append(('Alta taxa de usuários one-time',
            f"{kpis['one_time']} ({pct:.0f}%) usuários vieram apenas uma vez. "
            f"Estratégia de ativação após a primeira-sessão pode aumentar retenção."))
    if kpis['idle_fee'] > 0:
        insights.append(('Idle Fee ativo',
            f"R$ {kpis['idle_fee']:,.2f} coletados em {kpis['idle_sessions']} sessões por ociosidade."))
    if kpis['rejection_rate'] > 5:
        insights.append(('Taxa de reprovação elevada',
            f"{kpis['rejection_rate']:.1f}% dos pagamentos foram reprovados ({kpis['not_paid']} sessões). "
            f"Verificar gateway e meios de pagamento disponíveis."))
    daily_rev = df[df['paid']].groupby('data')['Receita(R$)'].sum()
    if len(daily_rev) >= 7:
        first7 = daily_rev.iloc[:7].mean()
        last7  = daily_rev.iloc[-7:].mean()
        if first7 > 0:
            growth = (last7 - first7) / first7 * 100
            if growth > 10:
                insights.append(('Crescimento semanal',
                    f"Receita da ultima semana (R$ {last7:,.0f}/dia) cresceu {growth:.0f}% "
                    f"vs primeira semana (R$ {first7:,.0f}/dia)."))
            elif growth < -10:
                insights.append(('Queda na última semana',
                    f"Receita caiu {abs(growth):.0f}% vs primeira semana. "
                    f"Investigar causa: manutenção, sazonalidade ou falha técnica."))
    insights.append(('Projeção anual',
        f"R$ {kpis['proj_annual']:,.0f}/ano baseado em {kpis['days']} dias de dados "
        f"(R$ {kpis['rev_per_day']:,.0f}/dia de média)."))
    return insights


# ─── UNIFIED RENDERER ─────────────────────────────────────────────────────────
def _revenue_sources(df):
    """Calcula as três fontes de receita para sessões pagas."""
    paid = df[df['paid']].copy()
    for c in ['Receita(R$) por Início de Recarga', 'Receita(R$) por kWh', 'Valor Ociosidade', 'Energia(kWh)']:
        if c not in paid.columns:
            paid[c] = 0
        paid[c] = pd.to_numeric(paid[c], errors='coerce').fillna(0)
    r_inicio = paid['Receita(R$) por Início de Recarga'].sum()
    r_kwh    = (paid['Energia(kWh)'] * paid['Receita(R$) por kWh']).sum()
    r_ocio   = paid['Valor Ociosidade'].sum()
    return r_inicio, r_kwh, r_ocio

def fig_revenue_sources(df, color):
    """Gráfico de pizza — receita por origem (início, kWh, ociosidade)."""
    r_inicio, r_kwh, r_ocio = _revenue_sources(df)
    total = r_inicio + r_kwh + r_ocio
    if total == 0:
        return go.Figure()
    labels = ['Inicio de Recarga', 'Venda de Energia (kWh)', 'Ociosidade']
    values = [r_inicio, r_kwh, r_ocio]
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    pie_colors = [color, f'rgba({r},{g},{b},0.55)', COLORS[2]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=pie_colors, line=dict(color='#0D0F14', width=2)),
        textinfo='label+percent',
        textfont=dict(size=11),
        insidetextorientation='horizontal',
        sort=False,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation='v', x=1.02, y=0.5,
                    xanchor='left', yanchor='middle', font=dict(size=10)),
        annotations=[dict(
            text=f"R$ {total:,.0f}".replace(',','.'),
            x=0.5, y=0.5, font=dict(size=14, color=TEXT_PRIMARY),
            showarrow=False,
        )],
    )
    return fig

def fig_revenue_sources_bar(df, color):
    """Gráfico de barras — receita por origem e por semana."""
    paid = df[df['paid']].copy()
    for c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
        if c not in paid.columns: paid[c] = 0
        paid[c] = pd.to_numeric(paid[c], errors='coerce').fillna(0)
    paid['r_inicio'] = paid['Receita(R$) por Início de Recarga']
    paid['r_kwh']    = paid['Energia(kWh)'] * paid['Receita(R$) por kWh']
    paid['r_ocio']   = paid['Valor Ociosidade']
    paid['semana']   = paid['data_inicio'].dt.isocalendar().week
    weekly = paid.groupby('semana').agg(
        r_inicio=('r_inicio','sum'),
        r_kwh=('r_kwh','sum'),
        r_ocio=('r_ocio','sum'),
    ).reset_index()
    x = ['Sem ' + str(w) for w in weekly['semana']]
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=weekly['r_inicio'], name='Inicio de Recarga',
                         marker_color=color, opacity=0.9))
    fig.add_trace(go.Bar(x=x, y=weekly['r_kwh'], name='Venda de Energia (kWh)',
                         marker_color=f'rgba({r},{g},{b},0.5)', opacity=0.9))
    fig.add_trace(go.Bar(x=x, y=weekly['r_ocio'], name='Ociosidade',
                         marker_color=COLORS[2], opacity=0.9))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='stack', height=280)
    fig.update_layout(showlegend=True)
    fig.update_xaxes(gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(tickprefix='R$ ', tickformat=',.0f', gridcolor='#1E2330', linecolor='#1E2330')
    return fig

def build_dre_table(df, custo_kwh, custo_pct):
    """Monta o DataFrame da DRE semanal."""
    paid = df[df['paid']].copy()
    for c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
        if c not in paid.columns: paid[c] = 0
        paid[c] = pd.to_numeric(paid[c], errors='coerce').fillna(0)
    paid['r_inicio'] = paid['Receita(R$) por Início de Recarga']
    paid['r_kwh']    = paid['Energia(kWh)'] * paid['Receita(R$) por kWh']
    paid['r_ocio']   = paid['Valor Ociosidade']
    paid['semana']   = paid['data_inicio'].dt.isocalendar().week

    weekly = paid.groupby('semana').agg(
        r_inicio=('r_inicio','sum'),
        r_kwh_rec=('r_kwh','sum'),
        r_ocio=('r_ocio','sum'),
        sessoes=('Receita(R$)','count'),
        kwh=('Energia(kWh)','sum'),
        receita=('Receita(R$)','sum'),
    ).reset_index()

    weekly['receita_total'] = weekly['r_inicio'] + weekly['r_kwh_rec'] + weekly['r_ocio']
    weekly['custo_energia'] = weekly['kwh'] * custo_kwh
    weekly['custo_operacional'] = weekly['receita_total'] * (custo_pct / 100)
    weekly['custo_total'] = weekly['custo_energia'] + weekly['custo_operacional']
    weekly['lucro_bruto'] = weekly['receita_total'] - weekly['custo_total']
    weekly['margem'] = weekly.apply(
        lambda r: r['lucro_bruto']/r['receita_total']*100 if r['receita_total'] else 0, axis=1)

    return weekly


def render_dashboard(df, dfs, kpis, color, is_consolidated, custo_kwh, custo_pct, anon, horas_dia=24):
    """Renderiza todos os KPIs e graficos — identico para modo individual e consolidado."""

    # ── ROW 1: 4 cards principais ─────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Receita Confirmada",
                      f"R$ {kpis['revenue']:,.2f}",
                      f"{kpis['paid_sessions']:,} sessões pagas", color)
    with c2: kpi_card("Energia Entregue",
                      f"{kpis['energy_kwh']:,.0f} kWh",
                      f"R$ {kpis['rev_per_kwh']:.2f}/kWh médio", COLORS[1])
    with c3: kpi_card("Ticket Médio",
                      f"R$ {kpis['avg_ticket']:.2f}",
                      f"{kpis['sessions_per_day']:.1f} sessões/dia", COLORS[2])
    with c4: kpi_card("Projeção Anual",
                      f"R$ {kpis['proj_annual']:,.0f}",
                      f"baseado em {kpis['days']} dias de dados", COLORS[3])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2: 4 cards secundarios ────────────────────────────────────────────
    c5,c6,c7,c8 = st.columns(4)
    with c5: kpi_card("Conversão",
                      f"{kpis['conversion']:.1f}%",
                      f"{kpis['approval']:.1f}% do total de sessões monetizado", COLORS[4])
    with c6: kpi_card("Usuários Únicos",
                      f"{kpis['unique_users']:,}",
                      f"{kpis['one_time']} one-time  |  {kpis['power_users']} power users", COLORS[5])
    with c7: kpi_card("Power Users (5+ sessões)",
                      str(kpis['power_users']),
                      f"{kpis['power_rev_pct']:.1f}% da receita total", COLORS[6])
    with c8: kpi_card("Receita Pendente",
                      f"R$ {kpis['pending_rev']:,.2f}",
                      "status pending — risco financeiro", COLORS[2])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 3: 4 cards operacionais ───────────────────────────────────────────
    c9,c10,c11,c12 = st.columns(4)
    with c9:  kpi_card("Receita / Dia",
                       f"R$ {kpis['rev_per_day']:,.0f}",
                       f"em {kpis['days']} dias analisados", color)
    with c10: kpi_card("kWh / Dia",
                       f"{kpis['kwh_per_day']:.1f} kWh",
                       f"{kpis['avg_kwh']:.1f} kWh por sessão média", COLORS[1])
    with c11: kpi_card("Receita por Ociosidade",
                       f"R$ {kpis['idle_fee']:,.2f}",
                       f"{kpis['idle_sessions']} sessões cobradas", COLORS[3])
    with c12: kpi_card("Taxa de Reprovação",
                       f"{kpis['rejection_rate']:.1f}%",
                       f"{kpis['not_paid']} pagamentos não aprovados", COLORS[2])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ALERTA ────────────────────────────────────────────────────────────────
    if kpis['pending_rev'] > 0:
        st.markdown(
            f'<div class="alert-risk">&#9888; <strong>Risco financeiro:</strong> '
            f'R$ {kpis["pending_rev"]:,.2f} em pagamentos com status <em>pending</em>. '
            f'Verificar integração de gateway nas estações afetadas.</div>',
            unsafe_allow_html=True
        )

    # ── RECEITA DIARIA ────────────────────────────────────────────────────────
    section("Receita Diária")
    st.plotly_chart(fig_daily(dfs), width='stretch')

    # ── HORARIO + FUNIL ───────────────────────────────────────────────────────
    ca, cb = st.columns([3, 2])
    with ca:
        section("Distribuição Horária de Sessões")
        st.plotly_chart(fig_hourly(dfs if is_consolidated else {list(dfs.keys())[0]: df}),
                        width='stretch')
    with cb:
        section("Funil de Conversão")
        st.plotly_chart(fig_funnel(kpis), width='stretch')

    # ── MEIOS DE PAGAMENTO + CONECTORES ───────────────────────────────────────
    cc, cd = st.columns(2)
    with cc:
        section("Meios de Pagamento")
        st.plotly_chart(fig_payment(df, color), width='stretch')
    with cd:
        section("Conectores (Sessões e Receita)")
        st.plotly_chart(fig_connectors(df), width='stretch')

    # ── DURACAO + SEMANAL ─────────────────────────────────────────────────────
    ce, cf = st.columns(2)
    with ce:
        section("Duração das Sessões com Ticket Médio")
        st.plotly_chart(fig_duration(df, color), width='stretch')
    with cf:
        section("Evolução Semanal (Receita e Sessões)")
        st.plotly_chart(fig_weekly(df, color), width='stretch')

    # ── TOP ESTACOES ──────────────────────────────────────────────────────────
    col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
    n_stations = min(df[col_est].nunique(), 15) if col_est in df.columns else 0
    if n_stations > 0:
        cg, ch = st.columns(2)
        with cg:
            section("Top 15 Estações por Receita")
            st.plotly_chart(fig_top_stations(df, top_n=n_stations), width='stretch')
        with ch:
            section("Top 15 Estações por Sessões/Dia")
            st.plotly_chart(fig_top_stations_by_sessions(df, top_n=n_stations), width='stretch')

        col_occ_title, col_occ_help = st.columns([10, 1])
        with col_occ_title:
            section(f"Taxa de Ocupação — Top 15 Carregadores ({horas_dia}h/dia uteis)")
    
        st.plotly_chart(fig_occupancy(df, top_n=n_stations, horas_dia=horas_dia), width='stretch')

    # ── DIA DA SEMANA ─────────────────────────────────────────────────────────
    ci, cj = st.columns(2)
    with ci:
        section("Receita por Dia da Semana")
        st.plotly_chart(fig_weekday_revenue(df, color), width='stretch')
    with cj:
        section("Sessões por Dia da Semana")
        st.plotly_chart(fig_weekday_sessions(df, color), width='stretch')

    # ── RECEITA VS CUSTO VS LUCRO ─────────────────────────────────────────────
    section("Receita vs Custo vs Lucro")
    fig_cost, daily_cost = fig_revenue_cost_profit(df, custo_kwh, custo_pct)
    # KPIs de custo
    total_r = daily_cost['receita'].sum()
    total_c = daily_cost['custo'].sum()
    total_l = daily_cost['lucro'].sum()
    margem  = total_l / total_r * 100 if total_r else 0
    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1: kpi_card("Receita Total", f"R$ {total_r:,.0f}", f"Custo R$/kWh: {custo_kwh:.2f}", ACCENT)
    with ck2: kpi_card("Custo Total", f"R$ {total_c:,.0f}", f"Op. {custo_pct:.1f}% + energia", COLORS[2])
    with ck3: kpi_card("Lucro Total", f"R$ {total_l:,.0f}", f"Margem {margem:.1f}%", COLORS[1])
    with ck4: kpi_card("Lucro/Dia", f"R$ {total_l/max(kpis['days'],1):,.0f}", "média do período", COLORS[3])
    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_cost, width='stretch')

    # ── RECEITA POR ORIGEM ────────────────────────────────────────────────────
    section("Receita por Origem")
    r_inicio, r_kwh, r_ocio = _revenue_sources(df)
    total_src = r_inicio + r_kwh + r_ocio
    rs1, rs2, rs3 = st.columns(3)
    with rs1: kpi_card("Inicio de Recarga",
                       f"R$ {r_inicio:,.2f}",
                       f"{r_inicio/total_src*100:.1f}% da receita" if total_src else "–",
                       color)
    with rs2: kpi_card("Venda de Energia (kWh)",
                       f"R$ {r_kwh:,.2f}",
                       f"{r_kwh/total_src*100:.1f}% da receita" if total_src else "–",
                       COLORS[1])
    with rs3: kpi_card("Ociosidade",
                       f"R$ {r_ocio:,.2f}",
                       f"{r_ocio/total_src*100:.1f}% da receita" if total_src else "–",
                       COLORS[2])
    st.markdown("<br>", unsafe_allow_html=True)

    col_pie, col_bar = st.columns([1, 2])
    with col_pie:
        st.plotly_chart(fig_revenue_sources(df, color), width='stretch')
    with col_bar:
        st.plotly_chart(fig_revenue_sources_bar(df, color), width='stretch')

    # ── SEGMENTACAO USUARIOS ──────────────────────────────────────────────────
    section("Segmentacao de Usuarios e Receita por Segmento")
    st.plotly_chart(fig_users(df, color, kpis['tag_col']), width='stretch')

    # ── INSIGHTS ──────────────────────────────────────────────────────────────
    section("Insights e Oportunidades")
    insights = generate_insights(kpis, df)
    for i in range(0, len(insights), 2):
        cols = st.columns(2)
        for j, col_item in enumerate(cols):
            if i+j < len(insights):
                title, body = insights[i+j]
                with col_item:
                    st.markdown(
                        f'<div class="insight-card">'
                        f'<div class="insight-title">{title}</div>'
                        f'<div style="font-size:0.72rem;color:#9CA3AF;line-height:1.65">{body}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── RESUMO POR ARQUIVO (somente consolidado com multiplos arquivos) ────────
    if is_consolidated and len(dfs) > 1:
        section("Resumo por Arquivo")
        rows = []
        for name, sdf in dfs.items():
            k = compute_kpis(sdf)
            rows.append({
                'Arquivo / Estacao': name,
                'Sessões': f"{k['total_sessions']:,}",
                'Receita (R$)': f"{k['revenue']:,.2f}",
                'R$/dia': f"{k['rev_per_day']:,.0f}",
                'Ticket Medio': f"R$ {k['avg_ticket']:.2f}",
                'R$/kWh': f"{k['rev_per_kwh']:.2f}",
                'Conversão': f"{k['conversion']:.1f}%",
                'kWh Total': f"{k['energy_kwh']:,.0f}",
                'Proj. Anual': f"R$ {k['proj_annual']:,.0f}",
            })
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)

    # ── DRE SEMANAL (transposta: indicadores=linhas, semanas=colunas) ────────────
    section("DRE — Demonstrativo de Resultado por Semana")
    dre = build_dre_table(df, custo_kwh, custo_pct)
    if len(dre) == 0:
        st.caption("Dados insuficientes para gerar a DRE.")
    else:
        semana_cols = [f"Sem {int(w)}" for w in dre['semana']]

        total_vals = {
            'Sessões Pagas':     f"{int(dre['sessoes'].sum()):,}",
            'kWh Entregues':     f"{dre['kwh'].sum():,.1f}",
            'R$ Início Recarga': f"R$ {dre['r_inicio'].sum():,.2f}",
            'R$ Energia (kWh)':  f"R$ {dre['r_kwh_rec'].sum():,.2f}",
            'R$ Ociosidade':     f"R$ {dre['r_ocio'].sum():,.2f}",
            'RECEITA TOTAL':     f"R$ {dre['receita_total'].sum():,.2f}",
            '(-) Custo Energia': f"R$ {dre['custo_energia'].sum():,.2f}",
            '(-) Custo Operac.': f"R$ {dre['custo_operacional'].sum():,.2f}",
            '(=) LUCRO BRUTO':   f"R$ {dre['lucro_bruto'].sum():,.2f}",
            'Margem (%)':        (f"{dre['lucro_bruto'].sum()/dre['receita_total'].sum()*100:.1f}%"
                                  if dre['receita_total'].sum() else '–'),
        }

        indicadores = [
            ('Sessões Pagas',     [f"{int(r['sessoes']):,}"           for _,r in dre.iterrows()], ''),
            ('kWh Entregues',     [f"{r['kwh']:,.1f}"                  for _,r in dre.iterrows()], ''),
            ('R$ Início Recarga', [f"R$ {r['r_inicio']:,.2f}"          for _,r in dre.iterrows()], ''),
            ('R$ Energia (kWh)',  [f"R$ {r['r_kwh_rec']:,.2f}"         for _,r in dre.iterrows()], ''),
            ('R$ Ociosidade',     [f"R$ {r['r_ocio']:,.2f}"            for _,r in dre.iterrows()], ''),
            ('RECEITA TOTAL',     [f"R$ {r['receita_total']:,.2f}"     for _,r in dre.iterrows()], 'receita'),
            ('(-) Custo Energia', [f"R$ {r['custo_energia']:,.2f}"     for _,r in dre.iterrows()], 'custo'),
            ('(-) Custo Operac.', [f"R$ {r['custo_operacional']:,.2f}" for _,r in dre.iterrows()], 'custo'),
            ('(=) LUCRO BRUTO',   [f"R$ {r['lucro_bruto']:,.2f}"       for _,r in dre.iterrows()], 'lucro'),
            ('Margem (%)',        [f"{r['margem']:.1f}%"               for _,r in dre.iterrows()], 'lucro'),
        ]

        st.markdown("""
        <style>
        .dre-t{width:100%;border-collapse:collapse;font-size:0.72rem;font-family:monospace;}
        .dre-t th{background:#1E2330;color:#6B7280;text-transform:uppercase;
                  letter-spacing:.06em;padding:7px 14px;text-align:right;
                  border-bottom:1px solid #2D3340;white-space:nowrap;}
        .dre-t th:first-child{text-align:left;min-width:170px;}
        .dre-t td{padding:5px 14px;border-bottom:1px solid #1A1C24;
                  color:#F0F2F8;text-align:right;white-space:nowrap;}
        .dre-t td:first-child{text-align:left;color:#9CA3AF;font-weight:500;}
        .dre-t .tc{background:#13161D!important;font-weight:700;
                   border-left:1px solid #2D3340;}
        .dre-t .row-receita td{background:rgba(0,201,167,0.04);}
        .dre-t .row-receita td:first-child{color:#F0F2F8;font-weight:700;}
        .dre-t .row-lucro td{background:rgba(0,201,167,0.07);}
        .dre-t .row-lucro td:first-child,.dre-t .row-lucro .tc{color:#00C9A7;font-weight:700;}
        .dre-t .row-custo td:first-child,.dre-t .row-custo .tc{color:#FF6B6B;}
        .dre-t tr:hover td{background:#13161D!important;}
        </style>
        """, unsafe_allow_html=True)

        th_sem = "".join(f"<th>{s}</th>" for s in semana_cols)
        header = f"<th>Indicador</th>{th_sem}<th class=\'tc\'>TOTAL</th>"

        rows_html = ""
        for label, vals, row_type in indicadores:
            row_cls = f" class=\'row-{row_type}\'" if row_type else ""
            cells = f"<td>{label}</td>"
            cells += "".join(f"<td>{v}</td>" for v in vals)
            cells += f"<td class=\'tc\'>{total_vals[label]}</td>"
            rows_html += f"<tr{row_cls}>{cells}</tr>"

        st.markdown(
            f'<div style="overflow-x:auto"><table class="dre-t">'
            f'<thead><tr>{header}</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── EXPORTAR PDF ──────────────────────────────────────────────────────────
    section("Exportar Relatório")
    pdf_label = "Arquivo 01" if anon else list(dfs.keys())[0] if len(dfs)==1 else "Consolidado"
    btn_key = f"pdf_btn_{pdf_label.replace(' ','_').replace('/','_')}"
    dl_key  = f"pdf_dl_{pdf_label.replace(' ','_').replace('/','_')}"
    if st.button("Gerar PDF do Dashboard", type="primary", width='stretch', key=btn_key):
        with st.spinner("Gerando PDF com gráficos..."):
            pdf_bytes = generate_pdf(df, kpis, custo_kwh, custo_pct,
                                     dfs=dfs, color=color, title=pdf_label,
                                     horas_dia=horas_dia)
        if pdf_bytes and not pdf_bytes[:3].isalpha():
            st.download_button(
                label="Baixar PDF",
                data=pdf_bytes,
                file_name=f"relatorio_eletropostos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                width='stretch',
                key=dl_key,
            )
        else:
            err = pdf_bytes.decode() if pdf_bytes else "Erro desconhecido"
            st.error(f"Erro ao gerar PDF: {err[:200]}")



# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:1rem 0 1.5rem">'
        '<div style="font-size:1.3rem;font-weight:800;color:#00C9A7">Dashboard financeiro</div>'
        '<div style="font-size:0.62rem;color:#6B7280;margin-top:2px">Análise financeira da operação da rede de recarga</div>'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Carregar arquivos .xlsx", type=["xlsx"], accept_multiple_files=True,
        help="Arquivos de relatório de recargas no mesmo formato exportado pelo sistema."
    )

    st.markdown("---")

    if uploaded_files:
        st.markdown('<div style="font-size:0.65rem;color:#6B7280;margin-bottom:0.5rem">ARQUIVOS CARREGADOS</div>', unsafe_allow_html=True)
        for f in uploaded_files:
            st.markdown(f'<div style="font-size:0.68rem;color:#F0F2F8;padding:3px 0">&#128196; {f.name}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.62rem;color:#6B7280">MODO DE ANÁLISE</div>', unsafe_allow_html=True)
    mode = st.radio("", ["Por estação (individual)", "Consolidado (todos os arquivos)"],
                    label_visibility="collapsed")

    anon = False
    if uploaded_files:
        st.markdown("---")
        anon = st.toggle("Anonimizar nomes (A, B, C...)", value=False)

    st.markdown("---")
    st.markdown('<div style="font-size:0.62rem;color:#6B7280;margin-bottom:0.5rem">PARAMETROS DE CUSTO</div>', unsafe_allow_html=True)
    custo_kwh = st.number_input("Custo da energia (R$/kWh)", min_value=0.0, value=0.75, step=0.01, format="%.2f")
    custo_pct  = st.number_input("Custo operacional (% da receita)", min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f")

    st.markdown("---")
    st.markdown('<div style="font-size:0.62rem;color:#6B7280;margin-bottom:0.5rem">HORÁRIO DE FUNCIONAMENTO</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.70rem;color:#9CA3AF;margin-bottom:0.5rem">Usado para calcular a taxa de ocupação real dos carregadores</div>', unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hora_inicio = st.number_input("Abertura", min_value=0, max_value=23, value=0, step=1,
                                       help="Horário de abertura do estabelecimento (0 = meia-noite)")
    with col_h2:
        hora_fim = st.number_input("Fechamento", min_value=1, max_value=24, value=24, step=1,
                                    help="Horário de fechamento (24 = meia-noite)")
    horas_dia = max(1, hora_fim - hora_inicio)
    st.markdown(f'<div style="font-size:0.68rem;color:#00C9A7;margin-top:2px">&#9201; {horas_dia}h disponiveis/dia</div>', unsafe_allow_html=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-bottom:1.5rem">'
    '<div class="page-title">Dashboard <span style="color:#00C9A7">Financeiro</span></div>'
    '<div class="page-subtitle">Software em testes, confira os dados antes de transmiti-los</div>'
    '</div>',
    unsafe_allow_html=True
)

if not uploaded_files:
    st.markdown(
        '<div style="text-align:center;padding:4rem 2rem;color:#6B7280">'
        '<div style="font-size:3rem;margin-bottom:1rem">&#9889;</div>'
        '<div style="font-size:1.2rem;font-weight:700;color:#F0F2F8;margin-bottom:0.5rem">Nenhum arquivo carregado</div>'
        '<div style="font-size:0.75rem;line-height:1.7">Use o painel lateral para fazer upload dos arquivos .xlsx de relatorio de recargas.</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.stop()

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
with st.spinner("Processando arquivos..."):
    dfs = {}
    for f in uploaded_files:
        raw = load_file(f.read(), f.name)
        processed = process_df(raw)
        col = 'Estação' if 'Estação' in processed.columns else 'Estacao'
        stations_in_file = processed[col].dropna().unique() if col in processed.columns else []
        station_name = stations_in_file[0] if len(stations_in_file) == 1 else f.name.replace('.xlsx','')
        dfs[station_name] = processed

if anon:
    col_est = 'Estação' if 'Estação' in next(iter(dfs.values())).columns else 'Estacao'

    # Coleta todos os nomes únicos de estação em ordem de aparição
    all_stations = []
    for sdf in dfs.values():
        if col_est in sdf.columns:
            for s in sdf[col_est].dropna().unique():
                s = str(s)
                if s not in all_stations:
                    all_stations.append(s)

    # IDs sempre únicos: Est-001, Est-002, ... (nunca repete)
    station_map = {name: f"Est-{i+1:03d}" for i, name in enumerate(all_stations)}

    # Aplica o mapa nos DataFrames e renomeia as chaves do dict
    new_dfs = {}
    for i, (file_key, sdf) in enumerate(dfs.items()):
        sdf = sdf.copy()
        if col_est in sdf.columns:
            sdf[col_est] = sdf[col_est].astype(str).map(station_map).fillna(sdf[col_est])
        new_key = f"Arquivo {i+1:02d}"
        new_dfs[new_key] = sdf

    dfs = new_dfs

df_all = pd.concat(dfs.values(), ignore_index=True)

# ─── FILTROS (CONECTOR + ESTAÇÃO) ────────────────────────────────────────────
_col_conn = 'Conector(Tipo)' if 'Conector(Tipo)' in df_all.columns else None
_col_est  = 'Estação' if 'Estação' in df_all.columns else ('Estacao' if 'Estacao' in df_all.columns else None)

_connector_options = sorted(df_all[_col_conn].dropna().unique().tolist()) if _col_conn else []
_station_options   = sorted(df_all[_col_est].dropna().unique().tolist())  if _col_est  else []

# Filtros nativos na sidebar — causam soft-rerun preservando o arquivo carregado
_selected_connector = ""
_selected_station   = ""

with st.sidebar:
    if _connector_options or _station_options:
        st.markdown("---")
        st.markdown('<div style="font-size:0.62rem;color:#6B7280;margin-bottom:0.5rem">FILTROS</div>',
                    unsafe_allow_html=True)
        if _connector_options:
            _conn_choice = st.selectbox(
                "Conector", ["Todos os conectores"] + _connector_options,
                index=0, key="filter_connector"
            )
            _selected_connector = "" if _conn_choice == "Todos os conectores" else _conn_choice
        if _station_options:
            _stat_choice = st.selectbox(
                "Estação", ["Todas as estações"] + _station_options,
                index=0, key="filter_station"
            )
            _selected_station = "" if _stat_choice == "Todas as estações" else _stat_choice

# Aplica filtros em df_all e em cada dfs
if _selected_connector and _col_conn:
    df_all = df_all[df_all[_col_conn] == _selected_connector]
    dfs = {k: v[v[_col_conn] == _selected_connector] if _col_conn in v.columns else v
           for k, v in dfs.items()}

if _selected_station and _col_est:
    df_all = df_all[df_all[_col_est] == _selected_station]
    dfs = {k: v[v[_col_est] == _selected_station] if _col_est in v.columns else v
           for k, v in dfs.items()}

# ─── CONSOLIDATED VIEW ────────────────────────────────────────────────────────
if mode == "Consolidado (todos os arquivos)" or len(dfs) == 1:
    kpis = compute_kpis(df_all)
    render_dashboard(df_all, dfs, kpis, ACCENT, is_consolidated=True,
                     custo_kwh=custo_kwh, custo_pct=custo_pct, anon=anon, horas_dia=horas_dia)

# ─── INDIVIDUAL VIEW ──────────────────────────────────────────────────────────
else:
    tabs = st.tabs([f"&#9889; {name}" for name in dfs.keys()])
    for tab, (name, df) in zip(tabs, dfs.items()):
        color = COLORS[list(dfs.keys()).index(name) % len(COLORS)]
        kpis = compute_kpis(df)
        with tab:
            st.markdown(
                f'<div style="margin-bottom:1rem">'
                f'<span style="font-size:1.1rem;font-weight:700;color:{color}">{name}</span>'
                f'<span style="font-size:0.65rem;color:#6B7280;margin-left:0.75rem">'
                f'{kpis["days"]} dias &middot; {kpis["total_sessions"]:,} sessões</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            render_dashboard(df, {name: df}, kpis, color, is_consolidated=False,
                             custo_kwh=custo_kwh, custo_pct=custo_pct, anon=anon, horas_dia=horas_dia)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="text-align:center;padding:2rem 0 1rem;font-size:0.62rem;color:#3D4560;'
    f'border-top:1px solid #1E2330;margin-top:2rem">'
    f'&#9889; MVP do dashboard financeiro v0.1 &middot; {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}'
    f'</div>',
    unsafe_allow_html=True
)
