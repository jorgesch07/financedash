# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import os
import hashlib
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = ["#00C9A7","#0088FE","#FF6B6B","#FFD93D","#A855F7","#F97316","#06B6D4","#84CC16"]
DARK_BG = "#0D0F14"; CARD_BG = "#13161D"; CARD_BORDER = "#1E2330"
TEXT_PRIMARY = "#F0F2F8"; TEXT_MUTED = "#6B7280"; ACCENT = "#00C9A7"

C = dict(
    bg=DARK_BG, card_bg=CARD_BG, card_border=CARD_BORDER,
    sidebar_bg="#0A0C10", text_primary=TEXT_PRIMARY, text_muted=TEXT_MUTED,
    grid="#1E2330", row_alt="#181B23", dre_tc=DARK_BG, dre_hdr=CARD_BORDER,
    dre_td_first="#9CA3AF", dre_border="#2D3340", dre_hover=CARD_BG,
)

# ─── CREDENCIAIS ──────────────────────────────────────────────────────────────
# Para alterar: substitua o valor pelo hash SHA-256 da nova senha.
# Gere com: python -c "import hashlib; print(hashlib.sha256(b'suasenha').hexdigest())"
def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

_CREDENTIALS: dict[str, str] = {
    # usuário : sha256(senha)
    "admin":     "9531bb8a0886f2fe7f29f91fbadf09d0903aede2f2c00e9c12d95ba785c22298",
    "comercial": "ea7d5b4094d4b7ca52588ab674da3ef3fb6d78cc4394b2776d88d7f176761964",
    "test": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
}

# Usuários que não podem remover o anonimato dos datasets pré-definidos
_RESTRICTED_USERS = {"comercial"}

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
[data-testid="InputInstructions"] { font-size:0 !important; max-width:calc(100% - 44px); }
[data-testid="InputInstructions"]::after { content:"Pressione Enter"; font-size:0.72rem; color:#6B7280; }
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

    // Substitui "Select all" → "Selecionar todos" nos dropdowns de multiselect
    // ("Pressione Enter" é tratado via CSS para não conflitar com o React)
    var selectAllPending = false;
    function applySelectAll() {
        var pd = window.parent.document;
        pd.querySelectorAll('[role="option"]').forEach(function(el) {
            if (el.textContent.trim() === 'Select all') {
                var walker = pd.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
                var node;
                while ((node = walker.nextNode())) {
                    if (node.textContent.trim() === 'Select all') {
                        node.textContent = 'Selecionar todos';
                    }
                }
            }
        });
        selectAllPending = false;
    }
    function scheduleSelectAll() {
        if (!selectAllPending) {
            selectAllPending = true;
            window.parent.requestAnimationFrame(applySelectAll);
        }
    }
    var selectAllObs = new MutationObserver(scheduleSelectAll);
    if (window.parent.document.body) {
        selectAllObs.observe(window.parent.document.body, { childList: true, subtree: true });
    }
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
    paid = df[df['paid']].copy()
    for _c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
        if _c not in paid.columns: paid[_c] = 0.0
        paid[_c] = pd.to_numeric(paid[_c], errors='coerce').fillna(0)
    paid['_rev'] = (paid['Receita(R$) por Início de Recarga']
                    + paid['Energia(kWh)'] * paid['Receita(R$) por kWh']
                    + paid['Valor Ociosidade'])
    energy = df[df['Energia(kWh)'] > 0]
    paid_e = paid[paid['Energia(kWh)'] > 0]
    attempts = df['Pago?'].isin(['sim','nao']).sum()
    days = df['data'].nunique() or 1
    total_rev = paid['_rev'].sum()
    pending_rev = df[df['pending']]['Receita(R$)'].sum()
    tag_col = 'Usuário(Tag)' if 'Usuário(Tag)' in df.columns else 'Usuário (ID)'
    user_counts = df.groupby(tag_col).size()
    kwh_total = energy['Energia(kWh)'].sum()
    rev_per_kwh = (paid_e['_rev'].sum() / paid_e['Energia(kWh)'].sum()
                   if paid_e['Energia(kWh)'].sum() > 0 else 0)
    power_rev = paid[paid[tag_col].isin(user_counts[user_counts>=5].index)]['_rev'].sum()
    return dict(
        total_sessions=len(df), paid_sessions=len(paid), revenue=total_rev,
        pending_rev=pending_rev, energy_kwh=kwh_total,
        avg_kwh=energy['Energia(kWh)'].mean() if len(energy) else 0,
        avg_ticket=paid['_rev'].mean() if len(paid) else 0,
        rev_per_kwh=rev_per_kwh, rev_per_day=total_rev/days,
        kwh_per_day=kwh_total/days,
        sessions_per_day=len(df)/days, days=days,
        conversion=len(paid)/attempts*100 if attempts else 0,
        approval=len(paid)/len(df)*100 if len(df) else 0,
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
        _paid = sdf[sdf['paid']].copy()
        for _c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
            if _c not in _paid.columns: _paid[_c] = 0.0
            _paid[_c] = pd.to_numeric(_paid[_c], errors='coerce').fillna(0)
        _paid['_rev'] = (_paid['Receita(R$) por Início de Recarga']
                         + _paid['Energia(kWh)'] * _paid['Receita(R$) por kWh']
                         + _paid['Valor Ociosidade'])
        daily = (_paid.groupby('data')['_rev'].sum()
                 .reset_index()
                 .sort_values('data'))
        daily['data'] = pd.to_datetime(daily['data'])
        c = COLORS[i % len(COLORS)]
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        fig.add_trace(go.Scatter(
            x=daily['data'], y=daily['_rev'],
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
        legend=dict(font=dict(size=9), orientation='v', yanchor='middle', y=0.5, xanchor='left', x=0.7))
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



DIAS_SEMANA = ['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo']

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
    for _c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
        if _c not in paid.columns: paid[_c] = 0.0
        paid[_c] = pd.to_numeric(paid[_c], errors='coerce').fillna(0)
    paid['_rev'] = (paid['Receita(R$) por Início de Recarga']
                    + paid['Energia(kWh)'] * paid['Receita(R$) por kWh']
                    + paid['Valor Ociosidade'])
    daily = paid.groupby('data').agg(
        receita=('_rev','sum'),
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
    )
    fig2.update_xaxes(gridcolor='#E5E5E5', linecolor='#CCC', tickfont=dict(color='#333', size=11),
                      automargin=True)
    fig2.update_yaxes(gridcolor='#E5E5E5', linecolor='#CCC', tickfont=dict(color='#333', size=11),
                      automargin=True)
    return fig2.to_image(format='png', width=w, height=h, scale=4)



def _plotly_dl(fig, filename: str) -> None:
    """Exibe o gráfico com o botão de câmera nativo do Plotly configurado para PNG 300 DPI.
    O botão aparece ao passar o mouse sobre o gráfico — sem UI extra."""
    fn = filename.replace("'", "").replace('"', "")
    st.plotly_chart(fig, width='stretch', config={
        'toImageButtonOptions': {'format': 'png', 'filename': fn, 'scale': 3.125},
        'displaylogo': False,
    })


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

        # ── Pré-computa valores de custo (usados no sumário e na seção de custos) ──
        paid_df = df[df['paid']].copy()
        for _c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
            if _c not in paid_df.columns: paid_df[_c] = 0.0
            paid_df[_c] = pd.to_numeric(paid_df[_c], errors='coerce').fillna(0)
        paid_df['_rev'] = (paid_df['Receita(R$) por Início de Recarga']
                           + paid_df['Energia(kWh)'] * paid_df['Receita(R$) por kWh']
                           + paid_df['Valor Ociosidade'])
        daily_c = paid_df.groupby('data').agg(
            receita=('_rev','sum'), kwh=('Energia(kWh)','sum')).reset_index()
        daily_c['custo'] = daily_c['receita']*(custo_pct/100) + daily_c['kwh']*custo_kwh
        daily_c['lucro'] = daily_c['receita'] - daily_c['custo']
        total_r = daily_c['receita'].sum()
        total_c = daily_c['custo'].sum()
        total_l = daily_c['lucro'].sum()
        margem  = total_l/total_r*100 if total_r else 0

        # ── Tenta carregar o logo ────────────────────────────────────────────
        _logo_img = None
        try:
            import os as _os
            _logo_local = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                        'Logomarca_Intelbras_verde (1).png')
            if _os.path.exists(_logo_local):
                _logo_img = RLImage(_logo_local, width=3.6*cm, height=1.4*cm)
            else:
                import urllib.request as _ur
                _logo_data = _ur.urlopen(
                    'https://upload.wikimedia.org/wikipedia/commons/2/2b/Logomarca_Intelbras_verde.png',
                    timeout=5).read()
                _logo_img = RLImage(io.BytesIO(_logo_data), width=3.6*cm, height=1.4*cm)
        except Exception:
            pass

        story = []

        # ── CAPA ─────────────────────────────────────────────────────────────
        story.append(Spacer(1, 0.5*cm))
        _cover_hdr_left = [
            Paragraph('RELATÓRIO FINANCEIRO', S(8, bold=True, color=C_GREY)),
        ]
        _cover_hdr_right = [_logo_img] if _logo_img else [Paragraph('', S(8))]
        _cov_tbl = Table(
            [[ _cover_hdr_left[0], _cover_hdr_right[0] ]],
            colWidths=[W - 4.2*cm, 4.2*cm],
        )
        _cov_tbl.setStyle(TableStyle([
            ('ALIGN',   (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN',  (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(_cov_tbl)
        story.append(Spacer(1, 6))
        story.append(Paragraph('Dashboard Financeiro', S(20, bold=True, color=C_BLACK)))
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

        # ── SUMÁRIO EXECUTIVO ─────────────────────────────────────────────────
        story += section_hdr('SUMÁRIO EXECUTIVO')
        _exec_items = [
            ('Período', f"{kpis['days']} dias  ·  {kpis['total_sessions']:,} sessões registradas"),
            ('Receita confirmada',
             f"R$ {kpis['revenue']:,.2f}  (R$ {kpis['rev_per_day']:,.0f}/dia de média)"),
            ('Energia entregue',
             f"{kpis['energy_kwh']:,.0f} kWh  ·  R$ {kpis['rev_per_kwh']:.2f}/kWh médio"),
            ('Ticket médio',
             f"R$ {kpis['avg_ticket']:.2f}  ·  {kpis['sessions_per_day']:.1f} sessões/dia"),
            ('Conversão',
             f"{kpis['conversion']:.1f}% de aprovação  ·  reprovação de {kpis['rejection_rate']:.1f}%"),
            ('Usuários',
             f"{kpis['unique_users']:,} únicos  ·  {kpis['power_users']} power users "
             f"({kpis['power_rev_pct']:.1f}% da receita)"),
            ('Resultado estimado',
             f"Lucro bruto de R$ {total_l:,.0f}  ·  margem de {margem:.1f}%"),
            ('Projeção anual',
             f"R$ {kpis['proj_annual']:,.0f}  (baseado no ritmo do período)"),
        ]
        if kpis['pending_rev'] > 0:
            _exec_items.append(('(!) Risco',
                f"R$ {kpis['pending_rev']:,.2f} em pagamentos pendentes — revisar gateway"))
        if kpis['idle_fee'] > 0:
            _exec_items.append(('Idle fee',
                f"R$ {kpis['idle_fee']:,.2f} em {kpis['idle_sessions']} sessões por ociosidade"))

        _exec_data = [[Paragraph(k, S(8, bold=True, color=C_GREY)),
                       Paragraph(v, S(8, color=C_BLACK))]
                      for k, v in _exec_items]
        _exec_tbl = Table(_exec_data, colWidths=[4.2*cm, W - 4.2*cm])
        _exec_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_BG),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [C_BG, C_WHITE]),
            ('GRID', (0, 0), (-1, -1), 0.3, C_BORD),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Linha de risco em tom vermelho claro
            *([('BACKGROUND', (0, len(_exec_items)-1), (-1, len(_exec_items)-1),
                rl_colors.HexColor('#FDECEA'))]
              if kpis['pending_rev'] > 0 else []),
        ]))
        story.append(_exec_tbl)
        story.append(Spacer(1, 10))

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

        # ── ANÁLISE DE CUSTOS ─────────────────────────────────────────────────
        story += section_hdr('ANÁLISE DE CUSTOS')
        story.append(kv_table([
            ['Custo energia (R$/kWh)', f"R$ {custo_kwh:.2f}",
             'Custo operacional (%)', f"{custo_pct:.1f}%"],
            ['Receita total', f"R$ {total_r:,.2f}",
             'Custo total', f"R$ {total_c:,.2f}"],
            ['Lucro bruto total', f"R$ {total_l:,.2f}",
             'Margem líquida', f"{margem:.1f}%"],
        ]))
        story.append(Spacer(1, 10))
        story.append(PageBreak())

        # ── DRE ADAPTATIVA (semana → mês → trimestre conforme espaço) ────────────
        _dre_sem = build_dre_table(df, custo_kwh, custo_pct)
        if len(_dre_sem) == 0:
            story.append(Paragraph('Dados insuficientes para gerar a DRE.', S(8, color=C_GREY)))
        else:
            _ind_w = 4.0*cm; _tot_w = 2.6*cm; _MIN_COL = 1.6*cm
            _avail  = W - _ind_w - _tot_w

            def _choose_dre():
                if len(_dre_sem) * _MIN_COL <= _avail:
                    cols = [f"Sem {int(w)}" for w in _dre_sem['semana']]
                    return _dre_sem, cols, 'POR SEMANA'
                _dre_mes = build_dre_monthly(df, custo_kwh, custo_pct)
                if len(_dre_mes) * _MIN_COL <= _avail:
                    return _dre_mes, _dre_mes['label'].tolist(), 'POR MÊS'
                _dre_tri = build_dre_quarterly(df, custo_kwh, custo_pct)
                return _dre_tri, _dre_tri['label'].tolist(), 'POR TRIMESTRE'

            _dre, _per_cols, _gran = _choose_dre()
            _n    = len(_per_cols)
            _cw   = min(_avail / max(_n, 1), _avail)
            _cw_dre = [_ind_w] + [_cw]*_n + [_tot_w]

            story += section_hdr(f'DRE — DEMONSTRATIVO DE RESULTADO {_gran}')

            _C_RED      = rl_colors.HexColor('#C0392B')
            _C_LGREEN   = rl_colors.HexColor('#D5F5ED')
            _C_LRED     = rl_colors.HexColor('#FDECEA')
            _C_LGREEN2  = rl_colors.HexColor('#EAF7F4')   # fundo suave para RECEITA BRUTA
            _C_DKGREEN2 = rl_colors.HexColor('#059669')   # texto verde mais escuro
            _C_GREY_COL = rl_colors.HexColor('#9CA3AF')   # texto neutro para desconto

            _pdf_has_voucher = (
                'desconto_voucher' in _dre.columns and _dre['desconto_voucher'].sum() > 0
            )
            _dre_totals = {
                'Sessões Pagas':           f"{int(_dre['sessoes'].sum()):,}",
                'kWh Entregues':           f"{_dre['kwh'].sum():,.1f}",
                'R$ Início Recarga':       f"R$ {_dre['r_inicio'].sum():,.2f}",
                'R$ Energia (kWh)':        f"R$ {_dre['r_kwh_rec'].sum():,.2f}",
                'R$ Ociosidade':           f"R$ {_dre['r_ocio'].sum():,.2f}",
                'RECEITA BRUTA PRESUMIDA': (f"R$ {_dre['receita_bruta_presumida'].sum():,.2f}"
                                            if _pdf_has_voucher else '–'),
                '(−) Desconto Voucher':    (f"(−) R$ {_dre['desconto_voucher'].sum():,.2f}"
                                            if _pdf_has_voucher else '–'),
                'RECEITA LÍQUIDA':         f"R$ {_dre['receita_total'].sum():,.2f}",
                '(-) Custo Energia':       f"R$ {_dre['custo_energia'].sum():,.2f}",
                '(-) Custo Operac.':       f"R$ {_dre['custo_operacional'].sum():,.2f}",
                '(=) LUCRO BRUTO':         f"R$ {_dre['lucro_bruto'].sum():,.2f}",
                'Margem (%)':              (f"{_dre['lucro_bruto'].sum()/_dre['receita_total'].sum()*100:.1f}%"
                                            if _dre['receita_total'].sum() else '–'),
            }
            _dre_inds = [
                ('Sessões Pagas',    [f"{int(r['sessoes']):,}"           for _,r in _dre.iterrows()]),
                ('kWh Entregues',    [f"{r['kwh']:,.1f}"                  for _,r in _dre.iterrows()]),
                ('R$ Início Recarga',[f"R$ {r['r_inicio']:,.2f}"          for _,r in _dre.iterrows()]),
                ('R$ Energia (kWh)', [f"R$ {r['r_kwh_rec']:,.2f}"         for _,r in _dre.iterrows()]),
                ('R$ Ociosidade',    [f"R$ {r['r_ocio']:,.2f}"            for _,r in _dre.iterrows()]),
            ]
            if _pdf_has_voucher:
                _dre_inds += [
                    ('RECEITA BRUTA PRESUMIDA',
                     [f"R$ {r['receita_bruta_presumida']:,.2f}" for _,r in _dre.iterrows()]),
                    ('(−) Desconto Voucher',
                     [f"(−) R$ {r['desconto_voucher']:,.2f}"   for _,r in _dre.iterrows()]),
                ]
            _dre_inds += [
                ('RECEITA LÍQUIDA',  [f"R$ {r['receita_total']:,.2f}"     for _,r in _dre.iterrows()]),
                ('(-) Custo Energia',[f"R$ {r['custo_energia']:,.2f}"     for _,r in _dre.iterrows()]),
                ('(-) Custo Operac.',[f"R$ {r['custo_operacional']:,.2f}" for _,r in _dre.iterrows()]),
                ('(=) LUCRO BRUTO',  [f"R$ {r['lucro_bruto']:,.2f}"       for _,r in _dre.iterrows()]),
                ('Margem (%)',       [f"{r['margem']:.1f}%"               for _,r in _dre.iterrows()]),
            ]
            _hdr_dre  = [Paragraph('Indicador', S(7, bold=True, color=C_GREY))]
            _hdr_dre += [Paragraph(s, S(7, bold=True, color=C_GREY, align=TA_RIGHT)) for s in _per_cols]
            _hdr_dre += [Paragraph('TOTAL', S(7, bold=True, color=C_GREY, align=TA_RIGHT))]
            _trows_dre = [_hdr_dre]
            _style_dre = [
                ('BACKGROUND',(0,0),(-1,0),C_HDR),
                ('GRID',(0,0),(-1,-1),0.3,C_BORD),
                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
                ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_BG,C_WHITE]),
                ('ALIGN',(1,0),(-1,-1),'RIGHT'),
            ]
            for _i, (_lbl, _vals) in enumerate(_dre_inds):
                _ri    = _i + 1
                _is_r  = _lbl == 'RECEITA LÍQUIDA'
                _is_l  = _lbl == '(=) LUCRO BRUTO'
                _is_c  = _lbl.startswith('(-)')
                _is_m  = _lbl == 'Margem (%)'
                _is_b  = _lbl == 'RECEITA BRUTA PRESUMIDA'
                _is_dv = _lbl == '(−) Desconto Voucher'
                if _is_l or _is_m:
                    _lc = C_GREEN
                elif _is_b:
                    _lc = _C_DKGREEN2
                elif _is_dv:
                    _lc = _C_GREY_COL
                elif _is_c:
                    _lc = _C_RED
                else:
                    _lc = C_BLACK
                _bold = _is_r or _is_l or _is_b
                # italic via inline markup para desconto voucher
                _lbl_txt = f'<i>{_lbl}</i>' if _is_dv else _lbl
                _val_fmt = lambda v: f'<i>{v}</i>' if _is_dv else v
                _sl = S(7, bold=_bold, color=_lc)
                _sv = S(7, bold=_bold, color=_lc, align=TA_RIGHT)
                _row  = [Paragraph(_lbl_txt, _sl)]
                _row += [Paragraph(_val_fmt(v), _sv) for v in _vals]
                _row += [Paragraph(_val_fmt(_dre_totals[_lbl]), _sv)]
                _trows_dre.append(_row)
                if _is_r or _is_l or _is_m:
                    _style_dre.append(('BACKGROUND',(0,_ri),(-1,_ri),_C_LGREEN))
                elif _is_b:
                    _style_dre.append(('BACKGROUND',(0,_ri),(-1,_ri),_C_LGREEN2))
                elif _is_c:
                    _style_dre.append(('BACKGROUND',(0,_ri),(-1,_ri),_C_LRED))
            _dre_tbl2 = Table(_trows_dre, colWidths=_cw_dre)
            _dre_tbl2.setStyle(TableStyle(_style_dre))
            story.append(_dre_tbl2)
        story.append(Spacer(1, 8))

        # ── GRAFICOS — cada um em linha própria ───────────────────────────────
        #story.append(PageBreak())
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

        #story.append(PageBreak())
        story += section_hdr('RECEITA POR DIA DA SEMANA')
        story.append(chart(fig_weekday_revenue(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        story.append(PageBreak())
        story += section_hdr('SESSÕES POR DIA DA SEMANA')
        story.append(chart(fig_weekday_sessions(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        #story.append(PageBreak())
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

        #story += section_hdr('EVOLUÇÃO SEMANAL (RECEITA E SESSÕES)')
        story.append(chart(fig_weekly(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        # Top estações
        col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
        n_st = min(df[col_est].nunique(), 15) if col_est in df.columns else 0
        if n_st > 0:
            h_st = max(5.5, n_st * 0.48)
            #story.append(PageBreak())
            story += section_hdr('TOP 15 ESTAÇÕES POR RECEITA')
            story.append(chart(fig_top_stations(df, top_n=n_st), h_cm=h_st))
            story.append(Spacer(1, 10))

            story.append(PageBreak())
            story += section_hdr('TOP 15 ESTAÇÕES POR SESSÕES/DIA')
            story.append(chart(fig_top_stations_by_sessions(df, top_n=n_st), h_cm=h_st))
            story.append(Spacer(1, 10))

            #story.append(PageBreak())
            story += section_hdr('TAXA DE OCUPAÇÃO — TOP 15 CARREGADORES')
            story.append(chart(fig_occupancy(df, top_n=n_st, horas_dia=horas_dia), h_cm=h_st))
            story.append(Spacer(1, 10))

        story += section_hdr('SEGMENTAÇÃO DE USUÁRIOS')
        story.append(chart(fig_users(df, color, kpis['tag_col']), h_cm=5.5))
        story.append(Spacer(1, 10))

        story += section_hdr('RECEITA POR ORIGEM')
        story.append(chart(fig_revenue_sources(df, color), h_cm=5.5))
        story.append(Spacer(1, 10))

        #story.append(PageBreak())
        story += section_hdr('RECEITA POR ORIGEM — EVOLUÇÃO SEMANAL')
        story.append(chart(fig_revenue_sources_bar(df, color), h_cm=5))
        story.append(Spacer(1, 10))

        # ── TABELAS ───────────────────────────────────────────────────────────
        story.append(PageBreak())

        col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
        if col_est in df.columns:
            story += section_hdr('TABELA — TOP 15 ESTAÇÕES POR RECEITA')
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
        story += section_hdr('TABELA — DISTRIBUIÇÃO POR DIA DA SEMANA')
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

        # ── VOUCHERS — LISTA DE USUÁRIOS ─────────────────────────────────────
        _pv = df[df['paid']].copy()
        for _vc in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Energia(kWh)']:
            if _vc not in _pv.columns: _pv[_vc] = 0
            _pv[_vc] = pd.to_numeric(_pv[_vc], errors='coerce').fillna(0)
        _pv['Receita(R$)'] = pd.to_numeric(_pv.get('Receita(R$)', 0), errors='coerce').fillna(0)
        _pv['is_voucher']  = _voucher_mask(_pv)
        _vdf = _pv[_pv['is_voucher']].copy()

        if len(_vdf) > 0:
            _vdf['bruta']    = (_vdf['Energia(kWh)'] * _vdf['Receita(R$) por kWh']
                                + _vdf['Receita(R$) por Início de Recarga'])
            _vdf['desconto'] = (_vdf['bruta'] - _vdf['Receita(R$)']).clip(lower=0)

            def _vtype(row):
                for _col in ['Pagamento(Tipo)', 'Origem']:
                    if _col in row.index:
                        _v = str(row.get(_col, ''))
                        if 'voucher' in _v.lower():
                            return _v
                return 'Subsídio total'
            _vdf['tipo_voucher'] = _vdf.apply(_vtype, axis=1)

            _tag_col = next((c for c in ['Usuário(Tag)', 'Usuário', 'usuario']
                             if c in _vdf.columns), None)

            story.append(PageBreak())
            story += section_hdr('VOUCHERS — DESCONTOS CONCEDIDOS')

            story.append(kv_table([
                ['Sessões com Voucher', f"{len(_vdf):,}",
                 'Desconto Total Concedido', f"R$ {_vdf['desconto'].sum():,.2f}"],
                ['Receita Bruta Hipotética', f"R$ {_vdf['bruta'].sum():,.2f}",
                 'Receita Líquida (Voucher)', f"R$ {_vdf['Receita(R$)'].sum():,.2f}"],
            ]))
            story.append(Spacer(1, 8))

            _C_RED_V = rl_colors.HexColor('#C0392B')
            if _tag_col:
                _grp = (_vdf.groupby([_tag_col, 'tipo_voucher'])
                        .agg(sessoes=('desconto','count'), kwh=('Energia(kWh)','sum'),
                             bruta=('bruta','sum'), desconto=('desconto','sum'))
                        .reset_index()
                        .sort_values('desconto', ascending=False))
                _v_hdr = [Paragraph(h, S(7, bold=True, color=C_GREY))
                          for h in ['Usuário (Voucher)', 'Sessões', 'kWh', 'Rec. Bruta', 'Desconto']]
                _v_rows = [_v_hdr]
                for _, _r in _grp.iterrows():
                    _user_label = (f"{str(_r[_tag_col])[:26]}\n"
                                   f"({str(_r['tipo_voucher'])[:30]})")
                    _v_rows.append([
                        Paragraph(_user_label, S(7)),
                        Paragraph(f"{int(_r['sessoes']):,}", S(7)),
                        Paragraph(f"{_r['kwh']:,.1f}", S(7)),
                        Paragraph(f"R$ {_r['bruta']:,.2f}", S(7)),
                        Paragraph(f"R$ {_r['desconto']:,.2f}", S(7, bold=True, color=_C_RED_V)),
                    ])
                _v_tbl = Table(_v_rows, colWidths=[6.0*cm, 1.8*cm, 1.8*cm, 3.8*cm, 4.0*cm])
            else:
                _grp = (_vdf.groupby('tipo_voucher')
                        .agg(sessoes=('desconto','count'), kwh=('Energia(kWh)','sum'),
                             bruta=('bruta','sum'), desconto=('desconto','sum'))
                        .reset_index()
                        .sort_values('desconto', ascending=False))
                _v_hdr = [Paragraph(h, S(7, bold=True, color=C_GREY))
                          for h in ['Voucher', 'Sessões', 'kWh', 'Rec. Bruta', 'Desconto']]
                _v_rows = [_v_hdr]
                for _, _r in _grp.iterrows():
                    _v_rows.append([
                        Paragraph(str(_r['tipo_voucher'])[:40], S(7)),
                        Paragraph(f"{int(_r['sessoes']):,}", S(7)),
                        Paragraph(f"{_r['kwh']:,.1f}", S(7)),
                        Paragraph(f"R$ {_r['bruta']:,.2f}", S(7)),
                        Paragraph(f"R$ {_r['desconto']:,.2f}", S(7, bold=True, color=_C_RED_V)),
                    ])
                _v_tbl = Table(_v_rows, colWidths=[6.4*cm, 2*cm, 2*cm, 3.6*cm, 3.4*cm])

            _v_tbl.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),C_HDR),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_BG, C_WHITE]),
                ('GRID',(0,0),(-1,-1),0.3,C_BORD),
                ('TOPPADDING',(0,0),(-1,-1),4),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),
                ('LEFTPADDING',(0,0),(-1,-1),6),
                ('RIGHTPADDING',(0,0),(-1,-1),6),
                ('ALIGN',(2,0),(-1,-1),'RIGHT'),
            ]))
            story.append(_v_tbl)
            story.append(Spacer(1, 10))

        # ── RODAPÉ ────────────────────────────────────────────────────────────
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width=W, thickness=0.5, color=C_BORD))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f'Dashboard financeiro  |  {datetime.date.today().strftime("%d/%m/%Y")}  |  '
            f'Relatório gerado automaticamente',
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
    labels = ['Início de Recarga', 'Venda de Energia (kWh)', 'Ociosidade']
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
    fig.add_trace(go.Bar(x=x, y=weekly['r_inicio'], name='Início de Recarga',
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

def _inspect_voucher_cols(df: pd.DataFrame) -> None:
    """Imprime no terminal valores únicos das colunas usadas para detectar voucher."""
    print("\n─── Inspeção voucher ───────────────────────────────────────────")
    for col in ['Usuário(Tag)', 'Origem', 'Pagamento(Tipo)']:
        if col in df.columns:
            vals = sorted(str(v) for v in df[col].dropna().unique()[:50])
            print(f"  {col}: {vals}")
        else:
            print(f"  {col}: [coluna não encontrada]")
    print("────────────────────────────────────────────────────────────────\n")


def _voucher_mask(df: pd.DataFrame) -> pd.Series:
    """Máscara booleana de sessões identificadas como voucher.

    Critérios (OR):
    - 'Pagamento(Tipo)' ou 'Origem' contém 'voucher' (case-insensitive)
    - kWh entregue > 0 mas Receita(R$) == 0 (subsídio total)
    """
    mask = pd.Series(False, index=df.index)
    for col in ['Pagamento(Tipo)', 'Origem']:
        if col in df.columns:
            mask |= df[col].astype(str).str.contains('voucher', case=False, na=False)
    if 'Energia(kWh)' in df.columns and 'Receita(R$)' in df.columns:
        kwh     = pd.to_numeric(df['Energia(kWh)'], errors='coerce').fillna(0)
        receita = pd.to_numeric(df['Receita(R$)'],  errors='coerce').fillna(0)
        mask   |= (kwh > 0) & (receita == 0)
    return mask


def build_dre_table(df, custo_kwh, custo_pct):
    """Monta o DataFrame da DRE semanal."""
    # Imprime colunas de voucher no terminal uma vez por sessão
    if not st.session_state.get('_voucher_inspected'):
        _inspect_voucher_cols(df)
        st.session_state['_voucher_inspected'] = True

    paid = df[df['paid']].copy()
    for c in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh','Valor Ociosidade','Energia(kWh)']:
        if c not in paid.columns: paid[c] = 0
        paid[c] = pd.to_numeric(paid[c], errors='coerce').fillna(0)
    if 'Receita(R$)' in paid.columns:
        paid['Receita(R$)'] = pd.to_numeric(paid['Receita(R$)'], errors='coerce').fillna(0)
    else:
        paid['Receita(R$)'] = 0.0

    paid['r_inicio'] = paid['Receita(R$) por Início de Recarga']
    paid['r_kwh']    = paid['Energia(kWh)'] * paid['Receita(R$) por kWh']
    paid['r_ocio']   = paid['Valor Ociosidade']
    paid['semana']   = paid['data_inicio'].dt.isocalendar().week

    # Voucher: receita bruta hipotética e desconto
    paid['is_voucher']      = _voucher_mask(paid)
    paid['bruta_sessao']    = paid['r_inicio'] + paid['r_kwh'] + paid['r_ocio']
    paid['desconto_sessao'] = np.where(
        paid['is_voucher'],
        (paid['bruta_sessao'] - paid['Receita(R$)']).clip(lower=0),
        0.0,
    )

    weekly = paid.groupby('semana').agg(
        r_inicio=('r_inicio','sum'),
        r_kwh_rec=('r_kwh','sum'),
        r_ocio=('r_ocio','sum'),
        sessoes=('Receita(R$)','count'),
        kwh=('Energia(kWh)','sum'),
        receita=('Receita(R$)','sum'),
        receita_bruta=('bruta_sessao','sum'),
        desconto_voucher=('desconto_sessao','sum'),
    ).reset_index()

    weekly['receita_total']           = weekly['r_inicio'] + weekly['r_kwh_rec'] + weekly['r_ocio']
    weekly['receita_bruta_presumida'] = weekly['receita_total'] + weekly['desconto_voucher']
    weekly['custo_energia'] = weekly['kwh'] * custo_kwh
    weekly['custo_operacional'] = weekly['receita_total'] * (custo_pct / 100)
    weekly['custo_total'] = weekly['custo_energia'] + weekly['custo_operacional']
    weekly['lucro_bruto'] = weekly['receita_total'] - weekly['custo_total']
    weekly['margem'] = weekly.apply(
        lambda r: r['lucro_bruto']/r['receita_total']*100 if r['receita_total'] else 0, axis=1)
    weekly = weekly.sort_values('semana').reset_index(drop=True)
    weekly['var_receita'] = weekly['receita_total'].pct_change() * 100
    weekly['var_lucro']   = weekly['lucro_bruto'].pct_change() * 100
    return weekly


def _dre_agg(paid, custo_kwh, custo_pct):
    """Agrega colunas financeiras comuns a todas as granularidades de DRE."""
    df = paid.copy()
    df['receita_total']           = df['r_inicio'] + df['r_kwh_rec'] + df['r_ocio']
    df['receita_bruta_presumida'] = df['receita_total'] + df['desconto_voucher']
    df['custo_energia']    = df['kwh'] * custo_kwh
    df['custo_operacional']= df['receita_total'] * (custo_pct / 100)
    df['custo_total']      = df['custo_energia'] + df['custo_operacional']
    df['lucro_bruto']      = df['receita_total'] - df['custo_total']
    df['margem']           = df.apply(
        lambda r: r['lucro_bruto']/r['receita_total']*100 if r['receita_total'] else 0, axis=1)
    return df


def _dre_paid_base(df):
    """Extrai e normaliza as colunas de receita das sessões pagas.
    Inclui colunas de voucher (bruta_sessao, desconto_sessao) para todas as granularidades.
    """
    paid = df[df['paid']].copy()
    for col in ['Receita(R$) por Início de Recarga','Receita(R$) por kWh',
                'Valor Ociosidade','Energia(kWh)']:
        if col not in paid.columns: paid[col] = 0
        paid[col] = pd.to_numeric(paid[col], errors='coerce').fillna(0)
    if 'Receita(R$)' in paid.columns:
        paid['Receita(R$)'] = pd.to_numeric(paid['Receita(R$)'], errors='coerce').fillna(0)
    else:
        paid['Receita(R$)'] = 0.0
    paid['r_inicio'] = paid['Receita(R$) por Início de Recarga']
    paid['r_kwh']    = paid['Energia(kWh)'] * paid['Receita(R$) por kWh']
    paid['r_ocio']   = paid['Valor Ociosidade']
    paid['is_voucher']      = _voucher_mask(paid)
    paid['bruta_sessao']    = paid['r_inicio'] + paid['r_kwh'] + paid['r_ocio']
    paid['desconto_sessao'] = np.where(
        paid['is_voucher'],
        (paid['bruta_sessao'] - paid['Receita(R$)']).clip(lower=0),
        0.0,
    )
    return paid


def build_dre_monthly(df, custo_kwh, custo_pct):
    """DRE agrupada por mês. Coluna 'label' = 'Jan/25' etc."""
    paid = _dre_paid_base(df)
    paid['periodo'] = paid['data_inicio'].dt.to_period('M')
    g = paid.groupby('periodo').agg(
        r_inicio=('r_inicio','sum'), r_kwh_rec=('r_kwh','sum'),
        r_ocio=('r_ocio','sum'), sessoes=('Receita(R$)','count'),
        kwh=('Energia(kWh)','sum'), receita=('Receita(R$)','sum'),
        receita_bruta=('bruta_sessao','sum'),
        desconto_voucher=('desconto_sessao','sum'),
    ).reset_index()
    g = _dre_agg(g, custo_kwh, custo_pct)
    g = g.sort_values('periodo').reset_index(drop=True)
    g['var_receita'] = g['receita_total'].pct_change() * 100
    g['var_lucro']   = g['lucro_bruto'].pct_change() * 100
    g['label'] = g['periodo'].dt.strftime('%b/%y')
    return g


def build_dre_quarterly(df, custo_kwh, custo_pct):
    """DRE agrupada por trimestre. Coluna 'label' = 'T1/25' etc."""
    paid = _dre_paid_base(df)
    paid['periodo'] = paid['data_inicio'].dt.to_period('Q')
    g = paid.groupby('periodo').agg(
        r_inicio=('r_inicio','sum'), r_kwh_rec=('r_kwh','sum'),
        r_ocio=('r_ocio','sum'), sessoes=('Receita(R$)','count'),
        kwh=('Energia(kWh)','sum'), receita=('Receita(R$)','sum'),
        receita_bruta=('bruta_sessao','sum'),
        desconto_voucher=('desconto_sessao','sum'),
    ).reset_index()
    g = _dre_agg(g, custo_kwh, custo_pct)
    g = g.sort_values('periodo').reset_index(drop=True)
    g['var_receita'] = g['receita_total'].pct_change() * 100
    g['var_lucro']   = g['lucro_bruto'].pct_change() * 100
    g['label'] = g['periodo'].apply(lambda p: f"T{p.quarter}/{str(p.year)[2:]}")
    return g


_PB_DEFAULTS = {
    'pb_n_carr': 1, 'pb_custo_hw': 15000, 'pb_custo_inst': 5000,
    'pb_pagamento': 'À vista',
    'pb_taxa_plat': 8.0, 'pb_fixo_plat': 50.0, 'pb_impostos': 6.0,
    'pb_manutencao': 100.0, 'pb_split': 0.0, 'pb_depre_anos': 10,
    'pb_taxa_juros': 12.0, 'pb_custo_kwh': 0.75,
    'pb_tarifa_kwh': 1.80, 'pb_tarifa_inicio': 0.0,
    'pb_kwh_medio': 15.0, 'pb_dur_sessao': 60.0,
    'pb_portfolio': False,
}


def _render_payback_sidebar(horas_dia):
    """Popula a sidebar com os inputs da calculadora de payback."""
    for k, v in _PB_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v
    ss = st.session_state

    st.markdown('---')
    st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">INVESTIMENTO</div>',
                unsafe_allow_html=True)
    n_carr = st.number_input('Nº de carregadores', min_value=1, step=1, key='pb_n_carr')
    custo_hw   = st.number_input('Custo unitário hardware (R$)',         min_value=0, step=500,   key='pb_custo_hw')
    custo_inst = st.number_input('Custo de instalação por unidade (R$)', min_value=0, step=500,   key='pb_custo_inst')
    inv_unit = custo_hw + custo_inst
    st.markdown(
        f'<div style="font-size:0.73rem;color:#00C9A7;margin:2px 0 4px">'
        f'Subtotal/unid: R$ {inv_unit:,.0f} &nbsp;|&nbsp; Total: R$ {inv_unit * n_carr:,.0f}</div>',
        unsafe_allow_html=True)
    pagamento = st.selectbox('Forma de pagamento', ['À vista', '10x sem juros'], key='pb_pagamento')
    if pagamento == '10x sem juros':
        st.markdown(
            f'<div style="font-size:0.70rem;color:#9CA3AF">'
            f'HW: 10× R$ {custo_hw/10:,.0f}/mês  ·  '
            f'Instalação R$ {custo_inst:,.0f} sempre à vista</div>',
            unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">CUSTOS OPERACIONAIS</div>',
                unsafe_allow_html=True)
    st.number_input('Taxa plataforma Intelbras (%)',        min_value=0.0, max_value=100.0, step=0.5, format='%.1f', key='pb_taxa_plat')
    st.number_input('Custo fixo plataforma/unid (R$/mês)', min_value=0.0, step=5.0,   format='%.0f', key='pb_fixo_plat')
    st.number_input('Custo de energia (R$/kWh)',           min_value=0.0, step=0.05,  format='%.2f', key='pb_custo_kwh')
    st.number_input('Impostos — Simples Nacional (%)',      min_value=0.0, max_value=100.0, step=0.5, format='%.1f', key='pb_impostos')
    st.number_input('Manutenção/operação por unid (R$/mês)', min_value=0.0, step=10.0, format='%.0f', key='pb_manutencao')
    st.number_input('Split com estabelecimento (%)',        min_value=0.0, max_value=100.0, step=1.0, format='%.1f', key='pb_split')
    st.number_input('Prazo de depreciação (anos)',          min_value=1,   max_value=30,   step=1,               key='pb_depre_anos')
    st.number_input('Taxa de juros / renda fixa (% a.a.)', min_value=0.0, max_value=100.0, step=0.5, format='%.1f', key='pb_taxa_juros')

    st.markdown('---')
    st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">PROJEÇÃO DE RECEITA</div>',
                unsafe_allow_html=True)
    st.number_input('Tarifa cobrada (R$/kWh)',              min_value=0.0, step=0.05, format='%.2f', key='pb_tarifa_kwh')
    st.number_input('Tarifa início de recarga (R$/sessão)', min_value=0.0, step=0.50, format='%.2f', key='pb_tarifa_inicio')
    st.number_input('kWh médio por sessão',                 min_value=0.1, step=0.5,  format='%.1f', key='pb_kwh_medio')
    st.number_input('Duração média da sessão (min)',        min_value=1.0, max_value=480.0, step=5.0, format='%.0f', key='pb_dur_sessao')
    st.markdown(f'<div style="font-size:0.70rem;color:#9CA3AF">Funcionamento: {horas_dia}h/dia (parâmetro global)</div>',
                unsafe_allow_html=True)

    st.markdown('---')
    st.toggle('Visão portfólio (total de carregadores)', key='pb_portfolio')


def render_payback(df_all=None, horas_dia=24, custo_kwh=0.75):
    """Calculadora prospectiva de payback para investimento em carregadores EV."""
    for k, v in _PB_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v
    ss = st.session_state
    n_carr        = int(ss['pb_n_carr'])
    custo_hw      = float(ss['pb_custo_hw'])
    custo_inst    = float(ss['pb_custo_inst'])
    parcelado     = ss['pb_pagamento'] == '10x sem juros'
    taxa_plat     = float(ss['pb_taxa_plat'])
    fixo_plat     = float(ss['pb_fixo_plat'])
    impostos_pct  = float(ss['pb_impostos'])
    manutencao    = float(ss['pb_manutencao'])
    split_pct     = float(ss['pb_split'])
    depre_anos    = int(ss['pb_depre_anos'])
    taxa_juros    = float(ss['pb_taxa_juros'])
    tarifa_kwh    = float(ss['pb_tarifa_kwh'])
    tarifa_inicio = float(ss['pb_tarifa_inicio'])
    kwh_medio     = float(ss['pb_kwh_medio'])
    dur_sessao    = float(ss['pb_dur_sessao'])
    portfolio     = bool(ss['pb_portfolio'])
    custo_kwh     = float(ss['pb_custo_kwh'])   # sobrescreve parâmetro global

    inv_unit     = custo_hw + custo_inst
    inv_total    = inv_unit * n_carr
    depre_mensal = inv_total / max(depre_anos * 12, 1)
    mult         = n_carr if portfolio else 1
    inv_display  = inv_total if portfolio else inv_unit
    # Instalação sempre à vista; hardware pode ser parcelado
    hw_display   = (custo_hw   * n_carr) if portfolio else custo_hw
    inst_display = (custo_inst * n_carr) if portfolio else custo_inst

    # ── Dados reais ──────────────────────────────────────────────────────────────
    occ_real   = None
    banner_txt = None
    if df_all is not None and len(df_all) > 0:
        paid_df = df_all[df_all['paid']].copy()
        for _c in ['Energia(kWh)', 'Receita(R$) por kWh', 'Receita(R$) por Início de Recarga', 'Valor Ociosidade']:
            if _c not in paid_df.columns: paid_df[_c] = 0.0
            paid_df[_c] = pd.to_numeric(paid_df[_c], errors='coerce').fillna(0)
        col_est  = 'Estação' if 'Estação' in df_all.columns else ('Estacao' if 'Estacao' in df_all.columns else None)
        n_stat   = max(df_all[col_est].nunique(), 1) if col_est else 1
        days     = df_all['data'].nunique() or 1
        min_used = df_all['duracao_min'].sum() if 'duracao_min' in df_all.columns else 0
        min_avail = days * horas_dia * 60 * n_stat
        occ_real  = min(min_used / min_avail * 100, 100) if min_avail > 0 else None
        dt0 = df_all['data'].min().strftime('%d/%m/%y')
        dt1 = df_all['data'].max().strftime('%d/%m/%y')
        banner_txt = f"Usando dados de {len(paid_df):,} sessões pagas · {dt0} – {dt1}"

    # ── Renda fixa: taxa mensal e histórico de referência ────────────────────────
    _rf_m = (1 + taxa_juros / 100) ** (1 / 12) - 1  # taxa mensal equivalente

    def _rf_hist(n_meses):
        """Acumulado da renda fixa: mesma saída de caixa que o investimento."""
        h = [0.0 if parcelado else -inv_display]
        for m in range(1, n_meses + 1):
            parc_rf = (inv_display / 10) if parcelado and m <= 10 else 0.0
            h.append(h[-1] - parc_rf + inv_display * _rf_m * (m if parcelado else 1))
        return h

    # ── Cálculo de cenário ────────────────────────────────────────────────────────
    def _calc(occ_pct):
        sess     = (horas_dia * 30 * 60 / max(dur_sessao, 1)) * (occ_pct / 100)
        kwh_m    = sess * kwh_medio
        rec      = kwh_m * tarifa_kwh + sess * tarifa_inicio
        ded_taxa = rec * taxa_plat / 100
        ded_imp  = rec * impostos_pct / 100
        ded_spl  = rec * split_pct / 100
        ded_en   = kwh_m * custo_kwh
        # DRE: EBITDA antes de impostos e D&A; impostos sempre calculados sobre receita bruta
        ROL      = rec - ded_spl
        LB       = ROL - ded_en
        EBITDA   = LB - (ded_taxa + fixo_plat + manutencao)
        DA       = depre_mensal / n_carr        # sempre por unidade; *mult no return dict
        EBIT     = EBITDA - DA                  # pré-imposto; base para ROIC
        LL       = EBIT - ded_imp               # lucro líquido por unidade
        marg_u   = rec - ded_taxa - fixo_plat - ded_imp - ded_en - ded_spl - manutencao
        # Retorno acumulado (base econômica, inclui depreciação):
        # D0: instalação sempre à vista; parcelado financia só o hardware
        hist     = [-inst_display if parcelado else -inv_display]
        pb       = None
        for mes in range(1, 241):
            parc = (custo_hw / 10) * mult if parcelado and mes <= 10 else 0.0
            hist.append(hist[-1] + LL * mult - parc)
            if pb is None and hist[-1] >= 0:
                pb = mes
        return dict(
            occ=occ_pct, rec=rec*mult, marg=marg_u*mult, pb=pb, hist=hist,
            sess=sess*mult, kwh_m=kwh_m*mult,
            ded_taxa=ded_taxa*mult, ded_imp=ded_imp*mult,
            ded_spl=ded_spl*mult, ded_en=ded_en*mult,
            man=manutencao*mult, fixo=fixo_plat*mult,
            ROL=ROL*mult, LB=LB*mult, mg_bruta=(LB/ROL*100 if ROL else 0),
            EBITDA=EBITDA*mult, mg_ebitda=(EBITDA/ROL*100 if ROL else 0),
            DA=DA*mult, EBIT=EBIT*mult, LL=LL*mult,
            mg_liq=(LL/ROL*100 if ROL else 0),
            ROIC_aa=(EBIT*12/inv_display*100 if inv_display else 0),
            parc=(custo_hw/10)*mult if parcelado else 0.0,
        )

    OCCS       = [10, 20, 40, 60]
    OCC_LABELS = ['10% — conservador', '20% — moderado', '40% — otimista', '60% — agressivo']
    OCC_COLORS = [COLORS[2], COLORS[3], COLORS[1], COLORS[0]]
    scenarios  = [_calc(o) for o in OCCS]
    if occ_real is not None:
        scenarios.append(_calc(occ_real))
        OCC_LABELS.append(f'{occ_real:.1f}% — real observado')
        OCC_COLORS.append(COLORS[4])

    # ── Banner ────────────────────────────────────────────────────────────────────
    if banner_txt:
        st.markdown(
            f'<div style="background:#1A2640;border:1px solid #2D3340;border-radius:8px;'
            f'padding:0.5rem 1rem;font-size:0.72rem;color:#9CA3AF;margin-bottom:1rem">'
            f'&#128202; {banner_txt}</div>', unsafe_allow_html=True)

    mode_lbl = "Portfólio total" if portfolio else "Por carregador"
    section(f"Payback — Retorno sobre Investimento ({mode_lbl})")
    if portfolio:
        inv_info = (f'Investimento total: <span style="color:#F0F2F8;font-weight:700">R$ {inv_total:,.0f}</span> '
                    f'({n_carr} carregador{"es" if n_carr>1 else ""} × R$ {inv_unit:,.0f})')
    else:
        inv_info = (f'Investimento unitário: <span style="color:#F0F2F8;font-weight:700">R$ {inv_unit:,.0f}</span>')
    if parcelado:
        inv_info += (f'  ·  HW 10× R$ {(hw_display/10):,.0f}'
                     f'  +  inst. R$ {inst_display:,.0f} à vista')
    st.markdown(f'<div style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem">{inv_info}</div>',
                unsafe_allow_html=True)

    # ── Cards de cenário ──────────────────────────────────────────────────────────
    cols = st.columns(len(scenarios))
    for col, sc, lbl, clr in zip(cols, scenarios, OCC_LABELS, OCC_COLORS):
        pb = sc['pb']
        if pb is None:
            pb_str    = '> 20 anos'
            card_clr  = COLORS[2]
        elif pb <= 36:
            pb_str    = f'{pb}m  ({pb/12:.1f}a)'
            card_clr  = COLORS[0]
        elif pb <= 60:
            pb_str    = f'{pb}m  ({pb/12:.1f}a)'
            card_clr  = COLORS[3]
        else:
            pb_str    = f'{pb}m  ({pb/12:.1f}a)'
            card_clr  = COLORS[2]
        with col:
            kpi_card(
                f"Ocupação {lbl.split('—')[0].strip()}",
                pb_str,
                f"Rec R$ {sc['rec']:,.0f}/mês · Margem R$ {sc['marg']:,.0f}/mês",
                card_clr,
            )
    st.markdown('<br>', unsafe_allow_html=True)

    # ── Gráfico acumulado ─────────────────────────────────────────────────────────
    section('Evolução do Retorno Acumulado')
    max_pb   = max((sc['pb'] or 240) for sc in scenarios)
    x_limit  = min(int(max_pb * 1.3) + 12, 240)
    fig = go.Figure()
    for sc, lbl, clr in zip(scenarios, OCC_LABELS, OCC_COLORS):
        xs = list(range(min(len(sc['hist']), x_limit + 1)))
        ys = sc['hist'][:x_limit + 1]
        r, g, b = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
        is_real = 'real' in lbl
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            name=lbl.split('—')[0].strip(),
            mode='lines',
            line=dict(color=clr, width=2, dash='dash' if is_real else 'solid'),
            fillcolor=f'rgba({r},{g},{b},0.04)',
        ))
        if sc['pb'] and sc['pb'] <= x_limit:
            fig.add_annotation(
                x=sc['pb'], y=0, text=f"{sc['pb']}m",
                showarrow=True, arrowhead=2, arrowsize=0.8,
                arrowcolor=clr, font=dict(color=clr, size=14), ax=0, ay=-28,
            )
    # Renda fixa: ganho líquido = inv_display*(1+_rf_m)^m - inv_display
    rf_ys = [inv_display * ((1 + _rf_m) ** m - 1) for m in range(x_limit + 1)]
    fig.add_trace(go.Scatter(
        x=list(range(x_limit + 1)), y=rf_ys,
        name=f'Renda Fixa {taxa_juros:.1f}% a.a.',
        mode='lines',
        line=dict(color='#6B7280', width=1.5, dash='longdash'),
    ))
    fig.add_hline(y=0, line=dict(color='#3D4451', dash='dot', width=1))
    fig.update_layout(**PLOTLY_LAYOUT, height=340)
    fig.update_xaxes(title_text='Meses', gridcolor='#1E2330', linecolor='#1E2330')
    fig.update_yaxes(tickprefix='R$ ', tickformat=',.0f', gridcolor='#1E2330', linecolor='#1E2330')
    st.plotly_chart(fig, width='stretch')

    # ── VPL & TIR ────────────────────────────────────────────────────────────────
    # Horizonte de análise = vida útil do equipamento (depre_anos × 12 meses)
    eol_m = depre_anos * 12

    def _npv_sc(sc):
        """VPL — traz cada FCL mensal a valor presente usando _rf_m como taxa de desconto.
        CF_0 = -inst_display (parcelado, instalação à vista) ou -inv_display (à vista)."""
        pv = -inst_display if parcelado else -inv_display
        for m in range(1, eol_m + 1):
            parc = sc['parc'] if parcelado and m <= 10 else 0.0
            pv  += (sc['marg'] - parc) / (1 + _rf_m) ** m
        return pv

    def _irr_annual(sc):
        """TIR — bissecção para encontrar a taxa mensal r tal que VPL(r)=0;
        converte para taxa anual efetiva: (1+r_mensal)^12 - 1."""
        cfs = [-inst_display if parcelado else -inv_display]
        for m in range(1, eol_m + 1):
            parc = sc['parc'] if parcelado and m <= 10 else 0.0
            cfs.append(sc['marg'] - parc)
        def _npv_r(r):
            return sum(c / (1 + r) ** t for t, c in enumerate(cfs))
        lo, hi = -0.9999, 10.0
        try:
            # Verifica se existe raiz real no intervalo
            if _npv_r(lo) * _npv_r(hi) > 0:
                return None
            # Bissecção com convergência de 1e-9
            for _ in range(200):
                mid = (lo + hi) / 2
                if abs(hi - lo) < 1e-9:
                    break
                if _npv_r(lo) * _npv_r(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            r_m = (lo + hi) / 2
            return (1 + r_m) ** 12 - 1   # taxa anual efetiva
        except Exception:
            return None

    with st.expander(f'VPL & TIR — Análise de Valor ({depre_anos} anos · TMA {taxa_juros:.1f}% a.a.)', expanded=False):
        st.markdown(
            f'<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.4rem">'
            f'VPL — Valor Presente Líquido (taxa de desconto: {taxa_juros:.1f}% a.a.)</div>',
            unsafe_allow_html=True)
        _vpl_cols = st.columns(len(scenarios))
        for _col, _sc, _lbl, _ in zip(_vpl_cols, scenarios, OCC_LABELS, OCC_COLORS):
            _npv = _npv_sc(_sc)
            _nc  = COLORS[0] if _npv >= 0 else COLORS[2]
            with _col:
                kpi_card(
                    _lbl.split('—')[0].strip(),
                    f'R$ {_npv:,.0f}',
                    'VPL > 0 → cria valor' if _npv >= 0 else 'VPL < 0 → destrói valor',
                    _nc,
                )
        st.markdown('<br>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.4rem">'
            f'TIR — Taxa Interna de Retorno  ·  benchmark: Renda Fixa {taxa_juros:.1f}% a.a.</div>',
            unsafe_allow_html=True)
        _tir_cols = st.columns(len(scenarios))
        for _col, _sc, _lbl in zip(_tir_cols, scenarios, OCC_LABELS):
            _tir = _irr_annual(_sc)
            if _tir is None:
                _ts, _tc, _sub = 'N/D', COLORS[5], 'payback não atingido no período'
            elif _tir * 100 > taxa_juros:
                _ts  = f'{_tir*100:.1f}% a.a.'
                _tc  = COLORS[0]
                _sub = f'supera RF em {_tir*100 - taxa_juros:.1f}pp'
            elif _tir > 0:
                _ts  = f'{_tir*100:.1f}% a.a.'
                _tc  = COLORS[3]
                _sub = f'abaixo da RF em {taxa_juros - _tir*100:.1f}pp'
            else:
                _ts  = f'{_tir*100:.1f}% a.a.'
                _tc  = COLORS[2]
                _sub = 'retorno negativo no período'
            with _col:
                kpi_card(_lbl.split('—')[0].strip(), _ts, _sub, _tc)
        st.markdown('<br>', unsafe_allow_html=True)

        st.markdown(
            '<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.4rem">'
            'Fluxo de Caixa Livre — selecione o cenário</div>',
            unsafe_allow_html=True)
        _sc_dcf_lbl = st.selectbox('', OCC_LABELS, key='pb_sel_dcf', label_visibility='collapsed')
        _sc_dcf = scenarios[OCC_LABELS.index(_sc_dcf_lbl)]
        # D0: instalação à vista (parcelado) ou investimento total (à vista)
        _d0      = -inst_display if parcelado else -inv_display
        _mon_cf  = [_d0]
        _mon_dcf = [_d0]    # D0 já está em valor presente
        _xs      = [0]
        for _m in range(1, eol_m + 1):
            _par = _sc_dcf['parc'] if parcelado and _m <= 10 else 0.0
            _cf  = _sc_dcf['marg'] - _par
            _mon_cf.append(_cf)
            _mon_dcf.append(_cf / (1 + _rf_m) ** _m)
            _xs.append(_m)
        _fig_dcf = go.Figure()
        _fig_dcf.add_trace(go.Bar(
            x=_xs, y=_mon_cf,
            name='FCL nominal', marker_color='rgba(0,201,167,0.22)',
        ))
        _fig_dcf.add_trace(go.Bar(
            x=_xs, y=_mon_dcf,
            name='FCL descontado', marker_color='#00C9A7',
        ))
        _fig_dcf.add_hline(y=0, line=dict(color='#6B7280', dash='dot', width=1))
        _fig_dcf.update_layout(**PLOTLY_LAYOUT, height=300, barmode='overlay',
                               xaxis_title='Mês', yaxis_tickprefix='R$ ', yaxis_tickformat=',.0f')
        st.plotly_chart(_fig_dcf, width='stretch')

    # ── DRE padrão ouro ───────────────────────────────────────────────────────────
    section('DRE — Demonstrativo de Resultado (Mensal)')
    sel_lbl = st.selectbox('Cenário', OCC_LABELS, key='pb_sel_dre', label_visibility='collapsed')
    sc  = scenarios[OCC_LABELS.index(sel_lbl)]
    # (label, value, is_ded, is_tot, is_pct)
    dre_rows = []
    if split_pct > 0:
        dre_rows.append(('Receita operacional bruta',     f"R$ {sc['rec']:,.2f}",           False, False, False))
        dre_rows.append(('(−) Split estabelecimento',     f"(−) R$ {sc['ded_spl']:,.2f}",   True,  False, False))
    dre_rows += [
        ('ROL — Receita Operacional Líquida',     f"R$ {sc['ROL']:,.2f}",           False, True,  False),
        ('(−) Custo energia (CPV)',                f"(−) R$ {sc['ded_en']:,.2f}",   True,  False, False),
        ('(=) LUCRO BRUTO',                       f"R$ {sc['LB']:,.2f}",            False, True,  False),
        ('    Margem Bruta',                      f"{sc['mg_bruta']:.1f}%",         False, False, True),
        ('(−) Taxa plataforma',                   f"(−) R$ {sc['ded_taxa']:,.2f}",  True,  False, False),
        ('(−) Custo fixo plataforma',             f"(−) R$ {sc['fixo']:,.2f}",      True,  False, False),
        ('(−) Manutenção / operação',             f"(−) R$ {sc['man']:,.2f}",       True,  False, False),
        ('(=) EBITDA',                            f"R$ {sc['EBITDA']:,.2f}",        False, True,  False),
        ('    Margem EBITDA',                     f"{sc['mg_ebitda']:.1f}%",        False, False, True),
        ('(−) Depreciação (D&A)',                 f"(−) R$ {sc['DA']:,.2f}",        True,  False, False),
        ('(−) Impostos s/ receita bruta',         f"(−) R$ {sc['ded_imp']:,.2f}",   True,  False, False),
        ('(=) LUCRO LÍQUIDO',                     f"R$ {sc['LL']:,.2f}",            False, True,  False),
        ('    Margem Líquida',                    f"{sc['mg_liq']:.1f}%",           False, False, True),
        ('    ROIC pré-tax (a.a.)',               f"{sc['ROIC_aa']:.1f}%",          False, False, True),
    ]
    if parcelado:
        dre_rows.append(('    [memo] Parcela financ. (1–10)', f"(−) R$ {sc['parc']:,.2f}", True, False, False))

    html = ('<div class="dre-t"><table style="width:100%;border-collapse:collapse">'
            '<tr><th style="text-align:left;padding:6px 8px;font-size:0.72rem;color:#6B7280">Indicador</th>'
            '<th style="text-align:right;padding:6px 8px;font-size:0.72rem;color:#6B7280">Valor/Mês</th></tr>')
    for i, (lbl_r, val_r, is_ded, is_tot, is_pct) in enumerate(dre_rows):
        bg  = 'rgba(0,201,167,0.06)' if is_tot else ('#181B23' if i % 2 else '#13161D')
        lc  = '#00C9A7' if is_tot else ('#4B9EFF' if is_pct else ('#9CA3AF' if is_ded else '#F0F2F8'))
        vc  = '#4B9EFF' if is_pct else ('#FF6B6B' if (is_ded and not is_tot) else ('#00C9A7' if is_tot else '#F0F2F8'))
        fw  = '700' if is_tot else '400'
        html += (f'<tr style="background:{bg}">'
                 f'<td style="padding:5px 8px;font-size:0.72rem;color:{lc};font-weight:{fw}">{lbl_r}</td>'
                 f'<td style="padding:5px 8px;font-size:0.72rem;color:{vc};text-align:right;font-weight:{fw}">{val_r}</td>'
                 f'</tr>')
    html += '</table></div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # ── Comparativo: Carregador vs Renda Fixa ─────────────────────────────────────
    section(f'Comparativo: Carregador vs Renda Fixa ({taxa_juros:.1f}% a.a.)')
    st.markdown(
        '<div style="font-size:0.72rem;color:#6B7280;margin-bottom:0.75rem">'
        '⚠️ Valores nominais (não descontados) ao final da vida útil.</div>',
        unsafe_allow_html=True)
    rf_eol    = inv_display * ((1 + _rf_m) ** eol_m - 1)
    rf_mensal = inv_display * _rf_m

    c_rf, c_oc, c_delta = st.columns(3)
    with c_rf:
        kpi_card(
            f'Renda Fixa — {depre_anos} anos',
            f'R$ {rf_eol:,.0f}',
            f'Rendimento total · R$ {rf_mensal:,.0f}/mês equiv.',
            COLORS[5],
        )
    best_sc  = max(scenarios, key=lambda s: s['hist'][min(eol_m, len(s['hist']) - 1)])
    best_eol = best_sc['hist'][min(eol_m, len(best_sc['hist']) - 1)]
    best_lbl = OCC_LABELS[scenarios.index(best_sc)].split('—')[0].strip()
    with c_oc:
        kpi_card(
            f'Carregador ({best_lbl}) — {depre_anos} anos',
            f'R$ {best_eol:,.0f}',
            f'Retorno líquido acumulado em {depre_anos} anos',
            COLORS[0] if best_eol > rf_eol else COLORS[2],
        )
    delta = best_eol - rf_eol
    with c_delta:
        kpi_card(
            'Vantagem vs Renda Fixa',
            f'{"+" if delta >= 0 else ""}R$ {delta:,.0f}',
            f'{"Carregador supera RF" if delta >= 0 else "RF supera o carregador"} · cenário {best_lbl}',
            COLORS[0] if delta >= 0 else COLORS[2],
        )
    st.markdown('<br>', unsafe_allow_html=True)

    # tabela comparativa todos os cenários
    _cmp_rows = []
    for _sc, _lbl in zip(scenarios, OCC_LABELS):
        _sc_eol = _sc['hist'][min(eol_m, len(_sc['hist']) - 1)]
        _d      = _sc_eol - rf_eol
        _cmp_rows.append({
            'Cenário':                       _lbl,
            f'Carregador {depre_anos}a (R$)': f'{_sc_eol:,.0f}',
            f'Renda Fixa {depre_anos}a (R$)': f'{rf_eol:,.0f}',
            'Diferença (R$)':               f'{"▲ " if _d >= 0 else "▼ "}{abs(_d):,.0f}',
            'Melhor':                        '⚡ Carregador' if _d >= 0 else '📈 Renda Fixa',
        })
    st.dataframe(pd.DataFrame(_cmp_rows).set_index('Cenário'), use_container_width=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # ── Sensibilidade ─────────────────────────────────────────────────────────────
    section('Análise de Sensibilidade — Payback (meses)')
    tarifas_s = [1.20, 1.50, 1.80, 2.10, 2.50]
    occs_s    = [10, 20, 40, 60]

    def _pb_sens(tar, occ_pct):
        hm      = horas_dia * 30
        dur_med = max(dur_sessao, 5)
        sess    = (hm * 60 / dur_med) * (occ_pct / 100)
        kwh_m   = sess * kwh_medio
        rec     = kwh_m * tar + sess * tarifa_inicio
        ded     = (rec * taxa_plat / 100 + fixo_plat + rec * impostos_pct / 100
                   + kwh_m * custo_kwh + rec * split_pct / 100 + manutencao)
        marg    = (rec - ded) * mult
        if marg <= 0:
            return None
        acc = -inst_display if parcelado else -inv_display
        for mes in range(1, 241):
            parc = (custo_hw / 10) * mult if parcelado and mes <= 10 else 0.0
            acc += marg - parc
            if acc >= 0:
                return mes
        return None

    sens_rows = {}
    for tar in tarifas_s:
        row = {}
        for occ in occs_s:
            v = _pb_sens(tar, occ)
            row[f'{occ}%'] = v if v is not None else 999
        sens_rows[f'R$ {tar:.2f}/kWh'] = row
    df_sens = pd.DataFrame(sens_rows).T

    def _color_pb(v):
        if v >= 999:  return 'background-color:#3D1515;color:#FF6B6B'
        if v <= 36:   return 'background-color:#0D2B1A;color:#00C9A7'
        if v <= 60:   return 'background-color:#2B2510;color:#FFD93D'
        return             'background-color:#2B1810;color:#FF6B6B'

    styled = (df_sens.style
              .map(_color_pb)
              .format(lambda v: '> 20a' if v >= 999 else f'{int(v)}m'))
    st.dataframe(styled, use_container_width=True)



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
    _plotly_dl(fig_daily(dfs), "receita_diaria")

    # ── HORARIO + FUNIL ───────────────────────────────────────────────────────
    ca, cb = st.columns([3, 2])
    with ca:
        section("Distribuição Horária de Sessões")
        _plotly_dl(fig_hourly(dfs if is_consolidated else {list(dfs.keys())[0]: df}),
                   "distribuicao_horaria")
    with cb:
        section("Funil de Conversão")
        _plotly_dl(fig_funnel(kpis), "funil_conversao")

    # ── MEIOS DE PAGAMENTO + CONECTORES ───────────────────────────────────────
    cc, cd = st.columns(2)
    with cc:
        section("Meios de Pagamento")
        _plotly_dl(fig_payment(df, color), "meios_pagamento")
    with cd:
        section("Conectores (Sessões e Receita)")
        _plotly_dl(fig_connectors(df), "conectores")

    # ── DURACAO + SEMANAL ─────────────────────────────────────────────────────
    ce, cf = st.columns(2)
    with ce:
        section("Duração das Sessões com Ticket Médio")
        _plotly_dl(fig_duration(df, color), "duracao_sessoes")
    with cf:
        section("Evolução Semanal (Receita e Sessões)")
        _plotly_dl(fig_weekly(df, color), "evolucao_semanal")

    # ── TOP ESTACOES ──────────────────────────────────────────────────────────
    col_est = 'Estação' if 'Estação' in df.columns else 'Estacao'
    n_stations = min(df[col_est].nunique(), 15) if col_est in df.columns else 0
    if n_stations > 0:
        cg, ch = st.columns(2)
        with cg:
            section("Top 15 Estações por Receita")
            _plotly_dl(fig_top_stations(df, top_n=n_stations), "top_estacoes_receita")
        with ch:
            section("Top 15 Estações por Sessões/Dia")
            _plotly_dl(fig_top_stations_by_sessions(df, top_n=n_stations), "top_estacoes_sessoes")

        section(f"Taxa de Ocupação — Top 15 Carregadores ({horas_dia}h/dia uteis)")
        _plotly_dl(fig_occupancy(df, top_n=n_stations, horas_dia=horas_dia), "ocupacao")

    # ── DIA DA SEMANA ─────────────────────────────────────────────────────────
    ci, cj = st.columns(2)
    with ci:
        section("Receita por Dia da Semana")
        _plotly_dl(fig_weekday_revenue(df, color), "receita_dia_semana")
    with cj:
        section("Sessões por Dia da Semana")
        _plotly_dl(fig_weekday_sessions(df, color), "sessoes_dia_semana")

    # ── RECEITA VS CUSTO VS LUCRO ─────────────────────────────────────────────
    section("Receita vs Custo vs Lucro")
    fig_cost, daily_cost = fig_revenue_cost_profit(df, custo_kwh, custo_pct)
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
    _plotly_dl(fig_cost, "receita_custo_lucro")

    # ── RECEITA POR ORIGEM ────────────────────────────────────────────────────
    section("Receita por Origem")
    r_inicio, r_kwh, r_ocio = _revenue_sources(df)
    total_src = r_inicio + r_kwh + r_ocio
    rs1, rs2, rs3 = st.columns(3)
    with rs1: kpi_card("Início de Recarga",
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
        _plotly_dl(fig_revenue_sources(df, color), "receita_por_origem")
    with col_bar:
        _plotly_dl(fig_revenue_sources_bar(df, color), "receita_origem_semanal")

    # ── SEGMENTACAO USUARIOS ──────────────────────────────────────────────────
    section("Segmentação de Usuarios e Receita por Segmento")
    _plotly_dl(fig_users(df, color, kpis['tag_col']), "segmentacao_usuarios")

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
    dre     = build_dre_table(df, custo_kwh, custo_pct)
    dre_mes = build_dre_monthly(df, custo_kwh, custo_pct)

    def _var_cell(val):
        if pd.isna(val):
            return '–'
        color = '#00C9A7' if val >= 0 else '#FF6B6B'
        sign  = '+' if val >= 0 else ''
        return f'<span style="color:{color}">{sign}{val:.1f}%</span>'

    def _dre_html(data, period_cols, total_vals, indicadores_list):
        th_cols = "".join(f"<th>{s}</th>" for s in period_cols)
        header  = f"<th>Indicador</th>{th_cols}<th class='tc'>TOTAL</th>"
        rows_html = ""
        for label, vals, row_type in indicadores_list:
            row_cls = f" class='row-{row_type}'" if row_type else ""
            cells   = f"<td>{label}</td>"
            cells  += "".join(f"<td>{v}</td>" for v in vals)
            cells  += f"<td class='tc'>{total_vals[label]}</td>"
            rows_html += f"<tr{row_cls}>{cells}</tr>"
        var_rec = "".join(f"<td>{_var_cell(r['var_receita'])}</td>" for _,r in data.iterrows())
        var_luc = "".join(f"<td>{_var_cell(r['var_lucro'])}</td>"   for _,r in data.iterrows())
        rows_html += (
            f"<tr class='row-var'><td>▲ Var% Receita</td>{var_rec}<td class='tc'>–</td></tr>"
            f"<tr class='row-var'><td>▲ Var% Lucro</td>{var_luc}<td class='tc'>–</td></tr>"
        )
        return (
            f'<div style="overflow-x:auto"><table class="dre-t">'
            f'<thead><tr>{header}</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            f'</table></div>'
        )

    st.markdown(f"""
    <style>
    .dre-t{{width:100%;border-collapse:collapse;font-size:0.72rem;font-family:monospace;}}
    .dre-t th{{background:{C['dre_hdr']};color:{C['text_muted']};text-transform:uppercase;
              letter-spacing:.06em;padding:7px 14px;text-align:right;
              border-bottom:1px solid {C['dre_border']};white-space:nowrap;}}
    .dre-t th:first-child{{text-align:left;min-width:170px;}}
    .dre-t td{{padding:5px 14px;border-bottom:1px solid {C['dre_border']};
              color:{C['text_primary']};text-align:right;white-space:nowrap;}}
    .dre-t td:first-child{{text-align:left;color:{C['dre_td_first']};font-weight:500;}}
    .dre-t .tc{{background:{C['card_bg']}!important;font-weight:700;
               border-left:1px solid {C['dre_border']};}}
    .dre-t .row-receita td{{background:rgba(0,201,167,0.04);}}
    .dre-t .row-receita td:first-child{{color:{C['text_primary']};font-weight:700;}}
    .dre-t .row-lucro td{{background:rgba(0,201,167,0.07);}}
    .dre-t .row-lucro td:first-child,.dre-t .row-lucro .tc{{color:#00C9A7;font-weight:700;}}
    .dre-t .row-custo td:first-child,.dre-t .row-custo .tc{{color:#FF6B6B;}}
    .dre-t .row-var td{{background:rgba(168,85,247,0.04);font-size:0.68rem;}}
    .dre-t .row-var td:first-child{{color:{C['text_muted']};font-style:italic;}}
    .dre-t .row-desconto td:first-child{{color:#9CA3AF;font-style:italic;}}
    .dre-t .row-bruta-hipo td{{background:rgba(0,201,167,0.025);}}
    .dre-t .row-bruta-hipo td:first-child{{color:#34D399;font-weight:700;}}
    .dre-t tr:hover td{{background:{C['dre_hover']}!important;}}
    </style>
    """, unsafe_allow_html=True)

    if len(dre) == 0:
        st.caption("Dados insuficientes para gerar a DRE.")
    else:
        semana_cols  = [f"Sem {int(w)}" for w in dre['semana']]
        _has_voucher = dre['desconto_voucher'].sum() > 0

        total_sem = {
            'Sessões Pagas':           f"{int(dre['sessoes'].sum()):,}",
            'kWh Entregues':           f"{dre['kwh'].sum():,.1f}",
            'R$ Início Recarga':       f"R$ {dre['r_inicio'].sum():,.2f}",
            'R$ Energia (kWh)':        f"R$ {dre['r_kwh_rec'].sum():,.2f}",
            'R$ Ociosidade':           f"R$ {dre['r_ocio'].sum():,.2f}",
            'RECEITA BRUTA PRESUMIDA': f"R$ {dre['receita_bruta_presumida'].sum():,.2f}",
            '(−) Desconto Voucher':    f"(−) R$ {dre['desconto_voucher'].sum():,.2f}",
            'RECEITA LÍQUIDA':         f"R$ {dre['receita_total'].sum():,.2f}",
            '(-) Custo Energia':       f"R$ {dre['custo_energia'].sum():,.2f}",
            '(-) Custo Operac.':       f"R$ {dre['custo_operacional'].sum():,.2f}",
            '(=) LUCRO BRUTO':         f"R$ {dre['lucro_bruto'].sum():,.2f}",
            'Margem (%)':              (f"{dre['lucro_bruto'].sum()/dre['receita_total'].sum()*100:.1f}%"
                                        if dre['receita_total'].sum() else '–'),
        }
        ind_sem = [
            ('Sessões Pagas',     [f"{int(r['sessoes']):,}"           for _,r in dre.iterrows()], ''),
            ('kWh Entregues',     [f"{r['kwh']:,.1f}"                  for _,r in dre.iterrows()], ''),
            ('R$ Início Recarga', [f"R$ {r['r_inicio']:,.2f}"          for _,r in dre.iterrows()], ''),
            ('R$ Energia (kWh)',  [f"R$ {r['r_kwh_rec']:,.2f}"         for _,r in dre.iterrows()], ''),
            ('R$ Ociosidade',     [f"R$ {r['r_ocio']:,.2f}"            for _,r in dre.iterrows()], ''),
        ]
        if _has_voucher:
            ind_sem += [
                ('RECEITA BRUTA PRESUMIDA', [f"R$ {r['receita_bruta_presumida']:,.2f}" for _,r in dre.iterrows()], 'bruta-hipo'),
                ('(−) Desconto Voucher',    [f"(−) R$ {r['desconto_voucher']:,.2f}"    for _,r in dre.iterrows()], 'desconto'),
            ]
        ind_sem += [
            ('RECEITA LÍQUIDA',   [f"R$ {r['receita_total']:,.2f}"     for _,r in dre.iterrows()], 'receita'),
            ('(-) Custo Energia', [f"R$ {r['custo_energia']:,.2f}"     for _,r in dre.iterrows()], 'custo'),
            ('(-) Custo Operac.', [f"R$ {r['custo_operacional']:,.2f}" for _,r in dre.iterrows()], 'custo'),
            ('(=) LUCRO BRUTO',   [f"R$ {r['lucro_bruto']:,.2f}"       for _,r in dre.iterrows()], 'lucro'),
            ('Margem (%)',        [f"{r['margem']:.1f}%"               for _,r in dre.iterrows()], 'lucro'),
        ]
        st.markdown(_dre_html(dre, semana_cols, total_sem, ind_sem), unsafe_allow_html=True)

    # ── DRE MENSAL ────────────────────────────────────────────────────────────────
    if len(dre_mes) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        section("DRE — Demonstrativo de Resultado por Mês")
        mes_cols         = dre_mes['label'].tolist()
        _has_voucher_mes = dre_mes['desconto_voucher'].sum() > 0
        total_mes = {
            'Sessões Pagas':           f"{int(dre_mes['sessoes'].sum()):,}",
            'kWh Entregues':           f"{dre_mes['kwh'].sum():,.1f}",
            'R$ Início Recarga':       f"R$ {dre_mes['r_inicio'].sum():,.2f}",
            'R$ Energia (kWh)':        f"R$ {dre_mes['r_kwh_rec'].sum():,.2f}",
            'R$ Ociosidade':           f"R$ {dre_mes['r_ocio'].sum():,.2f}",
            'RECEITA BRUTA PRESUMIDA': f"R$ {dre_mes['receita_bruta_presumida'].sum():,.2f}",
            '(−) Desconto Voucher':    f"(−) R$ {dre_mes['desconto_voucher'].sum():,.2f}",
            'RECEITA LÍQUIDA':         f"R$ {dre_mes['receita_total'].sum():,.2f}",
            '(-) Custo Energia':       f"R$ {dre_mes['custo_energia'].sum():,.2f}",
            '(-) Custo Operac.':       f"R$ {dre_mes['custo_operacional'].sum():,.2f}",
            '(=) LUCRO BRUTO':         f"R$ {dre_mes['lucro_bruto'].sum():,.2f}",
            'Margem (%)':              (f"{dre_mes['lucro_bruto'].sum()/dre_mes['receita_total'].sum()*100:.1f}%"
                                        if dre_mes['receita_total'].sum() else '–'),
        }
        ind_mes = [
            ('Sessões Pagas',     [f"{int(r['sessoes']):,}"           for _,r in dre_mes.iterrows()], ''),
            ('kWh Entregues',     [f"{r['kwh']:,.1f}"                  for _,r in dre_mes.iterrows()], ''),
            ('R$ Início Recarga', [f"R$ {r['r_inicio']:,.2f}"          for _,r in dre_mes.iterrows()], ''),
            ('R$ Energia (kWh)',  [f"R$ {r['r_kwh_rec']:,.2f}"         for _,r in dre_mes.iterrows()], ''),
            ('R$ Ociosidade',     [f"R$ {r['r_ocio']:,.2f}"            for _,r in dre_mes.iterrows()], ''),
        ]
        if _has_voucher_mes:
            ind_mes += [
                ('RECEITA BRUTA PRESUMIDA', [f"R$ {r['receita_bruta_presumida']:,.2f}" for _,r in dre_mes.iterrows()], 'bruta-hipo'),
                ('(−) Desconto Voucher',    [f"(−) R$ {r['desconto_voucher']:,.2f}"    for _,r in dre_mes.iterrows()], 'desconto'),
            ]
        ind_mes += [
            ('RECEITA LÍQUIDA',   [f"R$ {r['receita_total']:,.2f}"     for _,r in dre_mes.iterrows()], 'receita'),
            ('(-) Custo Energia', [f"R$ {r['custo_energia']:,.2f}"     for _,r in dre_mes.iterrows()], 'custo'),
            ('(-) Custo Operac.', [f"R$ {r['custo_operacional']:,.2f}" for _,r in dre_mes.iterrows()], 'custo'),
            ('(=) LUCRO BRUTO',   [f"R$ {r['lucro_bruto']:,.2f}"       for _,r in dre_mes.iterrows()], 'lucro'),
            ('Margem (%)',        [f"{r['margem']:.1f}%"               for _,r in dre_mes.iterrows()], 'lucro'),
        ]
        st.markdown(_dre_html(dre_mes, mes_cols, total_mes, ind_mes), unsafe_allow_html=True)

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



# ─── AUTH ─────────────────────────────────────────────────────────────────────
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
    .login-logo{font-size:1.6rem;font-weight:800;color:#00C9A7;letter-spacing:-0.02em;
                margin-bottom:0.2rem;text-align:center;}
    .login-sub{font-size:0.72rem;color:#6B7280;text-align:center;}
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            '<div style="padding:2rem 0 1.5rem">'
            '<div class="login-logo">⚡ Dashboard Financeiro</div>'
            '<div class="login-sub">Análise financeira de redes de recarga — acesso restrito</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.form("login_form", border=False):
            user = st.text_input("Usuário", placeholder="usuário")
            pw   = st.text_input("Senha",   placeholder="senha", type="password")
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        if submitted:
            if user in _CREDENTIALS and _hash_pw(pw) == _CREDENTIALS[user]:
                st.session_state.authenticated = True
                st.session_state.logged_user   = user
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.", icon="🔒")
    st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:1rem 0 1.5rem">'
        '<div style="font-size:1.3rem;font-weight:800;color:#00C9A7">Dashboard financeiro</div>'
        '<div style="font-size:0.75rem;color:#6B7280;margin-top:2px">Análise financeira da operação da rede de recarga. Use com cuidado e não transmita dados sensíveis.</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.radio(
        'Página', ['📊 Dashboard', '⚡ Payback'],
        key='nav_page', horizontal=True, label_visibility='collapsed',
    )

    uploaded_files = st.file_uploader(
        "Carregar arquivos .xlsx", type=["xlsx"], accept_multiple_files=True,
        help="Arquivos de relatório de recargas no mesmo formato exportado pelo sistema."
    )

    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">DATASETS DE EXEMPLO</div>', unsafe_allow_html=True)
    _DATASETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets')
    _EXAMPLE_MAP = {
        'Supermercados — Cidade':           '4AC-supermercados-cidade-jan-abr.xlsx',
        'Posto Cidade — Metrópole':         '1AC-1DC30-postocidade-metropole-jan-abr.xlsx',
        'Posto Cidade — Turismo (AC+DC60)': '2AC-1DC60-postocidade-turismo-jan-abr.xlsx',
        'Posto Cidade — Turismo (DC30)':    '2DC30-postocidade-turismo-jan-abr.xlsx',
        'Posto Cidade — Nordeste':          '1AC-1DC60-postocidade-nordeste-jan-abr.xlsx',
    }
    _example_choices = st.multiselect(
        "Selecionar dataset", options=list(_EXAMPLE_MAP.keys()),
        default=[], key="example_datasets", label_visibility="collapsed",
        placeholder="Selecionar dados",
    )

    st.markdown("---")

    if uploaded_files:
        st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">ARQUIVOS CARREGADOS</div>', unsafe_allow_html=True)
        for f in uploaded_files:
            st.markdown(f'<div style="font-size:0.68rem;color:#F0F2F8;padding:3px 0">&#128196; {f.name}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#6B7280">MODO DE ANÁLISE</div>', unsafe_allow_html=True)
    mode = st.radio("", ["Por estação (individual)", "Consolidado (todos os arquivos)"],
                    label_visibility="collapsed")

    anon = False
    if uploaded_files or _example_choices:
        st.markdown("---")
        _is_restricted = st.session_state.get('logged_user') in _RESTRICTED_USERS
        _force_anon    = _is_restricted and bool(_example_choices)
        _anon_default  = _force_anon or bool(_example_choices and not uploaded_files)
        anon = st.toggle(
            "Anonimizar nomes (A, B, C...)",
            value=_anon_default,
            disabled=_force_anon,
            help="Anonimização obrigatória para datasets pré-definidos neste perfil." if _force_anon else None,
        )
        if _force_anon:
            anon = True  # garante o valor mesmo com o toggle desabilitado

    _pb_active = st.session_state.get('nav_page', '📊 Dashboard') == '⚡ Payback'
    if not _pb_active:
        st.markdown("---")
        st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">PARÂMETROS DE CUSTO</div>', unsafe_allow_html=True)
        custo_kwh = st.number_input("Custo da energia (R$/kWh)", min_value=0.0, value=0.75, step=0.01, format="%.2f")
        custo_pct  = st.number_input("Custo operacional (% da receita)", min_value=0.0, max_value=100.0, value=15.0, step=0.5, format="%.1f")
    else:
        custo_kwh = float(st.session_state.get('pb_custo_kwh', 0.75))
        custo_pct = 15.0

    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">HORÁRIO DE FUNCIONAMENTO</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.70rem;color:#9CA3AF;margin-bottom:0.5rem">Usado para calcular a taxa de ocupação real dos carregadores</div>', unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hora_inicio = st.number_input("Abertura", min_value=0, max_value=23, value=0, step=1,
                                       help="Horário de abertura do estabelecimento (0 = meia-noite)")
    with col_h2:
        hora_fim = st.number_input("Fechamento", min_value=1, max_value=24, value=24, step=1,
                                    help="Horário de fechamento (24 = meia-noite)")
    horas_dia = max(1, hora_fim - hora_inicio)
    st.markdown(f'<div style="font-size:0.75rem;color:#00C9A7;margin-top:2px">&#9201; {horas_dia}h disponíveis/dia</div>', unsafe_allow_html=True)

    # Slot reservado para os FILTROS — será preenchido após o carregamento dos dados
    _filtros_slot = st.empty()

    st.markdown("---")
    _logged_user = st.session_state.get('logged_user', 'admin')
    st.markdown(
        f'<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.4rem">'
        f'Conectado como <span style="color:#F0F2F8">{_logged_user}</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.logged_user   = ""
        st.rerun()

# ─── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-bottom:1.5rem">'
    '<div class="page-title">Dashboard <span style="color:#00C9A7">Financeiro</span></div>'
    '<div class="page-subtitle">Software em testes, confira os dados antes de transmiti-los</div>'
    '</div>',
    unsafe_allow_html=True
)

_is_payback = st.session_state.get('nav_page', '📊 Dashboard') == '⚡ Payback'

# Payback sem dados: preenche sidebar e renderiza imediatamente
if _is_payback and not uploaded_files and not _example_choices:
    with _filtros_slot.container():
        _render_payback_sidebar(horas_dia)
    render_payback(df_all=None, horas_dia=horas_dia, custo_kwh=custo_kwh)
    st.stop()

if not uploaded_files and not _example_choices:
    st.markdown(
        '<div style="text-align:center;padding:4rem 2rem;color:#6B7280">'
        '<div style="font-size:3rem;margin-bottom:1rem">&#9889;</div>'
        '<div style="font-size:1.2rem;font-weight:700;color:#F0F2F8;margin-bottom:0.5rem">Nenhum arquivo carregado</div>'
        '<div style="font-size:0.75rem;line-height:1.7">Use o painel lateral para fazer upload de arquivos .xlsx ou selecione um dataset de exemplo.</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.stop()

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
_file_sources = [(f.read(), f.name) for f in (uploaded_files or [])]
for _label in _example_choices:
    _fpath = os.path.join(_DATASETS_DIR, _EXAMPLE_MAP[_label])
    with open(_fpath, 'rb') as _fh:
        _file_sources.append((_fh.read(), _EXAMPLE_MAP[_label]))

with st.spinner("Processando arquivos..."):
    dfs = {}
    for _fbytes, _fname in _file_sources:
        raw = load_file(_fbytes, _fname)
        processed = process_df(raw)
        col = 'Estação' if 'Estação' in processed.columns else 'Estacao'
        stations_in_file = processed[col].dropna().unique() if col in processed.columns else []
        station_name = stations_in_file[0] if len(stations_in_file) == 1 else _fname.replace('.xlsx','')
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

# Payback com dados carregados
if _is_payback:
    with _filtros_slot.container():
        _render_payback_sidebar(horas_dia)
    render_payback(df_all=df_all, horas_dia=horas_dia, custo_kwh=custo_kwh)
    st.stop()

# ─── FILTROS (CONECTOR + ESTAÇÃO) ────────────────────────────────────────────
_col_conn = 'Conector(Tipo)' if 'Conector(Tipo)' in df_all.columns else None
_col_est  = 'Estação' if 'Estação' in df_all.columns else ('Estacao' if 'Estacao' in df_all.columns else None)

_connector_options = sorted(df_all[_col_conn].dropna().unique().tolist()) if _col_conn else []
_station_options   = sorted(df_all[_col_est].dropna().unique().tolist())  if _col_est  else []

# Filtros nativos na sidebar — causam soft-rerun preservando o arquivo carregado
_selected_connector = ""
_selected_station   = ""
_date_min_all = df_all['data'].min()
_date_max_all = df_all['data'].max()
_selected_dates = (_date_min_all, _date_max_all)

with _filtros_slot.container():
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#6B7280;margin-bottom:0.5rem">FILTROS</div>',
                unsafe_allow_html=True)
    _date_range = st.date_input(
        "Período",
        value=(_date_min_all, _date_max_all),
        min_value=_date_min_all,
        max_value=_date_max_all,
        key="filter_dates",
    )
    if isinstance(_date_range, (list, tuple)) and len(_date_range) == 2:
        _selected_dates = (_date_range[0], _date_range[1])
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
_d0, _d1 = _selected_dates
df_all = df_all[(df_all['data'] >= _d0) & (df_all['data'] <= _d1)]
dfs = {k: v[(v['data'] >= _d0) & (v['data'] <= _d1)] for k, v in dfs.items()}

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
                     custo_kwh=custo_kwh, custo_pct=custo_pct, anon=anon, horas_dia=horas_dia,
)

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
                             custo_kwh=custo_kwh, custo_pct=custo_pct, anon=anon, horas_dia=horas_dia,
)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="text-align:center;padding:2rem 0 1rem;font-size:0.62rem;color:#3D4560;'
    f'border-top:1px solid #1E2330;margin-top:2rem">'
    f'&#9889; MVP do dashboard financeiro v0.1 &middot; {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}'
    f'</div>',
    unsafe_allow_html=True
)
