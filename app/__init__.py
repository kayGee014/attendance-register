import os
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from . import db

STATUSES = [("P", "Present"), ("R", "Remote / field"), ("L", "Leave"),
            ("S", "Sick"), ("A", "Absent"), ("H", "Public holiday")]

def monday(d):
    return d - timedelta(days=d.weekday())

def current_manager():
    email = (request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")  # set by Entra / Easy Auth
             or os.environ.get("DEV_USER", "manager1@example.org"))
    rows = db.query("SELECT * FROM Managers WHERE Email = ?", (email,))
    if not rows:
        abort(403, "You are not registered as a manager.")
    return rows[0]

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-only")
    db.init_demo()

    @app.route("/", methods=["GET", "POST"])
    def week():
        mgr = current_manager()
        raw = request.values.get("week")
        start = monday(datetime.strptime(raw, "%Y-%m-%d").date() if raw else date.today())
        days = [start + timedelta(i) for i in range(5)]
        interns = db.query("SELECT * FROM Interns WHERE ManagerId = ? ORDER BY Name", (mgr["ManagerId"],))

        if request.method == "POST":
            submit = request.form.get("action") == "submit"
            conn = db.get_conn()
            for i in interns:
                wk = db.query("SELECT * FROM AttendanceWeek WHERE InternId=? AND WeekStart=?",
                              (i["InternId"], str(start)), conn)
                if wk and wk[0]["Status"] == "Submitted":
                    continue  # locked
                if not wk:
                    conn.cursor().execute("INSERT INTO AttendanceWeek (InternId, WeekStart) VALUES (?,?)",
                                          (i["InternId"], str(start)))
                    wk = db.query("SELECT * FROM AttendanceWeek WHERE InternId=? AND WeekStart=?",
                                  (i["InternId"], str(start)), conn)
                wid = wk[0]["WeekId"]
                cur = conn.cursor()
                cur.execute("DELETE FROM AttendanceDay WHERE WeekId=?", (wid,))
                for n, d in enumerate(days):
                    code = request.form.get(f"s_{i['InternId']}_{n}", "P")
                    cur.execute("INSERT INTO AttendanceDay (WeekId, Day, StatusCode) VALUES (?,?,?)",
                                (wid, str(d), code))
                cur.execute("UPDATE AttendanceWeek SET Comment=?, Status=?, SubmittedBy=?, SubmittedAt=? WHERE WeekId=?",
                            (request.form.get(f"c_{i['InternId']}", "")[:500],
                             "Submitted" if submit else "Draft",
                             mgr["Email"] if submit else None,
                             datetime.utcnow().isoformat(sep=" ", timespec="seconds") if submit else None, wid))
            conn.commit(); conn.close()
            flash("Week submitted." if submit else "Draft saved.")
            return redirect(url_for("week", week=start))

        saved = {}
        for i in interns:
            wk = db.query("SELECT * FROM AttendanceWeek WHERE InternId=? AND WeekStart=?",
                          (i["InternId"], str(start)))
            codes = {}
            if wk:
                for r in db.query("SELECT Day, StatusCode FROM AttendanceDay WHERE WeekId=?", (wk[0]["WeekId"],)):
                    codes[str(r["Day"])[:10]] = r["StatusCode"].strip()
            saved[i["InternId"]] = {"wk": wk[0] if wk else None, "codes": codes}

        locked = bool(saved) and all(v["wk"] and v["wk"]["Status"] == "Submitted" for v in saved.values())
        return render_template("week.html", mgr=mgr, interns=interns, days=days, saved=saved,
                               statuses=STATUSES, start=start, locked=locked,
                               prev=start - timedelta(7), next=start + timedelta(7))
    return app
