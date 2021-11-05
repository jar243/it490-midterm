<?php
include('protected/header.php');

if (!is_null($active_user)) {
    header("location: my-profile.php");
    exit();
}

$err_msg = null;

if (isset($_POST['registration'])) {
    $username = $_POST['username'];
    $display_name = $_POST['display_name'];
    $email = $_POST['email'];
    $password = $_POST['password'];
    $password_check = $_POST['password_check'];

    if ($password == $password_check) {
        $res = $rc->user_create($username, $display_name, $email, $password);
        if ($res->is_error === true) {
            $err_msg = $res->msg;
        } else {
            setcookie('token', $res->token);
            header("location: index.php");
            exit();
        }
    } else {
        $err_msg = 'Passwords must match';
    }
}
?>

<div class="card mx-auto" style="max-width: 500px;">
    <div class="card-body">
        <?php
        if (!is_null($err_msg)) {
            echo ('<div class="alert alert-danger">' . $err_msg . '</div>');
        }
        ?>
        <h4 class="card-title">Registration</h4>
        <form method='POST'>
            <div class="form-group">
                <label>Username</label><br>
                <input class="form-control" type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Display Name</label><br>
                <input class="form-control" type="text" name="display_name" required>
            </div>
            <div class="form-group">
                <label>Email</label><br>
                <input class="form-control" type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Password</label><br>
                <input class="form-control" type="password" name="password" required>
            </div>
            <div class="form-group">
                <label>Password Check</label><br>
                <input class="form-control" type="password" name="password_check" required>
            </div>
            <input class="btn btn-success" type="submit" name="registration" value="Register">
        </form>
    </div>
    <div class="card-footer text-muted">
        Have an account already? <a href="login.php">Login here</a>
    </div>
</div>

<?php include('protected/footer.php'); ?>