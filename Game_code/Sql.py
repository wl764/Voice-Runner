import sqlite3


# 初始化数据库
def init_db():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    # 创建 scores 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# 插入分数并保持最多 10 个分数
def save_score(username, score):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    # 插入新的分数
    cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
    conn.commit()

    # 获取用户的分数列表，按分数从大到小排序
    cursor.execute("SELECT id, score FROM scores WHERE username = ? ORDER BY score DESC", (username,))
    scores = cursor.fetchall()

    # 如果分数超过 10 个，删除最小的
    if len(scores) > 5:
        min_score_id = scores[-1][0]  # 获取最小分数的 id
        cursor.execute("DELETE FROM scores WHERE id = ?", (min_score_id,))
        conn.commit()

    conn.close()