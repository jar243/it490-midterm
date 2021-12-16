<?php
include('protected/header.php');

$err_msg = null;

if (isset($_GET['id'])) {
    $movie_id = $_GET['id'];
    $res = $rc->get_movie($movie_id);
    if ($res->is_error) {
        $err_msg = $res->msg;
    } else {
        $movie = $res;
        $has_ratings = property_exists($movie, 'ratings') && count($movie->ratings) > 0;

        $able_to_rate = false;
        if (!is_null($active_user)) {
            $able_to_rate = true;
            $res = $rc->user_get_private($token);
            if ($res->is_error) {
                $err_msg = $res->msg;
            } else {
                foreach ($res->movie_ratings as $rating) {
                    if ($rating->movie->id == $movie->id) {
                        $able_to_rate = false;
                        break;
                    }
                }
            }
        }
    }
} else {
    $err_msg = 'No movie ID supplied';
}

if (is_null($err_msg) && isset($_POST['submit_review'])) {
    $stars = $_POST['stars'];
    $comment = $_POST['comment'];
    $res = $rc->submit_review($token, $movie->id, $stars, $comment);
    header("location: /movie.php?id=$movie->id");
    exit();
}

if (!is_null($err_msg)) : ?>
    <div class="alert alert-danger mx-auto" style="max-width:500px;"><?= $err_msg ?></div>
<?php
    include('protected/footer.php');
    exit();
endif;

?>

<div class="row g-3">
    <div class="col-md-4">
        <?php if ($is_logged_in) : ?>
            <a class="btn btn-success mb-2" style="width: 100%;" href="/create-watch-party.php?movie_id=<?= $movie->id ?>">Create Watch Party</a>
        <?php endif; ?>
        <div class="card mb-3">
            <img src="<?= $movie->poster_url ?>" class='card-img-top'>
            <div class="card-body">
                <h2 class="card-title"><?= $movie->title ?></h2>
                <h5 class="card-subtitle text-muted"><?= $movie->year ?></h5>
                <p class="card-text mt-2"><?= $movie->description ?></p>

            </div>
        </div>
    </div>
    <div class="col-md-8">
        <?php if (!$has_ratings) : ?>
            <div class="alert alert-info" style="width: 100%;">Movie has no ratings yet...</div>
        <?php endif; ?>

        <div class='row'>
            <?php if ($able_to_rate) : ?>
                <div class='col-lg-4'>
                    <div class="card mb-3 d-flex">
                        <div class="card-body">
                            <h4 class="card-title">Rate this Movie</h4>
                            <form method="POST">
                                <div class="form-group">
                                    <label class="form-label">Stars ⭐</label>
                                    <input class="form-control" type="number" name="stars" min="1" max="5" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Comment</label>
                                    <textarea class="form-control" rows="3" name="comment"></textarea>
                                </div>
                                <input class="btn btn-success ml-auto" type="submit" name="submit_review" value="Submit">
                            </form>
                        </div>
                    </div>
                </div>
            <?php
            endif;
            if ($has_ratings) : ?>
                <?php foreach ($movie->ratings as $rating) :
                    $star_string = str_repeat('⭐', $rating->stars);
                ?>
                    <div class="col-lg-4">
                        <div class="card mb-3">
                            <div class="card-body">
                                <a href="/profile.php?username=<?= $rating->user->username ?>">
                                    <h3 class="card-title"><?= $rating->user->display_name ?></h3>
                                </a>
                                <h3 class="card-subtitle text-muted"><?= $star_string ?></h3>
                                <?php if (strlen($rating->comment) > 0) : ?>
                                    <p class="card-text mt-2"><?= $rating->comment ?></p>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </div>
</div>


<?php include('protected/footer.php'); ?>