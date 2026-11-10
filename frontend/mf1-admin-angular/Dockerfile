FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY dist/mf1-admin-angular/browser/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["sh", "-c", "sed -i 's/8080/'\"${PORT:-8080}\"'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]

