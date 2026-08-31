import json
import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_FILE = "data.json"

# === ЯДРО (тот же код, что работал) ===
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
import streamlit as st
import os

# PWA-подключение (добавляем meta-теги в HTML)
PWA_HTML = """
<link rel="manifest" href="manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js');
  }
</script>
"""
st.markdown(PWA_HTML, unsafe_allow_html=True)

# === ВЕБ-ИНТЕРФЕЙС ===
st.set_page_config(page_title="Трекер Отжиманий", layout="wide")
st.title("💪 Трекер отжиманий")

# Ввод
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_input("Введите подходы (например: 30, 15+15, +10)", placeholder="30")
with col2:
    st.write(" ")
    if st.button("Сохранить"):
        if user_input:
            parse_and_save(user_input)
            st.success(f"Сохранено! Сегодня: {load_data().get(datetime.today().strftime('%Y-%m-%d'), [])}")

# Данные для графиков
stats = get_stats()
if stats:
    df = pd.DataFrame([
        {"Дата": date, "Факт": vals["total"], "Подходы": len(vals["sets"])}
        for date, vals in sorted(stats.items())
    ])
    df["Дата"] = pd.to_datetime(df["Дата"])
    df = df.sort_values("Дата")
    
    # График 1: Факт + Цель (50)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Дата"], y=df["Факт"], name="Факт"))
    fig.add_trace(go.Scatter(x=df["Дата"], y=[50]*len(df), mode="lines", name="Цель (50)", line=dict(dash="dash", color="red")))
    fig.update_layout(title="Цель vs Факт", xaxis_title="Дата", yaxis_title="Отжимания")
    st.plotly_chart(fig, use_container_width=True)
    
    # График 2: Накопительный
    df["Накопительно"] = df["Факт"].cumsum()
    fig2 = px.line(df, x="Дата", y="Накопительно", title="Общий прогресс (сумма с первого дня)")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Таблица последних дней
    st.subheader("Последние записи")
    st.dataframe(df[["Дата", "Факт", "Подходы"]].tail(10))
else:
    st.info("Пока нет данных. Введите первую тренировку!")

# Кнопка сброса (для тестов)
if st.button("Сбросить все данные"):
    save_data({})
    st.warning("Все данные удалены")