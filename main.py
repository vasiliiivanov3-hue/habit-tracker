import json
import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_FILE = "data.json"

# ==================== ЯДРО (БЕЗ ИЗМЕНЕНИЙ) ====================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_and_save(raw_input, date_str=None):
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    raw_input = raw_input.replace(" ", "")
    data = load_data()
    if date_str not in data:
        data[date_str] = []
    if raw_input.startswith("+"):
        new_value = int(raw_input[1:])
        data[date_str].append(new_value)
    elif "+" in raw_input:
        new_sets = [int(x) for x in raw_input.split("+")]
        data[date_str] = new_sets
    else:
        data[date_str] = [int(raw_input)]
    save_data(data)
    return data[date_str]

def get_stats():
    data = load_data()
    stats = {}
    for date, sets in data.items():
        stats[date] = {"sets": sets, "total": sum(sets), "count": len(sets)}
    return stats

# ==================== НОВЫЕ ФУНКЦИИ ДЛЯ СТРИКОВ ====================
def calculate_streak(stats):
    """Рассчитывает текущую серию (количество дней подряд с отжиманиями > 0)"""
    if not stats:
        return 0
    
    # Сортируем даты по убыванию (с сегодня вглубь)
    sorted_dates = sorted(stats.keys(), reverse=True)
    streak = 0
    
    # Проверяем сегодняшний день
    today = datetime.today().strftime("%Y-%m-%d")
    if today not in stats or stats[today]["total"] == 0:
        # Если сегодня нет тренировки, начинаем проверку со вчера
        # (это позволяет не терять стрик, если сегодня еще не занимался)
        sorted_dates = [d for d in sorted_dates if d < today]
    
    for date in sorted_dates:
        if stats[date]["total"] > 0:
            streak += 1
        else:
            break
    return streak

def render_calendar(stats):
    """Рисует мини-календарь (зеленый/красный) для последних 30 дней"""
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, -1, -1)]
    
    cols = st.columns(7)  # 7 дней в неделе
    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for i, name in enumerate(day_names):
        cols[i].write(f"**{name}**")
    
    # Рисуем сетку
    for i, date in enumerate(dates):
        col_idx = (i + 1) % 7  # +1 чтобы начать с понедельника
        if col_idx == 0:
            # Новая строка
            st.write("---")
            cols = st.columns(7)
        
        day = datetime.strptime(date, "%Y-%m-%d").day
        is_weekend = datetime.strptime(date, "%Y-%m-%d").weekday() in [5, 6]
        
        if date in stats and stats[date]["total"] > 0:
            color = "🟩"  # Был тренинг
        elif date < today.strftime("%Y-%m-%d"):
            color = "⬛"  # Пропуск
        else:
            color = "⬜"  # Будущий день
        
        cols[col_idx].write(f"{color} {day}")

# ==================== ВЕБ-ИНТЕРФЕЙС ====================
st.set_page_config(page_title="Трекер Отжиманий", layout="wide")
st.title("💪 Трекер отжиманий")

# ---- БЛОК СТРИКА (НОВЫЙ) ----
stats = get_stats()
streak = calculate_streak(stats)

col_streak, col_goal, _ = st.columns([1, 2, 2])
with col_streak:
    st.metric("🔥 Текущая серия", f"{streak} дней")

# ---- ВВОД (БЕЗ ИЗМЕНЕНИЙ) ----
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_input("Введите подходы (например: 30, 15+15, +10)", placeholder="30")
with col2:
    st.write(" ")
    if st.button("Сохранить", use_container_width=True):
        if user_input:
            parse_and_save(user_input)
            st.success(f"Сохранено! Сегодня: {load_data().get(datetime.today().strftime('%Y-%m-%d'), [])}")
            st.rerun()

# ---- ГРАФИКИ (БЕЗ ИЗМЕНЕНИЙ) ----
stats = get_stats()
if stats:
    df = pd.DataFrame([
        {"Дата": date, "Факт": vals["total"], "Подходы": len(vals["sets"])}
        for date, vals in sorted(stats.items())
    ])
    df["Дата"] = pd.to_datetime(df["Дата"])
    df = df.sort_values("Дата")
    df["Накопительно"] = df["Факт"].cumsum()  # <-- ЭТА СТРОКА БЫЛА ПОТЕРЯНА!
    
    # ===== ГРАФИК 1: Цель vs Факт (с подписями) =====
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["Дата"], 
        y=df["Факт"], 
        name="Факт",
        text=df["Факт"],
        textposition="outside",
        textfont=dict(size=12, color="black")
    ))
    
    fig.add_trace(go.Scatter(
        x=df["Дата"], 
        y=[50]*len(df), 
        mode="lines", 
        name="Цель (50)", 
        line=dict(dash="dash", color="red")
    ))
    
    fig.update_layout(
        title="Цель vs Факт (цифры на столбцах)",
        xaxis_title="Дата",
        yaxis_title="Отжимания"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ===== ГРАФИК 2: Накопительный (с подписями) =====
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=df["Дата"], 
        y=df["Накопительно"], 
        mode="lines+markers+text",
        name="Накопительный итог",
        text=df["Накопительно"],
        textposition="top center",
        textfont=dict(size=11, color="darkblue"),
        marker=dict(size=10)
    ))
    
    fig2.update_layout(
        title="Общий прогресс (сумма с первого дня)",
        xaxis_title="Дата",
        yaxis_title="Всего отжиманий"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # ---- КАЛЕНДАРЬ ----
    st.subheader("📅 Календарь активности (последние 30 дней)")
    render_calendar(stats)
    
    # ---- ТАБЛИЦА ----
    st.subheader("Последние записи")
    st.dataframe(df[["Дата", "Факт", "Подходы"]].tail(10))
else:
    st.info("Пока нет данных. Введите первую тренировку!")
# ---- СБРОС (ДЛЯ ТЕСТОВ) ----
if st.button("Сбросить все данные"):
    save_data({})
    st.warning("Все данные удалены")
    st.rerun()