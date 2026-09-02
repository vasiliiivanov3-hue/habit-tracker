import json
import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_FILE = "data.json"
APP_TITLE = "💎 Мои привычки"  # Меняй здесь название

# === ДЕФОЛТНЫЙ СПИСОК ПРИВЫЧЕК (можно менять) ===
DEFAULT_HABITS = {
    "pushups": {"name": "Отжимания", "unit": "раз", "min": 15},
    "book": {"name": "Книга", "unit": "стр.", "min": 10},
    "abs": {"name": "Пресс", "unit": "раз", "min": 15},
    "squats": {"name": "Приседания", "unit": "раз", "min": 15},
    "bedtime": {"name": "Отбой до 23:00", "unit": "", "min": 1},
    "wakeup": {"name": "Подъем до 7:00", "unit": "", "min": 1},
    "meditation": {"name": "Медитация", "unit": "", "min": 1},
    "abstinence": {"name": "Воздержание", "unit": "", "min": 1},
    "savings": {"name": "Отложил 1000₽", "unit": "₽", "min": 1000},
    "nofoul": {"name": "Не матерился", "unit": "", "min": 1},
}

# === ЗАГРУЗКА/СОХРАНЕНИЕ ===
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

def get_day_data(date_str):
    data = load_data()
    return data.get(date_str, {})

def save_habit(date_str, habit_key, value):
    data = load_data()
    if date_str not in data:
        data[date_str] = {}
    data[date_str][habit_key] = value
    save_data(data)

# === ПАРСЕР (исправлен) ===
def parse_habit_value(raw_input, habit_key, date_str):
    """Принимает 10+20, 30, +15 и сохраняет сумму"""
    raw_input = raw_input.replace(" ", "")
    data = load_data()
    if date_str not in data:
        data[date_str] = {}
    current_val = data[date_str].get(habit_key, 0)
    if raw_input.startswith("+"):
        add_val = int(raw_input[1:])
        new_val = current_val + add_val
    elif "+" in raw_input:
        parts = [int(x) for x in raw_input.split("+")]
        new_val = sum(parts)
    else:
        new_val = int(raw_input)
    data[date_str][habit_key] = new_val
    save_data(data)
    return new_val

# === РУССКИЕ ДАТЫ ===
def format_date_ru(date_obj):
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return f"{date_obj.day} {months[date_obj.month-1]} {date_obj.year}"

# === ОТРИСОВКА ===
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# --- ЗАГРУЗКА КАСТОМНЫХ ПРИВЫЧЕК (если есть в data) ---
habits_config = load_data().get("_habits_config", DEFAULT_HABITS)

# --- НАСТРОЙКА ПРИВЫЧЕК (добавление/редактирование) ---
with st.expander("⚙️ Настройка привычек"):
    st.write("Измени лимиты или добавь новую привычку")
    new_habit_name = st.text_input("Название новой привычки (например: 'Планка')")
    new_habit_unit = st.text_input("Единица измерения (например: 'сек', 'раз')")
    new_habit_min = st.number_input("Минимальное значение для засчета", min_value=1, value=10)
    if st.button("➕ Добавить привычку"):
        if new_habit_name:
            key = new_habit_name.lower().replace(" ", "_")
            habits_config[key] = {"name": new_habit_name, "unit": new_habit_unit, "min": new_habit_min}
            data = load_data()
            data["_habits_config"] = habits_config
            save_data(data)
            st.success(f"Привычка '{new_habit_name}' добавлена!")
            st.rerun()
    st.divider()
    for key, habit in habits_config.items():
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            new_min = st.number_input(f"Минимум для {habit['name']}", value=habit["min"], key=f"min_{key}")
        with col2:
            if st.button(f"Обновить {habit['name']}", key=f"upd_{key}"):
                habits_config[key]["min"] = new_min
                data = load_data()
                data["_habits_config"] = habits_config
                save_data(data)
                st.rerun()
        with col3:
            if st.button(f"❌ Удалить {habit['name']}", key=f"del_{key}"):
                habits_config.pop(key)
                data = load_data()
                data["_habits_config"] = habits_config
                save_data(data)
                st.rerun()

# --- ВЫБОР ДАТЫ ---
today = datetime.today().date()
date_input = st.date_input("Выберите дату", value=today, max_value=today)
date_str = date_input.strftime("%Y-%m-%d")
day_data = get_day_data(date_str)

st.write(f"## {format_date_ru(date_input)}")

# --- ВВОД ДЛЯ КАЖДОЙ ПРИВЫЧКИ ---
cols = st.columns(3)
for idx, (key, habit) in enumerate(habits_config.items()):
    with cols[idx % 3]:
        val = day_data.get(key, None)
        # Отображаем нейтрально
        if val is not None:
            if habit["unit"]:
                st.write(f"**{habit['name']}:** {val} {habit['unit']}")
            else:
                st.write(f"**{habit['name']}:** {'✅' if val else '❌'}")
        else:
            st.write(f"**{habit['name']}:** —")
        # Поле ввода для чисел
        if habit["unit"]:
            user_input = st.text_input(f"Добавить ({habit['name']})", key=f"inp_{date_str}_{key}", placeholder="10+20 или 30")
            if st.button(f"Сохранить {habit['name']}", key=f"btn_{date_str}_{key}"):
                if user_input:
                    new_val = parse_habit_value(user_input, key, date_str)
                    st.success(f"Сохранено! {habit['name']}: {new_val} {habit['unit']}")
                    st.rerun()
        else:
            # Галочка для булевых привычек
            if st.button(f"Переключить {habit['name']}", key=f"tog_{date_str}_{key}"):
                new_val = not val if val is not None else True
                save_habit(date_str, key, new_val)
                st.rerun()

st.divider()

# --- МАТРИЦА ЗА МЕСЯЦ ---
st.subheader("📊 Календарь привычек за месяц")
data = load_data()
first_day = date_input.replace(day=1)
last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
dates_in_month = [(first_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(last_day.day)]

matrix = {}
for key in habits_config:
    matrix[key] = []
    for d in dates_in_month:
        day_info = data.get(d, {})
        val = day_info.get(key, None)
        if habits_config[key]["unit"]:
            # Числовая привычка
            if val is None:
                matrix[key].append("⬜")
            elif val >= habits_config[key]["min"]:
                matrix[key].append("🟩")
            else:
                matrix[key].append("⬛")
        else:
            # Булева
            matrix[key].append("✅" if val else ("⬜" if val is None else "❌"))

df_matrix = pd.DataFrame(matrix, index=[f"{i+1}" for i in range(len(dates_in_month))])
df_matrix.rename(columns={k: habits_config[k]["name"] for k in habits_config}, inplace=True)
st.dataframe(df_matrix.T, use_container_width=True)

# --- ГРАФИКИ: ЕЖЕДНЕВНЫЙ И НАКОПИТЕЛЬНЫЙ (РАЗДЕЛЬНО) ---
st.subheader("📈 Прогресс по привычкам")

for key, habit in habits_config.items():
    if habit["unit"]:  # Для числовых привычек
        dates = []
        values = []
        cumulative = []
        cum_sum = 0
        for d, day_info in sorted(data.items()):
            if d <= date_str and d != "_habits_config":
                val = day_info.get(key)
                if val is not None:
                    dates.append(d)
                    values.append(val)
                    cum_sum += val
                    cumulative.append(cum_sum)
        if dates:
            # --- ГРАФИК 1: Ежедневный (столбцы) ---
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=dates,
                y=values,
                name="Ежедневно",
                marker_color="blue",
                text=values,
                textposition="outside"
            ))
            fig1.add_hline(
                y=habit["min"],
                line_dash="dot",
                line_color="red",
                annotation_text=f"Цель {habit['min']} {habit['unit']}"
            )
            fig1.update_layout(
                title=f"{habit['name']} (ежедневно)",
                xaxis_title="Дата",
                yaxis_title=habit['unit'],
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)

            # --- ГРАФИК 2: Накопительный (линия) ---
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=dates,
                y=cumulative,
                mode="lines+markers",
                name="Накоплено всего",
                line=dict(color="green", width=2),
                marker=dict(color="green", size=8),
                text=cumulative,
                textposition="top center"
            ))
            fig2.update_layout(
                title=f"{habit['name']} (всего: {cum_sum} {habit['unit']})",
                xaxis_title="Дата",
                yaxis_title="Накоплено",
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)

    else:  # Для булевых привычек (галочек)
        dates = []
        cumulative = []
        total_days = 0
        done_days = 0
        for d, day_info in sorted(data.items()):
            if d <= date_str and d != "_habits_config":
                val = day_info.get(key)
                if val is not None:
                    dates.append(d)
                    total_days += 1
                    if val:
                        done_days += 1
                    cumulative.append(done_days)
        if dates:
            # --- ГРАФИК 1: Ежедневный (столбцы 1/0) ---
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=dates,
                y=[1 if val else 0 for val in cumulative],
                name="Выполнено",
                marker_color="blue",
                text=["✅" if val else "❌" for val in cumulative],
                textposition="outside"
            ))
            fig1.update_layout(
                title=f"{habit['name']} (ежедневно)",
                xaxis_title="Дата",
                yaxis_title="Выполнено (1=да, 0=нет)",
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)

            # --- ГРАФИК 2: Накопительный (линия) ---
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=dates,
                y=cumulative,
                mode="lines+markers",
                name="Всего дней выполнено",
                line=dict(color="green", width=2),
                marker=dict(color="green", size=8),
                text=cumulative,
                textposition="top center"
            ))
            fig2.update_layout(
                title=f"{habit['name']} (выполнено дней: {done_days} из {total_days})",
                xaxis_title="Дата",
                yaxis_title="Всего дней",
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)