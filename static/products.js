/* =========================================================
   SHOPEASE PROFILE PAGE JS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       CART COUNT
    ===================================================== */

    updateCartCount();


    /* =====================================================
       EDIT PROFILE
    ===================================================== */

    const editButton =
        document.getElementById("editProfileBtn");

    const profileView =
        document.getElementById("profileView");

    const profileEditForm =
        document.getElementById("profileEditForm");

    const cancelEdit =
        document.getElementById("cancelEdit");

    const saveProfile =
        document.getElementById("saveProfile");


    if (editButton) {

        editButton.addEventListener("click", function () {

            profileView.style.display = "none";

            profileEditForm.style.display = "block";

            editButton.style.display = "none";

        });

    }


    /* =====================================================
       CANCEL EDIT
    ===================================================== */

    if (cancelEdit) {

        cancelEdit.addEventListener("click", function () {

            profileEditForm.style.display = "none";

            profileView.style.display = "grid";

            editButton.style.display = "block";

        });

    }


    /* =====================================================
       SAVE PROFILE
       Frontend session display update
    ===================================================== */

    if (saveProfile) {

        saveProfile.addEventListener("click", function () {

            const nameInput =
                document.getElementById("editName");

            const newName =
                nameInput.value.trim();


            if (!newName) {

                alert("Please enter your name.");

                nameInput.focus();

                return;

            }


            /*
             * Backend database update is not connected here.
             * This only updates the page display.
             */

            const detailValues =
                document.querySelectorAll(".detail-value");


            if (detailValues.length > 0) {

                detailValues[0].textContent =
                    newName;

            }


            const userName =
                document.querySelector(".user-info strong");


            if (userName) {

                userName.textContent =
                    newName;

            }


            profileEditForm.style.display =
                "none";

            profileView.style.display =
                "grid";

            editButton.style.display =
                "block";


            alert(
                "Profile updated on this page."
            );

        });

    }


    /* =====================================================
       SIDEBAR SECTION NAVIGATION
    ===================================================== */

    const sidebarLinks =
        document.querySelectorAll(
            ".sidebar-link[data-section]"
        );


    sidebarLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const sectionId =
                link.getAttribute("data-section");

            const section =
                document.getElementById(sectionId);


            if (section) {

                event.preventDefault();

                section.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }


            sidebarLinks.forEach(function (item) {

                item.classList.remove("active");

            });


            link.classList.add("active");

        });

    });


    /* =====================================================
       SEARCH
    ===================================================== */

    const searchInput =
        document.getElementById("profileSearch");


    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key !== "Enter") {
                    return;
                }


                const search =
                    searchInput.value.trim();


                if (!search) {

                    return;

                }


                window.location.href =
                    "/products?search=" +
                    encodeURIComponent(search);

            }
        );

    }


    /* =====================================================
       ADD ADDRESS
    ===================================================== */

    const addAddressButton =
        document.getElementById("addAddressBtn");


    if (addAddressButton) {

        addAddressButton.addEventListener(
            "click",
            function () {

                alert(
                    "Address management will be available here."
                );

            }
        );

    }

});


/* =========================================================
   CART COUNT FUNCTION
========================================================= */

function updateCartCount() {

    const cartCount =
        document.getElementById("cartCount");


    if (!cartCount) {
        return;
    }


    try {

        const cart =
            JSON.parse(
                localStorage.getItem("cart")
            ) || [];


        let totalQuantity = 0;


        cart.forEach(function (item) {

            const quantity =
                parseInt(
                    item.quantity,
                    10
                ) || 0;


            totalQuantity += quantity;

        });


        cartCount.textContent =
            totalQuantity;


    } catch (error) {

        console.error(
            "Unable to read cart:",
            error
        );

        cartCount.textContent =
            "0";

    }

}