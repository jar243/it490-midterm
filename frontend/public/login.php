<?php
include('protected/header.php');

if (!is_null($active_user)) {
    header("location: /");
    exit();
}

$err_msg = null;

if (isset($_POST['login'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];

    $res = $rc->token_generate($username, $password);
    if ($res->is_error === true) {
        $err_msg = $res->msg;
    } else {
        setcookie('token', $res->token);
        header("location: /");
        exit();
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
        <h4 class="card-title">Login</h4>
        <form method="POST">
            <div class="form-group">
                <label>Username</label><br>
                <input class="form-control" type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label><br>
                <input class="form-control" type="password" name="password" required>
            </div>
            <input class="btn btn-dark" type="submit" name="login" value="Login">
        </form>
    </div>
    <div class="card-footer text-muted">
        Don't Have an account? <a href="registration.php">Sign up here</a>
    </div>
</div>

<?php include('protected/footer.php'); ?>