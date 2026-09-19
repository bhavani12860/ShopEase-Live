/* =====================================================
   SHOP EASE
   PAYMENT PAGE JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    console.log("ShopEase Payment JS Loaded");


    /* =================================================
       ELEMENTS
    ================================================= */

    const paymentForm =
        document.getElementById("paymentForm");


    const paymentOptions =
        document.querySelectorAll(
            ".payment-option"
        );


    const codRadio =
        document.getElementById("cod");


    const upiRadio =
        document.getElementById("upi");


    const cardRadio =
        document.getElementById("card");


    const upiDetails =
        document.getElementById("upiDetails");


    const cardDetails =
        document.getElementById("cardDetails");


    const upiInput =
        document.getElementById("upi_id");


    const cardNumberInput =
        document.getElementById("card_number");


    const expiryInput =
        document.getElementById("expiry");


    const cvvInput =
        document.getElementById("cvv");


    const payViaUpiBtn =
        document.getElementById("payViaUpiBtn");


    const upiAppButtons =
        document.querySelectorAll(
            ".upi-app-btn"
        );


    /* =================================================
       SHOW / HIDE PAYMENT DETAILS
    ================================================= */

    function updatePaymentMethod() {


        /* Hide UPI */

        if (upiDetails) {

            upiDetails.style.display =
                "none";

        }


        /* Hide Card */

        if (cardDetails) {

            cardDetails.style.display =
                "none";

        }


        /* Remove selected class */

        paymentOptions.forEach(
            function (option) {

                option.classList.remove(
                    "selected"
                );

            }
        );


        /* =============================================
           UPI
        ============================================== */

        if (
            upiRadio &&
            upiRadio.checked
        ) {

            if (upiDetails) {

                upiDetails.style.display =
                    "block";

            }


            const upiOption =
                document.querySelector(
                    'label[for="upi"]'
                );


            if (upiOption) {

                upiOption.classList.add(
                    "selected"
                );

            }

        }


        /* =============================================
           CARD
        ============================================== */

        else if (
            cardRadio &&
            cardRadio.checked
        ) {

            if (cardDetails) {

                cardDetails.style.display =
                    "block";

            }


            const cardOption =
                document.querySelector(
                    'label[for="card"]'
                );


            if (cardOption) {

                cardOption.classList.add(
                    "selected"
                );

            }

        }


        /* =============================================
           COD
        ============================================== */

        else if (
            codRadio &&
            codRadio.checked
        ) {

            const codOption =
                document.querySelector(
                    'label[for="cod"]'
                );


            if (codOption) {

                codOption.classList.add(
                    "selected"
                );

            }

        }

    }



    /* =================================================
       RADIO EVENTS
    ================================================= */

    if (codRadio) {

        codRadio.addEventListener(
            "change",
            updatePaymentMethod
        );

    }


    if (upiRadio) {

        upiRadio.addEventListener(
            "change",
            updatePaymentMethod
        );

    }


    if (cardRadio) {

        cardRadio.addEventListener(
            "change",
            updatePaymentMethod
        );

    }



    /* =================================================
       CLICK ENTIRE PAYMENT OPTION
    ================================================= */

    paymentOptions.forEach(
        function (option) {

            option.addEventListener(
                "click",
                function () {

                    const radio =
                        option.querySelector(
                            'input[type="radio"]'
                        );


                    if (radio) {

                        radio.checked = true;

                        updatePaymentMethod();

                    }

                }
            );

        }
    );



    /* =================================================
       UPI INPUT FORMAT
    ================================================= */

    if (upiInput) {

        upiInput.addEventListener(
            "input",
            function () {

                this.value =
                    this.value
                        .replace(/\s/g, "")
                        .toLowerCase();

            }
        );

    }



    /* =================================================
       OPEN UPI PAYMENT APP
    ================================================= */

    function openUpiPayment(selectedApp) {


        const amount =
            payViaUpiBtn
                ? Number(
                    payViaUpiBtn.dataset.amount || 0
                )
                : 0;


        if (!amount || amount <= 0) {

            alert(
                "Invalid payment amount."
            );

            return;

        }


        /*
           DEMO MERCHANT DETAILS

           Change pa later real
           merchant/payment gateway details.
        */

        const merchantUpiId =
            "shopease@upi";


        const merchantName =
            "ShopEase";


        const transactionNote =
            "ShopEase Order Payment";


        /*
           CREATE UNIQUE TRANSACTION ID
        */

        const transactionId =
            "SE" +
            Date.now();


        /*
           STANDARD UPI PAYMENT URI
        */

        const upiUrl =
            "upi://pay" +
            "?pa=" +
            encodeURIComponent(
                merchantUpiId
            ) +
            "&pn=" +
            encodeURIComponent(
                merchantName
            ) +
            "&tr=" +
            encodeURIComponent(
                transactionId
            ) +
            "&tn=" +
            encodeURIComponent(
                transactionNote
            ) +
            "&am=" +
            encodeURIComponent(
                amount.toFixed(2)
            ) +
            "&cu=INR";


        console.log(
            "Selected UPI App:",
            selectedApp
        );


        console.log(
            "Opening UPI:",
            upiUrl
        );


        /*
           Desktop detection
        */

        const isMobile =
            /Android|iPhone|iPad|iPod/i.test(
                navigator.userAgent
            );


        if (!isMobile) {

            alert(
                "UPI app payment must be tested on an Android or mobile device. On this computer, PhonePe or Google Pay cannot be opened automatically."
            );

            return;

        }


        /*
           OPEN MOBILE UPI APP
        */

        window.location.href =
            upiUrl;


        /*
           Demo:
           App success callback browser ki automatic ga
           guarantee kaadu.

           Real project lo payment gateway
           verification use cheyyali.
        */

    }



    /* =================================================
       UPI APP BUTTONS
    ================================================= */

    upiAppButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();


                    const app =
                        button.dataset.upiApp ||
                        "upi";


                    openUpiPayment(app);

                }
            );

        }
    );



    /* =================================================
       PAY VIA ENTERED UPI ID
    ================================================= */

    if (payViaUpiBtn) {

        payViaUpiBtn.addEventListener(
            "click",
            function () {


                const upi =
                    upiInput
                        ? upiInput.value.trim()
                        : "";


                /*
                   If UPI ID entered,
                   validate it first
                */

                if (upi) {


                    const upiPattern =
                        /^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+$/;


                    if (
                        !upiPattern.test(upi)
                    ) {

                        alert(
                            "Please enter a valid UPI ID. Example: name@upi"
                        );


                        upiInput.focus();

                        return;

                    }

                }


                openUpiPayment(
                    "upi"
                );

            }
        );

    }



    /* =================================================
       CARD NUMBER FORMAT
    ================================================= */

    if (cardNumberInput) {

        cardNumberInput.addEventListener(
            "input",
            function () {


                let value =
                    this.value.replace(
                        /[^0-9]/g,
                        ""
                    );


                value =
                    value.substring(
                        0,
                        16
                    );


                const formatted =
                    value.match(
                        /.{1,4}/g
                    );


                this.value =
                    formatted
                        ? formatted.join(" ")
                        : "";

            }
        );

    }



    /* =================================================
       EXPIRY DATE FORMAT
    ================================================= */

    if (expiryInput) {

        expiryInput.addEventListener(
            "input",
            function () {


                let value =
                    this.value.replace(
                        /[^0-9]/g,
                        ""
                    );


                value =
                    value.substring(
                        0,
                        4
                    );


                if (value.length > 2) {

                    value =
                        value.substring(0, 2)
                        +
                        "/"
                        +
                        value.substring(2);

                }


                this.value = value;

            }
        );

    }



    /* =================================================
       CVV ONLY NUMBERS
    ================================================= */

    if (cvvInput) {

        cvvInput.addEventListener(
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
       FORM SUBMIT VALIDATION
    ================================================= */

    if (paymentForm) {

        paymentForm.addEventListener(
            "submit",
            function (event) {


                const selectedMethod =
                    document.querySelector(
                        'input[name="payment_method"]:checked'
                    );


                if (!selectedMethod) {

                    event.preventDefault();


                    alert(
                        "Please select a payment method."
                    );

                    return;

                }



                /* =====================================
                   UPI
                ====================================== */

                if (
                    selectedMethod.value === "UPI"
                ) {


                    event.preventDefault();


                    alert(
                        "Please complete the UPI payment using the UPI payment button."
                    );

                    return;

                }



                /* =====================================
                   CARD
                ====================================== */

                if (
                    selectedMethod.value === "CARD"
                ) {


                    const card =
                        cardNumberInput
                            ? cardNumberInput.value
                                .replace(
                                    /\s/g,
                                    ""
                                )
                            : "";


                    const expiry =
                        expiryInput
                            ? expiryInput.value.trim()
                            : "";


                    const cvv =
                        cvvInput
                            ? cvvInput.value.trim()
                            : "";


                    if (
                        !/^[0-9]{16}$/.test(
                            card
                        )
                    ) {

                        event.preventDefault();


                        alert(
                            "Please enter a valid 16-digit card number."
                        );


                        cardNumberInput.focus();

                        return;

                    }


                    if (
                        !/^(0[1-9]|1[0-2])\/[0-9]{2}$/
                            .test(expiry)
                    ) {

                        event.preventDefault();


                        alert(
                            "Please enter expiry date in MM/YY format."
                        );


                        expiryInput.focus();

                        return;

                    }


                    if (
                        !/^[0-9]{3}$/.test(cvv)
                    ) {

                        event.preventDefault();


                        alert(
                            "Please enter a valid 3-digit CVV."
                        );


                        cvvInput.focus();

                        return;

                    }

                }



                /* =====================================
                   COD
                ====================================== */

                if (
                    selectedMethod.value === "COD"
                ) {

                    console.log(
                        "COD selected. Placing order."
                    );

                }

            }
        );

    }



    /* =================================================
       INITIAL STATE
    ================================================= */

    updatePaymentMethod();


});