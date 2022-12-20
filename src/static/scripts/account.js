window.addEventListener('DOMContentLoaded', (event) => {
  const emailButton = document.getElementById("change-email");
  document.addEventListener("mouseup", hideEmailForm);
  // emailButton.addEventListener("mouseup", showEmailForm);
});

function showEmailForm() {
  console.log("Change email button clicked!");
  const formDiv = document.getElementById('email-form');
  const hidden = formDiv.classList.contains('d-none');
  if(hidden) {
    formDiv.classList.remove('d-none');
  }
}

function hideEmailForm(event) {
  const formDiv = document.getElementById('email-form');
  const hidden = formDiv.classList.contains('d-none');
  if(!hidden) {
    if(!formDiv.contains(event.target)) {
      formDiv.classList.add('d-none');
    }
  }
}
