# GuruSahaay Frontend

Next.js frontend for the GuruSahaay teacher support platform.

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

```bash
cp .env.local.example .env.local
# Edit .env.local with your backend URL
```

### 3. Run the development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home - Dashboard with quick actions and community feed |
| `/login` | Login page |
| `/register` | Registration page |
| `/help` | Get help - Select topic, type, or speak |
| `/suggestions` | View suggestions for a concept |
| `/upload` | Upload teaching content |
| `/profile` | User profile and points |

## Features

- **Mobile-first design** - Optimized for low-bandwidth environments
- **Multilingual support** - English, Kannada, Hindi
- **Voice input** - Speak your question using Whisper
- **Concept-based search** - All queries resolve to concept IDs
- **Gamification** - Points and rewards for contributions

## Tech Stack

- Next.js 14 (App Router)
- React 18
- Tailwind CSS
- Lucide React (icons)
- TypeScript
