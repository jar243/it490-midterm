<?php

class Utils
{
  public static function display_movies(array $movies)
  {
    $MAX_LEN = 150;
?>
    <div class="row">
      <?php foreach ($movies as $movie) :
        $desc = (strlen($movie->description) > $MAX_LEN) ? substr($movie->description, 0, $MAX_LEN) . '...' : $movie->description;
      ?>
        <div class="col-md-3 mb-4">
          <div class="card">
            <a href="/movie.php?id=<?= $movie->id ?>"><img src="<?= $movie->poster_url ?>" class='card-img-top'></a>
            <div class="card-body">
              <a href="/movie.php?id=<?= $movie->id ?>">
                <h3 class="card-title"><?= $movie->title ?></h3>
              </a>
              <h5 class="card-subtitle text-muted"><?= $movie->year ?></h5>
              <p class="card-text mt-2"><?= $desc ?></p>
            </div>
          </div>
        </div>
      <?php endforeach; ?>
    </div>
<?php
  }
}
