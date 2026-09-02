import json
import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_FILE = "data.json"
APP_TITLE = "💎 Мои привычки"

# === ДЕФОЛТНЫЙ СПИСОК ПРИВЫЧЕК ===
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

def parse_habit_value(raw_input, habit_key, date_str):
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

def format_date_ru(date_obj):
    months = ["января", "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return f"{date_obj.day} {months[date_obj.month-1]} {date_obj.year}"

# ==================== КОЛЕСО БАЛАНСА ====================
def render_wheel_balance(data):
    st.subheader("🎡 Колесо баланса")
    categories = ["health", "finances", "career", "relationships", "growth", "rest", "spirituality", "environment", "discipline"]
    category_names = {
        "health": "Здоровье", "finances": "Финансы", "career": "Карьера",
        "relationships": "Отношения", "growth": "Личностный рост",
        "rest": "Отдых", "spirituality": "Духовность", "environment": "Окружение",
        "discipline": "Дисциплина"
    }
    hints = {
        "health": "💡 *Здоровье — это энергия, чтобы делать всё остальное.*",
        "finances": "💡 *Финансы — это свобода выбирать.*",
        "career": "💡 *Карьера — это твой вклад в мир.*",
        "relationships": "💡 *Отношения — это зеркало твоих ценностей.*",
        "growth": "💡 *Личностный рост — расширение картины мира.*",
        "rest": "💡 *Отдых — это перезарядка.*",
        "spirituality": "💡 *Духовность — это опора внутри.*",
        "environment": "💡 *Окружение — это твоя средняя температура.*",
        "discipline": "💡 *Дисциплина — это умение делать то, что нужно, даже когда не хочется.*"
    }
    history = data.get("_wheel_history", [])
    current = history[-1].copy() if history else {cat: 5 for cat in categories}
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        with cols[i % 3]:
            current[cat] = st.slider(category_names[cat], 0, 10, current.get(cat, 5), key=f"wheel_{cat}", help=hints[cat])
            st.caption(hints[cat])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Сохранить слепок"):
            history.append({"date": datetime.today().strftime("%Y-%m-%d"), **current})
            data["_wheel_history"] = history
            save_data(data)
            st.success("Слепок сохранён!")
            st.rerun()
    with col2:
        if st.button("🔄 Обновить текущие оценки"):
            if history:
                history[-1] = {"date": datetime.today().strftime("%Y-%m-%d"), **current}
            else:
                history.append({"date": datetime.today().strftime("%Y-%m-%d"), **current})
            data["_wheel_history"] = history
            save_data(data)
            st.success("Обновлено!")
            st.rerun()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[current[cat] for cat in categories], theta=[category_names[cat] for cat in categories], fill='toself', line=dict(color="blue")))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    if len(history) > 1:
        df_history = pd.DataFrame(history)
        df_history["date"] = pd.to_datetime(df_history["date"])
        fig2 = go.Figure()
        for cat in categories:
            fig2.add_trace(go.Scatter(x=df_history["date"], y=df_history[cat], mode="lines+markers", name=category_names[cat]))
        fig2.update_layout(title="Динамика сфер", xaxis_title="Дата", yaxis_title="Оценка", height=400)
        st.plotly_chart(fig2, use_container_width=True)

# ==================== SMART-ЦЕЛИ ====================
def render_smart_goals(data):
    st.subheader("🎯 SMART-цели")
    goals = data.get("_smart_goals", [])
    with st.expander("➕ Добавить новую SMART-цель"):
        title = st.text_input("Название цели")
        specific = st.text_area("S (Specific) — Что именно?")
        measurable = st.text_input("M (Measurable) — Как измерить?")
        achievable = st.text_area("A (Achievable) — Какие шаги?")
        relevant = st.text_area("R (Relevant) — Зачем это тебе?")
        deadline = st.date_input("T (Time-bound) — Дедлайн", value=datetime.today().date() + timedelta(days=30))
        progress = st.slider("Прогресс (%)", 0, 100, 0)
        if st.button("✅ Добавить цель"):
            if title and specific and measurable:
                goals.append({"id": f"goal_{len(goals)}", "title": title, "specific": specific, "measurable": measurable, "achievable": achievable, "relevant": relevant, "deadline": deadline.strftime("%Y-%m-%d"), "progress": progress})
                data["_smart_goals"] = goals
                save_data(data)
                st.success("Цель добавлена!")
                st.rerun()
    if goals:
        for idx, goal in enumerate(goals):
            st.write(f"**{idx+1}. {goal['title']}**")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"- **S:** {goal['specific']}\n- **M:** {goal['measurable']}\n- **A:** {goal['achievable']}\n- **R:** {goal['relevant']}\n- **T:** {goal['deadline']}")
            with col2:
                st.metric("Прогресс", f"{goal['progress']}%")
                st.progress(goal['progress'] / 100)
                new_progress = st.slider(f"Обновить прогресс", 0, 100, goal['progress'], key=f"progress_{idx}")
                if new_progress != goal['progress']:
                    goals[idx]['progress'] = new_progress
                    data["_smart_goals"] = goals
                    save_data(data)
                    st.rerun()
            if st.button(f"❌ Удалить цель {idx+1}", key=f"del_goal_{idx}"):
                goals.pop(idx)
                data["_smart_goals"] = goals
                save_data(data)
                st.rerun()
            st.divider()

# ==================== ТРЕКЕР ТЕЛА ====================
def render_body_tracker(data):
    st.subheader("🧍 Анатомия (замеры тела)")
    body_history = data.get("_body_history", [])
    params = {
        "weight": "Вес (кг)",
        "height": "Рост (см)",
        "neck": "Шея (см)",
        "chest": "Грудь (см)",
        "biceps": "Бицепс (см)",
        "waist": "Талия (см)",
        "hips": "Бёдра (см)",
        "calves": "Икры (см)",
        "forearm": "Предплечье (см)"
    }
    current = body_history[-1].copy() if body_history else {param: 0 for param in params}
    cols = st.columns(3)
    for i, (param, label) in enumerate(params.items()):
        with cols[i % 3]:
            current[param] = st.number_input(label, min_value=0, step=1, value=current.get(param, 0), key=f"body_{param}")
    if st.button("📏 Сохранить замер"):
        current["date"] = datetime.today().strftime("%Y-%m-%d")
        body_history.append(current)
        data["_body_history"] = body_history
        save_data(data)
        st.success("Замер сохранён!")
        st.rerun()
    if body_history:
        df_body = pd.DataFrame(body_history)
        df_body["date"] = pd.to_datetime(df_body["date"])
        df_body = df_body.sort_values("date")
        st.write("**Динамика веса**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_body["date"], y=df_body["weight"], mode="lines+markers", name="Вес (кг)", line=dict(color="green")))
        fig.update_layout(xaxis_title="Дата", yaxis_title="Вес (кг)", height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.write("**Последние замеры**")
        st.dataframe(df_body.tail(5)[["date"] + list(params.keys())].style.format({"date": lambda x: x.strftime("%Y-%m-%d")}))

# ==================== РЕВЬЮ НЕДЕЛИ ====================
def render_weekly_review(data):
    st.subheader("📝 Ревью недели")
    
    # Выбор даты для ревью (по умолчанию сегодня)
    review_date = st.date_input("Дата ревью", value=datetime.today().date(), max_value=datetime.today().date())
    review_key = f"_weekly_review_{review_date.strftime('%Y-%m-%d')}"
    
    # Загружаем существующее ревью или создаём пустое
    review = data.get(review_key, {"done": "", "blocker": "", "win": "", "score": 5})
    
    # Поля ввода
    review["done"] = st.text_area("✅ Что сделано за неделю?", value=review.get("done", ""), height=68)
    review["blocker"] = st.text_area("🚧 Что мешало?", value=review.get("blocker", ""), height=68)
    review["win"] = st.text_area("🏆 Одна победа", value=review.get("win", ""), height=68)
    review["score"] = st.slider("Оценка недели (1–10)", 1, 10, review.get("score", 5))
    
    # Кнопка сохранения
    if st.button("💾 Сохранить ревью"):
        data[review_key] = review
        save_data(data)
        st.success("Ревью сохранено!")
        st.rerun()
    
    # --- ИСТОРИЯ РЕВЬЮ ---
    st.write("---")
    st.write("**📜 История ревью**")
    
    # Собираем все ревью из data
    all_reviews = []
    for key, value in data.items():
        if key.startswith("_weekly_review_"):
            date_str = key.replace("_weekly_review_", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                all_reviews.append({
                    "date": date_obj,
                    "date_str": date_str,
                    "done": value.get("done", ""),
                    "blocker": value.get("blocker", ""),
                    "win": value.get("win", ""),
                    "score": value.get("score", 5)
                })
            except:
                pass
    
    if all_reviews:
        # Сортируем по дате (сначала новые)
        all_reviews.sort(key=lambda x: x["date"], reverse=True)
        
        # График оценок недели
        df_reviews = pd.DataFrame(all_reviews)
        df_reviews = df_reviews.sort_values("date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_reviews["date"], y=df_reviews["score"], mode="lines+markers", name="Оценка недели", line=dict(color="purple")))
        fig.update_layout(title="Динамика оценок недели", xaxis_title="Дата", yaxis_title="Оценка (1–10)", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Показываем последние 5 ревью
        st.write("**Последние ревью**")
        for review in all_reviews[:5]:
            with st.expander(f"📅 {review['date_str']} — Оценка: {review['score']}/10"):
                st.write(f"**✅ Что сделано:** {review['done']}")
                st.write(f"**🚧 Что мешало:** {review['blocker']}")
                st.write(f"**🏆 Победа:** {review['win']}")
    else:
        st.info("Пока нет сохранённых ревью. Начни с первого!")

# ==================== ОСНОВНОЙ ИНТЕРФЕЙС ====================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
data = load_data()

# --- 1. КОЛЕСО БАЛАНСА ---
render_wheel_balance(data)
st.divider()

# --- 2. SMART-ЦЕЛИ ---
render_smart_goals(data)
st.divider()

# --- 3. ТРЕКЕР ТЕЛА ---
render_body_tracker(data)
st.divider()

# --- 4. РЕВЬЮ НЕДЕЛИ ---
render_weekly_review(data)
st.divider()

# --- 5. ПРИВЫЧКИ ---
st.subheader("📋 Ежедневные привычки")
habits_config = data.get("_habits_config", DEFAULT_HABITS)
with st.expander("⚙️ Настройка привычек"):
    st.write("Измени лимиты или добавь новую привычку")
    new_habit_name = st.text_input("Название новой привычки")
    new_habit_unit = st.text_input("Единица измерения")
    new_habit_min = st.number_input("Минимальное значение", min_value=1, value=10)
    if st.button("➕ Добавить привычку"):
        if new_habit_name:
            key = new_habit_name.lower().replace(" ", "_")
            habits_config[key] = {"name": new_habit_name, "unit": new_habit_unit, "min": new_habit_min}
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
                data["_habits_config"] = habits_config
                save_data(data)
                st.rerun()
        with col3:
            if st.button(f"❌ Удалить {habit['name']}", key=f"del_{key}"):
                habits_config.pop(key)
                data["_habits_config"] = habits_config
                save_data(data)
                st.rerun()

today = datetime.today().date()
date_input = st.date_input("Выберите дату", value=today, max_value=today)
date_str = date_input.strftime("%Y-%m-%d")
day_data = data.get(date_str, {})
st.write(f"## {format_date_ru(date_input)}")
cols = st.columns(3)
for idx, (key, habit) in enumerate(habits_config.items()):
    with cols[idx % 3]:
        val = day_data.get(key, None)
        if val is not None:
            if habit["unit"]:
                st.write(f"**{habit['name']}:** {val} {habit['unit']}")
            else:
                st.write(f"**{habit['name']}:** {'✅' if val else '❌'}")
        else:
            st.write(f"**{habit['name']}:** —")
        if habit["unit"]:
            user_input = st.text_input(f"Добавить ({habit['name']})", key=f"inp_{date_str}_{key}", placeholder="10+20 или 30")
            if st.button(f"Сохранить {habit['name']}", key=f"btn_{date_str}_{key}"):
                if user_input:
                    new_val = parse_habit_value(user_input, key, date_str)
                    st.success(f"Сохранено! {habit['name']}: {new_val} {habit['unit']}")
                    st.rerun()
        else:
            if st.button(f"Переключить {habit['name']}", key=f"tog_{date_str}_{key}"):
                new_val = not val if val is not None else True
                save_habit(date_str, key, new_val)
                st.rerun()

st.divider()
st.subheader("📊 Календарь привычек за месяц")
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
            if val is None:
                matrix[key].append("⬜")
            elif val >= habits_config[key]["min"]:
                matrix[key].append("🟩")
            else:
                matrix[key].append("⬛")
        else:
            matrix[key].append("✅" if val else ("⬜" if val is None else "❌"))
df_matrix = pd.DataFrame(matrix, index=[f"{i+1}" for i in range(len(dates_in_month))])
df_matrix.rename(columns={k: habits_config[k]["name"] for k in habits_config}, inplace=True)
st.dataframe(df_matrix.T, use_container_width=True)

st.divider()
st.subheader("📈 Прогресс по привычкам")
for key, habit in habits_config.items():
    if habit["unit"]:
        dates, values, cumulative, cum_sum = [], [], [], 0
        for d, day_info in sorted(data.items()):
            if d <= date_str and not d.startswith("_") and d != "_habits_config":
                val = day_info.get(key)
                if val is not None:
                    dates.append(d); values.append(val); cum_sum += val; cumulative.append(cum_sum)
        if dates:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=dates, y=values, name="Ежедневно", marker_color="blue", text=values, textposition="outside"))
            fig1.add_hline(y=habit["min"], line_dash="dot", line_color="red", annotation_text=f"Цель {habit['min']} {habit['unit']}")
            fig1.update_layout(title=f"{habit['name']} (ежедневно)", xaxis_title="Дата", yaxis_title=habit['unit'], height=300)
            st.plotly_chart(fig1, use_container_width=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=dates, y=cumulative, mode="lines+markers", name="Накоплено всего", line=dict(color="green", width=2), marker=dict(color="green", size=8), text=cumulative, textposition="top center"))
            fig2.update_layout(title=f"{habit['name']} (всего: {cum_sum} {habit['unit']})", xaxis_title="Дата", yaxis_title="Накоплено", height=300)
            st.plotly_chart(fig2, use_container_width=True)

st.divider()
if st.button("Сбросить все данные"):
    save_data({})
    st.warning("Все данные удалены")
    st.rerun()