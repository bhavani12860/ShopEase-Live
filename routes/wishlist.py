from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database import get_db_connection


wishlist_bp = Blueprint(
    "wishlist",
    __name__,
    url_prefix="/wishlist"
)


# =====================================================
# WISHLIST PAGE
# =====================================================

@wishlist_bp.route("/")
def wishlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("wishlist/wishlist.html")


# =====================================================
# WISHLIST COUNT
# =====================================================

@wishlist_bp.route("/count")
def wishlist_count():

    if "user_id" not in session:
        return jsonify({
            "count": 0
        })

    user_id = session["user_id"]

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM wishlist
            WHERE user_id = %s
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        return jsonify({
            "count": int(result["count"] or 0)
        })

    except Exception as e:

        print("WISHLIST COUNT ERROR:", e)

        return jsonify({
            "count": 0
        })

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()