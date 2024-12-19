/*=============== SHOW HIDDEN - PASSWORD ===============*/
const showHiddenPass = (loginPass, loginEye) => {
    const input = document.getElementById(loginPass),
          iconEye = document.getElementById(loginEye);
 
    iconEye.addEventListener('click', () => {
       // Change password to text
       if (input.type === 'password') {
          // Switch to text
          input.type = 'text';
 
          // Icon change
          iconEye.classList.add('ri-eye-line');
          iconEye.classList.remove('ri-eye-off-line');
       } else {
          // Change back to password
          input.type = 'password';
 
          // Icon change
          iconEye.classList.remove('ri-eye-line');
          iconEye.classList.add('ri-eye-off-line');
       }
    });
 };
 
 // Gọi hàm với id chính xác
 showHiddenPass('password', 'login-eye');
 