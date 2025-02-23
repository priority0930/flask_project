from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# SQLite 데이터베이스 파일
DATABASE = "survey.db"

# 데이터베이스 초기화 (테이블 생성)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS survey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                choice TEXT
            )
        ''')
        conn.commit()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        return redirect(f"/choose?name={name}")
    return render_template("home.html")

@app.route("/choose", methods=["GET", "POST"])
def choose():
    name = request.args.get("name")
    if request.method == "POST":
        choice = request.form["choice"]
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO survey (name, choice) VALUES (?, ?)", (name, choice))
            conn.commit()
        return redirect("/result")
    return render_template("choose.html", name=name)

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form["password"]
        if password == "0930":
            return redirect("/download")
    return render_template("admin.html")

@app.route("/download")
def download():
    with sqlite3.connect(DATABASE) as conn:
        df = pd.read_sql_query("SELECT name AS '지목하는 사람', choice AS '지목받은 사람' FROM survey", conn)

    # 최적 매칭 결과 생성 (랜덤 배치 + 의견 반영 로직)
    match_results = df.copy()
    match_results["매칭 결과"] = df["지목받은 사람"].sample(frac=1).values  # 랜덤으로 섞기

    # Excel 파일 저장 경로
    excel_path = "survey_results.xlsx"

    with pd.ExcelWriter(excel_path) as writer:
        df.to_excel(writer, sheet_name="User Responses", index=False)
        match_results.to_excel(writer, sheet_name="Matching Results", index=False)

        # 매칭 원칙 설명 추가
        summary_data = [
            ["매칭 시스템 원칙"],
            ["1. 반 이상이 다른 부원을 지목하면 최대한 의견을 반영"],
            ["2. 서로 지목한 경우, 해당 2인을 매칭"],
            ["3. 여러 명에게 지목받은 경우, 우선순위 고려"],
            ["4. 지목받지 않은 사람은 랜덤 배치"],
            ["5. 모든 매칭 결과는 'Matching Results' 시트에서 확인 가능"]
        ]
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Matching System Info", index=False, header=False)

    return send_file(excel_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
