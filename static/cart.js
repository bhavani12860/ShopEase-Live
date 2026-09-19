/* =====================================================
   SHOP EASE - CART JAVASCRIPT
===================================================== */
/* =====================================================
   USER-SPECIFIC CART KEY
===================================================== */

function getCartStorageKey() {

    return "shopEaseCart_user_" +
        String(SHOP_EASE_USER_ID);

}

/* =====================================================
   CART DATA
===================================================== */

let cartItems = [];


/* =====================================================
   GET CART
===================================================== */

function getCart() {

    try {

        const storageKey =
            getCartStorageKey();

        const savedCart =
            localStorage.getItem(storageKey);

        if (!savedCart) {
            return [];
        }

        const cart =
            JSON.parse(savedCart);

        return Array.isArray(cart)
            ? cart
            : [];

    } catch (error) {

        console.error(
            "Cart loading error:",
            error
        );

        return [];

    }

}


/* =====================================================
   SAVE CART
===================================================== */
function saveCart() {

    const storageKey =
        getCartStorageKey();

    localStorage.setItem(
        storageKey,
        JSON.stringify(cartItems)
    );

}


/* =====================================================
   FORMAT PRICE
===================================================== */

function formatPrice(price) {

    return "₹" +
        Number(price || 0).toLocaleString("en-IN");

}


/* =====================================================
   TOTAL ITEMS
===================================================== */

function getTotalItems() {

    return cartItems.reduce(
        function(total, item) {

            const quantity =
                Number(item.quantity || 1);

            return total + quantity;

        },
        0
    );

}


/* =====================================================
   TOTAL PRICE
===================================================== */

function getTotalPrice() {

    return cartItems.reduce(
        function(total, item) {

            const price =
                Number(item.price || 0);

            const quantity =
                Number(item.quantity || 1);

            return total + (price * quantity);

        },
        0
    );

}


/* =====================================================
   ESCAPE HTML
===================================================== */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value || "");

    return div.innerHTML;

}


/* =====================================================
   REMOVE ITEM
===================================================== */

function removeCartItem(index) {

    if (
        index < 0 ||
        index >= cartItems.length
    ) {
        return;
    }

    cartItems.splice(
        index,
        1
    );

    saveCart();

    renderCart();

}


/* =====================================================
   DECREASE QUANTITY
===================================================== */

function decreaseCartQuantity(index) {

    if (!cartItems[index]) {
        return;
    }

    let quantity =
        Number(
            cartItems[index].quantity || 1
        );

    if (quantity > 1) {

        cartItems[index].quantity =
            quantity - 1;

    } else {

        cartItems.splice(
            index,
            1
        );

    }

    saveCart();

    renderCart();

}


/* =====================================================
   INCREASE QUANTITY
===================================================== */

function increaseCartQuantity(index) {

    if (!cartItems[index]) {
        return;
    }

    let quantity =
        Number(
            cartItems[index].quantity || 1
        );

    cartItems[index].quantity =
        quantity + 1;

    saveCart();

    renderCart();

}


/* =====================================================
   PLACE ORDER
===================================================== */

async function placeOrder() {

    if (cartItems.length === 0) {

        alert("Your cart is empty.");

        return;
    }

    const checkoutButton =
        document.querySelector(".checkout-btn");

    if (checkoutButton) {

        checkoutButton.disabled = true;

        checkoutButton.innerHTML =
            "Saving Cart...";
    }

    try {

        const response =
            await fetch("/cart/sync", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    items: cartItems
                })

            });


        const result =
            await response.json();


        if (!response.ok || !result.success) {

            throw new Error(
                result.message ||
                "Cart could not be saved."
            );
        }


        console.log(
            "Cart successfully saved to MySQL."
        );


        window.location.href =
            "/checkout/";


    } catch (error) {

        console.error(
            "Checkout error:",
            error
        );

        alert(
            error.message ||
            "Unable to continue to checkout."
        );


        if (checkoutButton) {

            checkoutButton.disabled = false;

            checkoutButton.innerHTML =
                "PLACE ORDER";
        }

    }

}
/* =====================================================
   RENDER CART
===================================================== */

function renderCart() {

    const container =
        document.getElementById(
            "cartItems"
        );

    const countElement =
        document.getElementById(
            "cartItemCount"
        );

    if (!container) {
        return;
    }


    /* =================================================
       NORMALIZE QUANTITIES
    ================================================= */

    cartItems.forEach(
        function(item) {

            if (
                !item.quantity ||
                Number(item.quantity) < 1
            ) {

                item.quantity = 1;

            }

        }
    );


    /* =================================================
       EMPTY CART
    ================================================= */

    if (cartItems.length === 0) {

        container.innerHTML = `

            <div class="empty-cart">

                <i class="fa-solid fa-cart-shopping"></i>

                <h2>
                    Your cart is empty
                </h2>

                <p>
                    Add products to your cart to see them here.
                </p>

                <a
                    href="/products?category=all"
                    class="shop-btn"
                >
                    Continue Shopping
                </a>

            </div>

        `;


        if (countElement) {

            countElement.textContent =
                "0 items";

        }

        return;

    }


    /* =================================================
       TOTALS
    ================================================= */

    const totalItems =
        getTotalItems();

    const totalPrice =
        getTotalPrice();


    /* =================================================
       CART COUNT
    ================================================= */

    if (countElement) {

        countElement.textContent =
            totalItems +
            (
                totalItems === 1
                    ? " item"
                    : " items"
            );

    }


    /* =================================================
       PRODUCTS HTML
    ================================================= */

    let productsHTML = "";


    cartItems.forEach(
        function(item, index) {

            const quantity =
                Number(item.quantity || 1);

            const price =
                Number(item.price || 0);

            const itemTotal =
                price * quantity;


            /* =================================================
               PRODUCT IMAGE
            ================================================= */

            let imageHTML = "";


            if (item.image) {

                imageHTML = `

                    <img
                        src="${escapeHtml(item.image)}"
                        alt="${escapeHtml(item.name)}"
                        onerror="
                            this.style.display='none';
                            this.nextElementSibling.style.display='block';
                        "
                    >

                    <i
                        class="fa-solid fa-box"
                        style="display:none;"
                    ></i>

                `;

            } else {

                imageHTML = `

                    <i class="fa-solid fa-box"></i>

                `;

            }


            /* =================================================
               CART ITEM
            ================================================= */

            productsHTML += `

                <div class="cart-item">


                    <!-- IMAGE -->

                    <div class="cart-item-image">

                        ${imageHTML}

                    </div>


                    <!-- DETAILS -->

                    <div class="cart-item-details">

                        <h2>
                            ${escapeHtml(item.name)}
                        </h2>


                        <div class="cart-price">

                            ${formatPrice(price)}

                        </div>


                        <!-- QUANTITY -->

                        <div class="quantity-box">

                            <button
                                type="button"
                                onclick="decreaseCartQuantity(${index})"
                                aria-label="Decrease quantity"
                            >
                                −
                            </button>


                            <span class="quantity-value">

                                ${quantity}

                            </span>


                            <button
                                type="button"
                                onclick="increaseCartQuantity(${index})"
                                aria-label="Increase quantity"
                            >
                                +
                            </button>

                        </div>


                        <!-- REMOVE -->

                        <button
                            type="button"
                            class="remove-btn"
                            onclick="removeCartItem(${index})"
                        >

                            <i class="fa-solid fa-trash"></i>

                            REMOVE

                        </button>

                    </div>


                    <!-- ITEM TOTAL -->

                    <div class="cart-item-total">

                        ${formatPrice(itemTotal)}

                    </div>


                </div>

            `;

        }
    );


    /* =================================================
       COMPLETE CART
    ================================================= */

    container.innerHTML = `

        <div class="cart-layout">


            <!-- PRODUCTS -->

            <section class="cart-products">

                ${productsHTML}

            </section>


            <!-- SUMMARY -->

            <aside class="cart-summary">


                <div class="summary-title">

                    PRICE DETAILS

                </div>


                <div class="summary-content">


                    <div class="summary-row">

                        <span>
                            Price
                        </span>

                        <span>
                            ${formatPrice(totalPrice)}
                        </span>

                    </div>


                    <div class="summary-row">

                        <span>
                            Delivery
                        </span>

                        <span class="delivery-free">
                            FREE
                        </span>

                    </div>


                    <div class="summary-row summary-total">

                        <span>
                            Total Amount
                        </span>

                        <span id="cartTotal">

                            ${formatPrice(totalPrice)}

                        </span>

                    </div>


                    <button
                        type="button"
                        class="checkout-btn"
                        onclick="placeOrder()"
                    >

                        PLACE ORDER

                    </button>


                </div>

            </aside>


        </div>

    `;

}


/* =====================================================
   PAGE LOAD
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        cartItems =
            getCart();

        renderCart();

    }
);