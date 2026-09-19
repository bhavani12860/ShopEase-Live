/* =========================================================
   SHOP EASE - MAIN JAVASCRIPT
   USER-SPECIFIC CART + WISHLIST SYSTEM

   Cart:
   shopEaseCart_user_<user_id>

   Wishlist:
   shopEaseWishlist_user_<user_id>
========================================================= */


/* =========================================================
   USER ID
========================================================= */

function getShopEaseUserId() {

    if (
        typeof SHOP_EASE_USER_ID === "undefined" ||
        SHOP_EASE_USER_ID === null
    ) {
        return "guest";
    }

    return String(SHOP_EASE_USER_ID);
}


/* =========================================================
   STORAGE KEYS
========================================================= */

function getCartStorageKey() {

    return "shopEaseCart_user_" +
           getShopEaseUserId();
}


function getWishlistStorageKey() {

    return "shopEaseWishlist_user_" +
           getShopEaseUserId();
}


/* =========================================================
   CART STORAGE
========================================================= */

function getCart() {

    try {

        const data = localStorage.getItem(
            getCartStorageKey()
        );

        if (!data) {
            return [];
        }

        const parsed = JSON.parse(data);

        return Array.isArray(parsed)
            ? parsed
            : [];

    } catch (error) {

        console.error(
            "Cart read error:",
            error
        );

        return [];
    }
}


function saveCart(cart) {

    try {

        localStorage.setItem(
            getCartStorageKey(),
            JSON.stringify(cart)
        );

    } catch (error) {

        console.error(
            "Cart save error:",
            error
        );
    }
}


/* =========================================================
   WISHLIST STORAGE
========================================================= */

function getWishlist() {

    try {

        const data = localStorage.getItem(
            getWishlistStorageKey()
        );

        if (!data) {
            return [];
        }

        const parsed = JSON.parse(data);

        return Array.isArray(parsed)
            ? parsed
            : [];

    } catch (error) {

        console.error(
            "Wishlist read error:",
            error
        );

        return [];
    }
}


function saveWishlist(wishlist) {

    try {

        localStorage.setItem(
            getWishlistStorageKey(),
            JSON.stringify(wishlist)
        );

    } catch (error) {

        console.error(
            "Wishlist save error:",
            error
        );
    }
}


/* =========================================================
   TOAST
========================================================= */

let toastTimer = null;


function showToast(message, type = "success") {

    let toast = document.querySelector(
        ".shop-toast"
    );

    if (!toast) {

        toast = document.createElement("div");

        toast.className = "shop-toast";

        document.body.appendChild(toast);
    }

    toast.textContent = message;

    toast.className =
        "shop-toast show " + type;

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {

        toast.classList.remove("show");

    }, 2500);
}


/* =========================================================
   CART COUNT
========================================================= */

function updateCartCount() {

    const cart = getCart();

    const totalQuantity = cart.reduce(
        (total, item) => {

            const quantity =
                Number(item.quantity || 1);

            return total + quantity;

        },
        0
    );


    document
        .querySelectorAll("#cartCount, .cart-count")
        .forEach(element => {

            element.textContent =
                totalQuantity;

        });
}


/* =========================================================
   WISHLIST COUNT
========================================================= */

function updateWishlistCount() {

    const wishlist = getWishlist();

    document
        .querySelectorAll(
            "#wishlistCount, .wishlist-count"
        )
        .forEach(element => {

            element.textContent =
                wishlist.length;

        });
}


/* =========================================================
   PRODUCT DATA
========================================================= */

function getProductData(button) {

    if (!button) {
        return null;
    }


    const card =
        button.closest(
            ".home-product-card, " +
            ".product-card, " +
            ".shop-product-card, " +
            ".product-item, " +
            "[data-product-id]"
        );


    if (!card) {
        return null;
    }


    const id =
        card.dataset.productId ||
        button.dataset.productId;


    const name =
        card.dataset.productName ||
        card.querySelector(
            ".home-product-name, " +
            ".product-name, " +
            "h3, h2"
        )?.textContent?.trim() ||
        "Product";


    const priceElement =
        card.querySelector(
            ".home-current-price, " +
            ".current-price, " +
            ".product-price, " +
            ".price"
        );


    const imageElement =
        card.querySelector(
            ".home-product-image, " +
            "img"
        );


    const price =
        Number(
            card.dataset.productPrice ||
            button.dataset.productPrice ||
            priceElement?.textContent
                ?.replace(/[₹,\s]/g, "") ||
            0
        );


    const image =
        card.dataset.productImage ||
        button.dataset.productImage ||
        imageElement?.getAttribute("src") ||
        "";


    const stock =
        Number(
            card.dataset.productStock ||
            button.dataset.productStock ||
            999999
        );


    return {

        id: String(id || ""),

        name: name,

        price: price,

        image: image,

        stock: stock

    };
}


/* =========================================================
   ADD TO CART
========================================================= */

function addToCart(button) {

    const product =
        getProductData(button);


    if (!product || !product.id) {

        showToast(
            "Unable to add product.",
            "error"
        );

        return;
    }


    if (
        Number.isFinite(product.stock) &&
        product.stock <= 0
    ) {

        showToast(
            "This product is out of stock.",
            "error"
        );

        return;
    }


    let cart = getCart();


    const existingIndex =
        cart.findIndex(
            item =>
                String(item.id) ===
                String(product.id)
        );


    if (existingIndex !== -1) {

        const existing =
            cart[existingIndex];

        const newQuantity =
            Number(existing.quantity || 1) + 1;


        if (
            Number.isFinite(product.stock) &&
            product.stock > 0 &&
            newQuantity > product.stock
        ) {

            showToast(
                "Maximum available stock reached.",
                "error"
            );

            return;
        }


        existing.quantity =
            newQuantity;

    } else {

        cart.push({

            id: product.id,

            name: product.name,

            price: Number(product.price) || 0,

            image: product.image || "",

            quantity: 1,

            stock: product.stock

        });
    }


    saveCart(cart);

    updateCartCount();

    showToast(
        product.name +
        " added to cart."
    );
}


/* =========================================================
   REMOVE FROM CART
========================================================= */

function removeFromCart(productId) {

    let cart = getCart();

    cart = cart.filter(
        item =>
            String(item.id) !==
            String(productId)
    );

    saveCart(cart);

    updateCartCount();

    if (
        typeof renderCart === "function"
    ) {
        renderCart();
    }
}


/* =========================================================
   CHANGE CART QUANTITY
========================================================= */

function changeCartQuantity(
    productId,
    change
) {

    const cart = getCart();

    const item =
        cart.find(
            product =>
                String(product.id) ===
                String(productId)
        );


    if (!item) {
        return;
    }


    const currentQuantity =
        Number(item.quantity || 1);


    const newQuantity =
        currentQuantity +
        Number(change);


    if (newQuantity <= 0) {

        removeFromCart(productId);

        return;
    }


    if (
        item.stock &&
        Number(item.stock) > 0 &&
        newQuantity > Number(item.stock)
    ) {

        showToast(
            "Maximum available stock reached.",
            "error"
        );

        return;
    }


    item.quantity =
        newQuantity;


    saveCart(cart);

    updateCartCount();


    if (
        typeof renderCart === "function"
    ) {
        renderCart();
    }
}


/* =========================================================
   CLEAR CART
========================================================= */

function clearCart() {

    saveCart([]);

    updateCartCount();


    if (
        typeof renderCart === "function"
    ) {
        renderCart();
    }

    showToast("Cart cleared.");
}


/* =========================================================
   WISHLIST TOGGLE
========================================================= */

function toggleWishlist(button) {

    const product =
        getProductData(button);


    if (!product || !product.id) {

        showToast(
            "Unable to update wishlist.",
            "error"
        );

        return;
    }


    let wishlist =
        getWishlist();


    const existingIndex =
        wishlist.findIndex(
            item =>
                String(item.id) ===
                String(product.id)
        );


    if (existingIndex !== -1) {

        wishlist.splice(
            existingIndex,
            1
        );

        saveWishlist(wishlist);

        updateWishlistCount();

        updateWishlistButton(
            button,
            false
        );

        showToast(
            "Removed from wishlist."
        );

    } else {

        wishlist.push({

            id: product.id,

            name: product.name,

            price: Number(product.price) || 0,

            image: product.image || "",

            stock: product.stock

        });

        saveWishlist(wishlist);

        updateWishlistCount();

        updateWishlistButton(
            button,
            true
        );

        showToast(
            "Added to wishlist."
        );
    }
}


/* =========================================================
   UPDATE WISHLIST BUTTON
========================================================= */

function updateWishlistButton(
    button,
    active
) {

    if (!button) {
        return;
    }


    button.classList.toggle(
        "active",
        active
    );


    const icon =
        button.querySelector("i");


    if (!icon) {
        return;
    }


    if (active) {

        icon.classList.remove(
            "fa-regular"
        );

        icon.classList.add(
            "fa-solid"
        );

    } else {

        icon.classList.remove(
            "fa-solid"
        );

        icon.classList.add(
            "fa-regular"
        );
    }
}


/* =========================================================
   RESTORE WISHLIST BUTTONS
========================================================= */

function restoreWishlistButtons() {

    const wishlist =
        getWishlist();


    const wishlistIds =
        new Set(
            wishlist.map(
                item =>
                    String(item.id)
            )
        );


    document
        .querySelectorAll(
            ".home-wishlist, " +
            ".wishlist-btn, " +
            ".shop-wishlist, " +
            "[data-wishlist]"
        )
        .forEach(button => {

            const product =
                getProductData(button);


            if (!product) {
                return;
            }


            updateWishlistButton(
                button,
                wishlistIds.has(
                    String(product.id)
                )
            );

        });
}


/* =========================================================
   REMOVE FROM WISHLIST
========================================================= */

function removeFromWishlist(
    productId
) {

    let wishlist =
        getWishlist();


    wishlist =
        wishlist.filter(
            item =>
                String(item.id) !==
                String(productId)
        );


    saveWishlist(wishlist);

    updateWishlistCount();

    restoreWishlistButtons();


    if (
        typeof renderWishlist === "function"
    ) {
        renderWishlist();
    }
}


/* =========================================================
   ADD WISHLIST PRODUCT TO CART
========================================================= */

function addWishlistToCart(
    productId
) {

    const wishlist =
        getWishlist();


    const product =
        wishlist.find(
            item =>
                String(item.id) ===
                String(productId)
        );


    if (!product) {

        showToast(
            "Product not found.",
            "error"
        );

        return;
    }


    let cart =
        getCart();


    const existing =
        cart.find(
            item =>
                String(item.id) ===
                String(product.id)
        );


    if (existing) {

        existing.quantity =
            Number(existing.quantity || 1) + 1;

    } else {

        cart.push({

            id: String(product.id),

            name: product.name,

            price: Number(product.price) || 0,

            image: product.image || "",

            quantity: 1,

            stock: product.stock

        });
    }


    saveCart(cart);

    updateCartCount();

    showToast(
        product.name +
        " added to cart."
    );
}


/* =========================================================
   CLEAR WISHLIST
========================================================= */

function clearWishlist() {

    saveWishlist([]);

    updateWishlistCount();

    restoreWishlistButtons();


    if (
        typeof renderWishlist === "function"
    ) {
        renderWishlist();
    }

    showToast(
        "Wishlist cleared."
    );
}


/* =========================================================
   FORMAT PRICE
========================================================= */

function formatPrice(value) {

    const number =
        Number(value) || 0;


    return number.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 0
        }
    );
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHTML(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* =========================================================
   SEARCH
========================================================= */

function searchProducts() {

    const input =
        document.getElementById(
            "searchInput"
        );


    if (!input) {
        return;
    }


    const query =
        input.value.trim();


    if (!query) {

        showToast(
            "Please enter a product name.",
            "error"
        );

        input.focus();

        return;
    }


    window.location.href =
        "/products?search=" +
        encodeURIComponent(query);
}


/* =========================================================
   OPEN CART
========================================================= */

function openCart() {

    window.location.href =
        "/cart/";
}


/* =========================================================
   SHOP NOW
========================================================= */

function shopNow() {

    const section =
        document.querySelector(
            ".home-products-section"
        );


    if (section) {

        section.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } else {

        window.location.href =
            "/products";
    }
}


/* =========================================================
   HOME PRODUCT CARD CLICK
========================================================= */

function setupHomeProductClicks() {

    document
        .querySelectorAll(
            ".home-product-card"
        )
        .forEach(card => {

            card.addEventListener(
                "click",
                function (event) {

                    const clickedButton =
                        event.target.closest(
                            "button, a"
                        );


                    if (clickedButton) {
                        return;
                    }


                    const productId =
                        this.dataset.productId;


                    if (!productId) {
                        return;
                    }


                    window.location.href =
                        "/product/" +
                        encodeURIComponent(
                            productId
                        );
                }
            );

        });
}


/* =========================================================
   IMAGE ERROR HANDLER
========================================================= */

function handleHomeImageError(
    image
) {

    if (!image) {
        return;
    }


    if (
        image.dataset.fallbackApplied ===
        "true"
    ) {
        return;
    }


    image.dataset.fallbackApplied =
        "true";


    image.src =
        "data:image/svg+xml," +
        encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg"
                 width="400"
                 height="300"
                 viewBox="0 0 400 300">

                <rect width="400"
                      height="300"
                      fill="#f5f5f5"/>

                <text x="200"
                      y="145"
                      text-anchor="middle"
                      font-family="Arial"
                      font-size="22"
                      fill="#999">
                    ShopEase
                </text>

                <text x="200"
                      y="175"
                      text-anchor="middle"
                      font-family="Arial"
                      font-size="14"
                      fill="#aaa">
                    Product Image
                </text>

            </svg>
        `);
}


/* =========================================================
   IMAGE EVENTS
========================================================= */

function setupProductImages() {

    document
        .querySelectorAll(
            ".home-product-image, " +
            ".product-card img, " +
            ".shop-product-card img"
        )
        .forEach(image => {

            image.addEventListener(
                "error",
                function () {

                    handleHomeImageError(
                        this
                    );

                }
            );

        });
}


/* =========================================================
   EVENT DELEGATION
========================================================= */

function setupGlobalClicks() {

    document.addEventListener(
        "click",
        function (event) {

            /* -----------------------------------------
               ADD TO CART
            ----------------------------------------- */

            const cartButton =
                event.target.closest(
                    ".home-add-cart, " +
                    ".add-to-cart, " +
                    ".add-cart-btn, " +
                    "[data-add-to-cart]"
                );


            if (cartButton) {

                event.preventDefault();

                event.stopPropagation();

                addToCart(cartButton);

                return;
            }


            /* -----------------------------------------
               WISHLIST
            ----------------------------------------- */

            const wishlistButton =
                event.target.closest(
                    ".home-wishlist, " +
                    ".wishlist-btn, " +
                    ".shop-wishlist, " +
                    "[data-wishlist]"
                );


            if (wishlistButton) {

                event.preventDefault();

                event.stopPropagation();

                toggleWishlist(
                    wishlistButton
                );

                return;
            }

        }
    );
}


/* =========================================================
   SEARCH EVENTS
========================================================= */

function setupSearch() {

    const input =
        document.getElementById(
            "searchInput"
        );


    const button =
        document.getElementById(
            "searchButton"
        );


    if (button) {

        button.addEventListener(
            "click",
            searchProducts
        );

    }


    if (input) {

        input.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    searchProducts();
                }

            }
        );

    }
}


/* =========================================================
   HERO BUTTON
========================================================= */

function setupHeroButton() {

    const button =
        document.getElementById(
            "heroShopButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        shopNow
    );
}


/* =========================================================
   CART PAGE SUPPORT
========================================================= */

function renderCart() {

    const container =
        document.getElementById(
            "cartItems"
        );


    if (!container) {
        return;
    }


    const cart =
        getCart();


    if (cart.length === 0) {

        container.innerHTML = `
            <div class="empty-cart">
                <i class="fa-solid fa-cart-shopping"></i>
                <h2>Your cart is empty</h2>
                <p>Add some products to your cart.</p>
            </div>
        `;

        updateCartSummary();

        return;
    }


    container.innerHTML =
        cart.map(item => {

            const quantity =
                Number(item.quantity || 1);


            const total =
                Number(item.price || 0) *
                quantity;


            return `
                <div class="cart-item"
                     data-product-id="${escapeHTML(item.id)}">

                    <img
                        src="${escapeHTML(item.image || "")}"
                        alt="${escapeHTML(item.name)}"
                        class="cart-item-image"
                    >

                    <div class="cart-item-info">

                        <h3>
                            ${escapeHTML(item.name)}
                        </h3>

                        <strong>
                            ₹${formatPrice(item.price)}
                        </strong>

                        <div class="cart-quantity">

                            <button
                                type="button"
                                onclick="changeCartQuantity('${escapeHTML(item.id)}', -1)">
                                −
                            </button>

                            <span>
                                ${quantity}
                            </span>

                            <button
                                type="button"
                                onclick="changeCartQuantity('${escapeHTML(item.id)}', 1)">
                                +
                            </button>

                        </div>

                    </div>

                    <div class="cart-item-total">

                        <strong>
                            ₹${formatPrice(total)}
                        </strong>

                        <button
                            type="button"
                            onclick="removeFromCart('${escapeHTML(item.id)}')">
                            Remove
                        </button>

                    </div>

                </div>
            `;

        }).join("");


    updateCartSummary();
}


/* =========================================================
   CART SUMMARY
========================================================= */

function updateCartSummary() {

    const cart =
        getCart();


    const subtotal =
        cart.reduce(
            (total, item) => {

                return total +
                    (
                        Number(item.price || 0) *
                        Number(item.quantity || 1)
                    );

            },
            0
        );


    const summary =
        document.getElementById(
            "cartSubtotal"
        );


    const total =
        document.getElementById(
            "cartTotal"
        );


    if (summary) {

        summary.textContent =
            "₹" + formatPrice(subtotal);
    }


    if (total) {

        total.textContent =
            "₹" + formatPrice(subtotal);
    }
}


/* =========================================================
   WISHLIST PAGE SUPPORT
========================================================= */

function renderWishlist() {

    const container =
        document.getElementById(
            "wishlistItems"
        );


    if (!container) {
        return;
    }


    const wishlist =
        getWishlist();


    if (wishlist.length === 0) {

        container.innerHTML = `
            <div class="empty-wishlist">

                <i class="fa-regular fa-heart"></i>

                <h2>Your wishlist is empty</h2>

                <p>
                    Save products you love here.
                </p>

            </div>
        `;

        return;
    }


    container.innerHTML =
        wishlist.map(item => {

            return `
                <div class="wishlist-item"
                     data-product-id="${escapeHTML(item.id)}">

                    <img
                        src="${escapeHTML(item.image || "")}"
                        alt="${escapeHTML(item.name)}"
                    >

                    <div class="wishlist-item-info">

                        <h3>
                            ${escapeHTML(item.name)}
                        </h3>

                        <strong>
                            ₹${formatPrice(item.price)}
                        </strong>

                        <div class="wishlist-actions">

                            <button
                                type="button"
                                onclick="addWishlistToCart('${escapeHTML(item.id)}')">

                                <i class="fa-solid fa-cart-plus"></i>
                                Add to Cart

                            </button>

                            <button
                                type="button"
                                onclick="removeFromWishlist('${escapeHTML(item.id)}')">

                                <i class="fa-solid fa-trash"></i>
                                Remove

                            </button>

                        </div>

                    </div>

                </div>
            `;

        }).join("");
}


/* =========================================================
   CLEANUP OLD SHARED STORAGE
========================================================= */

function removeOldSharedStorage() {

    /*
       These were the OLD shared keys.

       Removing them prevents an old user's
       cart/wishlist from appearing again.
    */

    try {

        localStorage.removeItem(
            "shopEaseCart"
        );

        localStorage.removeItem(
            "shopEaseWishlist"
        );

    } catch (error) {

        console.error(
            "Old storage cleanup error:",
            error
        );
    }
}


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "ShopEase User ID:",
            getShopEaseUserId()
        );

        console.log(
            "Cart Key:",
            getCartStorageKey()
        );

        console.log(
            "Wishlist Key:",
            getWishlistStorageKey()
        );


        /* Remove old shared keys */

        removeOldSharedStorage();


        /* Counts */

        updateCartCount();

        updateWishlistCount();


        /* Restore wishlist hearts */

        restoreWishlistButtons();


        /* Product images */

        setupProductImages();


        /* Product card click */

        setupHomeProductClicks();


        /* Global button clicks */

        setupGlobalClicks();


        /* Search */

        setupSearch();


        /* Hero */

        setupHeroButton();


        /* Cart page */

        renderCart();


        /* Wishlist page */

        renderWishlist();

    }
);