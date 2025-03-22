FROM nginx:alpine

ARG HTPASSWD

RUN echo "${HTPASSWD}" > /etc/nginx/conf.d/.htpasswd

COPY ./index.html /var/www/index.html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
