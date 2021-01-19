FROM node:14.15-slim as build
WORKDIR /app
COPY src/index.html /app/


FROM nginx:1.19.6
COPY --from=build /app/ /usr/share/nginx/html
COPY conf/default.conf /etc/nginx/conf.d/default.conf

RUN touch /var/run/nginx.pid && \
    mkdir -p /var/cache/nginx/client_temp && \
    chown nginx:nginx /var/run/nginx.pid && \
    chown -R nginx:nginx /etc/nginx &&\
    chown -R nginx:nginx /var/cache

USER nginx:nginx
