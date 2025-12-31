# Trader Alpha WebApp

Next.js frontend for the Trader Alpha stock scanner.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local`:
```bash
cp .env.local.example .env.local
# Edit with your Supabase credentials
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Routes

- `/` - Redirects to `/lists`
- `/lists` - View all stock lists and scores
- `/lists/[listName]` - Stocks in specific list (e.g., `/lists/SP500`)
- `/stock/[symbol]` - Stock detail page with chart (e.g., `/stock/AAPL`)

## Environment Variables

```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_API_URL=https://api.trader-alpha.com
```

## Deploy

Deploy to Vercel:

```bash
vercel
```

Or connect your GitHub repo to Vercel for automatic deploys.