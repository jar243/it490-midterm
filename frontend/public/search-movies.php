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
<?php else :
    Utils::display_movies($movies);
endif;
include('protected/footer.php');
?>