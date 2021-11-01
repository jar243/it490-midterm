<?php
    
    if ( isset( $_POST['signup'] ) ) {
      
      $username = $_POST['username'];
      $email = $_POST['email'];
      $password = $_POST['password'];
      $password2 = $_POST['password2'];

	$_SESSION['username'] = $_POST['username'];
	//$_SESSION['email'] = $_POST['email'];      

      if ( $password == $password2 ) {

      
	$response = signup($email, $username, $password, $password2);
          if($response->status == 300){
		$_SESSION["user"] = $response->data;
		header ("refresh: 1 ; url = index.php");
	  }
          else{
            var_export($response);
          }
      }
	else
		echo "Passwords must be the same.";
    }


?>

<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
        crossorigin="anonymous"></script>


</head>

<body class="bg-secondary p-2">
    <nav class="navbar navbar-dark bg-dark mb-3">
        <div class="container">
            <div class="navbar-brand">IT490 Testing</div>
        </div>
    </nav>

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
                  <input
                    class="form-check-input me-2"
                    type="checkbox"
                    value=""
                    id="form2Example3cg"
                  />
                  <label class="form-check-label" for="form2Example3g">
                    I agree all statements in <a href="#!" class="text-body"><u>Terms of service</u></a>
                  </label>
                </div>

                <div class="d-flex justify-content-center">
		<a <input class="btn btn-success btn-block btn-lg gradient-custom-4 text-body"href="Login.html">Submit</a>
                </div>

                <p class="text-center text-muted mt-5 mb-0">Have already an account? <a href="Login.html" class="fw-bold text-body"><u>Login here</u></a></p>

              </form>
        </div>
    </div>

</body>

</html>