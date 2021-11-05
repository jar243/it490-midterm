<?php
include('protected/header.php');

if (is_null($token)) {
  header("location: .");
  exit();
}

setcookie('token', 'null', 1);
$rc->token_delete($token);

header("location: .");
exit();

include('protected/footer.php');
