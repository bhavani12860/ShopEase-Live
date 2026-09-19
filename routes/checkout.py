from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database import get_db_connection


# =========================================================
# BLUEPRINT
# =========================================================

checkout_bp = Blueprint(
    "checkout",
    __name__,
    url_prefix="/checkout"
)


# =========================================================
# CHECKOUT PAGE
# =========================================================

@checkout_bp.route("/", methods=["GET"])
def checkout():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please login to continue checkout.",
            "warning"
        )

        return redirect(url_for("login"))


    user_id = session["user_id"]


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # =================================================
        # GET CART
        # =================================================

        cursor.execute("""
            SELECT
                c.product_id,
                c.quantity,
                p.name,
                p.price,
                p.discount,
                p.image,
                p.stock
            FROM cart c
            JOIN products p
                ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))


        cart_items = cursor.fetchall()


        # =================================================
        # CALCULATE TOTALS
        # =================================================

        subtotal = 0
        discount_total = 0


        for item in cart_items:

            price = float(item["price"] or 0)

            discount = float(
                item["discount"] or 0
            )

            quantity = int(
                item["quantity"] or 1
            )


            discount_amount = (
                price * discount / 100
            )


            final_price = (
                price - discount_amount
            )


            item["final_price"] = final_price

            item["item_total"] = (
                final_price * quantity
            )


            subtotal += (
                price * quantity
            )


            discount_total += (
                discount_amount * quantity
            )


        total_amount = (
            subtotal - discount_total
        )


        # =================================================
        # GET SAVED ADDRESSES
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                full_name,
                phone,
                address,
                city,
                state,
                pincode,
                landmark
            FROM addresses
            WHERE user_id = %s
            ORDER BY id DESC
        """, (user_id,))


        addresses = cursor.fetchall()


        # =================================================
        # RENDER CHECKOUT
        # =================================================

        return render_template(
            "checkout/checkout.html",

            cart_items=cart_items,

            addresses=addresses,

            subtotal=subtotal,

            discount=discount_total,

            total_amount=total_amount
        )


    except Exception as e:

        print(
            "CHECKOUT ERROR:",
            e
        )

        flash(
            "Unable to load checkout.",
            "danger"
        )

        return redirect(
            url_for("cart.cart")
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# SAVE DELIVERY ADDRESS
# =========================================================

@checkout_bp.route(
    "/save-address",
    methods=["POST"]
)
def save_address():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please login to continue.",
            "warning"
        )

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    # =====================================================
    # GET FORM DATA
    # =====================================================

    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    state = request.form.get(
        "state",
        ""
    ).strip()

    pincode = request.form.get(
        "pincode",
        ""
    ).strip()

    landmark = request.form.get(
        "landmark",
        ""
    ).strip()

    # =====================================================
    # REQUIRED FIELD VALIDATION
    # =====================================================

    if not all([
        full_name,
        phone,
        address,
        city,
        state,
        pincode
    ]):

        flash(
            "Please fill all required address details.",
            "warning"
        )

        return redirect(
            url_for("checkout.checkout")
        )

    # =====================================================
    # PHONE VALIDATION
    # =====================================================

    if not phone.isdigit() or len(phone) != 10:

        flash(
            "Please enter a valid 10-digit mobile number.",
            "warning"
        )

        return redirect(
            url_for("checkout.checkout")
        )

    # =====================================================
    # PINCODE VALIDATION
    # =====================================================

    if not pincode.isdigit() or len(pincode) != 6:

        flash(
            "Please enter a valid 6-digit pincode.",
            "warning"
        )

        return redirect(
            url_for("checkout.checkout")
        )

    # =====================================================
    # DATABASE CONNECTION
    # =====================================================

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # =================================================
        # CHECK WHETHER SAME ADDRESS ALREADY EXISTS
        # =================================================

        cursor.execute("""
            SELECT id
            FROM addresses
            WHERE user_id = %s
              AND full_name = %s
              AND phone = %s
              AND address = %s
              AND city = %s
              AND state = %s
              AND pincode = %s
              AND COALESCE(landmark, '') = %s
            LIMIT 1
        """, (
            user_id,
            full_name,
            phone,
            address,
            city,
            state,
            pincode,
            landmark
        ))

        existing_address = cursor.fetchone()

        # =================================================
        # ADDRESS ALREADY SAVED
        # =================================================

        if existing_address:

            address_id = existing_address["id"]

            print(
                "ADDRESS ALREADY EXISTS:",
                address_id
            )

            flash(
                "Using your saved delivery address.",
                "success"
            )

            return redirect(
                url_for(
                    "checkout.payment",
                    address_id=address_id
                )
            )

        # =================================================
        # INSERT NEW ADDRESS
        # =================================================

        cursor.execute("""
            INSERT INTO addresses
            (
                user_id,
                full_name,
                phone,
                address,
                city,
                state,
                pincode,
                landmark
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            user_id,
            full_name,
            phone,
            address,
            city,
            state,
            pincode,
            landmark
        ))

        # =================================================
        # GET NEW ADDRESS ID
        # =================================================

        address_id = cursor.lastrowid

        # =================================================
        # COMMIT
        # =================================================

        conn.commit()

        print(
            "NEW ADDRESS SAVED:",
            address_id
        )

        flash(
            "Delivery address saved successfully.",
            "success"
        )

        # =================================================
        # GO TO PAYMENT
        # =================================================

        return redirect(
            url_for(
                "checkout.payment",
                address_id=address_id
            )
        )

    except Exception as e:

        conn.rollback()

        print(
            "SAVE ADDRESS ERROR:",
            e
        )

        flash(
            "Unable to save address. Please try again.",
            "danger"
        )

        return redirect(
            url_for(
                "checkout.checkout"
            )
        )

    finally:

        cursor.close()
        conn.close()

# =========================================================
# PAYMENT PAGE
# =========================================================

@checkout_bp.route(
    "/payment/<int:address_id>",
    methods=["GET"]
)
def payment(address_id):


    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # =================================================
        # VERIFY ADDRESS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                full_name,
                phone,
                address,
                city,
                state,
                pincode,
                landmark
            FROM addresses
            WHERE id = %s
              AND user_id = %s
        """, (
            address_id,
            user_id
        ))


        address = cursor.fetchone()


        if not address:

            flash(
                "Invalid delivery address.",
                "danger"
            )

            return redirect(
                url_for("checkout.checkout")
            )


        # =================================================
        # GET CART
        # =================================================

        cursor.execute("""
            SELECT
                c.product_id,
                c.quantity,
                p.name,
                p.price,
                p.discount,
                p.image,
                p.stock
            FROM cart c
            JOIN products p
                ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))


        cart_items = cursor.fetchall()


        if not cart_items:

            flash(
                "Your cart is empty.",
                "warning"
            )

            return redirect(
                url_for("cart.cart")
            )


        # =================================================
        # CALCULATE TOTAL
        # =================================================

        subtotal = 0

        discount_total = 0


        for item in cart_items:

            price = float(
                item["price"] or 0
            )

            discount = float(
                item["discount"] or 0
            )

            quantity = int(
                item["quantity"] or 1
            )


            discount_amount = (
                price * discount / 100
            )


            final_price = (
                price - discount_amount
            )


            item["final_price"] = final_price


            item["item_total"] = (
                final_price * quantity
            )


            subtotal += (
                price * quantity
            )


            discount_total += (
                discount_amount * quantity
            )


        total_amount = (
            subtotal - discount_total
        )


        # =================================================
        # RENDER PAYMENT
        # =================================================

        return render_template(
            "checkout/payment.html",

            address=address,

            cart_items=cart_items,

            subtotal=subtotal,

            discount=discount_total,

            total_amount=total_amount
        )


    except Exception as e:

        print(
            "PAYMENT PAGE ERROR:",
            e
        )

        flash(
            "Unable to load payment page.",
            "danger"
        )

        return redirect(
            url_for("checkout.checkout")
        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# PLACE ORDER
# =========================================================

@checkout_bp.route(
    "/place-order",
    methods=["POST"]
)
def place_order():


    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    # =====================================================
    # FORM DATA
    # =====================================================

    address_id = request.form.get(
        "address_id"
    )


    payment_method = request.form.get(
        "payment_method"
    )


    if (
        not address_id
        or not payment_method
    ):

        flash(
            "Please select address and payment method.",
            "warning"
        )

        return redirect(
            url_for(
                "checkout.checkout"
            )
        )


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    try:

        # =================================================
        # VERIFY ADDRESS
        # =================================================

        cursor.execute("""
            SELECT *
            FROM addresses
            WHERE id = %s
              AND user_id = %s
        """, (
            address_id,
            user_id
        ))


        address = cursor.fetchone()


        if not address:

            flash(
                "Invalid delivery address.",
                "danger"
            )

            return redirect(
                url_for(
                    "checkout.checkout"
                )
            )


        # =================================================
        # GET CART
        # =================================================

        cursor.execute("""
            SELECT
                c.product_id,
                c.quantity,
                p.name,
                p.price,
                p.discount,
                p.stock
            FROM cart c
            JOIN products p
                ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))


        cart_items = cursor.fetchall()


        if not cart_items:

            flash(
                "Your cart is empty.",
                "warning"
            )

            return redirect(
                url_for("cart.cart")
            )


        # =================================================
        # CALCULATE TOTAL
        # =================================================

        total_amount = 0


        for item in cart_items:

            price = float(
                item["price"] or 0
            )

            discount = float(
                item["discount"] or 0
            )

            quantity = int(
                item["quantity"] or 1
            )


            # ---------------------------------------------
            # STOCK CHECK
            # ---------------------------------------------

            if item["stock"] is None:

                raise Exception(
                    f"Stock unavailable for product {item['product_id']}"
                )


            if int(item["stock"]) < quantity:

                flash(
                    f"Insufficient stock for {item['name']}.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "checkout.payment",
                        address_id=address_id
                    )
                )


            # ---------------------------------------------
            # FINAL PRICE
            # ---------------------------------------------

            discount_amount = (
                price * discount / 100
            )


            final_price = (
                price - discount_amount
            )


            total_amount += (
                final_price * quantity
            )


        # =================================================
        # CREATE ORDER
        # =================================================

        cursor.execute("""
            INSERT INTO orders
            (
                user_id,
                address_id,
                total_amount,
                status,
                payment_method
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (

            user_id,

            address_id,

            total_amount,

            "Placed",

            payment_method

        ))


        order_id = cursor.lastrowid


        # =================================================
        # CREATE ORDER ITEMS
        # =================================================

        for item in cart_items:

            price = float(
                item["price"] or 0
            )

            discount = float(
                item["discount"] or 0
            )

            quantity = int(
                item["quantity"] or 1
            )


            discount_amount = (
                price * discount / 100
            )


            final_price = (
                price - discount_amount
            )


            cursor.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (

                order_id,

                item["product_id"],

                quantity,

                final_price

            ))


            # =================================================
            # REDUCE STOCK
            # =================================================

            cursor.execute("""
                UPDATE products
                SET stock = stock - %s
                WHERE id = %s
                  AND stock >= %s
            """, (

                quantity,

                item["product_id"],

                quantity

            ))


            if cursor.rowcount != 1:

                raise Exception(
                    f"Unable to update stock for product {item['product_id']}"
                )


        # =================================================
        # CLEAR CART
        # =================================================

        cursor.execute("""
            DELETE FROM cart
            WHERE user_id = %s
        """, (user_id,))


        # =================================================
        # COMMIT EVERYTHING
        # =================================================

        conn.commit()


        print(
            "ORDER CREATED:",
            order_id
        )


        # =================================================
        # SUCCESS PAGE
        # =================================================

        return redirect(
            url_for(
                "checkout.order_success",
                order_id=order_id
            )
        )


    except Exception as e:

        conn.rollback()


        print(
            "PLACE ORDER ERROR:",
            e
        )


        flash(
            "Unable to place order. Please try again.",
            "danger"
        )


        return redirect(
            url_for(
                "checkout.payment",
                address_id=address_id
            )
        )


    finally:

        cursor.close()
        conn.close()

# =========================================================
# ORDER SUCCESS
# =========================================================

@checkout_bp.route("/success/<int:order_id>", methods=["GET"])
def order_success(order_id):

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # =================================================
        # GET ORDER
        # =================================================

        cursor.execute("""
            SELECT
                o.id,
                o.user_id,
                o.address_id,
                o.total_amount,
                o.status,
                o.payment_method,
                o.created_at
            FROM orders o
            WHERE o.id = %s
              AND o.user_id = %s
        """, (
            order_id,
            user_id
        ))

        order = cursor.fetchone()

        # =================================================
        # ORDER NOT FOUND
        # =================================================

        if not order:

            flash(
                "Order not found.",
                "danger"
            )

            return redirect(
                url_for("orders.orders")
            )

        # =================================================
        # GET DELIVERY ADDRESS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                full_name,
                phone,
                address,
                city,
                state,
                pincode,
                landmark
            FROM addresses
            WHERE id = %s
              AND user_id = %s
        """, (
            order["address_id"],
            user_id
        ))

        address = cursor.fetchone()

        # =================================================
        # GET ORDER ITEMS
        # =================================================

        cursor.execute("""
            SELECT
                oi.id,
                oi.product_id,
                oi.quantity,
                oi.price,
                p.name,
                p.image
            FROM order_items oi
            LEFT JOIN products p
                ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))

        order_items = cursor.fetchall()

        # =================================================
        # RENDER SUCCESS PAGE
        # =================================================

        return render_template(
            "checkout/order_success.html",
            order=order,
            order_id=order_id,
            address=address,
            order_items=order_items
        )

    except Exception as e:

        print(
            "ORDER SUCCESS ERROR:",
            e
        )

        flash(
            "Unable to load order confirmation.",
            "danger"
        )

        return redirect(
            url_for("orders.orders")
        )

    finally:

        cursor.close()
        conn.close()