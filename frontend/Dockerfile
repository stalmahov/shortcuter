FROM node:24-alpine AS dependencies

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

FROM dependencies AS build
ENV VITE_API_URL=""
RUN npm run build

FROM nginx:stable-alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

FROM dependencies AS development

ENV HOST=0.0.0.0
EXPOSE 5173

CMD ["npm", "run", "dev"]
