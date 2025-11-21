# equilibrium_ultimate_v37_final_full.py
import asyncio
import time
import requests
import json
import re
import random
import tweepy
from datetime import datetime
from collections import Counter

# ================== CONFIG ==================
TELEGRAM_TOKEN   = "8304411899:AAF9CEYSMdD4vRfaRV63UYl-FCGcwYaorLw"
TELEGRAM_CHAT_ID = "-1002745894919"
HELIUS_API_KEY   = "026ad28c-cdc9-41d7-a6f8-e5dea66730a0"
X_USERNAME       = "Raidenn26080"
TWITTER_BEARER   = "AAAAAAAAAAAAAAAAAAAAAHHR5QEAAAAAfgzxXE5NEGUoJXQLP3z90oDpUI8%3DhXrtjBnp87z9EOWTg0j1ZIh7E8Rmd16HyRlajRIQ5DDyPDo9VD"

# Threshold
MIN_AI_SCORE = 88
MIN_LIQ      = 25000
MIN_VOL5     = 22000
MIN_BUYS5    = 72

# ================== 20 WHALE WALLET 2025 ==================
WHALE_WALLETS = [
    "515vh1DrPuwMATt9Zoq9kP4sJL9fyojA1dHJu4DQpNRp","EDM6SGUziMUHsQKRUF68iRpXMCoqbFbC2nAuzdbFS6Sf",
    "A3sC2Ni1We55ErsqhkuHxWymZC1AsrMrNiQRWJ9XfCcK","68XtwHKfUNvD78X5VH8kZGDYL43iU6N4RpHZHXwjupXx",
    "2gwiA6zaf2yRfBVDc5zbPPSq2fT9DSPybRyzvGCE3vYo","Etvf3w3kooBcsqwSiubNUMA2c89xz7Y6ZdaRSAZoAFPf",
    "5C5RjP6bQWy2KkEJ9YCZcf64aXmSMX42tX1tR1Uj7wP2","82EuJwGbKS38JMmBj5JS3xNhcFcpXpeZhH9nHsPeMD83",
    "EwTNPYTuwxMzrvL19nzBsSLXdAoEmVBKkisN87csKgtt","C2snMNd4eH7uyVgWtEbdwMHf438FcXGCR9rUWHdd3TXD",
    "6obeVmM9SZUagyHTE7Soi7FhdZtd73m4MwHpkcL9Mu9Y","G5nxEXuFMfV74DSnsrSatqCW32F34XUnBeq3PfDS7w5E",
    "ATmKENkRrL1JQQnoUNAQvkiwgjiHKUkzyncxTGxyzQL1","AJKXLpGVhDTfB7x2oRG8FuNsryoGPmBUm9WyHd7PdNyb",
    "FnpXCzB3oT4LpsvsW3Pfz1FmTZgixZAf9WHGQxHbQCHi","8RC6XNjh5mwoSx8cLgb77B2RjnnkDmNgfVovRbTCwRXB",
    "3tc4BVAdzjr1JpeZu6NAjLHyp4kK3iic7TexMBYGJ4Xk","C5tTsPKB9o9Jgqi1SfuwbHY9UHchx5w7VcmCMp5Tmsxu",
    "FVxeFYgyT4GC6D7gaLkMSu2qtSJfw2N4RVPZowi2A64Y","HyNiuntjo51d5paTG7rX5XLLAAi68GQMN1STwSmvna4F"
]

# ================== 100 ALPHA CALLER 2025 ==================
ALPHA_CALLERS = [
    "alphaplz","0x_gremlin","bonkbot_call","pumpdotfun","solanact","alpha_plz","degenalpha","solcallbot",
    "whale_alert_sol","solanawhale","alpha_snipe","solpumpcaller","degencallsol","alpha_hunter_sol",
    "pumpfun_caller","solwhalehunter","degensolana","alphacall_sol","solpumpalert","whalecall_sol",
    "solanadegen","pumpwhale","alpha_solana","solcallhunter","degenwhale_sol","pumpalpha","soldegenwhale",
    "alphapump_sol","whalealpha","solpumpwhale","degencall_sol","alpha_caller","solwhalealert",
    "pumpcaller_sol","degenpump","solalphacall","whalepump_sol","alphadegen","solcallwhale",
    "pumpdegen_sol","whalecall","solalphahunter","degenalpha_sol","pumpwhale_sol","alphacall",
    "solwhalecall","degenpump_sol","whaledegen","solpumpalpha","alphawhale_sol","callsolana",
    "pumpalert_sol","degenwhale","soldegenalpha","whalepump","alphasolcall","soldegencall",
    "pumpalphasol","whalesolcall","degensolcall","solwhalealpha","alphapump","solcallalpha",
    "degenalphasol","whalesolpump","pumpdegen","solalphawhale","callwhale_sol","degen_sol",
    "solpumpwhale","alphadegensol","whalealpha_sol","solcallpump","degenwhalesol","pumpalphawhale",
    "soldegenwhale","alphacallsol","whalecallsol","pumpcallsol","degencallsol","solalphacaller",
    "whalepumpsol","alphapumpsol","soldegencaller","callalphasol","degenpumpsol","whalecallalpha",
    "pumpwhalesol","alphacallwhale","solpumpcaller","degensolwhale","whalealphapump","alphasolpump"
]

BAD_WORDS = ["test","rug","gay","nigg","fag","scam","dead","retard","china","moonshot","1000x","safu","based","chad","homo","jeets","pajeet","nigger"]

seen_tokens = set()
last_x_tweet_ids = set()
whale_tx_cache = set()
last_following_tweets = set()

client = tweepy.Client(bearer_token=TWITTER_BEARER, wait_on_rate_limit=True)

def kirim(msg):
    for _ in range(3):
        try:
            msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                         data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True},
                         timeout=15).raise_for_status()
            time.sleep(1.2)
            return
        except: time.sleep(3)

# ================== DEXSCREENER + PUMP.FUN DOUBLE POWER (LEBIH CEPAT DARI BIRDEYE!) ==================
def dexscreener_pump_scanner():
    while True:
        try:
            # 1. Pump.fun New Coins
            r = requests.get("https://frontend-api.pump.fun/coins?offset=0&limit=50&sort=created_timestamp&order=DESC", timeout=12)
            for t in r.json():
                mint = t.get("mint")
                if mint in seen_tokens: continue
                mc = t.get("usd_market_cap", 0)
                name = t.get("name", "")
                symbol = t.get("symbol", "").upper()
                if 10000 <= mc <= 150000 and not any(bad in name.lower() for bad in BAD_WORDS):
                    kirim(f"PUMP.FUN ALPHA!\n{name} (<b>${symbol}</b>)\nMC: <b>${mc:,.0f}</b>\nCA: <code>{mint}</code>\nhttps://pump.fun/{mint}")
                    seen_tokens.add(mint)

            # 2. DexScreener Hot Pairs (Solana)
            headers = {"User-Agent": "Mozilla/5.0"}
            r2 = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana", headers=headers, timeout=12)
            for pair in r2.json().get("pairs", [])[:30]:
                addr = pair.get("baseToken", {}).get("address")
                if not addr or addr in seen_tokens: continue
                liq = pair.get("liquidity", {}).get("usd", 0)
                vol5 = pair.get("volume", {}).get("m5", 0)
                buys5 = pair.get("txns", {}).get("m5", {}).get("buys", 0)
                pc5 = pair.get("priceChange", {}).get("m5", 0)
                if liq > 25000 and vol5 > 22000 and buys5 > 70 and pc5 > 30:
                    symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
                    kirim(f"DEXSCREENER BULLISH!\n<b>{symbol.upper()}</b>\nLiq ${liq:,.0f} | Vol5 ${vol5:,.0f}\nBuys {buys5} | +{pc5:.1f}%\nCA: <code>{addr}</code>\nhttps://dexscreener.com/solana/{pair.get('pairAddress')}")
                    seen_tokens.add(addr)

            time.sleep(8)
        except: time.sleep(10)

# ================== FUNGSI LAMA TETAP ADA ==================
def screen_my_x():
    try:
        user = client.get_user(username=X_USERNAME)
        if not user.data: return
        tweets = client.get_users_tweets(user.data.id, max_results=10)
        if not tweets.data: return
        for t in tweets.data:
            tid = t.id
            if tid in last_x_tweet_ids: continue
            last_x_tweet_ids.add(tid)
            text = t.text
            cas = re.findall(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text)
            if cas or any(k in text.lower() for k in ["pump","alpha","100x","gem","lfg"]):
                msg = f"TWEET LU MASUK (<10 DETIK)!\n{text}\nhttps://x.com/{X_USERNAME}/status/{tid}"
                if cas: msg += f"\nCA: <code>{cas[0]}</code>"
                kirim(msg)
    except: pass

def helius_whale_tracker():
    try:
        for wallet in WHALE_WALLETS:
            url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions?api-key={HELIUS_API_KEY}"
            r = requests.get(url, timeout=10)
            if r.status_code != 200: continue
            for tx in r.json()[:3]:
                sig = tx.get("signature")
                if sig in whale_tx_cache: continue
                for tr in tx.get("tokenTransfers", []):
                    mint = tr.get("mint")
                    if mint:
                        kirim(f"WHALE {wallet[:6]}... BELI!\nCA: <code>{mint}</code>\nhttps://dexscreener.com/solana/{mint}")
                        whale_tx_cache.add(sig)
    except: pass

def alpha_caller_scanner():
    try:
        for username in random.sample(ALPHA_CALLERS, 40):
            try:
                user = client.get_user(username=username)
                if not user.data: continue
                tweets = client.get_users_tweets(user.data.id, max_results=5, exclude=["retweets"])
                if not tweets.data: continue
                for t in tweets.data:
                    tid = t.id
                    if tid in last_following_tweets: continue
                    last_following_tweets.add(tid)
                    text = t.text.lower()
                    cas = re.findall(r'[1-9A-HJ-NP-Za-km-z]{32,44}', t.text)
                    if any(bad in text for bad in BAD_WORDS): continue
                    if cas or any(kw in text for kw in ["pump","alpha","100x","gem","lfg","moon"]):
                        msg = f"ALPHA CALL @{username.upper()}!\n{t.text[:380]}"
                        if cas: msg += f"\nCA: <code>{cas[0]}</code>"
                        kirim(msg)
            except: continue
    except: pass

# ================== START ==================
kirim("""
EQUILIBRIUM ULTIMATE V37 — FINAL BOSS 2025

20 Whale Wallet
100 Alpha Caller
Pump.fun + DexScreener Double Power
Tweet Lu Real-time
Helius Whale Tracker
Alpha Caller Scanner

""")

# Jalankan semua fungsi
while True:
    dexscreener_pump_scanner()
    screen_my_x()
    helius_whale_tracker()
    alpha_caller_scanner()
    time.sleep(9)