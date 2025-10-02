
# Django Crypto Investments Dashboard
A simple Django app to track crypto holdings with live USD prices, totals, and charts — built with **Django**.

## Preview
![Dashboard](dashboard.png)
> **Live (Codespaces Preview):**  
> https://ubiquitous-tribble-v6759qjvxx46hxqv4-8000.app.github.dev/dashboard/  
> ⚠️ Codespaces URLs change when the workspace restarts. If the link breaks, restart the server and set port 8000 to **Public** (see below).

Tutorial followed: https://www.youtube.com/watch?v=6gh9nypmrbg

##  Features
- CRUD for investments (Create, Read, Update, Delete)
- **Live prices** and **24h % change** via CoinGecko (with caching)
- Per-row **value** = quantity × price
- KPIs (total records, total quantity, portfolio USD value)
- Charts (Chart.js): allocation by USD value (doughnut) & quantity by coin (bar)
- Clean, business-style UI (responsive table, messages, buttons)
