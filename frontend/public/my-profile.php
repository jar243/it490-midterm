<?php
include('protected/header.php');

if (is_null($active_user)) {
    header("location: login.php");
    exit();
}
?>


<h1>Hello, <?php echo ($active_user->display_name) ?></h1>


<?php
include('protected/footer.php');
?>