# Indraprastha — Weekly Meal Planner

A beautifully designed, offline-first Indian meal planning web app. Plan weekly meals, generate grocery lists, and track daily essentials — all in one place, with no account or internet connection required.

## Features

- **Weekly Planner** — Plan 4 weeks of meals across Breakfast, Lunch, Dinner, Snacks, and more
- **Grocery List** — Organize items by category with quantity, unit, and brand tracking
- **Meal-wise Summary** — Auto-generated ingredient overview from your weekly plan
- **Daily Essentials** — Persistent pantry staples organized by category
- **Buying List** — View and print/copy only the items marked for purchase
- **Religious Calendar** — Tag festival dates and plan meals accordingly
- **Customise Options** — Add or remove items from any meal dropdown
- **Bilingual** — English and Marathi language support

## Tech Stack

Pure HTML + CSS + JavaScript — no frameworks, no build tools, no dependencies.  
Data is stored in your browser's `localStorage`.

## Run Locally

No installation needed. Just serve the file with Python or Node:

**Python:**
```bash
python -m http.server 8000 --bind 0.0.0.0
```

**Node.js:**
```bash
npx serve -l 8000
```

Then open `http://localhost:8000` in your browser.

## Share on Local WiFi

After starting the server, find your machine's IP:

```bash
# Windows
ipconfig

# Mac / Linux
ifconfig
```

Share `http://<YOUR_IP>:8000` with anyone on the same WiFi network. No internet required.

> Each device stores its own data independently via `localStorage`.

## Data & Privacy

All data stays on your device. Nothing is sent to any server.  
Clearing browser storage will erase saved meal plans.
