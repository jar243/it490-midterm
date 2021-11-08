<?php
include('protected/header.php');

$err_msg = null;

if (isset($_GET['query'])) {
  $query = $_GET['query'];
  $res = $rc->search_movies($query);
  if ($res->is_error === true) {
    $err_msg = $res->msg;
  } else {
    $movies = $res->movies;
    if (count($movies) === 0) {
      $err_msg = "No movies found...";
    }
  }
} else {
  $err_msg = "No search query supplied";
}

if (!is_null($err_msg)) : ?>
  <div class="alert alert-danger mx-auto" style="max-width:500px;"><?= $err_msg ?></div>
<?php
  include('protected/footer.php');
  exit();
endif; ?>

<div class="row">
  <?php foreach ($movies as $movie) : ?>
    <div class="col-md-3 mb-3">
      <div class="card">
        <a href="/movie.php?id=<?= $movie->id ?>"><img src="<?= $movie->poster_path ?>" class='card-img-top'></a>
        <div class="card-body">
          <a href="/movie.php?id=<?= $movie->id ?>">
            <h3 class="card-title"><?= $movie->title ?></h3>
          </a>
          <h5 class="card-subtitle text-muted"><?= $movie->year ?></h5>
          <p class="card-text mt-2"><?= $movie->description ?></p>
        </div>
      </div>
    </div>
  <?php endforeach; ?>
</div>

<?php include('protected/footer.php'); ?>