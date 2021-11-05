<?php
include('protected/header.php');

if (isset($_GET['username'])) {
    $un = $_GET['username'];
    if (!is_null($active_user) && $active_user->username == $un) {
        header("location: my-profile.php");
        exit();
    }
} else {
    header("location: /");
    exit();
}

?>



<?php
include('protected/footer.php');
?>