# IT490 Frontend

## Requirements
1. [Apache Web Server](https://ubuntu.com/tutorials/install-and-configure-apache)
2. [Composer (PHP package manager)](https://getcomposer.org/)
3. [PHP 8](https://www.php.net/downloads)

## Composer Setup
1. Ensure the PHP extension "sockets" is enabled in php.ini
2. Navigate to frontend directory
3. Run `composer install`
4. Configure frontend either via the system's ENV variables or a .env file in the root frontend directory

## Environment Variables
- IT490_BROKER_HOST (default: 127.0.0.1)
- IT490_BROKER_PORT (default: 5672)
- IT490_BROKER_USER (default: guest)
- IT490_BROKER_PASSWORD (default: guest)

## Apache Setup
1. Take note of the /path/to/frontend/public/
2. Open Apache's `httpd.conf` file
3. Change `DocumentRoot` setting to public directory path
4. Change `<Directory "/var/www">` to public directory path
5. Save the `httpd.conf` file
6. Restart Apache2 via `sudo service apache2 restart`  
7. Apache should now be hosting the frontend successfully 