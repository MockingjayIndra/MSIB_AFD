sudo docker run --rm \
    -v $(pwd)/letsencrypt:/etc/letsencrypt \
    -v $(pwd)/public:/var/www/html \
    certbot/certbot certonly --webroot \
    --webroot-path=/var/www/html \
    --agree-tos \
    --email gananamfedr@gmail.com \
    -d kelompok7.site -d www.kelompok7.site