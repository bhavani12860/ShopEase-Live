/* =========================================================
   SHOP EASE - ORDERS PAGE JAVASCRIPT
   ========================================================= */


/* =========================================================
   DOM READY
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeOrderButtons();

    initializeOrderForms();

});


/* =========================================================
   ORDER BUTTONS
   ========================================================= */

function initializeOrderButtons() {

    const buttons = document.querySelectorAll(
        ".btn"
    );

    buttons.forEach(function (button) {

        button.addEventListener(
            "mouseenter",
            function () {

                if (
                    !button.disabled &&
                    !button.classList.contains("return-status-btn") &&
                    !button.classList.contains("cancelled-btn")
                ) {

                    button.style.transform =
                        "translateY(-1px)";

                }

            }
        );


        button.addEventListener(
            "mouseleave",
            function () {

                button.style.transform = "";

            }
        );

    });

}


/* =========================================================
   CANCEL / RETURN FORMS
   ========================================================= */

function initializeOrderForms() {

    const forms = document.querySelectorAll(
        ".buttons form"
    );


    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                /*
                 * HTML onsubmit confirmation already
                 * exists in orders.html.
                 *
                 * This JS only prevents double-clicks.
                 */

                const button =
                    form.querySelector(
                        "button[type='submit']"
                    );


                if (!button) {
                    return;
                }


                /*
                 * If browser confirmation is cancelled,
                 * submit event will not continue.
                 */

                setTimeout(
                    function () {

                        button.disabled = true;

                        const originalHTML =
                            button.innerHTML;


                        button.innerHTML =
                            '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';


                        /*
                         * Store original HTML.
                         */

                        button.dataset.originalHtml =
                            originalHTML;

                    },
                    10
                );

            }
        );

    });

}


/* =========================================================
   PREVENT DOUBLE CLICK
   ========================================================= */

function preventDoubleClick(button) {

    if (!button) {
        return;
    }

    if (button.dataset.processing === "true") {
        return false;
    }

    button.dataset.processing = "true";

    button.disabled = true;

    return true;

}


/* =========================================================
   CONFIRM CANCEL
   ========================================================= */

function confirmCancelOrder() {

    return confirm(
        "Are you sure you want to cancel this order?"
    );

}


/* =========================================================
   CONFIRM RETURN
   ========================================================= */

function confirmReturnOrder() {

    return confirm(
        "Do you want to request a return for this order?"
    );

}


/* =========================================================
   PAGE VISIBILITY
   ========================================================= */

document.addEventListener(
    "visibilitychange",
    function () {

        /*
         * Nothing special required here.
         * Kept ready for future order tracking.
         */

    }
);