<?php
ob_start();
require('protected/RabbitClient.php');
$rc = new RabbitClient('127.0.0.1', 5672, 'guest', 'guest');
$token = isset($_COOKIE['token']) ? $_COOKIE['token'] : null;
$active_user = null;
if (!is_null($token)) {
  $active_user = $rc->token_get_user($token);
  if (is_null($active_user)) {
    $token = null;
    setcookie('token', 'null', 1);
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
        <li class="nav-item">
          <a class="nav-link" href="./login.php">Login</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="./registration.php">Registration</a>
        </li>
      </ul>
    </div>

  </nav>