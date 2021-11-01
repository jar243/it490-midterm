<?php
        //--Check if form was posted to this file
        if ( isset( $_POST['login'] ) ) {

                $email_username = $_POST['email_username'];
                $password = $_POST['password'];

                if ( strpos( $email_username, '@' ) !== false ) {
                        //--User entered an email
                        $_SESSION['email']=  $_POST['email_username'];
                }
                else{
                        //--User entered an username
                        $_SESSION['username']=  $_POST['email_username'];

               }

                $response = login($email_username, $password);
                if($response->status == 200){
                        $_SESSION["user"] = $response->data;
                        header("location: index.php");
                }
                else{
                        var_export($response);
                }
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
            <h4 class="card-title">Login</h4>
            <form method="POST">
                <div class="form-group">
                    <label>Email/Username</label><br>
                    <input class="form-control" type="text" name="email_username" required>
                </div>

                <div class="form-group">
                    <label>Password</label><br>
                    <input class="form-control" type="password" name="password" required>
                </div>

                <div class="form-group">
                    <input class="btn btn-dark" type="submit" name="login" value="Login">
                </div>
                <br>

                Don't Have an account? <br><a href="registration.php">Signup Here</a><br>
                <br>

            </form>
        </div>
    </div>

</body>

</html>
