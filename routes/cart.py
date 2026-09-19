from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database import get_db_connection


cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/cart"
)


# =====================================================
# CART PAGE
# =====================================================

@cart_bp.route("/")
def cart():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("cart/cart.html")


# =====================================================
# SYNC LOCAL CART -> MYSQL
# =====================================================

@cart_bp.route("/sync", methods=["POST"])
def sync_cart():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No cart data received."
        }), 400

    items = data.get("items", [])

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # Remove old cart items for this user
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM cart
            WHERE user_id = %s
            """,
            (user_id,)
        )

        # -------------------------------------------------
        # Add current cart items
        # -------------------------------------------------

        for item in items:

            product_id = item.get("id")

            try:
                quantity = int(item.get("quantity", 1))
            except (TypeError, ValueError):
                quantity = 1

            if not product_id:
                continue

            if quantity < 1:
                quantity = 1

            # Verify product exists
            cursor.execute(
                """
                SELECT id, stock
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if not product:
                continue

            # Don't allow quantity above available stock
            if product["stock"] is not None:
                if product["stock"] <= 0:
                    continue

                quantity = min(
                    quantity,
                    product["stock"]
                )

            cursor.execute(
                """
                INSERT INTO cart
                (
                    user_id,
                    product_id,
                    quantity
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    product_id,
                    quantity
                )
            )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Cart synced successfully."
        })

    except Exception as e:

        if conn:
            conn.rollback()

        print("CART SYNC ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Unable to save cart."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()





# =====================================================
# CART COUNT
# =====================================================

@cart_bp.route("/count")
def cart_count():

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
            SELECT COALESCE(SUM(quantity), 0) AS count
            FROM cart
            WHERE user_id = %s
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        return jsonify({
            "count": int(result["count"] or 0)
        })

    except Exception as e:

        print("CART COUNT ERROR:", e)

        return jsonify({
            "count": 0
        })

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()