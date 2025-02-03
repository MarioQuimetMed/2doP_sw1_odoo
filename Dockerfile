FROM odoo:17

# Copiar el archivo requirements.txt al contenedor
COPY requirements.txt /tmp/requirements.txt

# Instalar las dependencias
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar el resto de los archivos necesarios
COPY ./odoo-addons /mnt/extra-addons