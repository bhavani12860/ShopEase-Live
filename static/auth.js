function validateRegister() {

    const password =
        document.getElementById("password").value;

    const confirmPassword =
        document.getElementById("confirm_password").value;


    if (password.length < 6) {

        alert("Password must contain at least 6 characters.");

        return false;
    }


    if (password !== confirmPassword) {

        alert("Passwords do not match.");

        return false;
    }


    return true;
}
function togglePassword(inputId, button) {

    const input = document.getElementById(inputId);
    const icon = button.querySelector("span");

    if (input.type === "password") {

        input.type = "text";
        icon.textContent = "🙈";

    } else {

        input.type = "password";
        icon.textContent = "👁";

    }
}

/* =====================================================
   PASSWORD SHOW / HIDE
===================================================== */

function togglePassword(inputId, icon) {

    const input = document.getElementById(inputId);

    if (!input) {
        return;
    }

    if (input.type === "password") {

        input.type = "text";

        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");

    } else {

        input.type = "password";

        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");

    }
}