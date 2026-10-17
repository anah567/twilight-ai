
# Utilizamos Node.js para construir el frontend
FROM node:22-alpine AS build

# Definimos la carpeta de trabajo
WORKDIR /app

# Copiamos los archivos de dependencias
COPY package*.json ./

# Instalamos las dependencias
RUN npm ci

# Copiamos el código del frontend
COPY . .

# Configuramos la URL del backend para Vite
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Construimos la aplicación React
RUN npm run build

# Utilizamos Nginx para servir el frontend
FROM nginx:alpine

# Copiamos los archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Exponemos el puerto del frontend
EXPOSE 80

# Iniciamos Nginx
CMD ["nginx", "-g", "daemon off;"]
