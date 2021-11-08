<?php
ob_start();
require('protected/RabbitClient.php');
require('protected/Utils.php');

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
$is_logged_in = !is_null($active_user);
?>

<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Movies App</title>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
</head>

<body class="bg-secondary">

  <nav class="navbar navbar-dark bg-dark navbar-expand-lg mb-3">
    <div class='container-fluid' style="max-width: 1500px;">

      <div class="navbar-brand">Movies App</div>

      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarToggleTarget">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarToggleTarget">
        <ul class="navbar-nav m-1 mr-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
        </ul>

        <form class="d-flex m-1" action="/search-movies.php" autocomplete="on">
          <input class="form-control" type="search" name="query" placeholder="Search Movies" required>
          <button class="btn btn-outline-light ml-2" type="submit">Search</button>
        </form>

        <div class="navbar-nav">
          <?php if (is_null($active_user)) : ?>
            <a class="btn btn-primary m-1" href="./login.php">Login</a>
            <a class="btn btn-success m-1" href="./registration.php">Register</a>
          <?php else : ?>
            <a class="btn btn-primary m-1" href="./profile.php?username=<?= $active_user->username ?>">My Profile</a>
            <a class="btn btn-secondary m-1" href="./logout.php">Logout</a>
          <?php endif; ?>
        </div>
      </div>

    </div>
  </nav>

  <div class='container-fluid' style="max-width: 1500px;">