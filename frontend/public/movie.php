<?php
include('protected/header.php');

$err_msg = null;

while (true) {
    if (!isset($_GET['id'])) {
        $err_msg = 'No movie ID supplied';
        break;
    }
    $movie_id = $_GET['id'];

    $res = $rc->get_movie($movie_id);
    if ($res->is_error) {
        $err_msg = $res->msg;
        break;
    }
    $movie = $res;
    $has_ratings = property_exists($movie, 'ratings') && count($movie->ratings) > 0;

    $able_to_rate = false;
    if (!is_null($active_user)) {
        $able_to_rate = true;
        $res = $rc->user_get_private($token);
        if ($res->is_error) {
            $err_msg = $res->msg;
            break;
        }
        foreach ($res->movie_ratings as $rating) {
            if ($rating->movie->id == $movie->id) {
                $able_to_rate = false;
                break;
            }
        }
    }

    if (isset($_POST['submit_review'])) {
        if (!$able_to_rate) {
            $err_msg = "You have already rated this movie";
            break;
        }
        $stars = $_POST['stars'];
        $comment = $_POST['comment'];
        $res = $rc->submit_review($token, $movie->id, $stars, $comment);
        if ($res->is_error) {
            $err_msg = $res->msg;
            break;
        }
        header("location: /movie.php?id=$movie->id");
        exit();
    } elseif (isset($_POST['favorite'])) {
        if (!$is_logged_in) {
            $err_msg = "You must be logged in to favorite";
            break;
        }
        $res = $rc->favorite_movie($token, $movie->id);
        if ($res->is_error) {
            $err_msg = $res->msg;
            break;
        }
        header("location: /movie.php?id=$movie->id");
        exit();
    } elseif (isset($_POST['unfavorite'])) {
        if (!$is_logged_in) {
            $err_msg = "You must be logged in to unfavorite";
            break;
        }
        $res = $rc->unfavorite_movie($token, $movie->id);
        if ($res->is_error) {
            $err_msg = $res->msg;
            break;
        }
        header("location: /movie.php?id=$movie->id");
        exit();
    }

    $is_favorited = false;
    if (!is_null($active_user)) {
        $res = $rc->user_get_private($token);
        if ($res->is_error) {
            $err_msg = $res->msg;
            break;
        }
        $active_user = $res;
        foreach ($active_user->favorites as $fav_movie) {
            if ($fav_movie->id === $movie->id) {
                $is_favorited = true;
                break;
            }
        }
    }

    break;
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
            <form method="POST" class="mb-2">
                <?php if ($is_favorited) : ?>
                    <input class="btn btn-warning" style="width: 100%;" type="submit" name="unfavorite" value="Unfavorite">
                <?php else : ?>
                    <input class="btn btn-outline-warning" style="width: 100%;" type="submit" name="favorite" value="Favorite">
                <?php endif; ?>
            </form>
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