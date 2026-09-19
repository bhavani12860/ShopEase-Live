document.addEventListener("DOMContentLoaded", function () {

    const addAddressBtn = document.getElementById("addAddressBtn");

    if (addAddressBtn) {

        addAddressBtn.addEventListener("click", function () {

            window.location.href = "/addresses";

        });

    }

});