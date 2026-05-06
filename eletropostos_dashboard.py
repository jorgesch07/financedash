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
# Injetada no documento pai via components.html (st.markdown usa iframe)
components.html("""
<script>
(function() {
    var LOGO_URL = 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Logomarca_Intelbras_verde.png';

    function buildTopbar() {
        var pdoc = window.parent.document;
        if (pdoc.getElementById('ib-topbar')) return;

        // Estilos injetados no <head> do pai
        var style = pdoc.createElement('style');
        style.textContent = [
            '#ib-topbar{position:fixed;top:0;left:0;right:0;z-index:99998;height:52px;',
            'background:#0A0C10;border-bottom:1px solid #1E2330;',
            'display:flex;align-items:center;padding:0 24px 0 66px;gap:14px;font-family:monospace;}',
            '#ib-topbar-label{font-size:10px;color:#6B7280;letter-spacing:.08em;white-space:nowrap;text-transform:uppercase;}',
            '#ib-connector-select{background:#13161D;border:1px solid #1E2330;border-radius:6px;',
            'color:#F0F2F8;font-size:11px;font-family:monospace;padding:5px 12px;cursor:pointer;min-width:200px;}',
            '#ib-connector-select:focus{outline:none;border-color:#00C9A7;}',
            '#ib-topbar-logo{height:40px;width:auto;object-fit:contain;margin-left:auto;}'
        ].join('');
        pdoc.head.appendChild(style);

        // Padding extra no conteúdo principal para não ficar atrás da barra
        var pstyle = pdoc.createElement('style');
        pstyle.textContent = '.block-container{padding-top:4.5rem !important;}';
        pdoc.head.appendChild(pstyle);

        // Monta a barra
        var bar = pdoc.createElement('div');
        bar.id = 'ib-topbar';

        var label = pdoc.createElement('span');
        label.id = 'ib-topbar-label';
        label.textContent = 'Conector';

        var sel = pdoc.createElement('select');
        sel.id = 'ib-connector-select';
        var opt0 = pdoc.createElement('option');
        opt0.value = ''; opt0.textContent = 'Todos os conectores';
        sel.appendChild(opt0);
        sel.addEventListener('change', function() {
            // Atualiza o query param e força reload do Streamlit
            var url = new URL(window.parent.location.href);
            if (this.value) {
                url.searchParams.set('connector', this.value);
            } else {
                url.searchParams.delete('connector');
            }
            window.parent.location.href = url.toString();
        });

        var logo = pdoc.createElement('img');
        logo.id = 'ib-topbar-logo';
        logo.src = LOGO_URL;
        logo.alt = 'Intelbras';

        bar.appendChild(label);
        bar.appendChild(sel);
        bar.appendChild(logo);
        pdoc.body.prepend(bar);
    }

    function populateOptions() {
        var pdoc = window.parent.document;
        var sel = pdoc.getElementById('ib-connector-select');
        if (!sel) { setTimeout(populateOptions, 500); return; }
        var opts = window.parent.__ib_connectors || [];
        // Remove antigas (exceto "Todos")
        while (sel.options.length > 1) sel.remove(1);
        opts.forEach(function(c) {
            var o = pdoc.createElement('option');
            o.value = c; o.textContent = c;
            sel.appendChild(o);
        });
        // Restaura seleção atual da URL
        var url = new URL(window.parent.location.href);
        var cur = url.searchParams.get('connector') || '';
        sel.value = cur;
    }

    buildTopbar();
    setTimeout(populateOptions, 600);
    setTimeout(populateOptions, 1500);

    // Re-injeta se o Streamlit re-renderizar o body
    var obs = new MutationObserver(function() {
        if (!window.parent.document.getElementById('ib-topbar')) buildTopbar();
        populateOptions();
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
    labels = ['Total de sessoes', 'Tentativa de pagamento', 'Pagas (aprovadas)']
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
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Sessoes','Receita (R$)'], horizontal_spacing=0.12)
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
    fig.add_trace(go.Bar(x=dur['dur_seg'], y=dur['count'], name='Sessoes',
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
                             name='Sessoes', mode='lines+markers',
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
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Usuarios por segmento','Receita por segmento'],
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

def fig_occupancy(df, top_n=15):
    col_est = 'Estacao' if 'Estacao' in df.columns else 'Estacao'
    for c in ['Estação', 'Estacao']:
        if c in df.columns:
            col_est = c
            break
    else:
        return go.Figure()
    days = df['data'].nunique() or 1
    occ = (df.groupby(col_est)
             .agg(sessions=('Receita(R$)','count'), total_min=('duracao_min','sum'))
             .assign(occupancy_pct=lambda x: (x['total_min'] / (days * 24 * 60) * 100).clip(0, 100))
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
    fig.update_layout(showlegend=False)
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


def _fig_to_img(fig, w=900, h=350, lmargin=60):
    """
    Converte figura Plotly para PNG usando matplotlib como backend.
    Não requer Chrome/kaleido — funciona em qualquer ambiente.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    fig_dict = fig.to_dict()
    traces   = fig_dict.get('data', [])
    layout   = fig_dict.get('layout', {})

    # Dimensões em polegadas (72dpi base → 2x = 144dpi final)
    dpi = 120
    fig_w = w / dpi
    fig_h = h / dpi

    mfig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    mfig.patch.set_facecolor('white')
    ax.set_facecolor('#F8F9FA')
    ax.tick_params(colors='#444', labelsize=8)
    ax.spines[:].set_color('#CCCCCC')
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
    ax.grid(axis='y', color='#E8E8E8', linewidth=0.5, zorder=0)

    PALETTE = ['#00C9A7','#0088FE','#FF6B6B','#FFD93D',
               '#A855F7','#F97316','#06B6D4','#84CC16']

    is_h   = any(t.get('orientation') == 'h' for t in traces)
    is_pie = any(t.get('type') == 'pie'       for t in traces)
    is_fun = any(t.get('type') == 'funnel'    for t in traces)
    is_scatter = any(t.get('type') in ('scatter', 'scattergl') for t in traces)

    legend_patches = []

    # ── PIE / DONUT ──────────────────────────────────────────────────────────
    if is_pie:
        ax.set_visible(False)
        ax2 = mfig.add_axes([0.05, 0.05, 0.55, 0.9])
        ax2.set_facecolor('white')
        t = traces[0]
        vals   = [float(v) for v in (t.get('values') or t.get('y') or [])]
        labels = list(t.get('labels') or t.get('x') or [f'Item {i}' for i in range(len(vals))])
        colors = t.get('marker', {}).get('colors', PALETTE[:len(vals)])
        # Convert rgba strings to hex if needed
        mcolors = []
        for c in colors[:len(vals)]:
            try:
                if isinstance(c, str) and c.startswith('rgba'):
                    parts = c.strip('rgba()').split(',')
                    r,g,b = int(parts[0]),int(parts[1]),int(parts[2])
                    mcolors.append(f'#{r:02x}{g:02x}{b:02x}')
                else:
                    mcolors.append(c)
            except Exception:
                mcolors.append(PALETTE[len(mcolors) % len(PALETTE)])
        hole = t.get('hole', 0)
        wedges, texts, autotexts = ax2.pie(
            vals, labels=None, colors=mcolors,
            autopct='%1.1f%%', pctdistance=0.75,
            wedgeprops=dict(width=1-hole if hole else 1, edgecolor='white', linewidth=1.5),
            startangle=90,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color('white')
        # Legend
        for lbl, col in zip(labels, mcolors):
            legend_patches.append(mpatches.Patch(color=col, label=lbl[:30]))
        mfig.legend(handles=legend_patches, loc='center right',
                    bbox_to_anchor=(0.98, 0.5), fontsize=8, frameon=False)
        total = sum(vals)
        if hole:
            ax2.text(0, 0, f"R$ {total:,.0f}".replace(',','.'),
                     ha='center', va='center', fontsize=9, fontweight='bold', color='#222')
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO()
        mfig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                     facecolor='white', edgecolor='none')
        plt.close(mfig)
        buf.seek(0)
        return buf.read()

    # ── FUNNEL ───────────────────────────────────────────────────────────────
    if is_fun:
        t = traces[0]
        xvals  = [float(v) for v in (t.get('x') or [])]
        ylabels = list(t.get('y') or [f'Step {i}' for i in range(len(xvals))])
        colors_f = [PALETTE[i % len(PALETTE)] for i in range(len(xvals))]
        max_v = max(xvals) if xvals else 1
        bar_w = [v / max_v for v in xvals]
        ys = range(len(xvals))
        bars = ax.barh([str(y) for y in ylabels], xvals,
                       color=colors_f, height=0.5, zorder=3)
        ax.set_xlabel('')
        ax.invert_yaxis()
        ax.set_xlim(0, max_v * 1.15)
        ax.xaxis.set_visible(False)
        ax.grid(False)
        for bar, val in zip(bars, xvals):
            ax.text(bar.get_width() + max_v * 0.01, bar.get_y() + bar.get_height()/2,
                    f'{val:,.0f}', va='center', fontsize=8, color='#333')
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO()
        mfig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                     facecolor='white', edgecolor='none')
        plt.close(mfig)
        buf.seek(0)
        return buf.read()

    # ── HORIZONTAL BARS ──────────────────────────────────────────────────────
    if is_h:
        ax.grid(axis='x', color='#E8E8E8', linewidth=0.5, zorder=0)
        ax.grid(axis='y', visible=False)
        n_traces = len(traces)
        all_labels = list(traces[0].get('y') or [])
        n = len(all_labels)
        y_pos = np.arange(n)
        bar_h = 0.7 / max(n_traces, 1)
        offsets = np.linspace(-(n_traces-1)/2, (n_traces-1)/2, n_traces) * bar_h
        for i, t in enumerate(traces):
            xvals  = [float(v) if v is not None else 0
                      for v in (t.get('x') or [])]
            labels = list(t.get('y') or all_labels)
            c = PALETTE[i % len(PALETTE)]
            if isinstance(t.get('marker'), dict):
                mc = t['marker'].get('color')
                if isinstance(mc, str) and mc.startswith('#'):
                    c = mc
            bars = ax.barh(y_pos + offsets[i], xvals[:n], height=bar_h * 0.9,
                           color=c, zorder=3, label=t.get('name', ''))
            legend_patches.append(mpatches.Patch(color=c, label=(t.get('name') or '')[:25]))
        ax.set_yticks(y_pos)
        ax.set_yticklabels([str(l)[:35] for l in all_labels], fontsize=8)
        ax.invert_yaxis()
        # x-axis formatting
        ticks = ax.get_xticks()
        ax.set_xticklabels(
            [f'R${v/1000:.0f}k' if abs(v) >= 1000 else str(int(v)) for v in ticks],
            fontsize=8
        )
        if n_traces > 1:
            ax.legend(handles=legend_patches, fontsize=7, frameon=False,
                      loc='lower right')
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO()
        mfig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                     facecolor='white', edgecolor='none')
        plt.close(mfig)
        buf.seek(0)
        return buf.read()

    # ── LINE / SCATTER ───────────────────────────────────────────────────────
    if is_scatter:
        ax.grid(axis='y', color='#E8E8E8', linewidth=0.5, zorder=0)
        for i, t in enumerate(traces):
            xvals = list(t.get('x') or [])
            yvals = [float(v) if v is not None else 0 for v in (t.get('y') or [])]
            c = PALETTE[i % len(PALETTE)]
            if isinstance(t.get('line'), dict):
                lc = t['line'].get('color','')
                if lc and isinstance(lc, str) and lc.startswith('#'):
                    c = lc
            lw = 1.5
            ls = '--' if isinstance(t.get('line'), dict) and t['line'].get('dash') else '-'
            ax.plot(xvals, yvals, color=c, linewidth=lw, linestyle=ls,
                    label=(t.get('name') or '')[:25], zorder=3)
            if t.get('fill') == 'tozeroy':
                ax.fill_between(range(len(yvals)), yvals, alpha=0.07, color=c)
        # Format y-axis
        ticks = ax.get_yticks()
        ax.set_yticklabels(
            [f'R${v/1000:.0f}k' if abs(v) >= 1000 else str(int(v)) for v in ticks],
            fontsize=8
        )
        # Format x-axis dates
        xlabels = [str(x)[:10] for x in (traces[0].get('x') or [])]
        step = max(1, len(xlabels) // 8)
        ax.set_xticks(range(0, len(xlabels), step))
        ax.set_xticklabels(xlabels[::step], rotation=30, ha='right', fontsize=8)
        if len(traces) > 1:
            ax.legend(fontsize=7, frameon=False, loc='upper left')
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO()
        mfig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                     facecolor='white', edgecolor='none')
        plt.close(mfig)
        buf.seek(0)
        return buf.read()

    # ── VERTICAL BARS (default) ──────────────────────────────────────────────
    n_traces = len(traces)
    if n_traces == 0:
        plt.close(mfig)
        return None
    all_x = list(traces[0].get('x') or [])
    n = len(all_x)
    x_pos = np.arange(n)
    bar_w = 0.7 / max(n_traces, 1)
    offsets = np.linspace(-(n_traces-1)/2, (n_traces-1)/2, n_traces) * bar_w
    barmode = layout.get('barmode', 'group')

    if barmode == 'stack':
        bottoms = np.zeros(n)
        for i, t in enumerate(traces):
            yvals = [float(v) if v is not None else 0 for v in (t.get('y') or [])]
            c = PALETTE[i % len(PALETTE)]
            if isinstance(t.get('marker'), dict):
                mc = t['marker'].get('color')
                if isinstance(mc, str) and mc.startswith('#'):
                    c = mc
            ax.bar(x_pos, yvals[:n], bottom=bottoms[:n], color=c,
                   width=0.6, zorder=3, label=(t.get('name') or '')[:25])
            bottoms[:n] += np.array(yvals[:n])
            legend_patches.append(mpatches.Patch(color=c, label=(t.get('name') or '')[:25]))
    else:
        for i, t in enumerate(traces):
            yvals = [float(v) if v is not None else 0 for v in (t.get('y') or [])]
            c = PALETTE[i % len(PALETTE)]
            if isinstance(t.get('marker'), dict):
                mc = t['marker'].get('color')
                if isinstance(mc, str) and mc.startswith('#'):
                    c = mc
            ax.bar(x_pos + offsets[i], yvals[:n], width=bar_w * 0.9,
                   color=c, zorder=3, label=(t.get('name') or '')[:25])
            legend_patches.append(mpatches.Patch(color=c, label=(t.get('name') or '')[:25]))

    step = max(1, n // 10)
    ax.set_xticks(x_pos[::step])
    ax.set_xticklabels([str(x)[:12] for x in all_x[::step]], rotation=30, ha='right', fontsize=8)
    ticks = ax.get_yticks()
    ax.set_yticklabels(
        [f'R${v/1000:.0f}k' if abs(v) >= 1000 else str(int(v)) for v in ticks],
        fontsize=8
    )
    if n_traces > 1:
        ax.legend(handles=legend_patches, fontsize=7, frameon=False, loc='upper right')

    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    mfig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    plt.close(mfig)
    buf.seek(0)
    return buf.read()



def generate_pdf(df, kpis, custo_kwh, custo_pct, dfs, color, title="Relatorio"):
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

        def chart(fig, w_cm=17.4, h_cm=6.5, px_h=None, lmargin=60):
            pw = int(w_cm * 42)
            ph = px_h or int(h_cm * 42)
            png = _fig_to_img(fig, w=pw, h=ph, lmargin=lmargin)
            if png is None:
                return Paragraph('[Grafico indisponivel]', S(8, color=C_GREY))
            return RLImage(io.BytesIO(png), width=w_cm*cm, height=h_cm*cm)

        def two_charts(fig_l, fig_r, h_cm=5.5, lw_cm=8.5, rw_cm=8.5,
                       lmargin_l=60, lmargin_r=60, px_h=None):
            ph = px_h or int(h_cm * 42)
            png_l = _fig_to_img(fig_l, w=int(lw_cm*42), h=ph, lmargin=lmargin_l)
            png_r = _fig_to_img(fig_r, w=int(rw_cm*42), h=ph, lmargin=lmargin_r)
            def img(png, w_cm, h_cm):
                if png is None:
                    return Paragraph('[Grafico indisponivel]', S(8, color=C_GREY))
                return RLImage(io.BytesIO(png), width=w_cm*cm, height=h_cm*cm)
            t = Table([[img(png_l, lw_cm, h_cm), img(png_r, rw_cm, h_cm)]],
                      colWidths=[lw_cm*cm, rw_cm*cm], hAlign='LEFT')
            t.setStyle(TableStyle([
                ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(0,-1),3),
                ('RIGHTPADDING',(1,0),(1,-1),0), ('TOPPADDING',(0,0),(-1,-1),0),
                ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ]))
            return t

        story = []

        # ── CAPA ─────────────────────────────────────────────────────────────
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph('RELATORIO FINANCEIRO', S(8, bold=True, color=C_GREY)))
        story.append(Spacer(1, 4))
        story.append(Paragraph('Dashboard Financeiro - Intelbras', S(20, bold=True, color=C_BLACK)))
        story.append(Paragraph(title, S(12, bold=True, color=C_BLUE)))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f'Gerado em {datetime.date.today().strftime("%d/%m/%Y")}  |  '
            f'{kpis["days"]} dias de dados  |  '
            f'{kpis["total_sessions"]:,} sessoes totais',
            S(8, color=C_GREY)))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width=W, thickness=2, color=C_GREEN))
        story.append(Spacer(1, 12))

        # ── KPIs PRINCIPAIS ───────────────────────────────────────────────────
        story += section_hdr('INDICADORES PRINCIPAIS')
        story.append(kv_table([
            ['Receita Confirmada', f"R$ {kpis['revenue']:,.2f}",
             'Sessoes Pagas', f"{kpis['paid_sessions']:,}"],
            ['Energia Entregue', f"{kpis['energy_kwh']:,.1f} kWh",
             'R$/kWh Medio', f"R$ {kpis['rev_per_kwh']:.2f}"],
            ['Ticket Medio', f"R$ {kpis['avg_ticket']:.2f}",
             'Sessoes/Dia', f"{kpis['sessions_per_day']:.1f}"],
            ['Receita/Dia', f"R$ {kpis['rev_per_day']:,.0f}",
             'kWh/Dia', f"{kpis['kwh_per_day']:.1f}"],
            ['Conversao', f"{kpis['conversion']:.1f}%",
             'Usuarios Unicos', f"{kpis['unique_users']:,}"],
            ['Power Users (5+)', f"{kpis['power_users']}",
             'Receita Power Users', f"{kpis['power_rev_pct']:.1f}%"],
            ['Receita Pendente', f"R$ {kpis['pending_rev']:,.2f}",
             'Idle Fee Total', f"R$ {kpis['idle_fee']:,.2f}"],
            ['Projecao Anual', f"R$ {kpis['proj_annual']:,.0f}",
             'Taxa Reprovacao', f"{kpis['rejection_rate']:.1f}%"],
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

        # ── GRAFICOS — PAGINA 2 ───────────────────────────────────────────────
        story.append(PageBreak())

        # Receita diária
        story += section_hdr('RECEITA DIARIA')
        story.append(chart(fig_daily(dfs), h_cm=6, lmargin=55))
        story.append(Spacer(1, 8))

        # Receita vs Custo vs Lucro
        story += section_hdr('RECEITA vs CUSTO vs LUCRO')
        fig_rcl, _ = fig_revenue_cost_profit(df, custo_kwh, custo_pct)
        story.append(chart(fig_rcl, h_cm=6, lmargin=55))
        story.append(Spacer(1, 8))

        # Horário + Funil lado a lado
        story += section_hdr('DISTRIBUICAO HORARIA  |  FUNIL DE CONVERSAO')
        story.append(two_charts(
            fig_hourly(dfs), fig_funnel(kpis),
            h_cm=5.5, lw_cm=11.0, rw_cm=6.0,
            lmargin_l=45, lmargin_r=5,
        ))
        story.append(Spacer(1, 8))

        # ── PAGINA 3 ──────────────────────────────────────────────────────────
        story.append(PageBreak())

        # Dia da semana lado a lado
        story += section_hdr('RECEITA POR DIA DA SEMANA  |  SESSOES POR DIA DA SEMANA')
        story.append(two_charts(
            fig_weekday_revenue(df, color), fig_weekday_sessions(df, color),
            h_cm=5.5, lmargin_l=55, lmargin_r=55,
        ))
        story.append(Spacer(1, 8))

        # Meios de pagamento (full width)
        story += section_hdr('MEIOS DE PAGAMENTO')
        story.append(chart(fig_payment(df, color), h_cm=5.5, lmargin=10))
        story.append(Spacer(1, 8))

        # Conectores (full width)
        story += section_hdr('CONECTORES (SESSOES E RECEITA)')
        story.append(chart(fig_connectors(df), h_cm=4.5, lmargin=70))
        story.append(Spacer(1, 8))

        # Duração + Semanal
        story += section_hdr('DURACAO DAS SESSOES  |  EVOLUCAO SEMANAL')
        story.append(two_charts(
            fig_duration(df, color), fig_weekly(df, color),
            h_cm=5.5, lmargin_l=55, lmargin_r=55,
        ))

        # ── PAGINA 4 ──────────────────────────────────────────────────────────
        story.append(PageBreak())

        # Top estações por receita
        story += section_hdr('TOP 15 ESTACOES POR RECEITA')
        n_st = min(df['Estação'].nunique() if 'Estação' in df.columns else
                   df['Estacao'].nunique() if 'Estacao' in df.columns else 0, 15)
        if n_st > 0:
            h_st  = max(5.5, n_st * 0.52)
            px_h_st = int(n_st * 30 + 90)
            story.append(chart(fig_top_stations(df, top_n=n_st),
                               h_cm=h_st, px_h=px_h_st))
            story.append(Spacer(1, 8))
            story += section_hdr('TOP 15 ESTACOES POR SESSOES/DIA')
            story.append(chart(fig_top_stations_by_sessions(df, top_n=n_st),
                               h_cm=h_st, px_h=px_h_st))
            story.append(Spacer(1, 8))
            story += section_hdr('TAXA DE OCUPACAO — TOP 15 CARREGADORES')
            story.append(chart(fig_occupancy(df, top_n=n_st),
                               h_cm=h_st, px_h=px_h_st))

        # ── PAGINA 5 ──────────────────────────────────────────────────────────
        story.append(PageBreak())

        # Segmentação de usuários
        story += section_hdr('SEGMENTACAO DE USUARIOS')
        story.append(chart(fig_users(df, color, kpis['tag_col']), h_cm=5.5, lmargin=55))
        story.append(Spacer(1, 8))

        # Tabela Top 15 estações
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
                   for h in ['Estacao','Sessoes','Receita (R$)','R$/Dia','kWh']]
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
                   for h in ['Dia','Sessoes','Receita (R$)','Ticket Medio']]
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
            f'Dashboard Financeiro  |  {datetime.date.today().strftime("%d/%m/%Y")}  |  '
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
            f"R$ {kpis['pending_rev']:,.2f} em status pending. Revisar integracao de gateway."))
    if kpis['power_rev_pct'] > 60:
        insights.append(('Concentracao em Power Users',
            f"{kpis['power_users']} usuarios (5+ sessoes) geram {kpis['power_rev_pct']:.1f}% da receita. "
            f"Programa de fidelidade pode reduzir risco de churn."))
    if kpis['unique_users'] > 0 and kpis['one_time'] / kpis['unique_users'] > 0.5:
        pct = kpis['one_time'] / kpis['unique_users'] * 100
        insights.append(('Alta taxa de usuarios one-time',
            f"{kpis['one_time']} ({pct:.0f}%) usuarios vieram apenas uma vez. "
            f"Estrategia de ativacao pos-primeira-sessao pode aumentar retencao."))
    if kpis['idle_fee'] > 0:
        insights.append(('Idle Fee ativo',
            f"R$ {kpis['idle_fee']:,.2f} coletados em {kpis['idle_sessions']} sessoes por ociosidade."))
    if kpis['rejection_rate'] > 5:
        insights.append(('Taxa de reprovacao elevada',
            f"{kpis['rejection_rate']:.1f}% dos pagamentos foram reprovados ({kpis['not_paid']} sessoes). "
            f"Verificar gateway e meios de pagamento disponiveis."))
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
                insights.append(('Queda na ultima semana',
                    f"Receita caiu {abs(growth):.0f}% vs primeira semana. "
                    f"Investigar causa: manutencao, sazonalidade ou falha tecnica."))
    insights.append(('Projecao anual',
        f"R$ {kpis['proj_annual']:,.0f}/ano baseado em {kpis['days']} dias de dados "
        f"(R$ {kpis['rev_per_day']:,.0f}/dia de media)."))
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


def render_dashboard(df, dfs, kpis, color, is_consolidated, custo_kwh, custo_pct, anon):
    """Renderiza todos os KPIs e graficos — identico para modo individual e consolidado."""

    # ── ROW 1: 4 cards principais ─────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Receita Confirmada",
                      f"R$ {kpis['revenue']:,.2f}",
                      f"{kpis['paid_sessions']:,} sessoes pagas", color)
    with c2: kpi_card("Energia Entregue",
                      f"{kpis['energy_kwh']:,.0f} kWh",
                      f"R$ {kpis['rev_per_kwh']:.2f}/kWh medio", COLORS[1])
    with c3: kpi_card("Ticket Medio",
                      f"R$ {kpis['avg_ticket']:.2f}",
                      f"{kpis['sessions_per_day']:.1f} sessoes/dia", COLORS[2])
    with c4: kpi_card("Projecao Anual",
                      f"R$ {kpis['proj_annual']:,.0f}",
                      f"baseado em {kpis['days']} dias de dados", COLORS[3])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2: 4 cards secundarios ────────────────────────────────────────────
    c5,c6,c7,c8 = st.columns(4)
    with c5: kpi_card("Conversao",
                      f"{kpis['conversion']:.1f}%",
                      f"{kpis['approval']:.1f}% do total de sessoes monetizado", COLORS[4])
    with c6: kpi_card("Usuarios Unicos",
                      f"{kpis['unique_users']:,}",
                      f"{kpis['one_time']} one-time  |  {kpis['power_users']} power users", COLORS[5])
    with c7: kpi_card("Power Users (5+ sessoes)",
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
                       f"{kpis['avg_kwh']:.1f} kWh por sessao media", COLORS[1])
    with c11: kpi_card("Receita por Ociosidade",
                       f"R$ {kpis['idle_fee']:,.2f}",
                       f"{kpis['idle_sessions']} sessoes cobradas", COLORS[3])
    with c12: kpi_card("Taxa de Reprovacao",
                       f"{kpis['rejection_rate']:.1f}%",
                       f"{kpis['not_paid']} pagamentos nao aprovados", COLORS[2])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ALERTA ────────────────────────────────────────────────────────────────
    if kpis['pending_rev'] > 0:
        st.markdown(
            f'<div class="alert-risk">&#9888; <strong>Risco financeiro:</strong> '
            f'R$ {kpis["pending_rev"]:,.2f} em pagamentos com status <em>pending</em>. '
            f'Verificar integracao de gateway nas estacoes afetadas.</div>',
            unsafe_allow_html=True
        )

    # ── RECEITA DIARIA ────────────────────────────────────────────────────────
    section("Receita Diaria")
    st.plotly_chart(fig_daily(dfs), use_container_width=True)

    # ── HORARIO + FUNIL ───────────────────────────────────────────────────────
    ca, cb = st.columns([3, 2])
    with ca:
        section("Distribuicao Horaria de Sessoes")
        st.plotly_chart(fig_hourly(dfs if is_consolidated else {list(dfs.keys())[0]: df}),
                        use_container_width=True)
    with cb:
        section("Funil de Conversao")
        st.plotly_chart(fig_funnel(kpis), use_container_width=True)

    # ── MEIOS DE PAGAMENTO + CONECTORES ───────────────────────────────────────
    cc, cd = st.columns(2)
    with cc:
        section("Meios de Pagamento")
        st.plotly_chart(fig_payment(df, color), use_container_width=True)
    with cd:
        section("Conectores (Sessoes e Receita)")
        st.plotly_chart(fig_connectors(df), use_container_width=True)

    # ── DURACAO + SEMANAL ─────────────────────────────────────────────────────
    ce, cf = st.columns(2)
    with ce:
        section("Duracao das Sessoes com Ticket Medio")
        st.plotly_chart(fig_duration(df, color), use_container_width=True)
    with cf:
        section("Evolucao Semanal (Receita e Sessoes)")
        st.plotly_chart(fig_weekly(df, color), use_container_width=True)

    # ── TOP ESTACOES ──────────────────────────────────────────────────────────
    col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
    n_stations = min(df[col_est].nunique(), 15) if col_est in df.columns else 0
    if n_stations > 0:
        cg, ch = st.columns(2)
        with cg:
            section("Top 15 Estacoes por Receita")
            st.plotly_chart(fig_top_stations(df, top_n=n_stations), use_container_width=True)
        with ch:
            section("Top 15 Estacoes por Sessoes/Dia")
            st.plotly_chart(fig_top_stations_by_sessions(df, top_n=n_stations), use_container_width=True)

        section("Taxa de Ocupacao — Top 15 Carregadores Mais Ocupados")
        st.caption("Ocupacao = tempo total em uso / (dias * 24h). Verde > 80%, Azul 50-80%, Vermelho < 50%.")
        st.plotly_chart(fig_occupancy(df, top_n=n_stations), use_container_width=True)

    # ── DIA DA SEMANA ─────────────────────────────────────────────────────────
    ci, cj = st.columns(2)
    with ci:
        section("Receita por Dia da Semana")
        st.plotly_chart(fig_weekday_revenue(df, color), use_container_width=True)
    with cj:
        section("Sessoes por Dia da Semana")
        st.plotly_chart(fig_weekday_sessions(df, color), use_container_width=True)

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
    with ck4: kpi_card("Lucro/Dia", f"R$ {total_l/max(kpis['days'],1):,.0f}", "media do periodo", COLORS[3])
    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_cost, use_container_width=True)

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
        st.plotly_chart(fig_revenue_sources(df, color), use_container_width=True)
    with col_bar:
        st.plotly_chart(fig_revenue_sources_bar(df, color), use_container_width=True)

    # ── SEGMENTACAO USUARIOS ──────────────────────────────────────────────────
    section("Segmentacao de Usuarios e Receita por Segmento")
    st.plotly_chart(fig_users(df, color, kpis['tag_col']), use_container_width=True)

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
                'Sessoes': f"{k['total_sessions']:,}",
                'Receita (R$)': f"{k['revenue']:,.2f}",
                'R$/dia': f"{k['rev_per_day']:,.0f}",
                'Ticket Medio': f"R$ {k['avg_ticket']:.2f}",
                'R$/kWh': f"{k['rev_per_kwh']:.2f}",
                'Conversao': f"{k['conversion']:.1f}%",
                'kWh Total': f"{k['energy_kwh']:,.0f}",
                'Proj. Anual': f"R$ {k['proj_annual']:,.0f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── DRE SEMANAL (transposta: indicadores=linhas, semanas=colunas) ────────────
    section("DRE — Demonstrativo de Resultado por Semana")
    dre = build_dre_table(df, custo_kwh, custo_pct)
    if len(dre) == 0:
        st.caption("Dados insuficientes para gerar a DRE.")
    else:
        semana_cols = [f"Sem {int(w)}" for w in dre['semana']]

        total_vals = {
            'Sessoes Pagas':     f"{int(dre['sessoes'].sum()):,}",
            'kWh Entregues':     f"{dre['kwh'].sum():,.1f}",
            'R$ Inicio Recarga': f"R$ {dre['r_inicio'].sum():,.2f}",
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
            ('Sessoes Pagas',     [f"{int(r['sessoes']):,}"           for _,r in dre.iterrows()], ''),
            ('kWh Entregues',     [f"{r['kwh']:,.1f}"                  for _,r in dre.iterrows()], ''),
            ('R$ Inicio Recarga', [f"R$ {r['r_inicio']:,.2f}"          for _,r in dre.iterrows()], ''),
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
    section("Exportar Relatorio")
    pdf_label = "Arquivo 01" if anon else list(dfs.keys())[0] if len(dfs)==1 else "Consolidado"
    btn_key = f"pdf_btn_{pdf_label.replace(' ','_').replace('/','_')}"
    dl_key  = f"pdf_dl_{pdf_label.replace(' ','_').replace('/','_')}"
    if st.button("Gerar PDF do Dashboard", type="primary", use_container_width=True, key=btn_key):
        with st.spinner("Gerando PDF com graficos..."):
            pdf_bytes = generate_pdf(df, kpis, custo_kwh, custo_pct,
                                     dfs=dfs, color=color, title=pdf_label)
        if pdf_bytes and not pdf_bytes[:3].isalpha():
            st.download_button(
                label="Baixar PDF",
                data=pdf_bytes,
                file_name=f"relatorio_eletropostos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=dl_key,
            )
        else:
            err = pdf_bytes.decode() if pdf_bytes else "Erro desconhecido"
            st.error(f"Erro ao gerar PDF: {err[:200]}")



# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:1rem 0 1.5rem">'
        '<div style="font-size:1.3rem;font-weight:800;color:#00C9A7">&#9889; eletropostos</div>'
        '<div style="font-size:0.62rem;color:#6B7280;margin-top:2px">dashboard financeiro</div>'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Carregar arquivos .xlsx", type=["xlsx"], accept_multiple_files=True,
        help="Arquivos de relatorio de recargas no mesmo formato exportado pelo sistema."
    )

    st.markdown("---")

    if uploaded_files:
        st.markdown('<div style="font-size:0.65rem;color:#6B7280;margin-bottom:0.5rem">ARQUIVOS CARREGADOS</div>', unsafe_allow_html=True)
        for f in uploaded_files:
            st.markdown(f'<div style="font-size:0.68rem;color:#F0F2F8;padding:3px 0">&#128196; {f.name}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.62rem;color:#6B7280">modo de analise</div>', unsafe_allow_html=True)
    mode = st.radio("", ["Por estacao (individual)", "Consolidado (todos os arquivos)"],
                    label_visibility="collapsed")

    anon = False
    if uploaded_files:
        st.markdown("---")
        anon = st.toggle("Anonimizar nomes (A, B, C...)", value=False)

    st.markdown("---")
    st.markdown('<div style="font-size:0.62rem;color:#6B7280;margin-bottom:0.5rem">PARAMETROS DE CUSTO</div>', unsafe_allow_html=True)
    custo_kwh = st.number_input("Custo da energia (R$/kWh)", min_value=0.0, value=0.75, step=0.01, format="%.2f")
    custo_pct  = st.number_input("Custo operacional (% da receita)", min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-bottom:1.5rem">'
    '<div class="page-title">Dashboard <span style="color:#00C9A7">Financeiro</span></div>'
    '<div class="page-subtitle">Rede de Eletropostos &middot; Analise de transacoes</div>'
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

# ─── FILTRO DE CONECTOR ───────────────────────────────────────────────────────
_col_conn = 'Conector(Tipo)' if 'Conector(Tipo)' in df_all.columns else None
_connector_options = sorted(df_all[_col_conn].dropna().unique().tolist()) if _col_conn else []

# Injeta lista de conectores no window.parent para o select da topbar
import json as _json
_opts_json = _json.dumps(_connector_options)
components.html(f"""
<script>
(function() {{
    window.parent.__ib_connectors = {_opts_json};
    var pdoc = window.parent.document;
    var sel = pdoc.getElementById('ib-connector-select');
    if (!sel) return;
    while (sel.options.length > 1) sel.remove(1);
    {_opts_json}.forEach(function(c) {{
        var o = pdoc.createElement('option');
        o.value = c; o.textContent = c;
        sel.appendChild(o);
    }});
    // Restaura valor atual da URL
    var url = new URL(window.parent.location.href);
    var cur = url.searchParams.get('connector') || '';
    if (cur) sel.value = cur;
}})();
</script>
""", height=0)

# Lê filtro selecionado via query_params do Streamlit
_selected_connector = st.query_params.get("connector", "")

# Aplica o filtro em df_all e em cada df dos dfs
if _selected_connector and _col_conn:
    df_all = df_all[df_all[_col_conn] == _selected_connector]
    dfs = {
        k: v[v[_col_conn] == _selected_connector] if _col_conn in v.columns else v
        for k, v in dfs.items()
    }

# ─── CONSOLIDATED VIEW ────────────────────────────────────────────────────────
if mode == "Consolidado (todos os arquivos)" or len(dfs) == 1:
    kpis = compute_kpis(df_all)
    render_dashboard(df_all, dfs, kpis, ACCENT, is_consolidated=True,
                     custo_kwh=custo_kwh, custo_pct=custo_pct, anon=anon)

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
                f'{kpis["days"]} dias &middot; {kpis["total_sessions"]:,} sessoes</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            render_dashboard(df, {name: df}, kpis, color, is_consolidated=False,
                             custo_kwh=custo_kwh, custo_pct=custo_pct, anon=anon)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="text-align:center;padding:2rem 0 1rem;font-size:0.62rem;color:#3D4560;'
    f'border-top:1px solid #1E2330;margin-top:2rem">'
    f'&#9889; eletropostos dashboard &middot; {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}'
    f'</div>',
    unsafe_allow_html=True
)
