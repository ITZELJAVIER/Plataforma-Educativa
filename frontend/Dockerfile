# Frontend React + TypeScript + Vite — infraestructura de la tarea 1.2.
#
# Los manifiestos, `index.html` y `src` ya están presentes. La imagen no ha
# sido construida ni ejecutada en este entorno: Docker no está disponible.
# No se incorpora nginx ni otro servidor: se usa Vite preview, tecnología autorizada.
# No se fijan broker MQTT, tópicos, QoS, retención ni topología.
FROM node:26-alpine

WORKDIR /app

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
RUN npm run build

EXPOSE 5173

CMD ["sh", "-c", "npm run preview -- --host 0.0.0.0 --port ${FRONTEND_PORT:-5173}"]
