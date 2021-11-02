<?php
//--Check if form was posted to this file
if (isset($_POST['login'])) {

    $email_username = $_POST['email_username'];
    $password = $_POST['password'];

    if (strpos($email_username, '@') !== false) {
        //--User entered an email
        $_SESSION['email'] =  $_POST['email_username'];
    } else {
        //--User entered an username
        $_SESSION['username'] =  $_POST['email_username'];
    }

    $response = login($email_username, $password);
    if ($response->status == 200) {
        $_SESSION["user"] = $response->data;
        header("location: index.php");
    } else {
        var_export($response);
    }
}

include('protected/header.php');
?>

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

<?php include('protected/footer.php'); ?>