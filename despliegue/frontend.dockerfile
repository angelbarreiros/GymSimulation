# Usa la imagen oficial de Nginx, que es liviana
FROM nginx:alpine

# Copia los archivos de tu aplicación frontend al directorio de Nginx para servir contenido estático
COPY ./frontend /usr/share/nginx/html
COPY  /despliegue/configs/nginx.conf  /etc/nginx/nginx.conf
# Exponer el puerto 80 (HTTP)
EXPOSE 80

# El contenedor arrancará con Nginx ejecutándose en modo foreground (modo por defecto de la imagen Nginx)
CMD ["nginx", "-g", "daemon off;"]
