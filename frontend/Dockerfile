# Dockerfile en ./frontend/
FROM node:20

WORKDIR /frontend

# Copiamos package.json y pnpm-lock.yaml al contenedor
COPY package.json pnpm-lock.yaml ./

# Instalamos pnpm globalmente
RUN npm install -g pnpm

# Instalamos dependencias con pnpm
RUN pnpm install

# Copiamos el resto del código
COPY . .

# Construimos la aplicación
RUN pnpm build

EXPOSE 4321

CMD ["pnpm", "preview"]
