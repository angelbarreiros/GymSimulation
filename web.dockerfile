FROM httpd:2.4

# Copiar el archivo index.html al contenedor

COPY index.html /usr/local/apache2/htdocs/index.html
COPY . /usr/local/apache2/htdocs/

# Exponer puerto 80
EXPOSE 80

# Ejecutar el servicio Apache
CMD ["apachectl", "-DFOREGROUND"]
