<?php
include('protected/header.php');

$err_msg = null;

$res = $rc->get_popular_movies();
if ($res->is_error === true) {
  $err_msg = $res->msg;
} else {
  $movies = $res->movies;
  if (count($movies) === 0) {
    $err_msg = "No movies found...";
  }
}

if (!is_null($err_msg)) : ?>
  <div class="alert alert-danger mx-auto" style="max-width:500px;"><?= $err_msg ?></div>
<?php
  include('protected/footer.php');
  exit();
endif; ?>

<h1 class="mb-4">Popular Movies this Week...</h1>

<?php
Utils::display_movies($movies);
include('protected/footer.php');
?>