# Шаг 1: Сборка фронтенда
FROM node:18.17.0 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build && \
    ls -la /app/build  # Проверка

# Шаг 2: Запуск Nginx
FROM nginx:alpine
RUN mkdir -p /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html
COPY --from=builder /app/build /usr/share/nginx/html 
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]