"""
Atelier Demo Bot (Discord) — a multi-feature bot built as a live portfolio piece.

Showcases the core skills a custom-bot client cares about:
  • Slash commands (the modern Discord standard)
  • Live third-party API integration (crypto prices, weather) — no API keys required
  • Automation / scheduling (set-a-reminder)
  • Interactive buttons, clean embeds, and proper error handling

Built with discord.py v2 (async).
Author: berrdz
"""

import asyncio
import logging
import os

import discord
import httpx
from discord import app_commands

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# The token is read from an environment variable so it's never hard-coded.
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")

HTTP_TIMEOUT = httpx.Timeout(10.0)
ACCENT = 0x1E4D3B  # pine green, to match the Atelier brand

# Syncing to a specific server makes slash commands appear INSTANTLY.
# (Global sync — leaving this as None — can take up to an hour to propagate.)
GUILD_ID = 1521497081880252516

WEATHER_CODES = {
    0: "Clear sky ☀️", 1: "Mainly clear 🌤️", 2: "Partly cloudy ⛅",
    3: "Overcast ☁️", 45: "Fog 🌫️", 48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌦️", 53: "Drizzle 🌦️", 55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️", 63: "Rain 🌧️", 65: "Heavy rain ⛈️",
    71: "Slight snow 🌨️", 73: "Snow 🌨️", 75: "Heavy snow ❄️",
    80: "Rain showers 🌦️", 81: "Rain showers 🌧️", 82: "Violent showers ⛈️",
    95: "Thunderstorm ⛈️", 96: "Thunderstorm + hail ⛈️", 99: "Thunderstorm + hail ⛈️",
}


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------
class DemoBot(discord.Client):
    def __init__(self) -> None:
        # Slash commands don't need the privileged message-content intent.
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        # Sync slash commands. If a GUILD_ID is set, copy the commands to that
        # server and sync there — they appear instantly. Otherwise sync globally
        # (which can take up to an hour to show up the first time).
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info("Slash commands synced to guild %s.", GUILD_ID)
        else:
            await self.tree.sync()
            logger.info("Slash commands synced globally.")


client = DemoBot()


@client.event
async def on_ready() -> None:
    logger.info("Logged in as %s — bot is running.", client.user)
    await client.change_presence(
        activity=discord.Game(name="/help — live demo bot")
    )


# ---------------------------------------------------------------------------
# Interactive help (buttons)
# ---------------------------------------------------------------------------
class HelpView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=120)

    @discord.ui.button(label="Crypto price", emoji="💰", style=discord.ButtonStyle.secondary)
    async def price_tip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "💰 Use `/price coin:btc` for a live price.", ephemeral=True
        )

    @discord.ui.button(label="Weather", emoji="🌦️", style=discord.ButtonStyle.secondary)
    async def weather_tip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🌦️ Use `/weather city:dubai` for current conditions.", ephemeral=True
        )

    @discord.ui.button(label="Reminder", emoji="⏰", style=discord.ButtonStyle.secondary)
    async def remind_tip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "⏰ Use `/remind minutes:10 message:stretch` to be pinged later.",
            ephemeral=True,
        )


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------
@client.tree.command(name="help", description="Show what this bot can do")
async def help_command(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        title="👋 Atelier Demo Bot",
        description=(
            "A live demo — every command actually works. A small showcase of what "
            "a custom Discord bot can do: pull live data, stay interactive, and run "
            "automations.\n\n"
            "**Commands**\n"
            "💰 `/price coin:btc` — live crypto price\n"
            "🌦️ `/weather city:dubai` — current conditions\n"
            "⏰ `/remind minutes:10 message:stretch` — get pinged later"
        ),
        color=ACCENT,
    )
    await interaction.response.send_message(embed=embed, view=HelpView())


@client.tree.command(name="price", description="Get a live crypto price")
@app_commands.describe(coin="Coin symbol or name, e.g. btc or ethereum")
async def price(interaction: discord.Interaction, coin: str) -> None:
    await interaction.response.defer()
    query = coin.strip().lower()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as http:
            search = await http.get(
                "https://api.coingecko.com/api/v3/search", params={"query": query}
            )
            search.raise_for_status()
            coins = search.json().get("coins", [])
            if not coins:
                await interaction.followup.send(
                    f"Couldn't find a coin matching “{coin}”. Try the full name?"
                )
                return

            c = coins[0]
            data = await http.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": c["id"], "vs_currencies": "usd", "include_24hr_change": "true"},
            )
            data.raise_for_status()
            info = data.json()[c["id"]]

        usd = info["usd"]
        change = info.get("usd_24h_change", 0) or 0
        arrow = "🟢 ▲" if change >= 0 else "🔴 ▼"
        price_str = f"${usd:,.2f}" if usd >= 1 else f"${usd:,.6f}"

        embed = discord.Embed(
            title=f"{c['name']} ({c['symbol'].upper()})", color=ACCENT
        )
        embed.add_field(name="Price", value=f"**{price_str}**", inline=True)
        embed.add_field(name="24h", value=f"{arrow} {abs(change):.2f}%", inline=True)
        await interaction.followup.send(embed=embed)
    except Exception:
        logger.exception("price command failed")
        await interaction.followup.send(
            "⚠️ Couldn't reach the price service right now. Try again in a moment."
        )


@client.tree.command(name="weather", description="Get current weather for a city")
@app_commands.describe(city="City name, e.g. dubai")
async def weather(interaction: discord.Interaction, city: str) -> None:
    await interaction.response.defer()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as http:
            geo = await http.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city.strip(), "count": 1},
            )
            geo.raise_for_status()
            results = geo.json().get("results")
            if not results:
                await interaction.followup.send(
                    f"Couldn't find “{city}”. Check the spelling?"
                )
                return

            place = results[0]
            forecast = await http.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m",
                },
            )
            forecast.raise_for_status()
            cur = forecast.json()["current"]

        label = f"{place['name']}, {place.get('country', '')}".strip(", ")
        desc = WEATHER_CODES.get(cur["weather_code"], "—")
        embed = discord.Embed(title=f"🌦️ {label}", description=desc, color=ACCENT)
        embed.add_field(
            name="Temperature",
            value=f"{cur['temperature_2m']}°C (feels {cur['apparent_temperature']}°C)",
            inline=False,
        )
        embed.add_field(name="Humidity", value=f"{cur['relative_humidity_2m']}%", inline=True)
        embed.add_field(name="Wind", value=f"{cur['wind_speed_10m']} km/h", inline=True)
        await interaction.followup.send(embed=embed)
    except Exception:
        logger.exception("weather command failed")
        await interaction.followup.send(
            "⚠️ Couldn't reach the weather service right now. Try again in a moment."
        )


@client.tree.command(name="remind", description="Set a reminder")
@app_commands.describe(minutes="In how many minutes (1–1440)", message="What to remind you about")
async def remind(interaction: discord.Interaction, minutes: int, message: str) -> None:
    if not 1 <= minutes <= 1440:
        await interaction.response.send_message(
            "Pick a time between 1 and 1440 minutes.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ Got it — I'll remind you in {minutes} minute(s):\n“{message}”"
    )

    async def fire() -> None:
        await asyncio.sleep(minutes * 60)
        try:
            await interaction.followup.send(
                f"⏰ {interaction.user.mention} Reminder: {message}"
            )
        except Exception:
            logger.exception("failed to deliver reminder")

    asyncio.create_task(fire())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "DISCORD_TOKEN is not set. Create a bot in the Discord Developer "
            "Portal and set its token as an environment variable (see README)."
        )
    client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
