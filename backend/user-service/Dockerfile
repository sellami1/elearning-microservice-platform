FROM node:20-bookworm-slim

WORKDIR /app

ENV NODE_ENV=dev \
	USER_BACKEND_ENV=dev

COPY package*.json ./

RUN npm ci --omit=dev && npm cache clean --force

COPY . .

RUN chown -R node:node /app

USER node

EXPOSE 8002

CMD ["node", "src/server.js"]
