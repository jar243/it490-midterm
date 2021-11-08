<?php
include('protected/header.php');
$err_msg = null;

if(!is_null(err_msg)) {
  echo ('<div class="alert alert-danger mx-auto" style="max-width:500px;">' . $err_msg . '</div>');
  include('protected/footer.php');
  exit();
}
?>
    <div class="row
        <?php
        foreach($mv as $res = $rc->get_trending_movies()){
          
       
         }

        ?>

        <img src="https://m.media-amazon.com/images/I/71zodDzU5hL._AC_SY679_.jpg" class="img-fluid" alt="Responsive image">
        <img src="https://cdn.shopify.com/s/files/1/1416/8662/products/dark_knight_rises_2012_quad_original_film_art_5000x.jpg?v=1607205303" class="col-sm-4 cenetr" alt="Responsive image">
        <img src="https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/mary-poppins-returns-1585876195.jpg?crop=0.9523809523809523xw:1xh;center,top&resize=480:*" class="col-sm-4 cenetr" alt="Responsive image">
    </div>
<?php
include('protected/footer.php');
?>
