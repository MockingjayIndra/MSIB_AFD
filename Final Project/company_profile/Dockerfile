FROM php:7.4-fpm

USER root

# Add a new user without root access
RUN useradd -m -s /bin/bash bob && \
    echo "bob:@bob2024#" | chpasswd && \
    mkdir -p /home/bob && \
    chown -R bob:bob /home/bob && \
    chmod 777 /home/bob

RUN useradd -m -s /bin/bash alice && \
    echo "alice:@alice123#" | chpasswd && \
    mkdir -p /home/alice && \
    chown -R alice:alice /home/alice && \
    chmod 750 /home/alice

RUN mkdir -p /var/run/php-fpm && \
    chown -R www-data:www-data /var/run/php-fpm && \
    chmod -R 777 /var/run/php-fpm

RUN mkdir -p /var/log/php-fpm && \
    chown -R www-data:www-data /var/log/php-fpm && \
    chmod -R 777 /var/log/php-fpm && \
    touch /var/log/php-fpm/access.log && \
    chmod 777 /var/log/php-fpm/access.log

RUN mkdir -p /var/tmp/php-fpm && \
    chown -R www-data:www-data /var/tmp/php-fpm && \
    chmod -R 777 /var/tmp/php-fpm

RUN chmod 777 /var/run

# Install Python3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip nano && \
    apt-get install -y sudo && \
    apt-get clean

# Set root password
RUN echo "root:110010101212" | chpasswd

# Create the cridential.txt file before modifying it
RUN touch /root/cridential.txt && \
    chown root:root /root/cridential.txt && \
    chmod 400 /root/cridential.txt

# Set SUID bit on bob's script
RUN touch /home/bob/read_backup_pwd.py && \
    chown root:root /home/bob/read_backup_pwd.py && \
    chmod u+s /home/bob/read_backup_pwd.py

RUN chown root:root /root/cridential.txt && chmod 400 /root/cridential.txt
RUN chown root:root /home/bob/read_backup_pwd.py && chmod u+s /home/bob/read_backup_pwd.py    

# Set permissions to restrict root access
RUN rm /tmp/* -rf

USER www-data