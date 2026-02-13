const togglePassword = document.querySelector("#togglePassword");
const passwordField = document.querySelector('input[name="password"]');

togglePassword.addEventListener("click", function () {
  const type =
    passwordField.getAttribute("type") === "password" ? "text" : "password";
  passwordField.setAttribute("type", type);
  this.classList.toggle("bi-eye");
  this.classList.toggle("bi-eye-slash");
});
