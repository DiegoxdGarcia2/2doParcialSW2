FROM php:8.3-cli-alpine

RUN apk add --no-cache postgresql-dev libzip-dev git bash \
    && docker-php-ext-install pdo pdo_pgsql bcmath zip sockets

WORKDIR /var/www/html

COPY . .

EXPOSE 8001

CMD ["php", "-S", "0.0.0.0:8001", "-t", "public"]
