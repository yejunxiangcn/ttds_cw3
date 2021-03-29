//Try enter an invalid email

function validateEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
}

const form = document.querySelector('form');

form.addEventListener('submit', function (e) {
  e.preventDefault();
  const email = this.querySelector('input[type="email"]');

  if (validateEmail(email.value)) {
    console.log('validate email');
    email.parentNode.classList.remove('error');
  } else {
    email.parentNode.classList.add('error');
  }
  this.reset();
});