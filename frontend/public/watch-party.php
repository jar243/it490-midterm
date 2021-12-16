<?php
include('protected/header.php');

if (is_null($active_user)) {
    header("location: /login.php");
    exit();
}

$err_msg = null;

if (isset($_GET['id'])) {
    $party_id = $_GET['id'];
    $res = $rc->get_watch_party($token, $party_id);
    if ($res->is_error) {
        $err_msg = $res->msg;
    } else {
        $watch_party = $res;
    }
} else {
    $err_msg = 'No movie id supplied';
}

$btn_err_msg = null;

if (!is_null($err_msg)) {
    // pass
} else if (isset($_POST['leave'])) {
    $res = $rc->leave_watch_party($token, $party_id);
    if ($res->is_error) {
        $btn_err_msg = $res->msg;
    } else {
        header("location: /profile.php?username=$active_user->username");
        exit();
    }
} else if (isset($_POST['play'])) {
    $res = $rc->play_watch_party($token, $party_id);
    if ($res->is_error) {
        $btn_err_msg = $res->msg;
    }
} else if (isset($_POST['pause'])) {
    $res = $rc->pause_watch_party($token, $party_id);
    if ($res->is_error) {
        $btn_err_msg = $res->msg;
    }
}

if (!is_null($err_msg)) : ?>
    <div class="alert alert-danger mx-auto" style="max-width:500px;"><?= $err_msg ?></div>
<?php elseif (isset($watch_party)) :
    $player_url = "https://www.youtube.com/embed/$watch_party->youtube_id?start=$watch_party->current_time";
    $status_change_msg = "Play";
    if ($watch_party->status === "playing") {
        $status_change_msg = "Pause";
        $player_url = $player_url . "&autoplay=1";
    }
?>
    <div class="row g-3">
        <div class="col-md-3">
            <div class="card mb-3">
                <div class="card-body">
                    <h2 class="card-title"><?= $watch_party->movie->title ?></h2>
                </div>
                <ul class="list-group list-group-flush">
                    <?php foreach ($watch_party->participants as $user) :
                        if ($user->username === $active_user->username) {
                            continue;
                        }
                    ?>
                        <li class="list-group-item">
                            <a href="/profile.php?username=<?= $user->username ?>" class='d-flex'>
                                <?= $user->display_name ?> &nbsp;
                                <div class='text-muted'>@<?= $user->username ?></div>
                            </a>
                        </li>
                    <?php endforeach; ?>
                </ul>
                <div class="card-body">
                    <form method="POST" class="d-flex">
                        <input class="btn btn-danger" type="submit" name="leave" value="Leave Party">
                    </form>
                </div>
            </div>
            <?php if (!is_null($btn_err_msg)) : ?>
                <div class="alert alert-danger mb-3" style="width: 100%;"><?= $btn_err_msg ?></div>
            <?php endif; ?>
        </div>
        <div class="col-md-9">
            <iframe style="width: 100%; height: 600px;" id="ytplayer" type="text/html" src="<?= $player_url ?>" frameborder="0">
            </iframe>
        </div>
    </div>
<?php
endif;
include('protected/footer.php');
