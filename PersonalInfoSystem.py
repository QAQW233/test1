import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

st.set_page_config(
    page_title="个人信息管理系统",
    page_icon="🌱",
    layout="wide"
)

# =========================
# 数据库配置
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "records.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = ["id", "title", "category", "notes", "created_at"]


# =========================
# 数据库初始化
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# =========================
# 加载数据
# =========================
def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT id, title, category, notes, created_at
        FROM records
        ORDER BY id
        """,
        conn
    )

    conn.close()

    return df

# =========================
# 保存数据
# =========================
def save_data(title: str, category: str, notes: str):
    conn = sqlite3.connect(DB_PATH)

    # 获取下一个 ID
    cursor = conn.execute(
        "SELECT COALESCE(MAX(id), -1) + 1 FROM records"
    )
    next_id = cursor.fetchone()[0]

    created_at = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        """
        INSERT INTO records
        (id, title, category, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            next_id,
            title,
            category,
            notes,
            created_at
        )
    )

    conn.commit()
    conn.close()

# =========================
# 输入表单
# =========================

def input_form():
    with st.form("add_form", clear_on_submit=True):

        title = st.text_input(
            "标题 *",
            placeholder="例如：三好学生"
        )

        categories = [
            "荣誉",
            "教育经历",
            "竞赛",
            "证书",
            "账号",
            "其他"
        ]

        category = st.selectbox(
            "类别",
            categories,
            index=0
        )

        notes = st.text_area(
            "备注（可选）",
            placeholder="关键信息、链接或行动项…",
            height=100
        )

        submitted = st.form_submit_button(
            "保存",
            type="primary",
            use_container_width=True
        )

    if submitted:

        if not title.strip():
            st.warning("请输入标题。")
            return

        save_data(
            title=title.strip(),
            category=category,
            notes=notes.strip()
        )

        st.success("已保存 ✅")

# =========================
# 初始化数据库
# =========================
init_db()

# =========================
# 页面
# =========================
st.title("🌱 个人信息管理系统")

st.caption(
    "用于记录个人荣誉、教育经历、竞赛、证书、账号等信息"
)

st.subheader("添加个人信息")

input_form()

# =========================
# 当前数据
# =========================
st.subheader("当前数据")

df = load_data()

if df.empty:
    st.info("暂无数据。")
else:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# =========================
# 数据下载
# =========================
st.subheader("数据库下载")

if DB_PATH.exists():

    with open(DB_PATH, "rb") as f:
        db_data = f.read()

    st.download_button(
        label="下载.db文件",
        data=db_data,
        file_name="records.db",
        mime="application/x-sqlite3",
        use_container_width=True
    )

    #st.caption("下载的是完整的 SQLite 数据库文件，可用于备份或迁移。")

else:
    st.warning("数据库文件不存在。")
