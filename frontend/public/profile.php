<?php
include('protected/header.php');

$err_msg = null;
$friend_request_msg = null;

if (isset($_GET['username'])) {
    $un = $_GET['username'];
    $is_active_user = (!is_null($active_user) && $active_user->username == $un);
    if ($is_logged_in) {
        $active_user = $rc->user_get_private($token);
    }
    $res = $is_active_user ? $rc->user_get_private($token) : $rc->user_get_public($un);
    if ($res->is_error) {
        $err_msg = $res->msg;
    } else {
        $user = $res;
    }
} else {
    $err_msg = 'No user requested';
}

if (isset($_POST['request_friend'])) {
    if ($is_active_user) {
        $friend_request_msg = "Cannot friend request yourself";
    } else {
        $res = $rc->friend_request_send($token, $user->username);
        $friend_request_msg = ($res->is_error) ? $res->msg : "Friend request sent";
    }
}

if (isset($_POST['accept_friend']) || isset($_POST['decline_friend'])) {
    $frq_username = $_POST['frq_username'];
    $res = (isset($_POST['accept_friend'])) ?
        $rc->friend_request_accept($token, $frq_username) : $rc->friend_request_decline($token, $frq_username);
    if ($res->is_error) {
        $friend_request_msg = $res->msg;
    }
    header("Refresh:0");
    exit();
}

if (!is_null($err_msg)) : ?>
    <div class="alert alert-danger mx-auto" style="max-width:500px;"><?= $err_msg ?></div>
<?php
    include('protected/footer.php');
    exit();
endif; ?>

<div class="row g-3">
    <div class="col-md-4">

        <div class="card mb-3">
            <div class="card-body">
                <h1 class="card-title"><?= $user->display_name ?></h1>
                <h3 class="card-subtitle mb-2 text-muted">@<?= $user->username ?></h3>
            </div>
            <ul class="list-group list-group-flush">
                <li class="list-group-item"><?= count($user->movie_ratings) ?> Movie Ratings</li>
                <?php if (strlen($user->bio) > 0) : ?>
                    <li class="list-group-item"><?= $user->bio ?></li>
                <?php endif; ?>
            </ul>

            <?php if (!is_null($active_user)) : ?>
                <div class="card-body">
                    <?php if ($is_active_user) : ?>
                        <a href="/edit-profile.php" class="btn btn-primary">Edit Profile</a>
                        <?php else :
                        $user_is_friend = false;
                        foreach ($active_user->friends as $friend) {
                            if ($friend->username === $user->username) {
                                $user_is_friend = true;
                                break;
                            }
                        }
                        if (!$user_is_friend) : ?>
                            <form method="POST">
                                <input class="btn btn-success" type="submit" name="request_friend" value="Send Friend Request">
                            </form>
                        <?php endif; ?>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

        </div>

        <?php
        if (!is_null($friend_request_msg)) : ?>
            <div class='alert alert-info' style='width: 100%;'><?= $friend_request_msg ?></div>
        <?php endif;
        if ($is_active_user && count($user->friend_requests) > 0) : ?>
            <div class="card mb-3">
                <div class="card-header">
                    <h4 class='mb-0'>Friend Requests</h4>
                </div>
                <ul class="list-group list-group-flush">
                    <?php foreach ($user->friend_requests as $frq) : ?>
                        <li class="list-group-item d-flex align-items-center">
                            <a href="/profile.php?username=<?= $frq->username ?>" class='d-flex'>
                                <?= $frq->display_name ?> &nbsp;
                                <div class="text-muted">@<?= $frq->username ?></div>
                            </a>
                            <form method="POST" class="ml-auto">
                                <input type="hidden" name='frq_username' value="<?= $frq->username ?>">
                                <input class="btn btn-success" type="submit" name="accept_friend" value="Accept">
                                <input class="btn btn-danger" type="submit" name="decline_friend" value="Decline">
                            </form>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>

        <div class="card mb-3">
            <div class="card-header">
                <h4 class='mb-0'>Friends</h4>
            </div>
            <?php if (count($user->friends) > 0) : ?>
                <ul class="list-group list-group-flush">
                    <?php foreach ($user->friends as $friend) : ?>
                        <li class="list-group-item">
                            <a href="/profile.php?username=<?= $friend->username ?>" class='d-flex'>
                                <?= $friend->display_name ?> &nbsp;
                                <div class='text-muted'>@<?= $friend->username ?></div>
                            </a>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php else : ?>
                <div class="card-body">
                    <p class="card-text text-muted">No friends yet...</p>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <div class="col-md-8">
        <?php if (count($user->movie_ratings) === 0) : ?>
            <div class="alert alert-info" style="width: 100%;">User has not rated any movies yet...</div>
        <?php else : ?>
            <div class="row">
                <?php foreach ($user->movie_ratings as $rating) :
                    $star_string = str_repeat('⭐', $rating->stars);
                ?>
                    <div class="col-lg-4">
                        <div class="card mb-3">
                            <a href="/movie.php?id=<?= $rating->movie->id ?>">
                                <img src="<?= $rating->movie->poster_url ?>" class='card-img-top'>
                            </a>
                            <div class="card-body">
                                <h3 class="card-title"><?= $star_string ?></h3>
                                <h3 class="card-subtitle text-muted"><?= $rating->movie->title ?></h3>
                                <?php if (strlen($rating->comment) > 0) : ?>
                                    <p class="card-text mt-2"><?= $rating->comment ?></p>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
    </div>
<?php endif; ?>
</div>

<?php include('protected/footer.php'); ?>