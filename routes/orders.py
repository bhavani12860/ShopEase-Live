from flask import Blueprint, render_template, redirect, url_for, session, flash

from database import get_db_connection


orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/orders"
)


# =========================================================
# MY ORDERS
# =========================================================

@orders_bp.route("/")
def orders():

    if "user_id" not in session:
        flash(
            "Please login to view your orders.",
            "warning"
        )
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # GET ALL ORDERS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                o.id,
                o.total_amount,
                o.status,
                o.payment_method,
                o.created_at
            FROM orders o
            WHERE o.user_id = %s
            ORDER BY o.id DESC
        """, (user_id,))

        orders_list = cursor.fetchall()


        # -------------------------------------------------
        # GET FIRST PRODUCT FOR EACH ORDER
        # -------------------------------------------------

        for order in orders_list:

            cursor.execute("""
                SELECT
                    oi.id,
                    oi.product_id,
                    oi.quantity,
                    oi.price,

                    p.name,
                    p.description,
                    p.image,
                    p.rating,
                    p.stock

                FROM order_items oi

                LEFT JOIN products p
                    ON oi.product_id = p.id

                WHERE oi.order_id = %s

                ORDER BY oi.id ASC

                LIMIT 1
            """, (order["id"],))

            first_item = cursor.fetchone()


            # Attach first item to order
            order["first_item"] = first_item


            # -------------------------------------------------
            # PREPARE IMAGE URL
            # -------------------------------------------------

            if first_item:

                image = first_item.get("image")

                if image:

                    image = str(image).replace(
                        "\\",
                        "/"
                    ).strip()


                    if image.startswith("/static/"):

                        first_item["image_url"] = image


                    elif image.startswith("static/"):

                        first_item["image_url"] = (
                            "/" + image
                        )


                    elif image.startswith("/uploads/"):

                        first_item["image_url"] = (
                            "/static" + image
                        )


                    elif image.startswith("uploads/"):

                        first_item["image_url"] = (
                            "/static/" + image
                        )


                    else:

                        first_item["image_url"] = (
                            "/static/uploads/products/"
                            + image
                        )

                else:

                    first_item["image_url"] = (
                        "/static/images/no-product.png"
                    )


        return render_template(
            "orders/orders.html",
            orders=orders_list
        )


    except Exception as e:

        print(
            "ORDERS ERROR:",
            e
        )

        flash(
            "Unable to load your orders.",
            "danger"
        )

        return redirect(
            url_for("home")
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# ORDER DETAILS
# =========================================================

@orders_bp.route("/<int:order_id>")
def order_details(order_id):

    if "user_id" not in session:
        flash(
            "Please login to view order details.",
            "warning"
        )
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # GET ORDER
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                o.id,
                o.user_id,
                o.address_id,
                o.total_amount,
                o.status,
                o.payment_method,
                o.created_at,

                a.full_name,
                a.phone,
                a.address,
                a.city,
                a.state,
                a.pincode,
                a.landmark

            FROM orders o

            LEFT JOIN addresses a
                ON o.address_id = a.id

            WHERE o.id = %s
              AND o.user_id = %s
        """, (
            order_id,
            user_id
        ))

        order = cursor.fetchone()


        if not order:

            flash(
                "Order not found.",
                "danger"
            )

            return redirect(
                url_for("orders.orders")
            )


        # -------------------------------------------------
        # GET ORDER ITEMS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                oi.id,
                oi.product_id,
                oi.quantity,
                oi.price,

                p.name,
                p.description,
                p.image,
                p.rating,
                p.stock

            FROM order_items oi

            LEFT JOIN products p
                ON oi.product_id = p.id

            WHERE oi.order_id = %s

            ORDER BY oi.id ASC
        """, (order_id,))

        order_items = cursor.fetchall()


        # -------------------------------------------------
        # PREPARE PRODUCT IMAGE PATH
        # -------------------------------------------------

        for item in order_items:

            image = item.get("image")

            if image:

                image = str(image).replace(
                    "\\",
                    "/"
                ).strip()


                # Already full static path
                if image.startswith("/static/"):

                    item["image_url"] = image


                # static/uploads/...
                elif image.startswith("static/"):

                    item["image_url"] = (
                        "/" + image
                    )


                # uploads/products/product.jpg
                elif image.startswith("uploads/"):

                    item["image_url"] = (
                        "/static/" + image
                    )


                # /uploads/products/product.jpg
                elif image.startswith("/uploads/"):

                    item["image_url"] = (
                        "/static" + image
                    )


                # Only filename
                else:

                    item["image_url"] = (
                        "/static/uploads/products/"
                        + image
                    )

            else:

                item["image_url"] = (
                    "/static/images/no-product.png"
                )


        return render_template(
            "orders/order_details.html",
            order=order,
            order_items=order_items
        )


    except Exception as e:

        print(
            "ORDER DETAILS ERROR:",
            e
        )

        flash(
            "Unable to load order details.",
            "danger"
        )

        return redirect(
            url_for("orders.orders")
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# TRACK ORDER
# =========================================================

@orders_bp.route("/<int:order_id>/track")
def track_order(order_id):

    if "user_id" not in session:
        flash(
            "Please login to track your order.",
            "warning"
        )
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                o.id,
                o.status,
                o.created_at,
                o.total_amount,
                o.payment_method

            FROM orders o

            WHERE o.id = %s
              AND o.user_id = %s
        """, (
            order_id,
            user_id
        ))

        order = cursor.fetchone()


        if not order:

            flash(
                "Order not found.",
                "danger"
            )

            return redirect(
                url_for("orders.orders")
            )


        return render_template(
            "orders/track_order.html",
            order=order
        )


    except Exception as e:

        print(
            "TRACK ORDER ERROR:",
            e
        )

        flash(
            "Unable to track order.",
            "danger"
        )

        return redirect(
            url_for("orders.orders")
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# CANCEL ORDER
# =========================================================

@orders_bp.route(
    "/<int:order_id>/cancel",
    methods=["POST"]
)
def cancel_order(order_id):

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # -------------------------------------------------
        # GET USER'S ORDER
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                status
            FROM orders
            WHERE id = %s
              AND user_id = %s
        """, (
            order_id,
            user_id
        ))

        order = cursor.fetchone()


        if not order:

            flash(
                "Order not found.",
                "danger"
            )

            return redirect(
                url_for("orders.orders")
            )


        # -------------------------------------------------
        # ALLOWED CANCELLATION STATUSES
        #
        # Your database currently uses "Placed"
        # -------------------------------------------------

        allowed_statuses = [
            "Placed",
            "Pending",
            "Confirmed",
            "Order Placed",
            "Processing"
        ]


        # -------------------------------------------------
        # CHECK WHETHER ORDER CAN BE CANCELLED
        # -------------------------------------------------

        if order["status"] not in allowed_statuses:

            flash(
                "This order cannot be cancelled now.",
                "warning"
            )

            return redirect(
                url_for("orders.orders")
            )


        # -------------------------------------------------
        # CANCEL ORDER
        # -------------------------------------------------

        cursor.execute("""
            UPDATE orders
            SET status = %s
            WHERE id = %s
              AND user_id = %s
        """, (
            "Cancelled",
            order_id,
            user_id
        ))


        conn.commit()


        flash(
            "Your order has been cancelled successfully.",
            "success"
        )


        return redirect(
            url_for("orders.orders")
        )


    except Exception as e:

        conn.rollback()

        print(
            "CANCEL ORDER ERROR:",
            e
        )


        flash(
            "Unable to cancel the order.",
            "danger"
        )


        return redirect(
            url_for("orders.orders")
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# RETURN ORDER
# =========================================================

@orders_bp.route(
    "/<int:order_id>/return",
    methods=["POST"]
)
def return_order(order_id):

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # -------------------------------------------------
        # GET USER'S ORDER
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                status
            FROM orders
            WHERE id = %s
              AND user_id = %s
        """, (
            order_id,
            user_id
        ))

        order = cursor.fetchone()


        if not order:

            flash(
                "Order not found.",
                "danger"
            )

            return redirect(
                url_for("orders.orders")
            )


        # -------------------------------------------------
        # RETURN ONLY DELIVERED ORDERS
        # -------------------------------------------------

        if order["status"] != "Delivered":

            flash(
                "Only delivered orders can be returned.",
                "warning"
            )

            return redirect(
                url_for("orders.orders")
            )


        # -------------------------------------------------
        # REQUEST RETURN
        # -------------------------------------------------

        cursor.execute("""
            UPDATE orders
            SET status = %s
            WHERE id = %s
              AND user_id = %s
        """, (
            "Return Requested",
            order_id,
            user_id
        ))


        conn.commit()


        flash(
            "Return request submitted successfully.",
            "success"
        )


        return redirect(
            url_for("orders.orders")
        )


    except Exception as e:

        conn.rollback()

        print(
            "RETURN ORDER ERROR:",
            e
        )


        flash(
            "Unable to submit return request.",
            "danger"
        )


        return redirect(
            url_for("orders.orders")
        )


    finally:

        cursor.close()
        conn.close()