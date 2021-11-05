<?php
ob_start();
require('protected/RabbitClient.php');
$rc = new RabbitClient('127.0.0.1', 5672, 'guest', 'guest');
$token = isset($_COOKIE['token']) ? $_COOKIE['token'] : null;
$active_user = null;
if (!is_null($token)) {
  $res = $rc->token_get_user($token);
  if ($res->is_error === true) {
    $token = null;
    setcookie('token', 'null', 1);
  } else {
    $active_user = (object) [
      'username' => $res->username,
      'display_name' => $res->display_name
    ];
  }
}
?>

<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
</head>

<body class="bg-secondary">

  <nav class="navbar navbar-dark bg-dark navbar-expand-lg mb-3">

    <div class="navbar-brand">Movies App</div>

    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarToggleTarget">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarToggleTarget">
      <ul class="navbar-nav mr-auto">
        <li class="nav-item">
          <a class="nav-link" href=".">Home</a>
        </li>
      </ul>
      <div class="btn-group navbar-nav ml-auto">
        <?php
        if (is_null($active_user)) {
          echo ('
                <a class="btn btn-primary" href="./login.php">Login</a>
                <a class="btn btn-success" href="./registration.php">Register</a>
            ');
        } else {
          echo ('
                <a class="btn btn-primary" href="./my-profile.php">' . $active_user->display_name . '</a>
                <a class="btn btn-secondary" href="./logout.php">Logout</a>
            ');
        }
        ?>
      </div>
    </div>

  </nav>