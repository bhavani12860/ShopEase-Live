/* =====================================================
   SHOP EASE - CHECKOUT JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    console.log("ShopEase Checkout Loaded");


    /* =================================================
       PHONE VALIDATION
    ================================================= */

    const phoneInput =
        document.getElementById("phone");


    if (phoneInput) {

        phoneInput.addEventListener(
            "input",
            function () {

                this.value =
                    this.value.replace(
                        /[^0-9]/g,
                        ""
                    );

            }
        );

    }



    /* =================================================
       PINCODE VALIDATION
    ================================================= */

    const pincodeInput =
        document.getElementById("pincode");


    if (pincodeInput) {

        pincodeInput.addEventListener(
            "input",
            function () {

                this.value =
                    this.value.replace(
                        /[^0-9]/g,
                        ""
                    );

            }
        );

    }



    /* =================================================
       ADDRESS FORM VALIDATION
    ================================================= */

    const checkoutForm =
        document.getElementById("checkoutForm");


    if (checkoutForm) {

        checkoutForm.addEventListener(
            "submit",
            function (event) {


                const phone =
                    phoneInput
                        ? phoneInput.value.trim()
                        : "";


                const pincode =
                    pincodeInput
                        ? pincodeInput.value.trim()
                        : "";


                if (!/^[0-9]{10}$/.test(phone)) {

                    event.preventDefault();

                    alert(
                        "Please enter a valid 10-digit mobile number."
                    );

                    phoneInput.focus();

                    return;

                }


                if (!/^[0-9]{6}$/.test(pincode)) {

                    event.preventDefault();

                    alert(
                        "Please enter a valid 6-digit pincode."
                    );

                    pincodeInput.focus();

                    return;

                }


                console.log(
                    "Saving delivery address..."
                );

            }
        );

    }

});