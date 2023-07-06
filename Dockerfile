FROM node:16 as build-stage
WORKDIR /app
COPY package*.json ./

RUN npm i -g pnpm
RUN pnpm install
COPY ./ .
RUN pnpm build

FROM nginx as production-stage
RUN mkdir /app
COPY --from=build-stage /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf