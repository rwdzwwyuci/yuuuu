# pmis-tutorial-student.py
# 练习版：包含 Todo1..Todo5，需要你逐一补齐关键代码。未完成时脚qin本仍可运行，便于即时验证。
# 存储层：使用 sqlite3 数据库替代 CSV

import sqlite3
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="个人信息管理系统（练习版）", page_icon="🌱", layout="wide")

BASE_DIR = Path().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "records.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Todo 1: 添加至少3个不同类型的数据收集需求，并在后续表单和输出中体现
# 说明：date(日期)、priority(数值/滑块)、amount(数值)、tags(多选→字符串)、is_public(布尔)
COLUMNS = ["id", "title", "category", "date", "priority", "amount", "tags", "is_public", "notes", "created_at"]

# 初始化数据库：若表不存在则创建
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id        INTEGER PRIMARY KEY,
            title     TEXT NOT NULL,
            category  TEXT,
            date      TEXT,
            priority  INTEGER,
            amount    REAL,
            tags      TEXT,
            is_public INTEGER,
            notes     TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Todo 2: 从 sqlite3 读取数据；若表为空则返回空表（列名为 COLUMNS）
def load_data() -> pd.DataFrame:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM records", conn)
    conn.close()
    # 补齐缺失列，保证结构稳定
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    return df

# Todo 3: 使用 DataFrame.to_sql 将 df 写回 sqlite3 数据库
def save_data(df: pd.DataFrame):
    try:
        # 👉 将 df 写回 sqlite3，不保留行索引，覆盖旧表数据
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("records", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
    except Exception:
        # 回退：忽略保存错误，保证应用不中断
        pass

# Todo 4: 设计输入表单，增加至少 3 种不同类型的输入控件（与 Todo1 对应）
def input_form(df: pd.DataFrame) -> pd.DataFrame:
    with st.form("add_form", clear_on_submit=True):
        new = {}
        new["id"] = (0 if df.empty else int(df["id"].max()) + 1)
        # —— 以下提供最小可运行输入；请按 Todo4 自行扩展更多类型 ——
        # 文本输入
        new["title"] = st.text_input("标题 *", placeholder="例如：三好学生")
        CATEGORIES = ["荣誉", "教育经历", "竞赛", "证书", "账号", "其他"]
        new["category"] = st.selectbox("类别", CATEGORIES, index=0)
        # 日期输入（与 Todo1 的 date 对应）
        new["date"] = st.date_input("日期", value=pd.Timestamp.now().date())
        # 滑块（与 Todo1 的 priority 对应）
        new["priority"] = st.slider("重要程度（1低 - 5高）", min_value=1, max_value=5, value=3, step=1)
        # 数值输入（与 Todo1 的 amount 对应）
        new["amount"] = st.number_input("数量/金额（可选）", min_value=0.0, step=1.0, value=0.0)
        # 多选（与 Todo1 的 tags 对应）
        new["tags"] = st.multiselect("标签（可多选）", ["学习", "工作", "生活", "兴趣", "重要", "紧急"])
        # 复选框（与 Todo1 的 is_public 对应）
        new["is_public"] = st.checkbox("是否公开", value=False)
        # 长文本
        new["notes"] = st.text_area("备注（可选）", placeholder="关键信息、链接或行动项…", height=100)
        submitted = st.form_submit_button("保存", type="primary", use_container_width=True)

        # 在这里添加自己的收集内容

    if submitted:
        # 必填校验
        if not new["title"]:
            st.warning("请填写标题")
            return df
        # 多选标签转为逗号字符串，便于 CSV 存储
        new["tags"] = ",".join(new["tags"]) if isinstance(new["tags"], list) else new["tags"]
        new["is_public"] = bool(new["is_public"])
        new["date"] = str(new["date"])
        new["created_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        df_new = pd.DataFrame(new, index=[0])
        df = pd.concat([df, df_new], ignore_index=True)
        save_data(df)
        st.success("已保存 ✅")
    return df

# === 页面骨架（Todo 5：完善页面结构与输出区） ===
df = load_data()

# Todo 5: 按“标题 → 说明 → 输入表单 → 输出与下载”的顺序组织页面
st.title("🌱 个人信息管理系统")
st.caption("一个轻量级单文件 MIS：记录荣誉、教育经历、竞赛、证书、账号等信息，支持新增与导出。")

st.subheader("➕ 新增记录")
df = input_form(df)

st.subheader("📋 记录列表")
if df.empty:
    st.info("暂无数据，请先在上方新增一条记录。")
else:
    st.dataframe(df, width="stretch", hide_index=True)
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ 下载为 CSV",
        data=csv_data,
        file_name="personal_records.csv",
        mime="text/csv",
    )
