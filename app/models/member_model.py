import sqlite3
from ..models.db_init import DB_PATH

ALL_SOCIETIES = ["UMT IEEE", "UMT ACM", "UMT CSS", "UMT IEEE-WIE", "UMT Robotics", "UMT Cybersecurity"]

def get_db():
    return sqlite3.connect(DB_PATH, timeout=10)

def add_member(data):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO members VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    finally:
        conn.close()

def find_by_student_id(student_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM members WHERE student_id=?", (student_id,))
        return cur.fetchall()
    finally:
        conn.close()

def find_by_society(society):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM members WHERE society_name=?", (society,))
        return cur.fetchall()
    finally:
        conn.close()

# ✅ FIXED: Ensures the ID is released immediately so it can be re-added
def delete_student_member_information(student_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM members WHERE student_id = ?", (student_id,))
        conn.commit()
        success = cur.rowcount > 0
        return success
    finally:
        conn.close()

def update_student_member_information(current_id, update_data):
    if not update_data:
        return False
    conn = get_db()
    cur = conn.cursor()
    try:
        fields = []
        values = []
        for key, value in update_data.items():
            if value:
                db_key = "society_name" if key == "society" else key
                fields.append(f"{db_key} = ?")
                values.append(value)
        if not fields:
            return False
        values.append(current_id)
        sql = f"UPDATE members SET {', '.join(fields)} WHERE student_id = ?"
        cur.execute(sql, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def sort_search_results(results, sort_by="last_name", order="asc"):
    if not results:
        return results
    key_map = {"first_name": 1, "last_name": 2, "student_id": 4, "society": 5, "position": 7}
    idx = key_map.get(sort_by, 2)
    return sorted(results, key=lambda x: str(x[idx]), reverse=(str(order).lower() == "desc"))

def view_all_member_using_graph():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT society_name, COUNT(*) FROM members GROUP BY society_name")
        counts = {row[0]: row[1] for row in cur.fetchall()}
        return {"labels": ALL_SOCIETIES, "values": [counts.get(s, 0) for s in ALL_SOCIETIES]}
    finally:
        conn.close()

def get_all_members():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM members")
        return cur.fetchall()
    finally:
        conn.close()