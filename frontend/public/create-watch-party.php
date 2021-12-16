<?php
include('protected/header.php');

if (is_null($active_user)) {
    header("location: /login.php");
    exit();
}

$err_msg = null;

while (true) {
    if (!isset($_GET['movie_id'])) {
        header("location: /");
        exit();
    }

    $res = $rc->user_get_private($token);
    if ($res->is_error) {
        $err_msg = $res->msg;
        break;
    }
    $active_user = $res;

    if (!isset($_POST['create'])) {
        break;
    }

    if (empty($_POST['participants'])) {
        $err_msg = 'No participants provided';
        break;
    }
    $participants = $_POST['participants'];

    $res = $rc->get_movie($movie_id);
    if ($res->is_error) {
        $err_msg = $res->msg;
        break;
    }
    $movie = $res;

    if (is_null($movie->youtube_id)) {
        $res = $rc->get_youtube_movie($movie->title);
        if ($res->is_error) {
            $err_msg = $res->msg;
            break;
        }
        $movie->youtube_id = $res->youtube_id;
        $movie->youtube_length = $res->youtube_length;
    }

    $res = $rc->schedule_watch_party(
        $token,
        $movie_id,
        $movie->youtube_length,
        $movie->youtube_id,
        $participants
    );
    if ($res->is_error) {
        $err_msg = $res->msg;
        break;
    }
    $watch_party = $res;

    header("location: /watch-party.php?id=$watch_party->id");
    exit();
}
?>

<div class="card mx-auto" style="max-width: 500px;">
    <div class="card-body">
        <?php if (!is_null($err_msg)) : ?>
            <div class="alert alert-danger"><?= $err_msg ?></div>
        <?php endif; ?>
        <h4 class="card-title">Create Watch Party</h4>
        <form method="POST">
            <?php foreach ($active_user->friends as $friend) : ?>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="participants[]" value="<?= $friend->username ?>">
                    <label class="form-check-label"><?= $friend->display_name ?></label>
                </div>
            <?php endforeach; ?>
            <input class="btn btn-success" type="submit" name="create" value="Create">
        </form>
    </div>
</div>


<?php include('protected/footer.php'); ?>