FROM node:20-alpine

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install --omit=dev || npm install --production

COPY . .
RUN npx tsc || true

EXPOSE 8002

CMD ["node", "src/main.ts"]
