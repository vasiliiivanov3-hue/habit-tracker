import json
import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_FILE = "data.json"
APP_TITLE = "💎 Мои привычки"

DEFAULT_HABITS = {
    "workout": {"name": "Тренировка", "unit": "", "min": 1},
    "pushups": {"name": "Отжимания", "unit": "раз", "min": 15},
    "book": {"name": "Книга", "unit": "стр.", "min": 10},
    "abs": {"name": "Пресс", "unit": "раз", "min": 15},
    "squats": {"name": "Приседания", "unit": "раз", "min": 15},
    "bedtime": {"name": "Отбой до 23:00", "unit": "", "min": 1},
    "wakeup": {"name": "Подъем до 7:00", "unit": "", "min": 1},
    "meditation": {"name": "Медитация", "unit": "", "min": 1},
    "savings": {"name": "Отложил 1000₽", "unit": "₽", "min": 1000},
    "nofoul": {"name": "Не матерился", "unit": "", "min": 1},
}

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

# ==================== ДОСТИЖЕНИЯ ====================
def calculate_streak(data, habit_key):
    """Считает текущую серию дней подряд с выполненной привычкой"""
    today = datetime.today().date()
    streak = 0
    for i in range(365):
        check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        day = data.get(check_date, {})
        if not isinstance(day, dict):
            break
        val = day.get(habit_key, 0)
        # Проверка: привычка выполнена (число > 0 или True)
        if isinstance(val, (int, float)) and val > 0:
            streak += 1
        elif isinstance(val, bool) and val:
            streak += 1
        else:
            if i == 0:
                continue  # сегодня ещё не отмечено — не разрываем серию
            break
    return streak

def render_achievements(data, habits_config):
    st.subheader("🏆 Достижения")
    st.caption("Вехи: 🥉 21 день, 🥈 30 дней, 🥇 66 дней (привычка закреплена)")
    
    achievements = []
    for key, habit in habits_config.items():
        if key in ["workout", "workout_details"]:
            continue
        streak = calculate_streak(data, key)
        if streak >= 66:
            medal = "🥇"
        elif streak >= 30:
            medal = "🥈"
        elif streak >= 21:
            medal = "🥉"
        elif streak >= 7:
            medal = "⭐"
        else:
            medal = ""
        
        if streak > 0 or medal:
            achievements.append({
                "Привычка": habit["name"],
                "Серия": streak,
                "Медаль": medal
            })
    
    if achievements:
        df_ach = pd.DataFrame(achievements)
        df_ach = df_ach.sort_values("Серия", ascending=False)
        st.dataframe(df_ach, use_container_width=True, hide_index=True)
    else:
        st.info("Пока нет активных серий. Начни отмечать привычки!")

# ==================== СИЛУЭТ ТЕЛА ====================
def render_body_silhouette(body):
    """Рисует схематичный силуэт человека с замерами"""
    fig = go.Figure()
    
    # Голова
    fig.add_shape(type="circle", x0=-0.5, y0=8.2, x1=0.5, y1=9.2,
                  line=dict(color="black", width=2), fillcolor="rgba(200,200,255,0.3)")
    # Шея
    fig.add_shape(type="rect", x0=-0.2, y0=7.9, x1=0.2, y1=8.2,
                  line=dict(color="black", width=2), fillcolor="rgba(200,200,255,0.3)")
    # Торс
    fig.add_shape(type="path", path="M -0.9 5.5 L -0.7 7.9 L 0.7 7.9 L 0.9 5.5 Z",
                  line=dict(color="black", width=2), fillcolor="rgba(200,200,255,0.3)")
    # Руки
    fig.add_shape(type="line", x0=-0.9, y0=7.7, x1=-1.6, y1=5.8, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0.9, y0=7.7, x1=1.6, y1=5.8, line=dict(color="black", width=2))
    # Предплечья
    fig.add_shape(type="line", x0=-1.6, y0=5.8, x1=-1.4, y1=4.0, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=1.6, y0=5.8, x1=1.4, y1=4.0, line=dict(color="black", width=2))
    # Талия
    fig.add_shape(type="line", x0=-0.6, y0=5.5, x1=0.6, y1=5.5, line=dict(color="black", width=1, dash="dot"))
    # Ноги
    fig.add_shape(type="line", x0=-0.5, y0=5.0, x1=-0.6, y1=2.5, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0.5, y0=5.0, x1=0.6, y1=2.5, line=dict(color="black", width=2))
    # Голени
    fig.add_shape(type="line", x0=-0.6, y0=2.5, x1=-0.5, y1=0.3, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0.6, y0=2.5, x1=0.5, y1=0.3, line=dict(color="black", width=2))
    
    # Подписи с замерами (последние сохранённые)
    def get_val(key):
        v = body.get(key, 0)
        return f"{v}" if v else "—"
    
    annotations = [
        # Рост и вес — сбоку от головы
        dict(x=1.0, y=9.0, text=f"Рост: {get_val('height')} см", showarrow=False, xanchor="left", font=dict(size=12, color="darkblue")),
        dict(x=1.0, y=8.6, text=f"Вес: {get_val('weight')} кг", showarrow=False, xanchor="left", font=dict(size=12, color="darkblue")),
        # Шея
        dict(x=0.9, y=8.05, text=f"Шея: {get_val('neck')}", showarrow=False, xanchor="left", font=dict(size=11, color="darkred")),
        # Грудь
        dict(x=1.0, y=7.4, text=f"Грудь: {get_val('chest')}", showarrow=False, xanchor="left", font=dict(size=11, color="darkred")),
        # Бицепсы
        dict(x=-1.8, y=6.8, text=f"Бицепс Л: {get_val('biceps_l')}", showarrow=False, xanchor="right", font=dict(size=10)),
        dict(x=1.8, y=6.8, text=f"Бицепс П: {get_val('biceps_r')}", showarrow=False, xanchor="left", font=dict(size=10)),
        # Предплечья
        dict(x=-1.8, y=4.9, text=f"Предпл. Л: {get_val('forearm_l')}", showarrow=False, xanchor="right", font=dict(size=10)),
        dict(x=1.8, y=4.9, text=f"Предпл. П: {get_val('forearm_r')}", showarrow=False, xanchor="left", font=dict(size=10)),
        # Талия
        dict(x=0.9, y=5.5, text=f"Талия: {get_val('waist')}", showarrow=False, xanchor="left", font=dict(size=11, color="darkred")),
        # Бёдра
        dict(x=-1.0, y=4.2, text=f"Бедро Л: {get_val('hips_l')}", showarrow=False, xanchor="right", font=dict(size=10)),
        dict(x=1.0, y=4.2, text=f"Бедро П: {get_val('hips_r')}", showarrow=False, xanchor="left", font=dict(size=10)),
        # Икры
        dict(x=-1.0, y=1.5, text=f"Икра Л: {get_val('calves_l')}", showarrow=False, xanchor="right", font=dict(size=10)),
        dict(x=1.0, y=1.5, text=f"Икра П: {get_val('calves_r')}", showarrow=False, xanchor="left", font=dict(size=10)),
    ]
    
    fig.update_layout(
        annotations=annotations,
        xaxis=dict(range=[-3, 3], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 10], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        showlegend=False,
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================== КОМПАС ====================
def render_goal_tree(data):
    st.subheader("🧭 Компас")
    goal_tree = data.get("_goal_tree", {
        "100_years": "", "10_20_years": "", "3_5_years": "", "1_year": "",
        "quarter": "", "week": "", "today": "", "now": ""
    })
    levels = [
        ("100_years", "🌍 Смысл жизни (100 лет)"),
        ("10_20_years", "🎯 Миссия (10–20 лет)"),
        ("3_5_years", "🏔 Большая цель (3–5 лет)"),
        ("1_year", "📅 Цель года"),
        ("quarter", "🗓 Квартал"),
        ("week", "📆 Фокус недели"),
        ("today", "☀️ Главное дело дня"),
        ("now", "⚡ Сейчас (1–3 часа)")
    ]
    show_all = st.toggle("Показать все уровни", value=False)
    visible = levels if show_all else [levels[0], levels[3], levels[6]]
    for key, label in visible:
        value = goal_tree.get(key, "")
        new_value = st.text_input(label, value=value, key=f"goal_tree_{key}")
        if new_value != value:
            goal_tree[key] = new_value
            data["_goal_tree"] = goal_tree
            save_data(data)
    st.caption("💡 В обычные дни видны 3 уровня. Включи тумблер — увидишь всю вертикаль.")

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
        "health": "💡 *Здоровье — это энергия.*",
        "finances": "💡 *Финансы — это свобода.*",
        "career": "💡 *Карьера — твой вклад в мир.*",
        "relationships": "💡 *Отношения — зеркало ценностей.*",
        "growth": "💡 *Рост — расширение картины мира.*",
        "rest": "💡 *Отдых — перезарядка.*",
        "spirituality": "💡 *Духовность — опора внутри.*",
        "environment": "💡 *Окружение — твоя среда.*",
        "discipline": "💡 *Дисциплина — делать, когда не хочется.*"
    }
    history = data.get("_wheel_history", [])
    current = history[-1].copy() if history else {cat: 5 for cat in categories}
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        with cols[i % 3]:
            current[cat] = st.slider(category_names[cat], 0, 10, current.get(cat, 5), key=f"wheel_{cat}", help=hints[cat])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Сохранить слепок"):
            history.append({"date": datetime.today().strftime("%Y-%m-%d"), **current})
            data["_wheel_history"] = history
            save_data(data)
            st.success("Слепок сохранён!")
            st.rerun()
    with col2:
        if st.button("🔄 Обновить текущие"):
            if history:
                history[-1] = {"date": datetime.today().strftime("%Y-%m-%d"), **current}
            else:
                history.append({"date": datetime.today().strftime("%Y-%m-%d"), **current})
            data["_wheel_history"] = history
            save_data(data)
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
        fig2.update_layout(title="Динамика сфер", height=400)
        st.plotly_chart(fig2, use_container_width=True)

# ==================== SMART-ЦЕЛИ ====================
def render_smart_goals(data):
    st.subheader("🎯 SMART-цели")
    goals = data.get("_smart_goals", [])
    for goal in goals:
        if "Отжимания" in goal["title"] or "отжимания" in goal["title"]:
            days_count = sum(1 for d, day in data.items() if d.startswith("20") and isinstance(day, dict) and day.get("pushups", 0) >= 15)
            goal["progress"] = min(100, int((days_count / 30) * 100))
    with st.expander("➕ Добавить новую SMART-цель"):
        title = st.text_input("Название цели")
        specific = st.text_area("S (Specific)")
        measurable = st.text_input("M (Measurable)")
        achievable = st.text_area("A (Achievable)")
        relevant = st.text_area("R (Relevant)")
        deadline = st.date_input("T (Deadline)", value=datetime.today().date() + timedelta(days=30))
        progress = st.slider("Прогресс (%)", 0, 100, 0)
        if st.button("✅ Добавить цель"):
            if title and specific and measurable:
                goals.append({"id": f"goal_{len(goals)}", "title": title, "specific": specific, "measurable": measurable, "achievable": achievable, "relevant": relevant, "deadline": deadline.strftime("%Y-%m-%d"), "progress": progress})
                data["_smart_goals"] = goals
                save_data(data)
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
            if st.button(f"❌ Удалить {idx+1}", key=f"del_goal_{idx}"):
                goals.pop(idx)
                data["_smart_goals"] = goals
                save_data(data)
                st.rerun()
            st.divider()

# ==================== АНАТОМИЯ ====================
def render_body_tracker(data):
    st.subheader("🧍 Анатомия (замеры тела)")
    body_history = data.get("_body_history", [])
    params = {
        "weight": "Вес (кг)", "height": "Рост (см)", "neck": "Шея (см)", "chest": "Грудь (см)",
        "biceps_l": "Бицепс (левая)", "biceps_r": "Бицепс (правая)",
        "forearm_l": "Предплечье (левое)", "forearm_r": "Предплечье (правое)",
        "waist": "Талия (см)", "hips_l": "Бедро (левое)", "hips_r": "Бедро (правое)",
        "calves_l": "Икра (левая)", "calves_r": "Икра (правая)",
    }
    current = body_history[-1].copy() if body_history else {param: 0 for param in params}
    cols = st.columns(3)
    for i, (param, label) in enumerate(params.items()):
        with cols[i % 3]:
            current[param] = st.number_input(label, min_value=0.0, step=0.5, value=float(current.get(param, 0.0)), key=f"body_{param}", format="%.1f")
    if st.button("📏 Сохранить замер"):
        current["date"] = datetime.today().strftime("%Y-%m-%d")
        body_history.append(current)
        data["_body_history"] = body_history
        save_data(data)
        st.success("Замер сохранён!")
        st.rerun()
    
    if body_history:
        # Силуэт
        st.write("**Схема тела (последние замеры)**")
        render_body_silhouette(body_history[-1])
        
        df_body = pd.DataFrame(body_history)
        df_body["date"] = pd.to_datetime(df_body["date"])
        df_body = df_body.sort_values("date")
        st.write("**Динамика веса**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_body["date"], y=df_body["weight"], mode="lines+markers", name="Вес", line=dict(color="green")))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.write("**Последние замеры**")
        st.dataframe(df_body.tail(5))

# ==================== РЕВЬЮ НЕДЕЛИ ====================
def render_weekly_review(data):
    st.subheader("📝 Ревью недели")
    review_date = st.date_input("Дата ревью", value=datetime.today().date(), max_value=datetime.today().date())
    review_key = f"_weekly_review_{review_date.strftime('%Y-%m-%d')}"
    review = data.get(review_key, {"done": "", "blocker": "", "win": "", "score": 5})
    review["done"] = st.text_area("✅ Что сделано?", value=review.get("done", ""), height=68)
    review["blocker"] = st.text_area("🚧 Что мешало?", value=review.get("blocker", ""), height=68)
    review["win"] = st.text_area("🏆 Победа", value=review.get("win", ""), height=68)
    review["score"] = st.slider("Оценка недели (1–10)", 1, 10, review.get("score", 5))
    if st.button("💾 Сохранить ревью"):
        data[review_key] = review
        save_data(data)
        st.success("Сохранено!")
        st.rerun()
    st.write("**📜 История ревью**")
    all_reviews = []
    for key, value in data.items():
        if key.startswith("_weekly_review_"):
            date_str = key.replace("_weekly_review_", "")
            try:
                all_reviews.append({"date": datetime.strptime(date_str, "%Y-%m-%d"), "date_str": date_str, "score": value.get("score", 5), "done": value.get("done",""), "blocker": value.get("blocker",""), "win": value.get("win","")})
            except: pass
    if all_reviews:
        all_reviews.sort(key=lambda x: x["date"], reverse=True)
        for r in all_reviews[:5]:
            with st.expander(f"📅 {r['date_str']} — Оценка: {r['score']}/10"):
                st.write(f"**✅** {r['done']}")
                st.write(f"**🚧** {r['blocker']}")
                st.write(f"**🏆** {r['win']}")

# ==================== ДНЕВНИК ====================
def render_diary(data):
    st.subheader("🧠 Дневник инсайтов")
    diary_date = st.date_input("Дата записи", value=datetime.today().date(), max_value=datetime.today().date(), key="diary_date")
    diary_key = f"_diary_{diary_date.strftime('%Y-%m-%d')}"
    diary_entry = data.get(diary_key, "")
    diary_entry = st.text_area("✍️ Поток сознания", value=diary_entry, height=200)
    if st.button("💾 Сохранить запись"):
        data[diary_key] = diary_entry
        save_data(data)
        st.success("Сохранено!")
        st.rerun()
    st.write("**📜 История**")
    all_diary = []
    for key, value in data.items():
        if key.startswith("_diary_") and value:
            try:
                date_str = key.replace("_diary_", "")
                all_diary.append({"date": datetime.strptime(date_str, "%Y-%m-%d"), "date_str": date_str, "text": value})
            except: pass
    if all_diary:
        all_diary.sort(key=lambda x: x["date"], reverse=True)
        for entry in all_diary[:10]:
            with st.expander(f"📅 {entry['date_str']}"):
                st.write(entry['text'])

# ==================== ПРИВЫЧКИ (ВВОД) ====================
def render_habits_input(data, habits_config):
    today = datetime.today().date()
    date_input = st.date_input("Выберите дату", value=today, max_value=today, key="habit_date")
    date_str = date_input.strftime("%Y-%m-%d")
    day_data = data.get(date_str, {})
    st.write(f"## {format_date_ru(date_input)}")
    
    st.write("---")
    st.write("**🏋️ Тренировка**")
    col_train_status, col_train_text = st.columns([1, 2])
    with col_train_status:
        workout_status = st.radio("Статус", options=["✅ Выполнена", "❌ Не выполнена"],
            index=0 if day_data.get("workout", 0) == 1 else 1, key=f"workout_status_{date_str}", horizontal=True)
        save_habit(date_str, "workout", 1 if workout_status == "✅ Выполнена" else 0)
    with col_train_text:
        workout_details = st.text_area("Детали тренировки", value=day_data.get("workout_details", ""),
            key=f"workout_details_{date_str}", height=68)
        if workout_details != day_data.get("workout_details", ""):
            save_habit(date_str, "workout_details", workout_details)
    st.write("---")
    
    cols = st.columns(3)
    for idx, (key, habit) in enumerate(habits_config.items()):
        if key == "workout":
            continue
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
                user_input = st.text_input(f"Добавить", key=f"inp_{date_str}_{key}", placeholder="10+20 или 30")
                if st.button(f"Сохранить", key=f"btn_{date_str}_{key}"):
                    if user_input:
                        parse_habit_value(user_input, key, date_str)
                        st.rerun()
            else:
                if st.button(f"Переключить", key=f"tog_{date_str}_{key}"):
                    save_habit(date_str, key, not val if val is not None else True)
                    st.rerun()

# ==================== КАЛЕНДАРЬ И ГРАФИКИ ====================
def render_calendar_and_graphs(data, habits_config):
    today = datetime.today().date()
    st.subheader("📊 Календарь за месяц")
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    dates_in_month = [(first_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(last_day.day)]
    matrix = {}
    for key in habits_config:
        matrix[key] = []
        for d in dates_in_month:
            day_info = data.get(d, {})
            val = day_info.get(key, None)
            if habits_config[key]["unit"]:
                if val is None: matrix[key].append("⬜")
                elif val >= habits_config[key]["min"]: matrix[key].append("🟩")
                else: matrix[key].append("⬛")
            else:
                matrix[key].append("✅" if val else ("⬜" if val is None else "❌"))
    df_matrix = pd.DataFrame(matrix, index=[f"{i+1}" for i in range(len(dates_in_month))])
    df_matrix.rename(columns={k: habits_config[k]["name"] for k in habits_config}, inplace=True)
    st.dataframe(df_matrix.T, use_container_width=True)
    
    st.divider()
    st.subheader("📈 Графики")
    for key, habit in habits_config.items():
        if habit["unit"]:
            dates, values, cumulative, cum_sum = [], [], [], 0
            for d, day_info in sorted(data.items()):
                if d <= today.strftime("%Y-%m-%d") and not d.startswith("_") and d != "_habits_config":
                    val = day_info.get(key) if isinstance(day_info, dict) else None
                    if val is not None:
                        dates.append(d); values.append(val); cum_sum += val; cumulative.append(cum_sum)
            if dates:
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(x=dates, y=values, marker_color="blue"))
                fig1.add_hline(y=habit["min"], line_dash="dot", line_color="red")
                fig1.update_layout(title=f"{habit['name']} (ежедневно)", height=250)
                st.plotly_chart(fig1, use_container_width=True)
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=dates, y=cumulative, mode="lines+markers", line=dict(color="green")))
                fig2.update_layout(title=f"{habit['name']} (всего: {cum_sum})", height=250)
                st.plotly_chart(fig2, use_container_width=True)

# ==================== ОСНОВНОЙ ИНТЕРФЕЙС ====================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

data = load_data()
habits_config = data.get("_habits_config", DEFAULT_HABITS)

# ---- ПОСЛЕДНЯЯ ЗАПИСЬ ----
all_dates = []
for d, day_data in data.items():
    if d.startswith("20") and isinstance(day_data, dict):
        if any((isinstance(v, (int, float)) and v > 0) or (isinstance(v, str) and v.strip()) for k, v in day_data.items()):
            all_dates.append(d)
if all_dates:
    last_date = max(all_dates)
    st.info(f"📅 Последняя запись была: **{format_date_ru(datetime.strptime(last_date, '%Y-%m-%d'))}**")

# ---- ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМОВ ----
st.write("---")
mode = st.radio("Режим", ["☀️ День", "🔍 Ревью"], horizontal=True, key="app_mode")
st.write("---")

# ==================== РЕЖИМ "ДЕНЬ" ====================
if mode == "☀️ День":
    render_goal_tree(data)
    st.divider()
    render_habits_input(data, habits_config)

# ==================== РЕЖИМ "РЕВЬЮ" ====================
else:
    render_goal_tree(data)
    st.divider()
    render_achievements(data, habits_config)
    st.divider()
    render_wheel_balance(data)
    st.divider()
    render_smart_goals(data)
    st.divider()
    render_body_tracker(data)
    st.divider()
    render_weekly_review(data)
    st.divider()
    render_diary(data)
    st.divider()
    render_calendar_and_graphs(data, habits_config)
    st.divider()
    st.subheader("💾 Резервное копирование")
    col_backup, col_restore = st.columns(2)
    with col_backup:
        if st.button("Подготовить бэкап"):
            st.download_button("📥 Скачать data.json", data=json.dumps(data, indent=2, ensure_ascii=False),
                file_name=f"data_backup_{datetime.today().strftime('%Y-%m-%d')}.json", mime="application/json")
    with col_restore:
        uploaded_file = st.file_uploader("Загрузить бэкап", type="json")
        if uploaded_file is not None:
            try:
                restored = json.load(uploaded_file)
                save_data(restored)
                st.success("✅ Восстановлено!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка: {e}")