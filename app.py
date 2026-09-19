from flask import (
    Flask,
    
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

import os
import random
import smtplib
import requests
from dotenv import load_dotenv

from config import Config
from database import get_db_connection
from routes.checkout import checkout_bp
from routes.orders import orders_bp
from routes.cart import cart_bp
from routes.wishlist import wishlist_bp
from email.message import EmailMessage
from authlib.integrations.flask_client import OAuth





# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
# =========================================================
# GOOGLE OAUTH
# =========================================================

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)

app.config.from_object(Config)
app.register_blueprint(checkout_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(wishlist_bp)

# Pexels API Key




# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/login/google")
def google_login():

    redirect_uri = url_for(
        "google_callback",
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )
# =========================================================
# GOOGLE CALLBACK
# =========================================================

@app.route("/google/callback")
def google_callback():

    try:

        token = google.authorize_access_token()

        user_info = token.get("userinfo")

        if not user_info:

            flash(
                "Unable to get Google account details.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        email = user_info.get("email")
        name = user_info.get("name")

        if not email:

            flash(
                "Google email not available.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    role
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

            # ---------------------------------------------
            # NEW GOOGLE USER
            # ---------------------------------------------

            if not user:

                cursor.execute(
                    """
                    INSERT INTO users
                    (
                        name,
                        email,
                        password,
                        role
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        name,
                        email,
                        generate_password_hash(
                            os.urandom(32).hex()
                        ),
                        "customer"
                    )
                )

                connection.commit()

                user_id = cursor.lastrowid

                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        role
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )

                user = cursor.fetchone()

            # ---------------------------------------------
            # SESSION
            # ---------------------------------------------

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            flash(
                "Google login successful!",
                "success"
            )

            return redirect(
                url_for("home")
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    except Exception as e:

        return f"Google login failed: {e}"
# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not email:

            flash(
                "Please enter your email address.",
                "error"
            )

            return redirect(
                url_for("forgot_password")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT id, name, email
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

            if not user:

                flash(
                    "No account found with this email.",
                    "error"
                )

                return redirect(
                    url_for("forgot_password")
                )

            # Generate 6-digit OTP
            otp = str(
                random.randint(100000, 999999)
            )

            # Store temporary reset information
            session["reset_email"] = user["email"]
            session["reset_otp"] = otp

            # Send OTP
            send_reset_otp(
                user["email"],
                user["name"],
                otp
            )

            flash(
                "OTP has been sent to your email.",
                "success"
            )

            return redirect(
                url_for("verify_otp")
            )

        except Exception as e:

            return f"Forgot password failed: {e}"

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "auth/forgot_password.html"
    )
# =========================================================
# SEND RESET OTP
# =========================================================
def send_reset_otp(
    receiver_email,
    user_name,
    otp
):

    sender_email = os.getenv("MAIL_USERNAME")
    sender_password = os.getenv("MAIL_PASSWORD")

    if not sender_email:
        raise Exception("MAIL_USERNAME is missing in .env")

    if not sender_password:
        raise Exception("MAIL_PASSWORD is missing in .env")

    message = EmailMessage()

    message["Subject"] = "ShopEase Password Reset OTP"

    message["From"] = sender_email

    message["To"] = receiver_email

    message.set_content(
        f"""
Hello {user_name},

Your ShopEase password reset OTP is:

{otp}

This OTP is required to reset your password.

If you did not request a password reset,
please ignore this email.

Regards,
ShopEase Team
"""
    )

    with smtplib.SMTP(
        os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        int(os.getenv("MAIL_PORT", "587"))
    ) as server:

        server.starttls()

        server.login(
            sender_email,
            sender_password
        )

        server.send_message(message)

# =========================================================
# VERIFY OTP
# =========================================================

@app.route(
    "/verify-otp",
    methods=["GET", "POST"]
)
def verify_otp():

    if "reset_email" not in session:

        return redirect(
            url_for("forgot_password")
        )

    if request.method == "POST":

        entered_otp = request.form.get(
            "otp",
            ""
        ).strip()

        saved_otp = session.get(
            "reset_otp"
        )

        if entered_otp != saved_otp:

            flash(
                "Invalid OTP. Please try again.",
                "error"
            )

            return redirect(
                url_for("verify_otp")
            )

        session["otp_verified"] = True

        session.pop(
            "reset_otp",
            None
        )

        return redirect(
            url_for("reset_password")
        )

    return render_template(
        "auth/verify_otp.html"
    )

# =========================================================
# RESET PASSWORD
# =========================================================

@app.route(
    "/reset-password",
    methods=["GET", "POST"]
)
def reset_password():

    if not session.get(
        "otp_verified"
    ):

        return redirect(
            url_for("forgot_password")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not password or not confirm_password:

            flash(
                "Please enter both passwords.",
                "error"
            )

            return redirect(
                url_for("reset_password")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("reset_password")
            )

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("reset_password")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            hashed_password = generate_password_hash(
                password
            )

            cursor.execute(
                """
                UPDATE users
                SET password = %s
                WHERE email = %s
                """,
                (
                    hashed_password,
                    session["reset_email"]
                )
            )

            connection.commit()

            # Clear reset session
            session.pop(
                "reset_email",
                None
            )

            session.pop(
                "otp_verified",
                None
            )

            flash(
                "Password reset successfully. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Exception as e:

            if connection:
                connection.rollback()

            return f"Password reset failed: {e}"

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "auth/reset_password.html"
    )
# =========================================================
# HOME
# =========================================================
@app.route("/")
def home():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.id,
                p.name,
                p.description,
                p.price,
                p.discount,
                p.stock,
                p.image,
                p.rating,
                c.name AS category
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.id
            ORDER BY p.id ASC
            LIMIT 20
        """)

        products = cursor.fetchall()

        # Convert dictionary/tuple data into a consistent format
        formatted_products = []

        for product in products:

            if isinstance(product, dict):

                formatted_products.append({
                    "id": product.get("id"),
                    "name": product.get("name", "Product"),
                    "description": product.get("description", ""),
                    "price": product.get("price", 0),
                    "discount": product.get("discount", 0),
                    "stock": product.get("stock", 0),
                    "image": product.get("image", ""),
                    "rating": product.get("rating", 0),
                    "category": product.get("category", "")
                })

            else:

                formatted_products.append({
                    "id": product[0],
                    "name": product[1],
                    "description": product[2],
                    "price": product[3],
                    "discount": product[4],
                    "stock": product[5],
                    "image": product[6],
                    "rating": product[7],
                    "category": product[8]
                })

        return render_template(
            "index.html",
            products=formatted_products
        )

    except Exception as e:

        print("HOME PRODUCTS ERROR:", e)

        return render_template(
            "index.html",
            products=[]
        )
def get_local_product_image(product):

    image = product.get("image")

    if image:

        image = str(image).strip()

        # Already a full external URL
        if image.startswith("http://") or image.startswith("https://"):
            return image

        # Already correct Flask static path
        if image.startswith("/static/"):
            return image

        # Remove old incorrect paths
        image = image.replace("\\", "/")

        if image.startswith("/uploads/products/"):
            image = image.replace(
                "/uploads/products/",
                ""
            )

        elif image.startswith("uploads/products/"):
            image = image.replace(
                "uploads/products/",
                ""
            )

        elif image.startswith("static/uploads/products/"):
            image = image.replace(
                "static/uploads/products/",
                ""
            )

        # Only filename remains
        filename = os.path.basename(image)

        return (
            "/static/uploads/products/"
            + filename
        )

    # If database image is empty,
    # try product ID based filename

    product_id = product.get("id")

    if product_id:

        filename = f"product_{product_id}.jpg"

        filepath = os.path.join(
            app.static_folder,
            "uploads",
            "products",
            filename
        )

        if os.path.exists(filepath):

            return (
                "/static/uploads/products/"
                + filename
            )

    return None
get_product_image = get_local_product_image
# =========================================================
# PRODUCT ICON
# =========================================================

def get_product_icon(category):

    category_name = (category or "").lower().strip()

    if "mobile" in category_name:

        return "fa-mobile-screen-button"

    elif "electronic" in category_name:

        return "fa-laptop"

    elif "fashion" in category_name:

        return "fa-shirt"

    elif "footwear" in category_name:

        return "fa-shoe-prints"

    elif category_name == "home":

        return "fa-house"

    elif "beauty" in category_name:

        return "fa-spa"

    elif "book" in category_name:

        return "fa-book"

    elif "grocery" in category_name:

        return "fa-basket-shopping"

    return "fa-box"
@app.route("/wishlist")
def wishlist():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    return render_template("cart/wishlist.html")
# =========================================================
# CART
# =========================================================
@app.route("/cart")
def cart():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    return render_template("cart/cart.html")
# =========================================================
# PRODUCTS
# =========================================================
@app.route("/products")
def products():

    # =====================================================
    # GET FILTER VALUES
    # =====================================================

    category = request.args.get(
        "category",
        "all"
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()

    connection = None
    cursor = None

    try:

        # =================================================
        # DATABASE CONNECTION
        # =================================================

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # =================================================
        # BASE QUERY
        # =================================================

        query = """
            SELECT
                p.id,
                p.name,
                p.description,
                p.price,
                p.discount,
                p.stock,
                p.image,
                p.rating,
                c.name AS category

            FROM products p

            LEFT JOIN categories c
                ON p.category_id = c.id

            WHERE 1 = 1
        """

        params = []

        # =================================================
        # CATEGORY FILTER
        # =================================================

        if category.lower() != "all":

            query += """
                AND LOWER(c.name) = LOWER(%s)
            """

            params.append(category)

        # =================================================
        # SEARCH FILTER
        # =================================================
        # Searches in:
        # 1. Product name
        # 2. Product description
        # 3. Category name
        # =================================================

        if search:

            query += """
                AND (
                    LOWER(p.name) LIKE LOWER(%s)

                    OR

                    LOWER(p.description) LIKE LOWER(%s)

                    OR

                    LOWER(c.name) LIKE LOWER(%s)
                )
            """

            search_value = "%" + search + "%"

            params.append(search_value)
            params.append(search_value)
            params.append(search_value)

        # =================================================
        # ORDER PRODUCTS
        # =================================================

        query += """
            ORDER BY p.created_at DESC
        """

        # =================================================
        # EXECUTE QUERY
        # =================================================

        cursor.execute(
            query,
            tuple(params)
        )

        products = cursor.fetchall()

        # =================================================
        # PROCESS PRODUCTS
        # =================================================

        database_changed = False

        for product in products:

            # =================================================
            # PRICE
            # =================================================

            price = float(
                product.get("price") or 0
            )

            # =================================================
            # DISCOUNT
            # =================================================

            discount = float(
                product.get("discount") or 0
            )

            # =================================================
            # OLD PRICE
            # =================================================

            if discount > 0 and discount < 100:

                old_price = price / (
                    1 - discount / 100
                )

                product["old_price"] = round(
                    old_price
                )

                product["discount"] = (
                    f"{discount:g}% OFF"
                )

            else:

                product["old_price"] = None

                product["discount"] = None

            # =================================================
            # PRODUCT IMAGE
            # =================================================

            existing_image = (
                product.get("image") or ""
            ).strip()

            # =================================================
            # IMAGE EXISTS
            # =================================================

            if existing_image:

                product["image"] = existing_image

            # =================================================
            # IMAGE DOES NOT EXIST
            # =================================================

            else:

                try:

                    local_image = get_product_image(
                        product
                    )

                except Exception as image_error:

                    print(
                        "IMAGE ERROR:",
                        image_error
                    )

                    local_image = None

                if local_image:

                    product["image"] = local_image

                    # -----------------------------------------
                    # SAVE IMAGE PATH TO DATABASE
                    # -----------------------------------------

                    cursor.execute(
                        """
                        UPDATE products
                        SET image = %s
                        WHERE id = %s
                        """,
                        (
                            local_image,
                            product["id"]
                        )
                    )

                    database_changed = True

                else:

                    product["image"] = None

            # =================================================
            # PRODUCT ICON
            # =================================================

            try:

                product["icon"] = get_product_icon(
                    product.get("category")
                )

            except Exception:

                product["icon"] = "fa-box"

            # =================================================
            # RATING
            # =================================================

            rating = product.get("rating")

            if rating is None:

                product["rating"] = 0

            else:

                try:

                    product["rating"] = float(
                        rating
                    )

                except (TypeError, ValueError):

                    product["rating"] = 0

            # =================================================
            # STOCK
            # =================================================

            try:

                product["stock"] = int(
                    product.get("stock") or 0
                )

            except (TypeError, ValueError):

                product["stock"] = 0

        # =================================================
        # SAVE DATABASE CHANGES
        # =================================================

        if database_changed:

            connection.commit()

        # =================================================
        # RENDER PRODUCTS PAGE
        # =================================================

        return render_template(
            "products/products.html",
            products=products,
            category=category
        )

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        print(
            "PRODUCTS ERROR:",
            e
        )

        # ---------------------------------------------
        # Rollback if database operation failed
        # ---------------------------------------------

        if connection:

            try:

                connection.rollback()

            except Exception:

                pass

        return (
            f"Products loading failed: {e}"
        )

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:

            try:

                cursor.close()

            except Exception:

                pass

        if connection:

            try:

                connection.close()

            except Exception:

                pass



           

# =========================================================
# PRODUCT DETAILS
# =========================================================

@app.route("/product/<int:product_id>")
def product_details(product_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # GET MAIN PRODUCT
        # =====================================================

        cursor.execute(
            """
            SELECT
                p.id,
                p.name,
                p.brand,
                p.description,
                p.price,
                p.discount,
                p.stock,
                p.image,
                p.rating,
                p.category_id,
                c.name AS category
            FROM products p
            LEFT JOIN categories c
                ON p.category_id = c.id
            WHERE p.id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        # =====================================================
        # PRODUCT NOT FOUND
        # =====================================================

        if not product:
            return render_template("404.html"), 404

        # =====================================================
        # NORMALIZE MAIN PRODUCT
        # =====================================================

        product["id"] = int(
            product.get("id") or 0
        )

        product["name"] = str(
            product.get("name") or "Product"
        )

        product["brand"] = str(
            product.get("brand") or ""
        )

        product["description"] = str(
            product.get("description")
            or "No description available for this product."
        )

        product["price"] = float(
            product.get("price") or 0
        )

        product["discount"] = float(
            product.get("discount") or 0
        )

        product["stock"] = int(
            product.get("stock") or 0
        )

        product["rating"] = float(
            product.get("rating") or 0
        )

        product["category"] = str(
            product.get("category") or "Product"
        )

        # =====================================================
        # OLD PRICE
        # =====================================================

        if (
            product["discount"] > 0
            and product["discount"] < 100
        ):

            old_price = (
                product["price"]
                /
                (
                    1
                    -
                    product["discount"] / 100
                )
            )

            product["old_price"] = round(
                old_price
            )

            product["discount_text"] = (
                f'{product["discount"]:g}% OFF'
            )

        else:

            product["old_price"] = None
            product["discount_text"] = None

        # =====================================================
        # MAIN IMAGE
        # =====================================================

        if not product.get("image"):

            product["image"] = get_product_image(
                product
            )

        if not product.get("image"):

            product["image"] = ""

        else:

            product["image"] = str(
                product["image"]
            )

        # =====================================================
        # ICON
        # =====================================================

        product["icon"] = get_product_icon(
            product.get("category")
        )

        if not product["icon"]:

            product["icon"] = "fa-box"

        # =====================================================
        # PRODUCT GALLERY
        # =====================================================

        product_images = []

        cursor.execute(
            """
            SELECT
                id,
                image
            FROM product_images
            WHERE product_id = %s
            ORDER BY id ASC
            """,
            (product_id,)
        )

        gallery_rows = cursor.fetchall()

        # -----------------------------------------------------
        # MAIN IMAGE FIRST
        # -----------------------------------------------------

        if product["image"]:

            product_images.append(
                {
                    "id": 0,
                    "image": product["image"]
                }
            )

        # -----------------------------------------------------
        # ADD GALLERY IMAGES
        # -----------------------------------------------------

        for row in gallery_rows:

            image = row.get("image")

            if image:

                image = str(image)

                existing_images = [
                    item["image"]
                    for item in product_images
                ]

                # Avoid duplicate images
                if image not in existing_images:

                    product_images.append(
                        {
                            "id": int(
                                row.get("id") or 0
                            ),
                            "image": image
                        }
                    )

        # =====================================================
        # SIMILAR PRODUCTS
        #
        # PRIORITY:
        #
        # 1. SAME BRAND + SAME CATEGORY
        # 2. SAME CATEGORY + OTHER BRANDS
        #
        # Example:
        #
        # Open:
        # Samsung Galaxy S24
        #
        # First:
        # Samsung Galaxy A55
        # Samsung Galaxy S23
        # Samsung Galaxy S23 Ultra
        # Samsung Galaxy S24 Plus
        # Samsung Galaxy S24 Ultra
        # Samsung Galaxy S23 FE
        # Samsung Galaxy A35 5G
        # Samsung Galaxy A25 5G
        #
        # Then, if needed:
        # iPhone / OnePlus / Redmi / etc.
        # =====================================================

        current_brand = product.get("brand")
        current_category_id = product.get("category_id")

        # =====================================================
        # GET SAME BRAND PRODUCTS FIRST
        # =====================================================

        same_brand_products = []

        if current_brand:

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    p.brand,
                    p.description,
                    p.price,
                    p.discount,
                    p.stock,
                    p.image,
                    p.rating,
                    p.category_id,
                    c.name AS category
                FROM products p
                LEFT JOIN categories c
                    ON p.category_id = c.id
                WHERE
                    p.category_id = %s
                    AND p.brand = %s
                    AND p.id != %s
                ORDER BY
                    p.rating DESC,
                    p.id DESC
                LIMIT 8
                """,
                (
                    current_category_id,
                    current_brand,
                    product_id
                )
            )

            same_brand_products = (
                cursor.fetchall()
            )

        # =====================================================
        # HOW MANY MORE PRODUCTS ARE NEEDED?
        # =====================================================

        remaining_count = (
            8 - len(same_brand_products)
        )

        # =====================================================
        # GET OTHER CATEGORY PRODUCTS
        #
        # ONLY IF SAME BRAND PRODUCTS ARE LESS THAN 8
        # =====================================================

        other_category_products = []

        if remaining_count > 0:

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    p.brand,
                    p.description,
                    p.price,
                    p.discount,
                    p.stock,
                    p.image,
                    p.rating,
                    p.category_id,
                    c.name AS category
                FROM products p
                LEFT JOIN categories c
                    ON p.category_id = c.id
                WHERE
                    p.category_id = %s
                    AND p.id != %s
                    AND (
                        p.brand IS NULL
                        OR p.brand != %s
                    )
                ORDER BY
                    p.rating DESC,
                    p.id DESC
                LIMIT %s
                """,
                (
                    current_category_id,
                    product_id,
                    current_brand or "",
                    remaining_count
                )
            )

            other_category_products = (
                cursor.fetchall()
            )

        # =====================================================
        # COMBINE PRODUCTS
        #
        # SAME BRAND FIRST
        # OTHER BRANDS SECOND
        # =====================================================

        similar_products = (
            same_brand_products
            +
            other_category_products
        )

        # Make absolutely sure only 8 are shown
        similar_products = similar_products[:8]

        # =====================================================
        # NORMALIZE SIMILAR PRODUCTS
        # =====================================================

        clean_similar_products = []

        for item in similar_products:

            # -------------------------------------------------
            # ID
            # -------------------------------------------------

            item["id"] = int(
                item.get("id") or 0
            )

            # -------------------------------------------------
            # NAME
            # -------------------------------------------------

            item["name"] = str(
                item.get("name") or "Product"
            )

            # -------------------------------------------------
            # BRAND
            # -------------------------------------------------

            item["brand"] = str(
                item.get("brand") or ""
            )

            # -------------------------------------------------
            # DESCRIPTION
            # -------------------------------------------------

            item["description"] = str(
                item.get("description") or ""
            )

            # -------------------------------------------------
            # PRICE
            # -------------------------------------------------

            item["price"] = float(
                item.get("price") or 0
            )

            # -------------------------------------------------
            # DISCOUNT
            # -------------------------------------------------

            item["discount"] = float(
                item.get("discount") or 0
            )

            # -------------------------------------------------
            # STOCK
            # -------------------------------------------------

            item["stock"] = int(
                item.get("stock") or 0
            )

            # -------------------------------------------------
            # RATING
            # -------------------------------------------------

            item["rating"] = float(
                item.get("rating") or 0
            )

            # -------------------------------------------------
            # CATEGORY
            # -------------------------------------------------

            item["category"] = str(
                item.get("category")
                or product["category"]
            )

            # =================================================
            # IMAGE
            # =================================================

            if not item.get("image"):

                item["image"] = get_product_image(
                    item
                )

            if not item.get("image"):

                item["image"] = ""

            else:

                item["image"] = str(
                    item["image"]
                )

            # =================================================
            # ICON
            # =================================================

            item["icon"] = get_product_icon(
                item["category"]
            )

            if not item["icon"]:

                item["icon"] = "fa-box"

            # =================================================
            # OLD PRICE
            # =================================================

            if (
                item["discount"] > 0
                and item["discount"] < 100
            ):

                item["old_price"] = round(
                    item["price"]
                    /
                    (
                        1
                        -
                        item["discount"] / 100
                    )
                )

                item["discount_text"] = (
                    f'{item["discount"]:g}% OFF'
                )

            else:

                item["old_price"] = None
                item["discount_text"] = None

            # =================================================
            # ADD TO CLEAN LIST
            # =================================================

            clean_similar_products.append(
                item
            )

        # =====================================================
        # DEBUG INFORMATION
        # =====================================================

        print(
            "================================================="
        )

        print(
            "PRODUCT:",
            product["name"]
        )

        print(
            "BRAND:",
            product["brand"]
        )

        print(
            "CATEGORY:",
            product["category"]
        )

        print(
            "SAME BRAND PRODUCTS:",
            len(same_brand_products)
        )

        print(
            "OTHER CATEGORY PRODUCTS:",
            len(other_category_products)
        )

        print(
            "TOTAL SIMILAR PRODUCTS:",
            len(clean_similar_products)
        )

        print(
            "================================================="
        )

        # =====================================================
        # RENDER
        # =====================================================

        return render_template(
            "products/product_details.html",
            product=product,
            product_images=product_images,
            similar_products=clean_similar_products
        )

    # =========================================================
    # ERROR HANDLING
    # =========================================================

    except Exception as e:

        print(
            "PRODUCT DETAILS ERROR:",
            repr(e)
        )

        return (
            f"Product details loading failed: {e}"
        )

    # =========================================================
    # CLOSE DATABASE
    # =========================================================

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()            
# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():


    if request.method == "POST":


        # =====================================================
        # FORM DATA
        # =====================================================

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # =====================================================
        # VALIDATION
        # =====================================================

        if not name or not email or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )


        connection = None
        cursor = None


        try:


            # =================================================
            # DATABASE
            # =================================================

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )


            # =================================================
            # CHECK EMAIL
            # =================================================

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing_user = cursor.fetchone()


            if existing_user:

                flash(
                    "Email already registered. Please login.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )


            # =================================================
            # PASSWORD HASH
            # =================================================

            hashed_password = generate_password_hash(
                password
            )


            # =================================================
            # INSERT USER
            # =================================================

            cursor.execute(
                """
                INSERT INTO users
                    (name, email, password, role)

                VALUES
                    (%s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    hashed_password,
                    "customer"
                )
            )


            connection.commit()


            flash(
                "Registration successful! Please login.",
                "success"
            )


            return redirect(
                url_for("login")
            )


        except Exception as e:


            if connection:

                connection.rollback()


            return (
                f"Registration failed: {e}"
            )


        finally:


            if cursor:

                cursor.close()


            if connection:

                connection.close()


    return render_template(
        "auth/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():


    if request.method == "POST":


        # =====================================================
        # FORM DATA
        # =====================================================

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # =====================================================
        # VALIDATION
        # =====================================================

        if not email or not password:

            flash(
                "Please enter email and password.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        connection = None
        cursor = None


        try:


            # =================================================
            # DATABASE
            # =================================================

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )


            # =================================================
            # GET USER
            # =================================================

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role

                FROM users

                WHERE email = %s
                """,
                (email,)
            )


            user = cursor.fetchone()


            # =================================================
            # CHECK LOGIN
            # =================================================

            if user and check_password_hash(
                user["password"],
                password
            ):


                # =============================================
                # SESSION
                # =============================================

                session["user_id"] = user["id"]

                session["user_name"] = user["name"]

                session["user_email"] = user["email"]

                session["user_role"] = user["role"]


                flash(
                    "Login successful!",
                    "success"
                )


                return redirect(
                    url_for("home")
                )


            # =================================================
            # INVALID LOGIN
            # =================================================

            flash(
                "Invalid email or password.",
                "error"
            )


            return redirect(
                url_for("login")
            )


        except Exception as e:


            return (
                f"Login failed: {e}"
            )


        finally:


            if cursor:

                cursor.close()


            if connection:

                connection.close()


    return render_template(
        "auth/login.html"
    )

@app.route("/profile")
def profile():
    return render_template("profile/profile.html")


# =========================================================
# EDIT PROFILE
# =========================================================

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    # User login ayyi undali
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # SAVE PROFILE
        # =====================================================

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()

            # Name validation
            if not name:

                flash(
                    "Full name cannot be empty.",
                    "error"
                )

                return redirect(
                    url_for("edit_profile")
                )

            # =================================================
            # UPDATE DATABASE
            # =================================================

            cursor.execute(
                """
                UPDATE users
                SET
                    name = %s,
                    phone = %s
                WHERE id = %s
                """,
                (
                    name,
                    phone,
                    session["user_id"]
                )
            )

            connection.commit()

            # =================================================
            # UPDATE SESSION
            # =================================================

            session["user_name"] = name
            session["user_phone"] = phone

            flash(
                "Profile updated successfully!",
                "success"
            )

            return redirect(
                url_for("profile")
            )

        # =====================================================
        # GET CURRENT USER DETAILS
        # =====================================================

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                role
            FROM users
            WHERE id = %s
            """,
            (
                session["user_id"],
            )
        )

        user = cursor.fetchone()

        # =====================================================
        # USER NOT FOUND
        # =====================================================

        if not user:

            flash(
                "User account not found.",
                "error"
            )

            return redirect(
                url_for("logout")
            )

        # =====================================================
        # OPEN EDIT PROFILE PAGE
        # =====================================================

        return render_template(
            "profile/edit_profile.html",
            user=user
        )

    # =========================================================
    # ERROR
    # =========================================================

    except Exception as e:

        if connection:

            connection.rollback()

        print(
            "EDIT PROFILE ERROR:",
            repr(e)
        )

        return (
            f"Edit profile failed: {e}"
        )

    # =========================================================
    # CLOSE DATABASE
    # =========================================================

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


@app.route("/profile/addresses")
def addresses():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "profile/addresses.html"
    )
# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():


    session.clear()


    flash(
        "You have been logged out.",
        "success"
    )


    return redirect(
        url_for("home")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )