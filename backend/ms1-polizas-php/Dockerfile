FROM php:8.3-cli-alpine

RUN apk add --no-cache linux-headers postgresql-dev libzip-dev git bash curl \
    && docker-php-ext-install pdo pdo_pgsql bcmath zip \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

WORKDIR /var/www/html

COPY . .

RUN composer install --no-dev --optimize-autoloader --no-interaction 2>/dev/null || true

EXPOSE 8001

CMD ["sh", "-c", "php -S 0.0.0.0:${PORT:-8001} -t public"]
