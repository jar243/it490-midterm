<?php
include('protected/header.php');

if (isset($_POST['signup'])) {
  
  $username = $_POST['username'];
  $email = $_POST['email'];
  $password = $_POST['password'];
  $password2 = $_POST['password2'];

  $_SESSION['username'] = $_POST['username'];
  
  if ($password == $password2) {
     $res = $rc->token_generate($email, $username, $password, $password2);
     if ($res->is_error === true) {
        $err_msg = $res->msg;
      }else {
        setcookie('token', $res->token);
        header("location: index.php");
        exit();
    }
}

?>
<div class="card mx-auto" style="max-width: 500px;">
  <div class="card-body">
    <h4 class="card-title">Registration</h4>
    <form>

      <div class="form-outline mb-4">
        <input type="text" class="form-control form-control-lg" id="validationDefault01" required>

        <label class="form-label" for="form3Example1cg">Your Name</label>
      </div>

      <div class="form-outline mb-4">
        <input type="email" id="form3Example3cg" class="form-control form-control-lg" />
        <label class="form-label" for="form3Example3cg">Your Email</label>
      </div>

      <div class="form-outline mb-4">
        <input type="password" id="form3Example4cg" class="form-control form-control-lg" />
        <label class="form-label" for="form3Example4cg">Password</label>
      </div>

      <div class="form-outline mb-4">
        <input type="password" id="form3Example4cdg" class="form-control form-control-lg" />
        <label class="form-label" for="form3Example4cdg">Repeat your password</label>
      </div>

      <div class="form-check d-flex justify-content-left mb-5">
        <input class="form-check-input me-2" type="checkbox" value="" id="form2Example3cg" />
        <label class="form-check-label" for="form2Example3g">
          I agree all statements in <a href="#!" class="text-body"><u>Terms of service</u></a>
        </label>
      </div>

      <div class="d-flex justify-content-center">
        <a <input class="btn btn-success btn-block btn-lg gradient-custom-4 text-body" href="Login.html">Submit</a>
      </div>

      <p class="text-center text-muted mt-5 mb-0">Have already an account? <a href="Login.html" class="fw-bold text-body"><u>Login here</u></a></p>

    </form>
  </div>
</div>

<?php include('protected/footer.php'); ?>
