# Atelier Demo Bot (Discord) 🤖

A live, multi-feature Discord bot built as a portfolio piece — every slash
command actually works. It demonstrates the core of what a custom bot client
pays for:

- **Slash commands** (the modern Discord standard)
- **Live API integration** — crypto prices (CoinGecko) and weather (Open-Meteo), *no API keys needed*
- **Automation / scheduling** — set-a-reminder
- **Interactive buttons**, clean embeds, and proper error handling

Built with [discord.py](https://discordpy.readthedocs.io/) v2 (async).

---

## Commands

| Command | What it does | Example |
|---|---|---|
| `/help` | Show the menu (with buttons) | `/help` |
| `/price` | Live crypto price + 24h change | `/price coin:btc` |
| `/weather` | Current conditions | `/weather city:dubai` |
| `/remind` | Get pinged later | `/remind minutes:10 message:stretch` |

---

## 1. Create your bot (5 min)

1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)**
2. **New Application** → name it → **Create**
3. Left sidebar → **Bot** → **Add Bot** → **Reset Token** → copy the **token**
4. Still on the Bot page, scroll to **Privileged Gateway Intents** — you can
   leave them all **off** (this bot uses slash commands, so it needs none)

### Invite it to a server
1. Left sidebar → **OAuth2 → URL Generator**
2. Scopes: tick **`bot`** and **`applications.commands`**
3. Bot Permissions: tick **Send Messages** and **Embed Links**
4. Copy the generated URL at the bottom, open it, and add the bot to your server

---

## 2. Run it locally (to test)

```bash
pip install -r requirements.txt
export DISCORD_TOKEN="paste-your-token-here"   # Windows: set DISCORD_TOKEN=...
python bot.py
```

In your server, type `/` and your commands appear. Try `/help`.

> First sync can take up to a minute for slash commands to show globally.

---

## 3. Deploy it 24/7 for free (Railway)

A bot has to stay running, so it needs a host. **Railway** deploys straight
from GitHub:

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → sign in with GitHub
3. **New Project → Deploy from GitHub repo** → pick this repo
4. Open the service → **Variables** → add `DISCORD_TOKEN` = your token
5. Railway auto-detects the `Procfile` and runs the worker

Your bot is now live around the clock. (Render and Fly.io also work via the
same `Procfile`.)

---

## Notes

- The token is read from the `DISCORD_TOKEN` environment variable and is never
  committed — `.env` is gitignored. **If a token ever leaks, reset it in the
  Developer Portal immediately.**
- Both APIs used are free and keyless — nothing to pay for or rotate.
- Easy extensions: auto-moderation, welcome messages, role management,
  scheduled broadcasts, database storage, CRM/Sheets integration.
