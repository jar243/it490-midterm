<?php
include('protected/header.php');

$err_msg = null;

while (true) {
  if (!isset($_GET['username'])) {
    $err_msg = "No username provided";
    break;
  }
  $username = $_GET['username'];

  $res = $rc->user_get_public($username);
  if ($res->is_error) {
    $err_msg = $rc->msg;
    break;
  }
  $user = $res;

  if (count($user->favorites) == 0) {
    $err_msg = "$user->display_name has no favorite movies";
    break;
  }

  break;
}

if (!is_null($err_msg)) : ?>
  <div class="alert alert-danger mx-auto" style="max-width:500px;"><?= $err_msg ?></div>
<?php else : ?>
  <h1 class="my-4 text-center"><?= $user->display_name ?>'s Favorite Movies</h1>
  <?php foreach ($user->favorites as $movie) : ?>
    <div class="card mb-3 mx-auto" style="max-width: 500px;">
      <div class="row g-0">
        <div class="col-md-4">
          <img src="<?= $movie->poster_url ?>" class="img-fluid rounded-start">
        </div>
        <div class="col-md-8">
          <div class="card-body" style="height: 100%;">
            <a href="/movie.php?id=<?= $movie->id ?>">
              <h2 class="card-title align-middle"><?= $movie->title ?></h2>
            </a>
          </div>
        </div>
      </div>
    </div>
  <?php endforeach; ?>
<?php endif;
include('protected/footer.php');
