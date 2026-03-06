import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import io
from datetime import datetime
import math
import json
import base64

# ============================================================================
# КОНФИГУРАЦИЯ И СТИЛИ
# ============================================================================
st.set_page_config(
    page_title="🏗️ Metal Constructor PRO",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Современный CSS дизайн (AI-стиль)
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .stMetric {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #00d9ff;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #00d9ff;
    }
    div[data-testid="stMetricLabel"] {
        color: #ffffff;
        font-size: 14px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00ffcc 0%, #00d9ff 100%);
    }
    h1, h2, h3 {
        color: #00d9ff;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
    }
    .info-box {
        background: rgba(0, 217, 255, 0.1);
        border-left: 4px solid #00d9ff;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background: rgba(255, 165, 0, 0.1);
        border-left: 4px solid #ffa500;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background: rgba(0, 255, 100, 0.1);
        border-left: 4px solid #00ff64;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# БАЗА ДАННЫХ ПРОФИЛЕЙ (ГОСТ 30245-2003)
# ============================================================================

@st.cache_data
def get_profiles_database():
    """Полная база профильных труб по ГОСТ"""
    return {
        'Квадратные': {
            '50×50×2': {'b': 50, 'h': 50, 't': 2, 'area': 3.74, 'ix': 1.93, 'weight': 2.96, 'price': 150},
            '50×50×3': {'b': 50, 'h': 50, 't': 3, 'area': 5.49, 'ix': 1.91, 'weight': 4.31, 'price': 160},
            '60×60×3': {'b': 60, 'h': 60, 't': 3, 'area': 6.69, 'ix': 2.29, 'weight': 5.25, 'price': 170},
            '60×60×4': {'b': 60, 'h': 60, 't': 4, 'area': 8.73, 'ix': 2.25, 'weight': 6.86, 'price': 180},
            '80×80×3': {'b': 80, 'h': 80, 't': 3, 'area': 9.09, 'ix': 3.10, 'weight': 7.14, 'price': 190},
            '80×80×4': {'b': 80, 'h': 80, 't': 4, 'area': 11.89, 'ix': 3.05, 'weight': 9.33, 'price': 200},
            '100×100×4': {'b': 100, 'h': 100, 't': 4, 'area': 15.29, 'ix': 3.95, 'weight': 12.00, 'price': 220},
            '100×100×5': {'b': 100, 'h': 100, 't': 5, 'area': 18.84, 'ix': 3.91, 'weight': 14.79, 'price': 240},
            '120×120×5': {'b': 120, 'h': 120, 't': 5, 'area': 22.84, 'ix': 4.71, 'weight': 17.93, 'price': 260},
            '120×120×6': {'b': 120, 'h': 120, 't': 6, 'area': 27.09, 'ix': 4.67, 'weight': 21.26, 'price': 280},
            '140×140×6': {'b': 140, 'h': 140, 't': 6, 'area': 31.89, 'ix': 5.54, 'weight': 25.03, 'price': 300},
            '150×150×6': {'b': 150, 'h': 150, 't': 6, 'area': 34.09, 'ix': 5.98, 'weight': 26.76, 'price': 320},
            '150×150×8': {'b': 150, 'h': 150, 't': 8, 'area': 44.69, 'ix': 5.91, 'weight': 35.08, 'price': 360},
            '180×180×8': {'b': 180, 'h': 180, 't': 8, 'area': 54.09, 'ix': 7.24, 'weight': 42.46, 'price': 400},
            '200×200×8': {'b': 200, 'h': 200, 't': 8, 'area': 60.49, 'ix': 8.14, 'weight': 47.48, 'price': 440},
        },
        'Прямоугольные': {
            '60×40×3': {'b': 60, 'h': 40, 't': 3, 'area': 5.49, 'ix': 2.12, 'weight': 4.31, 'price': 165},
            '80×40×3': {'b': 80, 'h': 40, 't': 3, 'area': 6.69, 'ix': 2.82, 'weight': 5.25, 'price': 175},
            '80×40×4': {'b': 80, 'h': 40, 't': 4, 'area': 8.73, 'ix': 2.77, 'weight': 6.86, 'price': 185},
            '100×50×4': {'b': 100, 'h': 50, 't': 4, 'area': 11.89, 'ix': 3.67, 'weight': 9.33, 'price': 210},
            '120×60×4': {'b': 120, 'h': 60, 't': 4, 'area': 14.29, 'ix': 4.35, 'weight': 11.22, 'price': 230},
            '140×80×4': {'b': 140, 'h': 80, 't': 4, 'area': 18.09, 'ix': 5.24, 'weight': 14.20, 'price': 260},
        }
    }

@st.cache_data
def get_steel_grades():
    """Марки стали по ГОСТ 27772-2015"""
    return {
        'С245': {'Ry': 240, 'Run': 240, 'price_factor': 1.0, 'description': 'Базовая строительная сталь'},
        'С255': {'Ry': 250, 'Run': 250, 'price_factor': 1.05, 'description': 'Улучшенная С245'},
        'С345': {'Ry': 320, 'Run': 345, 'price_factor': 1.25, 'description': 'Низколегированная (09Г2С)'},
        'С355': {'Ry': 335, 'Run': 355, 'price_factor': 1.30, 'description': 'Улучшенная С345'},
        'С390': {'Ry': 370, 'Run': 390, 'price_factor': 1.45, 'description': 'Высокопрочная'},
        'С440': {'Ry': 420, 'Run': 440, 'price_factor': 1.60, 'description': 'Повышенной прочности'},
    }

# ============================================================================
# РАСЧЁТНЫЕ ФУНКЦИИ ПО СП
# ============================================================================

def calculate_snow_load(district, roof_pitch_deg, region_type='A'):
    """Расчёт снеговой нагрузки по СП 20.13330.2016"""
    snow_map = {
        'I': 0.5, 'II': 0.7, 'III': 1.0, 'IV': 1.5,
        'V': 2.0, 'VI': 2.5, 'VII': 3.0, 'VIII': 3.5
    }
    Sg = snow_map.get(district, 1.5)
    
    # Коэффициент уклона (п. 10.5 СП 20.13330)
    if roof_pitch_deg <= 25:
        mu = 1.0
    elif roof_pitch_deg <= 60:
        mu = max(0, 1.0 - (roof_pitch_deg - 25) / 35 * 0.3)
    else:
        mu = 0.0
    
    # Коэффициент надёжности (п. 10.10)
    gamma_f = 1.4
    
    # Расчётная нагрузка
    S0 = 0.7 * mu * Sg * gamma_f
    
    return {'Sg': Sg, 'S0': S0, 'mu': mu, 'gamma_f': gamma_f}

def calculate_wind_load(district, height, terrain_type='B'):
    """Расчёт ветровой нагрузки по СП 20.13330.2016"""
    wind_map = {
        'Ia': 0.17, 'I': 0.23, 'II': 0.30, 'III': 0.38,
        'IV': 0.48, 'V': 0.60, 'VI': 0.73, 'VII': 0.85
    }
    w0 = wind_map.get(district, 0.30)
    
    # Коэффициент высоты (таблица 10.3)
    k_table = {
        'A': {0: 1.0, 5: 1.25, 10: 1.5, 20: 1.85, 40: 2.2},
        'B': {0: 0.65, 5: 0.85, 10: 1.0, 20: 1.25, 40: 1.55},
        'C': {0: 0.4, 5: 0.55, 10: 0.65, 20: 0.85, 40: 1.1}
    }
    
    k_heights = sorted(k_table[terrain_type].keys())
    for i in range(len(k_heights)-1):
        if k_heights[i] <= height <= k_heights[i+1]:
            k = k_table[terrain_type][k_heights[i]] + \
                (k_table[terrain_type][k_heights[i+1]] - k_table[terrain_type][k_heights[i]]) * \
                (height - k_heights[i]) / (k_heights[i+1] - k_heights[i])
            break
    else:
        k = k_table[terrain_type][max(k_heights)]
    
    # Аэродинамический коэффициент
    ce = 0.8
    gamma_fw = 1.4
    
    W0 = w0 * k * ce * gamma_fw
    
    return {'w0': w0, 'k': k, 'ce': ce, 'W0': W0, 'gamma_fw': gamma_fw}

def calculate_truss_forces(width, height, roof_pitch_deg, truss_spacing, snow_load, wind_load, truss_type):
    """Расчёт усилий в ферме"""
    # Геометрия
    truss_height = width / 6 if truss_type == 'Треугольная' else width / 8
    roof_height = height + truss_height
    
    # Нагрузки
    permanent_load = 0.15  # собственный вес
    total_load = snow_load + permanent_load
    q = total_load * truss_spacing
    
    # Усилия
    M_max = q * width**2 / 8
    N_chord = M_max / truss_height if truss_height > 0 else 0
    V_max = q * width / 2
    N_web = V_max / math.sin(math.radians(45))
    N_post = q * truss_spacing
    
    # Количество панелей
    num_panels = max(8, int(width / 1.5))
    panel_length = width / num_panels
    
    return {
        'truss_height': truss_height,
        'roof_height': roof_height,
        'num_panels': num_panels,
        'panel_length': panel_length,
        'permanent_load': permanent_load,
        'total_load': total_load,
        'q': q,
        'M_max': M_max,
        'N_chord': N_chord,
        'N_web': N_web,
        'N_post': N_post
    }

def select_sections(forces, steel_grade, optimization, profiles_db):
    """Подбор сечений по СП 16.13330.2017"""
    steel_props = get_steel_grades()
    Ry = steel_props.get(steel_grade, {'Ry': 320})['Ry']
    gamma_c = 0.9
    R = Ry * gamma_c / 1.05
    
    # Требуемые площади
    A_chord_req = forces['N_chord'] * 10 / R
    A_web_req = forces['N_web'] * 10 / R
    A_post_req = forces['N_post'] * 10 / R
    
    # Коэффициенты подбора
    opt_factors = {'💰 Экономия': 1.0, '⚖️ Баланс': 1.15, '💪 Прочность': 1.3, '🏆 Премиум': 1.5}
    af = opt_factors.get(optimization, 1.15)
    
    # Подбор из базы
    def find_profile(required_area, profiles):
        for name, props in sorted(profiles.items(), key=lambda x: x[1]['area']):
            if props['area'] >= required_area * af:
                return name, props
        return list(profiles.items())[-1]
    
    chord_name, chord_props = find_profile(A_chord_req, profiles_db['Квадратные'])
    web_name, web_props = find_profile(A_web_req, profiles_db['Квадратные'])
    post_name, post_props = find_profile(A_post_req, profiles_db['Квадратные'])
    purlin_name, purlin_props = find_profile(A_web_req * 0.5, profiles_db['Прямоугольные'])
    
    # Напряжения
    stress_chord = forces['N_chord'] * 10 / chord_props['area']
    stress_web = forces['N_web'] * 10 / web_props['area']
    stress_post = forces['N_post'] * 10 / post_props['area']
    
    # Утилизация
    util_chord = stress_chord / R * 100
    util_web = stress_web / R * 100
    util_post = stress_post / R * 100
    
    return {
        'chord': {'name': chord_name, 'props': chord_props, 'stress': stress_chord, 'util': util_chord},
        'web': {'name': web_name, 'props': web_props, 'stress': stress_web, 'util': util_web},
        'post': {'name': post_name, 'props': post_props, 'stress': stress_post, 'util': util_post},
        'purlin': {'name': purlin_name, 'props': purlin_props},
        'R': R,
        'required_areas': {'chord': A_chord_req, 'web': A_web_req, 'post': A_post_req}
    }

def calculate_foundation(length, width, height, sections, soil_type='Суглинок'):
    """Расчёт фундамента"""
    # Нагрузка на фундамент
    num_columns = int(length / 4) * 2 + 2
    
    # Вес металла
    total_metal_weight = (
        width * 2 * sections['chord']['props']['weight'] * (int(length / 4) + 1) +
        height * num_columns * sections['post']['props']['weight']
    )
    
    # Нагрузка на одну колонну
    load_per_column = (total_metal_weight * 9.81 / 1000) / num_columns
    
    # Площадь фундамента (по несущей способности грунта)
    soil_capacity = {'Песок': 2.5, 'Суглинок': 2.0, 'Глина': 1.5, 'Скальный': 4.0}
    capacity = soil_capacity.get(soil_type, 2.0)
    
    foundation_area = load_per_column / capacity
    foundation_size = math.sqrt(foundation_area) * 100  # см
    
    return {
        'num_columns': num_columns,
        'load_per_column': load_per_column,
        'foundation_size': foundation_size,
        'total_metal_weight': total_metal_weight,
        'soil_capacity': capacity
    }

def calculate_cost(length, width, sections, foundation, optimization):
    """Сметный расчёт"""
    num_trusses = int(length / 4) + 1
    
    # Металл
    chord_length = width * 2 * num_trusses
    post_length = height * 2 * num_trusses
    purlin_length = length * 5
    
    chord_cost = chord_length * sections['chord']['props']['weight'] * sections['chord']['props']['price'] * get_steel_grades()['С345']['price_factor']
    post_cost = post_length * sections['post']['props']['weight'] * sections['post']['props']['price'] * get_steel_grades()['С345']['price_factor']
    purlin_cost = purlin_length * sections['purlin']['props']['weight'] * sections['purlin']['props']['price']
    
    metal_cost = chord_cost + post_cost + purlin_cost
    
    # Крепёж (10% от металла)
    fastener_cost = metal_cost * 0.1
    
    # Фундамент (бетон М300, 5000 руб/м³)
    foundation_volume = (foundation['foundation_size']/100)**2 * 0.5 * foundation['num_columns']
    foundation_cost = foundation_volume * 5000
    
    # Работы
    labor_cost = metal_cost * 0.4
    
    # Итого
    total_cost = metal_cost + fastener_cost + foundation_cost + labor_cost
    
    return {
        'metal_cost': metal_cost,
        'fastener_cost': fastener_cost,
        'foundation_cost': foundation_cost,
        'labor_cost': labor_cost,
        'total_cost': total_cost,
        'metal_weight': chord_length * sections['chord']['props']['weight'] + post_length * sections['post']['props']['weight'] + purlin_length * sections['purlin']['props']['weight']
    }

# ============================================================================
# 3D ВИЗУАЛИЗАЦИЯ
# ============================================================================

def create_3d_model(length, width, height, roof_pitch_deg, truss_spacing, sections, calc):
    """Профессиональная 3D модель"""
    fig = go.Figure()
    
    num_trusses = int(length / truss_spacing) + 1
    truss_height = calc['truss_height']
    roof_height = calc['roof_height']
    num_panels = calc['num_panels']
    panel_length = calc['panel_length']
    
    # ЦВЕТОВАЯ СХЕМА (контрастная - видно на любом фоне)
    colors = {
        'columns': '#FF4444',        # красные - колонны
        'trusses': '#00FF88',        # зелёные - фермы
        'purlins': '#00D9FF',        # бирюзовые - прогоны
        'bracing': '#FFAA00',        # оранжевые - связи
        'nodes': '#FF00FF'           # фиолетовые - узлы
    }
    
    # 1. КОЛОННЫ
    for i in range(num_trusses):
        x = i * truss_spacing
        fig.add_trace(go.Scatter3d(x=[x, x], y=[0, 0], z=[0, height],
            mode='lines', line=dict(color=colors['columns'], width=12),
            name='Колонны' if i == 0 else '', showlegend=(i==0)))
        fig.add_trace(go.Scatter3d(x=[x, x], y=[width, width], z=[0, height],
            mode='lines', line=dict(color=colors['columns'], width=12), showlegend=False))
    
    # 2. ФЕРМЫ
    for i in range(num_trusses):
        x = i * truss_spacing
        
        # Нижний пояс
        fig.add_trace(go.Scatter3d(x=[x, x], y=[0, width], z=[height, height],
            mode='lines', line=dict(color=colors['trusses'], width=10),
            name='Фермы' if i == 0 else '', showlegend=(i==0)))
        
        # Верхний пояс
        y_left = np.linspace(0, width/2, num_panels//2 + 1)
        z_left = height + (y_left / (width/2)) * truss_height
        fig.add_trace(go.Scatter3d(x=[x]*len(y_left), y=y_left, z=z_left,
            mode='lines', line=dict(color=colors['trusses'], width=10), showlegend=False))
        
        y_right = np.linspace(width/2, width, num_panels//2 + 1)
        z_right = roof_height - ((y_right - width/2) / (width/2)) * truss_height
        fig.add_trace(go.Scatter3d(x=[x]*len(y_right), y=y_right, z=z_right,
            mode='lines', line=dict(color=colors['trusses'], width=10), showlegend=False))
        
        # Стойки фермы
        for j in range(num_panels + 1):
            y_pos = j * panel_length
            if y_pos <= width/2:
                z_top = height + (y_pos / (width/2)) * truss_height
            else:
                z_top = roof_height - ((y_pos - width/2) / (width/2)) * truss_height
            fig.add_trace(go.Scatter3d(x=[x, x], y=[y_pos, y_pos], z=[height, z_top],
                mode='lines', line=dict(color=colors['trusses'], width=6), showlegend=False))
    
    # 3. ПРОГОНЫ
    for j in range(5):
        y_pos = (j + 1) * width / 6
        if y_pos <= width/2:
            z_pos = height + (y_pos / (width/2)) * truss_height
        else:
            z_pos = roof_height - ((y_pos - width/2) / (width/2)) * truss_height
        fig.add_trace(go.Scatter3d(x=[0, length], y=[y_pos, y_pos], z=[z_pos, z_pos],
            mode='lines', line=dict(color=colors['purlins'], width=11),
            name='Прогоны' if j == 0 else '', showlegend=(j==0)))
    
    # 4. СВЯЗИ
    for x_pos in [0, length]:
        fig.add_trace(go.Scatter3d(x=[x_pos, x_pos], y=[0, width/3], z=[height/2, height],
            mode='lines', line=dict(color=colors['bracing'], width=5, dash='dash'),
            name='Связи' if x_pos == 0 else '', showlegend=(x_pos==0)))
        fig.add_trace(go.Scatter3d(x=[x_pos, x_pos], y=[width/3, 0], z=[height, height/2],
            mode='lines', line=dict(color=colors['bracing'], width=5, dash='dash'), showlegend=False))
    
    # 5. УЗЛЫ
    node_positions = []
    for i in range(num_trusses):
        x = i * truss_spacing
        node_positions.append([x, 0, height])
        node_positions.append([x, width, height])
        node_positions.append([x, width/2, roof_height])
    
    if node_positions:
        node_array = np.array(node_positions)
        fig.add_trace(go.Scatter3d(x=node_array[:, 0], y=node_array[:, 1], z=node_array[:, 2],
            mode='markers', marker=dict(size=10, color=colors['nodes'], opacity=0.9),
            name='Узлы'))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Длина (м)', range=[0, length], gridcolor='#444444', backgroundcolor='#1a1a2e'),
            yaxis=dict(title='Ширина (м)', range=[0, width], gridcolor='#444444', backgroundcolor='#1a1a2e'),
            zaxis=dict(title='Высота (м)', range=[0, roof_height + 2], gridcolor='#444444', backgroundcolor='#1a1a2e'),
            aspectmode='manual',
            aspectratio=dict(x=2.5, y=1, z=0.8),
            camera=dict(eye=dict(x=1.8, y=1.5, z=1.3))
        ),
        height=650,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(0,0,0,0.7)'),
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        font=dict(color='#ffffff', size=12)
    )
    
    return fig

# ============================================================================
# ЭКСПОРТ DXF
# ============================================================================

def generate_dxf_data(length, width, height, calc, sections):
    """Генерация данных для DXF чертежа"""
    dxf_content = f"""0
SECTION
2
HEADER
9
$ACADVER
1
AC1015
0
ENDSEC
0
SECTION
2
TABLES
0
TABLE
2
LAYER
0
LAYER
2
COLUMNS
70
0
62
1
6
CONTINUOUS
0
LAYER
2
TRUSSES
70
0
62
3
6
CONTINUOUS
0
LAYER
2
PURLINS
70
0
62
4
6
CONTINUOUS
0
ENDTAB
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
COLUMNS
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
{height}
0
LINE
8
COLUMNS
10
{length}
20
0.0
30
0.0
11
{length}
21
0.0
31
{height}
0
LINE
8
TRUSSES
10
0.0
20
0.0
30
{height}
11
0.0
21
{width/2}
31
{calc['roof_height']}
0
LINE
8
TRUSSES
10
0.0
20
{width/2}
30
{calc['roof_height']}
11
0.0
21
{width}
31
{height}
0
LINE
8
TRUSSES
10
0.0
20
0.0
30
{height}
11
0.0
21
{width}
31
{height}
0
ENDSEC
0
EOF
"""
    return dxf_content

# ============================================================================
# ГЕНЕРАЦИЯ ОТЧЁТОВ
# ============================================================================

def generate_report(length, width, height, roof_pitch_deg, calc, sections, loads, foundation, cost, steel_grade):
    """Генерация полного отчёта"""
    num_trusses = int(length / 4) + 1
    
    report = f"""
╔════════════════════════════════════════════════════════════════════════════════╗
║                    ПРОЕКТ КАРКАСА ЗДАНИЯ                                       ║
║                    Metal Constructor PRO v2.0                                  ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  ДАТА РАСЧЁТА: {datetime.now().strftime('%d.%m.%Y %H:%M')}                                    ║
║  СТАЛЬ: {steel_grade} (Ry={get_steel_grades()[steel_grade]['Ry']} МПа)                                   ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  1. ГЕОМЕТРИЯ ЗДАНИЯ                                                           ║
║  ──────────────────────                                                        ║
║  • Длина: {length:.1f} м                                                           ║
║  • Ширина: {width:.1f} м                                                          ║
║  • Высота: {height:.1f} м                                                         ║
║  • Уклон крыши: {roof_pitch_deg}°                                                       ║
║  • Шаг ферм: 4.0 м                                                              ║
║  • Количество ферм: {num_trusses} шт.                                                  ║
║  • Площадь застройки: {length*width:.1f} м²                                             ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  2. НАГРУЗКИ                                                                   ║
║  ──────────────                                                                ║
║  • Снеговая (норм.): {loads['snow']['Sg']:.2f} кПа                                                    ║
║  • Снеговая (расч.): {loads['snow']['S0']:.2f} кПа                                                    ║
║  • Ветровая: {loads['wind']['W0']:.2f} кПа                                                          ║
║  • Собственный вес: {calc['permanent_load']:.2f} кПа                                                  ║
║  • Итого: {calc['total_load']:.2f} кН/м                                                          ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  3. СЕЧЕНИЯ ЭЛЕМЕНТОВ                                                          ║
║  ──────────────────────                                                        ║
║  • Верхний пояс: {sections['chord']['name']} мм (σ={sections['chord']['stress']:.1f} МПа, {sections['chord']['util']:.1f}%)         ║
║  • Нижний пояс: {sections['chord']['name']} мм                                              ║
║  • Раскосы: {sections['web']['name']} мм (σ={sections['web']['stress']:.1f} МПа, {sections['web']['util']:.1f}%)                   ║
║  • Стойки: {sections['post']['name']} мм (σ={sections['post']['stress']:.1f} МПа, {sections['post']['util']:.1f}%)                   ║
║  • Прогоны: {sections['purlin']['name']} мм                                                 ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  4. ФУНДАМЕНТ                                                                  ║
║  ──────────────                                                                ║
║  • Количество колонн: {foundation['num_columns']} шт.                                              ║
║  • Нагрузка на колонну: {foundation['load_per_column']:.1f} кН                                          ║
║  • Размер фундамента: {foundation['foundation_size']:.0f}×{foundation['foundation_size']:.0f} см                              ║
║  • Глубина: 50 см                                                              ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  5. СМЕТНЫЙ РАСЧЁТ                                                             ║
║  ──────────────────                                                            ║
║  • Металлоконструкции: {cost['metal_cost']:,.0f} руб.                                         ║
║  • Крепёж: {cost['fastener_cost']:,.0f} руб.                                                          ║
║  • Фундамент: {cost['foundation_cost']:,.0f} руб.                                                      ║
║  • Работы: {cost['labor_cost']:,.0f} руб.                                                            ║
║  ──────────────────────────────────────────────────────────────────────────    ║
║  ИТОГО: {cost['total_cost']:,.0f} руб.                                                    ║
║  Вес металла: {cost['metal_weight']:.0f} кг                                                           ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  6. СТАТУС ПРОВЕРКИ                                                            ║
║  ────────────────────                                                          ║
"""
    
    # Статус по напряжениям
    max_util = max(sections['chord']['util'], sections['web']['util'], sections['post']['util'])
    if max_util > 100:
        report += "║  ⚠️ ВНИМАНИЕ: ПЕРЕГРУЗКА ЭЛЕМЕНТОВ! Требуется увеличение сечений.            ║\n"
    elif max_util > 80:
        report += "║  ⚡ ПОВЫШЕННЫЕ НАПРЯЖЕНИЯ: Рекомендуется увеличить запас прочности.          ║\n"
    else:
        report += "║  ✅ ВСЕ ЭЛЕМЕНТЫ В НОРМЕ: Напряжения в допустимых пределах.                  ║\n"
    
    report += """╚════════════════════════════════════════════════════════════════════════════════╝

⚠️ ВАЖНО: Данный расчёт является предварительным и не заменяет проектную документацию.
Для строительства необходим полный проект по СП 16.13330 и СП 20.13330 с экспертизой.

Metal Constructor PRO v2.0 | https://github.com
"""
    
    return report

# ============================================================================
# ОСНОВНОЙ ИНТЕРФЕЙС
# ============================================================================

# Заголовок
st.title("🏗️ Metal Constructor PRO")
st.markdown("**Профессиональный расчёт металлоконструкций с AI-дизайном** 🤖")

# Загрузка баз данных
profiles_db = get_profiles_database()
steel_grades = get_steel_grades()

# ============================================================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/construction.png", width=80)
    st.title("⚙️ ПАРАМЕТРЫ")
    
    st.subheader("📐 Геометрия")
    length = st.number_input("Длина здания (м)", min_value=6.0, max_value=120.0, value=30.0, step=1.0)
    width = st.number_input("Ширина/Пролёт (м)", min_value=4.0, max_value=40.0, value=12.0, step=1.0)
    height = st.number_input("Высота до карниза (м)", min_value=2.5, max_value=12.0, value=4.0, step=0.5)
    roof_pitch_deg = st.slider("Уклон крыши (градусы)", 5, 45, 15, 1)
    
    st.subheader("🔩 Конструкция")
    truss_type = st.radio("Тип фермы", ["Треугольная", "Трапециевидная"], index=0)
    truss_spacing = st.slider("Шаг ферм (м)", 2.0, 8.0, 4.0, 0.5)
    
    st.subheader("🌨️ Климат")
    snow_district = st.selectbox("Снеговой район", ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"], index=3)
    wind_district = st.selectbox("Ветровой район", ["Ia", "I", "II", "III", "IV", "V", "VI", "VII"], index=2)
    terrain_type = st.selectbox("Тип местности", ["A (открытая)", "B (городская)", "C (плотная)"], index=1)
    
    st.subheader("🏗️ Материалы")
    steel_grade = st.selectbox("Марка стали", list(steel_grades.keys()), index=2)
    optimization = st.radio("Оптимизация", ["💰 Экономия", "⚖️ Баланс", "💪 Прочность", "🏆 Премиум"], index=1)
    
    st.subheader("🏛️ Фундамент")
    soil_type = st.selectbox("Тип грунта", ["Песок", "Суглинок", "Глина", "Скальный"], index=1)
    
    st.markdown("---")
    
    # Кнопки управления
    if st.button("💾 Сохранить проект", use_container_width=True):
        project_data = {
            'length': length, 'width': width, 'height': height,
            'roof_pitch': roof_pitch_deg, 'steel_grade': steel_grade,
            'optimization': optimization, 'timestamp': datetime.now().isoformat()
        }
        st.session_state['saved_project'] = project_data
        st.success("Проект сохранён!")
    
    if st.button("📂 Загрузить проект", use_container_width=True):
        if 'saved_project' in st.session_state:
            st.info(f"Загружен проект от {st.session_state['saved_project']['timestamp']}")
        else:
            st.warning("Нет сохранённых проектов")

# ============================================================================
# РАСЧЁТЫ
# ============================================================================

snow_load = calculate_snow_load(snow_district, roof_pitch_deg, terrain_type[0])
wind_load = calculate_wind_load(wind_district, height, terrain_type[0])
truss_forces = calculate_truss_forces(width, height, roof_pitch_deg, truss_spacing, snow_load['S0'], wind_load['W0'], truss_type)
sections = select_sections(truss_forces, steel_grade, optimization, profiles_db)
foundation = calculate_foundation(length, width, height, sections, soil_type)
cost = calculate_cost(length, width, sections, foundation, optimization)

loads = {'snow': snow_load, 'wind': wind_load}

# ============================================================================
# МЕТРИКИ
# ============================================================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("❄️ Снег", f"{snow_load['S0']:.2f} кПа", f"μ={snow_load['mu']}")
with col2:
    st.metric("💨 Ветер", f"{wind_load['W0']:.2f} кПа", f"k={wind_load['k']:.2f}")
with col3:
    st.metric("🏗️ Нагрузка", f"{truss_forces['q']:.2f} кН/м")
with col4:
    st.metric("📐 Высота", f"{truss_forces['roof_height']:.2f} м")
with col5:
    st.metric("💰 Стоимость", f"{cost['total_cost']:,.0f} ₽")

st.markdown("---")

# ============================================================================
# 3D МОДЕЛЬ
# ============================================================================
st.subheader("🏗️ 3D Модель каркаса")

st.info("""
**🎨 Цветовая схема:**
- 🔴 **Красный** - Колонны
- 🟢 **Зелёный** - Фермы
- 🔵 **Бирюзовый** - Прогоны
- 🟠 **Оранжевый** - Связи
- 🟣 **Фиолетовый** - Узлы крепления
""")

fig_3d = create_3d_model(length, width, height, roof_pitch_deg, truss_spacing, sections, truss_forces)
st.plotly_chart(fig_3d, use_container_width=True)

# ============================================================================
# АНАЛИЗ НАПРЯЖЕНИЙ
# ============================================================================
st.markdown("---")
st.subheader("🔍 Анализ напряжённо-деформированного состояния")

def get_status_html(util, stress, R):
    if util > 100:
        return f"<span style='color:#FF0000; font-weight:bold; font-size:18px'>🔴 {util:.1f}% (ПЕРЕГРУЗ!)</span>"
    elif util > 80:
        return f"<span style='color:#FFA500; font-weight:bold'>🟡 {util:.1f}% (Повышенное)</span>"
    elif util > 60:
        return f"<span style='color:#FFFF00'>🟡 {util:.1f}% (Среднее)</span>"
    else:
        return f"<span style='color:#00FF64; font-weight:bold'>🟢 {util:.1f}% (Норма)</span>"

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="info-box">
    **🔷 Пояса ферм**  
    Сечение: **{sections['chord']['name']} мм**  
    {get_status_html(sections['chord']['util'], sections['chord']['stress'], sections['R'])}  
    Требуемая площадь: {sections['required_areas']['chord']:.2f} см²  
    Фактическая: {sections['chord']['props']['area']:.2f} см²
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="info-box">
    **🔶 Раскосы**  
    Сечение: **{sections['web']['name']} мм**  
    {get_status_html(sections['web']['util'], sections['web']['stress'], sections['R'])}  
    Требуемая площадь: {sections['required_areas']['web']:.2f} см²  
    Фактическая: {sections['web']['props']['area']:.2f} см²
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="info-box">
    **🔷 Стойки**  
    Сечение: **{sections['post']['name']} мм**  
    {get_status_html(sections['post']['util'], sections['post']['stress'], sections['R'])}  
    Требуемая площадь: {sections['required_areas']['post']:.2f} см²  
    Фактическая: {sections['post']['props']['area']:.2f} см²
    </div>
    """, unsafe_allow_html=True)

# Предупреждения
max_util = max(sections['chord']['util'], sections['web']['util'], sections['post']['util'])
if max_util > 100:
    st.error("""
    ⚠️ **КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ!**  
    Обнаружены элементы с перегрузкой! Необходимо:
    1. Увеличить сечение элементов
    2. Уменьшить шаг ферм
    3. Выбрать более прочную сталь
    4. Изменить режим оптимизации
    """)
elif max_util > 80:
    st.warning("⚠️ **ВНИМАНИЕ:** Некоторые элементы работают с повышенными напряжениями.")
else:
    st.success("✅ **Все элементы в пределах допустимых напряжений!**")

# ============================================================================
# СМЕТНЫЙ РАСЧЁТ
# ============================================================================
st.markdown("---")
st.subheader("💰 Сметный расчёт")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="success-box">
    **МАТЕРИАЛЫ:**  
    • Металлоконструкции: **{cost['metal_cost']:,.0f} ₽**  
    • Крепёж: **{cost['fastener_cost']:,.0f} ₽**  
    • Фундамент: **{cost['foundation_cost']:,.0f} ₽**  
    • Работы: **{cost['labor_cost']:,.0f} ₽**  
    ────────────────────────  
    **ИТОГО: {cost['total_cost']:,.0f} ₽**  
    Вес металла: **{cost['metal_weight']:.0f} кг**
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Диаграмма стоимости
    cost_data = pd.DataFrame({
        'Статья': ['Металл', 'Крепёж', 'Фундамент', 'Работы'],
        'Стоимость (тыс.₽)': [cost['metal_cost']/1000, cost['fastener_cost']/1000, 
                              cost['foundation_cost']/1000, cost['labor_cost']/1000]
    })
    fig_cost = go.Figure(data=[go.Pie(labels=cost_data['Статья'], values=cost_data['Стоимость (тыс.₽)')])
    fig_cost.update_layout(height=300, paper_bgcolor='#1a1a2e', font=dict(color='white'))
    st.plotly_chart(fig_cost, use_container_width=True)

# ============================================================================
# ФУНДАМЕНТ
# ============================================================================
st.markdown("---")
st.subheader("🏛️ Расчёт фундамента")

st.markdown(f"""
<div class="info-box">
**ПАРАМЕТРЫ:**  
• Тип грунта: **{soil_type}** (несущая способность: {foundation['soil_capacity']} кгс/см²)  
• Количество колонн: **{foundation['num_columns']} шт.**  
• Нагрузка на одну колонну: **{foundation['load_per_column']:.1f} кН**  
• Размер фундамента: **{foundation['foundation_size']:.0f}×{foundation['foundation_size']:.0f} см**  
• Рекомендуемая глубина: **50 см**  
• Бетон: **М300**  
</div>
""", unsafe_allow_html=True)

# ============================================================================
# ЭКСПОРТ
# ============================================================================
st.markdown("---")
st.subheader("💾 Экспорт проектной документации")

# Генерация отчёта
report = generate_report(length, width, height, roof_pitch_deg, truss_forces, sections, loads, foundation, cost, steel_grade)
dxf_data = generate_dxf_data(length, width, height, truss_forces, sections)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.download_button(
        label="📄 Полный отчёт (TXT)",
        data=report,
        file_name=f"Project_Report_{length}x{width}m.txt",
        mime="text/plain",
        use_container_width=True
    )

with col2:
    st.download_button(
        label="📐 Чертеж DXF",
        data=dxf_data,
        file_name=f"Frame_Drawing_{length}x{width}m.dxf",
        mime="application/dxf",
        use_container_width=True
    )

with col3:
    # CSV таблица
    materials_df = pd.DataFrame({
        'Элемент': ['Верхний пояс', 'Нижний пояс', 'Раскосы', 'Стойки', 'Прогоны'],
        'Сечение': [sections['chord']['name'], sections['chord']['name'], 
                    sections['web']['name'], sections['post']['name'], sections['purlin']['name']],
        'Длина_м': [width*2, width*2, width*4, height*2, length*5],
        'Вес_кг': [width*2*sections['chord']['props']['weight'], width*2*sections['chord']['props']['weight'],
                   width*4*sections['web']['props']['weight'], height*2*sections['post']['props']['weight'],
                   length*5*sections['purlin']['props']['weight']]
    })
    st.download_button(
        label="📊 Ведомость (CSV)",
        data=materials_df.to_csv(index=False, sep=';', decimal=','),
        file_name="Materials_Specification.csv",
        mime="text/csv",
        use_container_width=True
    )

with col4:
    # JSON проект
    project_json = json.dumps({
        'geometry': {'length': length, 'width': width, 'height': height, 'roof_pitch': roof_pitch_deg},
        'materials': {'steel_grade': steel_grade, 'optimization': optimization},
        'results': {
            'snow_load': snow_load['S0'],
            'wind_load': wind_load['W0'],
            'total_cost': cost['total_cost'],
            'metal_weight': cost['metal_weight'],
            'max_utilization': max_util
        },
        'timestamp': datetime.now().isoformat()
    }, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="💾 Проект (JSON)",
        data=project_json,
        file_name=f"Project_{length}x{width}m.json",
        mime="application/json",
        use_container_width=True
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")

with st.expander("📚 Нормативная база"):
    st.markdown("""
    **Расчёт выполнен по:**
    • СП 20.13330.2016 "Нагрузки и воздействия"
    • СП 16.13330.2017 "Стальные конструкции"
    • ГОСТ 30245-2003 "Профили стальные гнутые замкнутые"
    • ГОСТ 27772-2015 "Прокат для строительных стальных конструкций"
    """)

st.warning("""
⚠️ **ВАЖНО:** Данный расчёт является предварительным и не заменяет проектную документацию.
Для строительства необходимо выполнить полный расчёт в специализированном ПО (ЛИРА, SCAD) 
и получить экспертизу проекта в соответствии с Градостроительным кодексом РФ.
""")

st.markdown(f"""
<div style='text-align: center; color: #00d9ff; margin-top: 50px; padding: 20px; border-top: 2px solid #00d9ff;'>
<strong>🏗️ Metal Constructor PRO v2.0</strong><br>
Дата расчёта: {datetime.now().strftime('%d.%m.%Y %H:%M')} | 
Размеры: {length}м × {width}м × {height}м | 
Сталь: {steel_grade} | 
Стоимость: {cost['total_cost']:,.0f} ₽
</div>
""", unsafe_allow_html=True)