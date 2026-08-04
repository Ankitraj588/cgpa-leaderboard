// ================= Flash Auto Hide (3 Seconds) =================
setTimeout(() => {
  document.querySelectorAll(".alert").forEach(alert => {
    alert.classList.remove("show");
    alert.classList.add("fade");
    setTimeout(() => alert.remove(), 500);
  });
}, 3000);


// ================= Signup Password Match =================
function validateSignup(){
  let pass = document.getElementById("password").value;
  let confirm = document.getElementById("confirm").value;
  let error = document.getElementById("error");

  if(pass !== confirm){
      error.style.display = "block";
      return false;
  }

  error.style.display = "none";
  return true;
}
