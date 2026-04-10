# Frontend Setup

This frontend uses relative routes (`/api/*`, `/auth/*`) and Next.js rewrites, so no backend IPs are hardcoded in components.

## Local Development

1. Create `Frontend/.env.local` from `Frontend/.env.local.example`.
2. Set `BACKEND_ORIGIN` to your backend URL.
3. Start the app:

```bash
npm install
npm run dev
```

Examples:

- `BACKEND_ORIGIN=http://localhost:8000` for local backend
- `BACKEND_ORIGIN=http://40.76.254.32:8000` for deployed backend

## Docker Compose

In `docker-compose.yml`, frontend uses:

- `BACKEND_ORIGIN=http://backend:8000`

This works because `backend` is the Docker service hostname on the compose network.
