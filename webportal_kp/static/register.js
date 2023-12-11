const pw_toggle = document.getElementById("register-toggle-pw");
const pw_toggle2 = document.getElementById("register-toggle-pw2");
const pw_inputs = document.querySelectorAll("[type='password']");

const togglePWVisibility = () => {
    pw_toggle.classList.toggle("bi-eye-slash-fill")
    pw_toggle.classList.toggle("bi-eye-fill")
    pw_toggle2.classList.toggle("bi-eye-slash-fill")
    pw_toggle2.classList.toggle("bi-eye-fill")

    pw_inputs.forEach((elem) => {
        if(elem.type === "password") {
            elem.type = "text";
        }else{
            elem.type = "password";
        }
    })
}

const compare_pws = () => {
    if(pw_inputs[0].value !== pw_inputs[1].value) {
        pw_inputs[0].setCustomValidity("Passwörter sind nicht gleich");
    }else{
        pw_inputs[0].setCustomValidity("");
    }
}


pw_toggle.addEventListener("click", togglePWVisibility)
pw_toggle2.addEventListener("click", togglePWVisibility)

pw_inputs.forEach((elem) => {
    elem.addEventListener("input", compare_pws)
})