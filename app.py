import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import io
from datetime import datetime
import math
import json

# ============================================================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ============================================================================
st.set_page_config(
    page_title="🏗️ Metal Constructor PRO",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# БАЗА ДАННЫХ ПРОФИЛЕЙ
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
        },
        'Прямоугольные': {
            '60×40×3': {'b': 60, 'h': 40, 't': 3, 'area': 5.49, 'ix': 2.12, 'weight': 4.31, 'price': 165},
            '80×40×3': {'b': 80, 'h': 40, 't': 3, 'area': 6.69, 'ix': 2.82, 'weight': 5.25, 'price': 175},
            '80×40×4': {'b': 80, 'h': 40, 't': 4, 'area': 8.73, 'ix': 2.77, 'weight': 6.86, 'price': 185},
            '100×50×4': {'b': 100, 'h': 50, 't': 4, 'area': 11.89, 'ix': 3.67, 'weight': 9.33, 'price': 210},
        }
    }

@st.cache_data
def get_steel_grades():
    """Марки стали по ГОСТ 27772-2015"""
    return {
        'С245': {'Ry': 240, 'Run': 240, 'price_factor': 1.0},
        'С255': {'Ry': 250, 'Run': 250, 'price_factor': 1.05},
        'С345': {'Ry': 320, 'Run': 345, 'price_factor': 1.25},
        'С355': {'Ry': 335, 'Run': 355, 'price_factor': 1.30},
        'С390': {'Ry': 370, 'Run': 390, 'price_factor': 1.45},
    }

# ============================================================================
# РАСЧЁТНЫЕ ФУНКЦИИ
# ============================================================================

def calculate_snow_load(district, roof_pitch_deg):
    snow_map = {'I': 0.5, 'II': 0.7, 'III': 1.0, 'IV': 1.5, 'V': 2.0, 'VI': 2.5, 'VII': 3.0, 'VIII': 3.5}
    Sg = snow_map.get(district, 1.5)
    
    if roof_pitch_deg <= 25:
        mu = 1.0
    elif roof_pitch_deg <= 60:
        mu = max(0, 1.0 - (roof_pitch_deg - 25) / 35 * 0.3)
    else:
        mu = 0.0
    
    gamma_f = 1.4
    S0 = 0.7 * mu * Sg * gamma_f
    
    return {'Sg': Sg, 'S0': S0, 'mu': mu, 'gamma_f': gamma_f}

def calculate_wind_load(district, height):
    wind_map = {'Ia': 0.17, 'I': 0.23, 'II': 0.30, 'III': 0.38, 'IV': 0.48, 'V': 0.60}
    w0 = wind_map.get(district, 0.30)
    
    k = 1.0 if height < 10 else 1.25
    ce = 0.8
    gamma_fw = 1.4
    W0 = w0 * k * ce * gamma_fw
    
    return {'w0': w0, 'k': k, 'ce': ce, 'W0': W0}

def calculate_truss_forces(width, height, roof_pitch_deg, truss_spacing, snow_load, wind_load):
    truss_height = width / 6
    roof_height = height + truss_height
    
    permanent_load = 0.15
    total_load = snow_load + permanent_load
    q = total_load * truss_spacing
    
    M_max = q * width**2 / 8
    N_chord = M_max / truss_height if truss_height > 0 else 0
    V_max = q * width / 2
    N_web = V_max / math.sin(math.radians(45))
    N_post = q * truss_spacing
    
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
    steel_props = get_steel_grades()
    Ry = steel_props.get(steel_grade, {'Ry': 320})['Ry']
    gamma_c = 0.9
    R = Ry * gamma_c / 1.05
    
    A_chord_req = forces['N_chord'] * 10 / R
    A_web_req = forces['N_web'] * 10 / R
    A_post_req = forces['N_post'] * 10 / R
    
    opt_factors = {'💰 Экономия': 1.0, '⚖️ Баланс': 1.15, '💪 Прочность': 1.3, '🏆 Премиум': 1.5}
    af = opt_factors.get(optimization, 1.15)
    
    def find_profile(required_area, profiles):
        for name, props in sorted(profiles.items(), key=lambda x: x[1]['area']):
            if props['area'] >= required_area * af:
                return name, props
        return list(profiles.items())[-1]
    
    chord_name, chord_props = find_profile(A_chord_req, profiles_db['Квадратные'])
    web_name, web_props = find_profile(A_web_req, profiles_db['Квадратные'])
    post_name, post_props = find_profile(A_post_req, profiles_db['Квадратные'])
    purlin_name, purlin_props = find_profile(A_web_req * 0.5, profiles_db['Прямоугольные'])
    
    stress_chord = forces['N_chord'] * 10 / chord_props['area']
    stress_web = forces['N_web'] * 10 / web_props['area']
    stress_post = forces['N_post'] * 10 / post_props['area']
    
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

def calculate_cost(length, width, height, sections, truss_spacing):
    num_trusses = int(length / truss_spacing) + 1
    
    chord_length = width * 2 * num_trusses
    post_length = height * 2 * num_trusses
    purlin_length = length * 5
    
    metal_cost = (
        chord_length * sections['chord']['props']['weight'] * sections['chord']['props']['price'] +
        post_length * sections['post']['props']['weight'] * sections['post']['props']['price'] +
        purlin_length * sections['purlin']['props']['weight'] * sections['purlin']['props']['price']
    )
    
    fastener_cost = metal_cost * 0.1
    foundation_cost = num_trusses * 2 * 3000
    labor_cost = metal_cost * 0.4
    total_cost = metal_cost + fastener_cost + foundation_cost + labor_cost
    
    metal_weight = chord_length * sections['chord']['props']['weight'] + \
                   post_length * sections['post']['props']['weight'] + \
                   purlin_length * sections['purlin']['props']['weight']
    
    return {
        'metal_cost': metal_cost,
        'fastener_cost': fastener_cost,
        'foundation_cost': foundation_cost,
        'labor_cost': labor_cost,
        'total_cost': total_cost,
        'metal_weight': metal_weight
    }

# ============================================================================
# 3D ВИЗУАЛИЗАЦИЯ
# ============================================================================

def create_3d_model(length, width, height, roof_pitch_deg, truss_spacing, calc):
    fig = go.Figure()
    
    num_trusses = int(length / truss_spacing) + 1
    truss_height = calc['truss_height']
    roof_height = calc['roof_height']
    num_panels = calc['num_panels']
    panel_length = calc['panel_length']
    
    # Стойки (красные)
    for i in range(num_trusses):
        x = i * truss_spacing
        fig.add_trace(go.Scatter3d(x=[x, x], y=[0, 0], z=[0, height],
            mode='lines', line=dict(color='#FF4444', width=12),
            name='Колонны' if i == 0 else '', showlegend=(i==0)))
        fig.add_trace(go.Scatter3d(x=[x, x], y=[width, width], z=[0, height],
            mode='lines', line=dict(color='#FF4444', width=12), showlegend=False))
    
    # Фермы (зелёные)
    for i in range(num_trusses):
        x = i * truss_spacing
        
        fig.add_trace(go.Scatter3d(x=[x, x], y=[0, width], z=[height, height],
            mode='lines', line=dict(color='#00FF88', width=10),
            name='Фермы' if i == 0 else '', showlegend=(i==0)))
        
        y_left = np.linspace(0, width/2, num_panels//2 + 1)
        z_left = height + (y_left / (width/2)) * truss_height
        fig.add_trace(go.Scatter3d(x=[x]*len(y_left), y=y_left, z=z_left,
            mode='lines', line=dict(color='#00FF88', width=10), showlegend=False))
        
        y_right = np.linspace(width/2, width, num_panels//2 + 1)
        z_right = roof_height - ((y_right - width/2) / (width/2)) * truss_height
        fig.add_trace(go.Scatter3d(x=[x]*len(y_right), y=y_right, z=z_right,
            mode='lines', line=dict(color='#00FF88', width=10), showlegend=False))
        
        for j in range(num_panels + 1):
            y_pos = j * panel_length
            if y_pos <= width/2:
                z_top = height + (y_pos / (width/2)) * truss_height
            else:
                z_top = roof_height - ((y_pos - width/2) / (width/2)) * truss_height
            fig.add_trace(go.Scatter3d(x=[x, x], y=[y_pos, y_pos], z=[height, z_top],
                mode='lines', line=dict(color='#00FF88', width=6), showlegend=False))
    
    # Прогоны (бирюзовые)
    for j in range(5):
        y_pos = (j + 1) * width / 6
        if y_pos <= width/2:
            z_pos = height + (y_pos / (width/2)) * truss_height
        else:
            z_pos = roof_height - ((y_pos - width/2) / (width/2)) * truss_height
        fig.add_trace(go.Scatter3d(x=[0, length], y=[y_pos, y_pos], z=[z_pos, z_pos],
            mode='lines', line=dict(color='#00D9FF', width=11),
            name='Прогоны' if j == 0 else '', showlegend=(j==0)))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Длина (м)', range=[0, length]),
            yaxis=dict(title='Ширина (м)', range=[0, width]),
            zaxis=dict(title='Высота (м)', range=[0, roof_height + 2]),
            aspectmode='manual',
            aspectratio=dict(x=2.5, y=1, z=0.8)
        ),
        height=600,
        showlegend=True,
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    return fig

# ============================================================================
# ОСНОВНОЙ ИНТЕРФЕЙС
# ============================================================================

st.title("🏗️ Metal Constructor PRO")
st.markdown("**Профессиональный расчёт металлоконструкций**")

# Загрузка баз данных
profiles_db = get_profiles_database()
steel_grades = get_steel_grades()

# Боковая панель
with st.sidebar:
    st.header("⚙️ ПАРАМЕТРЫ")
    
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
    wind_district = st.selectbox("Ветровой район", ["Ia", "I", "II", "III", "IV", "V"], index=2)
    
    st.subheader("🏗️ Материалы")
    steel_grade = st.selectbox("Марка стали", list(steel_grades.keys()), index=2)
    optimization = st.radio("Оптимизация", ["💰 Экономия", "⚖️ Баланс", "💪 Прочность", "🏆 Премиум"], index=1)

# Расчёты
snow_load = calculate_snow_load(snow_district, roof_pitch_deg)
wind_load = calculate_wind_load(wind_district, height)
truss_forces = calculate_truss_forces(width, height, roof_pitch_deg, truss_spacing, snow_load['S0'], wind_load['W0'])
sections = select_sections(truss_forces, steel_grade, optimization, profiles_db)
cost = calculate_cost(length, width, height, sections, truss_spacing)

# Метрики
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("❄️ Снег", f"{snow_load['S0']:.2f} кПа")
with col2:
    st.metric("💨 Ветер", f"{wind_load['W0']:.2f} кПа")
with col3:
    st.metric("🏗️ Нагрузка", f"{truss_forces['q']:.2f} кН/м")
with col4:
    st.metric("📐 Высота", f"{truss_forces['roof_height']:.2f} м")
with col5:
    st.metric("💰 Стоимость", f"{cost['total_cost']:,.0f} ₽")

st.markdown("---")

# 3D модель
st.subheader("🏗️ 3D Модель каркаса")

st.info("**Цветовая схема:** 🔴 Колонны | 🟢 Фермы | 🔵 Прогоны")

fig_3d = create_3d_model(length, width, height, roof_pitch_deg, truss_spacing, truss_forces)
st.plotly_chart(fig_3d, use_container_width=True)

# Анализ напряжений
st.markdown("---")
st.subheader("🔍 Анализ напряжений")

col1, col2, col3 = st.columns(3)

with col1:
    status = "🔴 ПЕРЕГРУЗ" if sections['chord']['util'] > 100 else ("🟡 Повышенное" if sections['chord']['util'] > 80 else "🟢 Норма")
    st.metric("Пояса ферм", f"{sections['chord']['util']:.1f}%", delta=status)
    st.write(f"Сечение: {sections['chord']['name']} мм")
    st.write(f"Напряжение: {sections['chord']['stress']:.1f} МПа")

with col2:
    status = "🔴 ПЕРЕГРУЗ" if sections['web']['util'] > 100 else ("🟡 Повышенное" if sections['web']['util'] > 80 else "🟢 Норма")
    st.metric("Раскосы", f"{sections['web']['util']:.1f}%", delta=status)
    st.write(f"Сечение: {sections['web']['name']} мм")
    st.write(f"Напряжение: {sections['web']['stress']:.1f} МПа")

with col3:
    status = "🔴 ПЕРЕГРУЗ" if sections['post']['util'] > 100 else ("🟡 Повышенное" if sections['post']['util'] > 80 else "🟢 Норма")
    st.metric("Стойки", f"{sections['post']['util']:.1f}%", delta=status)
    st.write(f"Сечение: {sections['post']['name']} мм")
    st.write(f"Напряжение: {sections['post']['stress']:.1f} МПа")

# Предупреждения
max_util = max(sections['chord']['util'], sections['web']['util'], sections['post']['util'])
if max_util > 100:
    st.error("⚠️ **КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ!** Обнаружены элементы с перегрузкой!")
elif max_util > 80:
    st.warning("⚠️ **ВНИМАНИЕ:** Повышенные напряжения в элементах.")
else:
    st.success("✅ **Все элементы в норме!**")

# Сметный расчёт
st.markdown("---")
st.subheader("💰 Сметный расчёт")

col1, col2 = st.columns(2)

with col1:
    st.write("**МАТЕРИАЛЫ:**")
    st.write(f"• Металлоконструкции: **{cost['metal_cost']:,.0f} ₽**")
    st.write(f"• Крепёж: **{cost['fastener_cost']:,.0f} ₽**")
    st.write(f"• Фундамент: **{cost['foundation_cost']:,.0f} ₽**")
    st.write(f"• Работы: **{cost['labor_cost']:,.0f} ₽**")
    st.markdown("---")
    st.write(f"**ИТОГО: {cost['total_cost']:,.0f} ₽**")
    st.write(f"Вес металла: **{cost['metal_weight']:.0f} кг**")

with col2:
    cost_data = pd.DataFrame({
        'Статья': ['Металл', 'Крепёж', 'Фундамент', 'Работы'],
        'Стоимость': [cost['metal_cost']/1000, cost['fastener_cost']/1000, 
                      cost['foundation_cost']/1000, cost['labor_cost']/1000]
    })
    fig_cost = go.Figure(data=[go.Pie(labels=cost_data['Статья'], values=cost_data['Стоимость'])])
    st.plotly_chart(fig_cost, use_container_width=True)

# Экспорт
st.markdown("---")
st.subheader("💾 Экспорт")

report = f"""
ПРОЕКТ КАРКАСА ЗДАНИЯ
Metal Constructor PRO v2.0
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ГЕОМЕТРИЯ:
Длина: {length} м
Ширина: {width} м
Высота: {height} м
Уклон: {roof_pitch_deg}°

НАГРУЗКИ:
Снег: {snow_load['S0']:.2f} кПа
Ветер: {wind_load['W0']:.2f} кПа

СЕЧЕНИЯ:
Верхний пояс: {sections['chord']['name']} мм
Нижний пояс: {sections['chord']['name']} мм
Раскосы: {sections['web']['name']} мм
Стойки: {sections['post']['name']} мм
Прогоны: {sections['purlin']['name']} мм

СТОИМОСТЬ: {cost['total_cost']:,.0f} ₽
Вес металла: {cost['metal_weight']:.0f} кг
"""

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="📄 Скачать отчёт (TXT)",
        data=report,
        file_name=f"Project_{length}x{width}m.txt",
        mime="text/plain",
        use_container_width=True
    )

with col2:
    materials_df = pd.DataFrame({
        'Элемент': ['Верхний пояс', 'Нижний пояс', 'Раскосы', 'Стойки', 'Прогоны'],
        'Сечение': [sections['chord']['name'], sections['chord']['name'], 
                    sections['web']['name'], sections['post']['name'], sections['purlin']['name']],
        'Вес_кг': [width*2*sections['chord']['props']['weight'], width*2*sections['chord']['props']['weight'],
                   width*4*sections['web']['props']['weight'], height*2*sections['post']['props']['weight'],
                   length*5*sections['purlin']['props']['weight']]
    })
    st.download_button(
        label="📊 Ведомость (CSV)",
        data=materials_df.to_csv(index=False, sep=';', decimal=','),
        file_name="Materials.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.warning("⚠️ **ВАЖНО:** Расчёт предварительный. Для строительства нужен полный проект по СП.")

st.markdown(f"""
**Metal Constructor PRO v2.0** | {datetime.now().strftime('%d.%m.%Y %H:%M')} | 
{length}м × {width}м × {height}м | {cost['total_cost']:,.0f} ₽
""")
