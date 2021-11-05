<?php
include('protected/header.php');

$err_msg = null;

if (isset($_GET['username'])) {
    $un = $_GET['username'];
    $is_active_user = (!is_null($active_user) && $active_user->username == $un);
    $res = $is_active_user ? $rc->user_get_private($token) : $rc->user_get_public($un);
    if ($res->is_error) {
        $err_msg = $res->msg;
    } else {
        $user = $res;
    }
} else {
    $err_msg = 'No user requested';
}

if (!is_null($err_msg)) {
    echo ('<div class="alert alert-danger mx-auto" style="max-width:500px;">' . $err_msg . '</div>');
    include('protected/footer.php');
    exit();
}

?>

<div class="row g-3">
    <div class="col-md-4">

        <div class="card mb-3">
            <div class="card-body">
                <h1 class="card-title"><?php echo ($user->display_name) ?></h1>
                <h3 class="card-subtitle mb-2 text-muted">@<?php echo ($user->username) ?></h3>
            </div>
            <ul class="list-group list-group-flush">
                <li class="list-group-item">10 Friends</li>
                <li class="list-group-item"><?php echo (count($user->movie_ratings)) ?> Movie Ratings</li>
                <?php
                if (strlen($user->bio) > 0) {
                    echo ('<li class="list-group-item">' . $user->bio . '</li>');
                }
                ?>
            </ul>
            <?php
            if ($is_logged_in) {
                echo ('<div class="card-body">');
                if ($is_active_user) {
                    echo ('<a href="/edit-profile.php" class="btn btn-primary">Edit Profile</a>');
                } else {
                    // TODO add friendship buttons here
                }
                echo ('</div>');
            }
            ?>
        </div>


    </div>
    <div class="col-md-8">
        <?php
        if (count($user->movie_ratings) === 0) {
            echo ('<div class="alert alert-info" style="width: 100%;">User has not rated any movies yet...</div>');
        } else {
            echo ('<div class="row row-cols-1 row-cols-md-2 g-4">');
            foreach ($user->movie_ratings as $rating) {
                echo ('<div class="col"> <div class="card">');
                echo ('<img src="' . $rating->movie->poster_url . '" class="card-img-top">');
                echo ('<div class="card-body">');
                echo ('<h3 class="card-title">' . $rating->stars . '/5</h3>');
                echo ('<h5 class="card-subtitle text-muted">' . $rating->movie->title . '</h5>');
                if (strlen($rating->comment) > 0) {
                    echo ('<p class="card-text mt-2">' . $rating->comment . '</p>');
                }
                echo ('</div>');
                echo ('</div> </div>');
            }
            echo ("</div>");
        }
        ?>
    </div>
</div>

<?php
include('protected/footer.php');
?>