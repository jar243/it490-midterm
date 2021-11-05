<?php
include('protected/header.php');

if (is_null($active_user)) {
  header("location: /login.php");
  exit();
}

$err_msg = null;

if (isset($_POST['profile'])) {
  $display_name = $_POST['display_name'];
  $bio = $_POST['bio'];
  $res = $rc->user_update($token, $display_name, $bio);
  if ($res->is_error === true) {
    $err_msg = $res->msg;
  } else {
    header("location: /profile.php?username=" . $active_user->username);
    exit();
  }
}

$res = $rc->user_get_private($token);
if ($res->is_error === true) {
  $err_msg = $res->msg;
} else {
  $user = $res;
}

?>

<div class="card mx-auto" style="max-width: 500px;">
  <div class="card-body">
    <?php
    if (!is_null($err_msg)) {
      echo ('<div class="alert alert-danger">' . $err_msg . '</div>');
    }
    ?>
    <h4 class="card-title">Profile</h4>
    <form method='POST'>
      <div class="form-group">
        <label class="form-label">Display Name</label>
        <input class="form-control" type="text" name="display_name" value=<?php echo ('"' . $user->display_name . '"'); ?> required>
      </div>
      <div class="form-group">
        <label class="form-label">Bio</label>
        <textarea class="form-control" rows="3" name="bio"><?php echo ($user->bio); ?></textarea>
      </div>
      <input class="btn btn-success" type="submit" name="profile" value="Update">
    </form>
  </div>
</div>

<?php include('protected/footer.php'); ?>