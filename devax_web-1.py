#!/usr/bin/env python3
"""
devax_web.py — DEVA💗WINE Strike Tool · Web UI
Render: Build = pip install -r requirements.txt && playwright install chromium
        Start = python3 devax_web.py
"""

import asyncio, logging, os, random, shutil, threading
from urllib.parse import unquote

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, redirect, render_template_string, request, url_for
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("devax")

PORT = int(os.getenv("PORT", 5000))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "deva-wine-key")

# ── DEFAULTS (sp-1.py se) ─────────────────────────────────────────────────────
DEFAULT_SID = "76248746678%3AirYuiwG9HsICGO%3A16%3AAYhv33lYNP9duoepc2MnnXv0JMeP9MwKrugV-FGM9g"
DEFAULT_URL = "https://www.instagram.com/direct/t/1704768377345706/"
DEFAULT_GC  = "DEVA💗 की मां चुदके पागल"

_messages: list[str] = [
    "𝐃𝐄𝐕𝐀 𝐒𝐘𝐒𝐓𝐄𝐌 तेरी औकात नहीं हमसे लड़ने की 😹🥀",
    "𝐓𝐔𝐌𝐇𝐀𝐑𝐈 𝐌𝐀𝐀 𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐀𝐋𝐄𝐍𝐆𝐄 //~ 🔥",
    "𝐓𝐔𝐌𝐇𝐀𝐑𝐈 𝐌𝐌𝐘 𝐊𝐎 𝐊𝐈𝐍𝐍𝐄𝐑 𝐆𝐑𝐎𝐔𝐏 𝐖𝐀𝐋𝐄 𝐂𝐇𝐎𝐃𝐄𝐍𝐆𝐄 𝐘𝐀𝐀𝐃 𝐑𝐀𝐊𝐇𝐍𝐀 😝🤲🏻",
    "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐀𝐈 𝐈𝐓𝐍𝐄 𝐂𝐇𝐀𝐍𝐓𝐄 𝐌𝐀𝐑𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐀 𝐅𝐀𝐀𝐓 𝐉𝐘𝐆𝐀 🐒🤣🔥",
    "𝐃𝐄𝐕𝐀💗𝐖𝐈𝐍𝐄 𝐀𝐂𝐓𝐈𝐕𝐄 अब रोने का अलावा कोई रास्ता नहीं😹🥀 ꧁𓊈𒆜 𝘿𝙀𝙑𝘼 भगवान है👑 𒆜𓊉꧂",
]

# ── STATE ─────────────────────────────────────────────────────────────────────
_stop_flag  = threading.Event()
_state_lock = threading.Lock()
_state = {"running": False, "engines": {}, "total": 0, "url": "", "error": ""}
_form  = {
    "sids": DEFAULT_SID, "url": DEFAULT_URL, "gc_name": DEFAULT_GC,
    "engine_count": "4", "delay": "0.3", "lock_enabled": True,
}

def _inc(eid: int):
    with _state_lock:
        _state["engines"][eid] = _state["engines"].get(eid, 0) + 1
        _state["total"] = sum(_state["engines"].values())

# ── PLAYWRIGHT ────────────────────────────────────────────────────────────────
async def _block_media(route):
    if route.request.resource_type in ("image", "media", "font"):
        await route.abort()
    else:
        await route.continue_()

async def _force_lock(page, gc_name: str):
    try:
        gear = page.locator('svg[aria-label="Conversation information"]')
        await gear.click()
        await page.locator('div[aria-label="Change group name"][role="button"]').click()
        inp = page.locator('input[aria-label="Group name"][name="change-group-name"]')
        await inp.fill(gc_name)
        save = page.locator('div[role="button"]:has-text("Save")')
        if await save.is_enabled():
            await save.click()
        await gear.click()
    except Exception as e:
        log.warning("lock: %s", e)
        await page.reload()

def _payload() -> str:
    gap = "\n" * 160
    core = random.choice(_messages)
    return f"{core}{gap}{core}{gap}{core}\n🔱DEVA💗WINE [{random.randint(1000,9999)}] 🔱"

async def _engine(eid: int, sid: str, url: str, gc_name: str,
                  is_locker: bool, delay: float):
    udd = f"/tmp/deva_{eid}"
    while not _stop_flag.is_set():
        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                udd, headless=True,
                args=["--no-sandbox","--disable-gpu",
                      "--disable-dev-shm-usage",
                      "--disable-blink-features=AutomationControlled"],
            )
            await ctx.add_cookies([{
                "name": "sessionid", "value": unquote(sid.strip()),
                "domain": ".instagram.com", "path": "/",
                "secure": True, "httpOnly": True,
            }])
            page = await ctx.new_page()
            await page.route("**/*", _block_media)
            try:
                await page.goto(url, wait_until="networkidle", timeout=90000)
                await page.wait_for_selector(
                    'div[role="textbox"][aria-label],div[contenteditable="true"]',
                    timeout=30000
                )
                box = page.locator('div[role="textbox"][aria-label],div[contenteditable="true"]').first
                mc  = 0
                for _ in range(150):
                    if _stop_flag.is_set(): break
                    if mc > 0 and mc % 30 == 0:
                        await page.reload(wait_until="networkidle")
                        box = page.locator('div[role="textbox"][aria-label],div[contenteditable="true"]').first
                        await box.focus()
                    if is_locker and mc >= 19:
                        await _force_lock(page, gc_name)
                        mc = 0
                        await box.focus()
                    await box.focus()
                    # IG contenteditable fix — clipboard inject
                    payload = _payload()
                    await page.evaluate(
                        """(txt) => {
                            const dt = new DataTransfer();
                            dt.setData('text/plain', txt);
                            document.activeElement.dispatchEvent(
                                new ClipboardEvent('paste', {clipboardData: dt, bubbles: true})
                            );
                        }""",
                        payload
                    )
                    await asyncio.sleep(0.05)
                    await page.keyboard.press("Enter")
                    mc += 1
                    _inc(eid)
                    await asyncio.sleep(random.uniform(delay, delay + 0.1))
            except Exception as e:
                log.warning("E-%d: %s", eid, e)
            await ctx.close()
            shutil.rmtree(udd, ignore_errors=True)
            if not _stop_flag.is_set():
                await asyncio.sleep(1)

async def _main(sids, url, gc_name, n, delay):
    await asyncio.gather(*[
        _engine(i+1, sids[i%len(sids)], url, gc_name, i==0, delay)
        for i in range(n)
    ])

def _runner(sids, url, gc_name, n, delay):
    try:
        asyncio.run(_main(sids, url, gc_name, n, delay))
    except Exception as e:
        with _state_lock:
            _state["error"] = str(e)
            _state["running"] = False
    finally:
        with _state_lock:
            _state["running"] = False

def start_strike(sids, url, gc_name, n, delay):
    if _state["running"]: return "Pehle se chal raha hai."
    _stop_flag.clear()
    with _state_lock:
        _state.update({"running":True,"engines":{},"total":0,"url":url,"error":""})
    threading.Thread(target=_runner, args=(sids,url,gc_name,n,delay), daemon=True).start()
    return None

def stop_strike():
    _stop_flag.set()
    with _state_lock:
        _state["running"] = False

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DEVA💗WINE</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Mono:wght@300;400;500&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:       #0d0608;
  --s1:       #100509;
  --s2:       #180a0e;
  --s3:       #200d12;
  --b1:       #2a1018;
  --b2:       #3d1622;
  --b3:       #5c1f30;
  --txt:      #f0dce4;
  --txt2:     #c4919f;
  --txt3:     #7a4455;
  --v1:       #d4496a;
  --v2:       #b02249;
  --v3:       #8b1a3a;
  --r1:       #f2b8c6;
  --r2:       #e8809a;
  --g1:       #b02249;
  --g2:       #8b1a3a;
  --glow-v:   rgba(212,73,106,0.22);
  --glow-r:   rgba(242,184,198,0.15);
  --glow-g:   rgba(176,34,73,0.18);
}

html,body{min-height:100vh;background:var(--bg);color:var(--txt);
  font-family:'Cormorant Garamond',Georgia,serif;}

body{
  background-image:
    radial-gradient(ellipse 70% 55% at 50% -10%,rgba(139,26,58,.25),transparent),
    radial-gradient(ellipse 40% 30% at 90% 60%,rgba(176,34,73,.08),transparent),
    radial-gradient(ellipse 50% 40% at 10% 90%,rgba(93,15,35,.12),transparent);
  padding:32px 16px 80px;
}

.wrap{max-width:560px;margin:0 auto}

/* ── BANNER ── */
.banner{
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,#0d0608 0%,#180a0e 50%,#0d0608 100%);
  border:1px solid rgba(176,34,73,0.35);
  border-radius:20px;padding:32px 24px 28px;
  margin-bottom:20px;text-align:center;
}
.banner::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(176,34,73,0.2),transparent 70%);
  pointer-events:none;
}
.banner-eyebrow{
  font-family:'DM Mono',monospace;
  font-size:.65rem;letter-spacing:.25em;text-transform:uppercase;
  color:var(--v1);margin-bottom:14px;opacity:.8;
}
.banner-title{
  font-size:2.2rem;font-weight:700;letter-spacing:.06em;
  background:linear-gradient(135deg,#f2b8c6 0%,#e8809a 40%,#d4496a 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;line-height:1;margin-bottom:8px;
}
.banner-sub{
  font-family:'DM Mono',monospace;
  font-size:.7rem;color:var(--txt3);letter-spacing:.15em;
  text-transform:uppercase;margin-bottom:16px;
}
.badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:5px 14px;border-radius:100px;
  background:rgba(176,34,73,0.1);
  border:1px solid rgba(176,34,73,0.3);
  font-size:.65rem;font-family:'DM Mono',monospace;
  color:#e8809a;letter-spacing:.12em;text-transform:uppercase;
}
.badge::before{content:'';width:5px;height:5px;border-radius:50%;background:#d4496a}

/* ── CARD ── */
.card{
  background:var(--s1);
  border:1px solid var(--b1);
  border-radius:16px;padding:20px;margin-bottom:12px;
  position:relative;overflow:hidden;
}
.card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(139,92,246,0.4),transparent);
}
.card-label{
  display:flex;align-items:center;gap:8px;
  font-size:.62rem;font-weight:600;color:var(--txt3);
  text-transform:uppercase;letter-spacing:.12em;margin-bottom:16px;
  font-family:'DM Mono',monospace;
}
.card-label span{color:var(--v1)}

/* ── FIELDS ── */
.field{margin-bottom:14px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}

label{
  display:block;font-size:.62rem;font-weight:600;
  color:var(--txt3);text-transform:uppercase;
  letter-spacing:.1em;margin-bottom:7px;
  font-family:'DM Mono',monospace;
}

input[type=text],input[type=number],textarea{
  width:100%;
  background:var(--bg);
  border:1px solid var(--b2);
  border-radius:10px;
  padding:11px 13px;
  color:var(--txt);
  font-size:.82rem;
  font-family:'DM Mono',monospace;
  outline:none;
  transition:border-color .2s,box-shadow .2s;
  resize:vertical;
}
input::placeholder,textarea::placeholder{color:var(--txt3)}
input:focus,textarea:focus{
  border-color:var(--v1);
  box-shadow:0 0 0 3px var(--glow-v),0 0 20px var(--glow-v);
}
textarea{min-height:70px}

/* ── TOGGLE ── */
.tog-row{
  display:flex;align-items:center;
  justify-content:space-between;
  padding:10px 0;
  border-top:1px solid var(--b1);
  margin-top:4px;
}
.tog-left .lbl{font-size:.82rem;color:var(--txt);font-weight:500}
.tog-left .sub{font-size:.68rem;color:var(--txt3);margin-top:2px;
               font-family:'DM Mono',monospace}
.switch{position:relative;width:42px;height:23px;flex-shrink:0}
.switch input{opacity:0;width:0;height:0}
.track{
  position:absolute;inset:0;background:var(--b2);
  border-radius:23px;cursor:pointer;
  transition:background .2s,box-shadow .2s;
}
.track::before{
  content:'';position:absolute;
  width:17px;height:17px;left:3px;top:3px;
  background:#fff;border-radius:50%;
  transition:transform .2s;
}
.switch input:checked + .track{
  background:var(--v2);
  box-shadow:0 0 10px var(--glow-v);
}
.switch input:checked + .track::before{transform:translateX(19px)}

/* ── MESSAGES ── */
.msg-wrap{display:flex;flex-direction:column;gap:5px;margin-bottom:12px}
.msg-row{
  display:flex;align-items:flex-start;gap:8px;
  padding:9px 11px;
  background:var(--bg);
  border:1px solid var(--b1);border-radius:9px;
}
.msg-num{
  font-family:'DM Mono',monospace;font-size:.62rem;
  color:var(--v1);min-width:18px;margin-top:1px;font-weight:700;
}
.msg-txt{flex:1;font-size:.73rem;color:var(--txt2);line-height:1.5;word-break:break-all}
.del{
  background:none;border:none;color:var(--txt3);
  cursor:pointer;font-size:.8rem;padding:0 2px;
  flex-shrink:0;transition:color .15s;
  font-family:'DM Mono',monospace;
}
.del:hover{color:var(--r1);text-shadow:0 0 8px var(--glow-r)}

.add-area{
  background:var(--bg);border:1px solid var(--b2);
  border-radius:10px;padding:11px 13px;
  color:var(--txt);font-size:.8rem;
  font-family:'DM Mono',monospace;
  width:100%;resize:none;outline:none;
  min-height:60px;
  transition:border-color .2s,box-shadow .2s;
}
.add-area:focus{border-color:var(--v1);box-shadow:0 0 0 3px var(--glow-v)}
.add-area::placeholder{color:var(--txt3)}

.btn-add{
  margin-top:8px;
  background:var(--s2);border:1px solid var(--b2);
  border-radius:8px;padding:8px 16px;
  color:var(--txt2);font-size:.75rem;cursor:pointer;
  font-family:'DM Mono',monospace;
  transition:border-color .15s,color .15s,background .15s;
}
.btn-add:hover{border-color:var(--v1);color:var(--v1);background:rgba(139,92,246,.06)}

/* ── BUTTONS ── */
.btn-deploy{
  width:100%;
  background:linear-gradient(135deg,var(--v3),var(--v2),var(--v1));
  border:none;border-radius:12px;padding:15px;
  color:#f7e8ed;font-size:.95rem;font-weight:300;
  font-family:'Cormorant Garamond',serif;font-style:italic;
  cursor:pointer;letter-spacing:.08em;
  position:relative;overflow:hidden;
  transition:transform .1s,box-shadow .25s;
  box-shadow:0 4px 24px rgba(139,26,58,.4);
}
.btn-deploy::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.07),transparent 60%);
}
.btn-deploy:hover{transform:translateY(-1px);box-shadow:0 8px 32px rgba(176,34,73,.5)}
.btn-deploy:active{transform:translateY(0) scale(.98)}

.btn-stop{
  width:100%;
  background:linear-gradient(135deg,#2a0a0e,#5a1020,#7a1428);
  border:1px solid var(--b3);border-radius:12px;padding:15px;
  color:var(--r1);font-size:.95rem;font-weight:300;
  font-family:'Cormorant Garamond',serif;font-style:italic;
  cursor:pointer;letter-spacing:.08em;
  position:relative;overflow:hidden;
  transition:transform .1s,box-shadow .25s;
  box-shadow:0 4px 20px rgba(80,10,20,.35);
}
.btn-stop::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.05),transparent);
}
.btn-stop:hover{transform:translateY(-1px);box-shadow:0 6px 28px rgba(120,20,40,.4)}
.btn-stop:active{transform:translateY(0) scale(.98)}

/* ── ALERT ── */
.alert{
  padding:12px 15px;border-radius:11px;
  font-size:.78rem;margin-bottom:14px;line-height:1.5;
  font-family:'DM Mono',monospace;
}
.alert.err{
  background:rgba(239,68,68,.07);
  border:1px solid rgba(239,68,68,.22);color:#fca5a5;
}

/* ── LIVE ── */
.live{
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,#0d0608,#180a0e);
  border:1px solid rgba(176,34,73,.3);
  border-radius:20px;padding:28px 24px;margin-bottom:14px;
}
.live::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(176,34,73,.12),transparent 70%);
  pointer-events:none;
}
.live-hdr{display:flex;align-items:center;gap:10px;margin-bottom:20px}
.pulse-ring{
  position:relative;width:14px;height:14px;flex-shrink:0;
}
.pulse-ring::before,.pulse-ring::after{
  content:'';position:absolute;inset:0;
  border-radius:50%;background:var(--v1);
}
.pulse-ring::after{
  animation:ripple 1.5s ease-out infinite;
  background:transparent;border:2px solid var(--v1);
}
@keyframes ripple{
  0%{transform:scale(1);opacity:1}
  100%{transform:scale(2.5);opacity:0}
}
.live-lbl{
  font-size:.82rem;font-weight:700;color:var(--r2);
  font-family:'DM Mono',monospace;
  letter-spacing:.1em;text-transform:uppercase;
}

.big-counter{
  text-align:center;
  font-family:'DM Mono',monospace;
  font-size:4.5rem;font-weight:700;
  background:linear-gradient(135deg,#f2b8c6,#d4496a);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;line-height:1;
  filter:drop-shadow(0 0 20px rgba(212,73,106,.35));
  margin-bottom:4px;
}
.big-label{
  font-size:.62rem;color:var(--txt3);text-align:center;
  text-transform:uppercase;letter-spacing:.18em;
  font-family:'DM Mono',monospace;margin-bottom:22px;
}

.eng-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px}
.eng-card{
  background:rgba(0,0,0,.5);
  border:1px solid rgba(176,34,73,.2);
  border-radius:11px;padding:13px;text-align:center;
}
.eng-val{
  font-size:1.4rem;font-weight:300;
  color:var(--r2);font-family:'Cormorant Garamond',serif;font-style:italic;
}
.eng-key{
  font-size:.58rem;color:var(--txt3);
  text-transform:uppercase;letter-spacing:.1em;
  margin-top:4px;font-family:'DM Mono',monospace;
}

.divider{height:1px;background:var(--b1);margin:18px 0}
</style>
</head>
<body>
<div class="wrap">

<!-- BANNER -->
<div class="banner">
  <div class="banner-eyebrow">💗 SYSTEM · ACTIVE</div>
  <div class="banner-title">DEVA💗WINE</div>
  <div class="banner-sub">by mansuri · the absolute king</div>
  <span class="badge">target injection engine</span>
</div>

{% if error %}<div class="alert err">⚠ {{ error }}</div>{% endif %}

{% if state.running %}

<!-- LIVE DASHBOARD -->
<div class="live">
  <div class="live-hdr">
    <div class="pulse-ring"></div>
    <span class="live-lbl">Engines Active</span>
  </div>
  <div class="big-counter" id="total">{{ state.total }}</div>
  <div class="big-label">Total Strikes Delivered</div>
  <div class="eng-grid" id="eng-grid">
    {% for eid, cnt in state.engines.items() %}
    <div class="eng-card">
      <div class="eng-val">{{ cnt }}</div>
      <div class="eng-key">Engine {{ eid }}</div>
    </div>
    {% endfor %}
  </div>
</div>

<form method="post" action="/stop">
  <button class="btn-stop" type="submit">⬛ &nbsp;terminate all engines</button>
</form>

{% else %}

<!-- SETUP FORM -->
<form method="post" action="/start" id="mf">

  <div class="card">
    <div class="card-label"><span>▸</span> Session Config</div>
    <div class="field">
      <label>Session ID(s) — comma se multiple</label>
      <textarea name="sids" rows="3"
        placeholder="SID1, SID2, SID3 ...">{{ form.sids }}</textarea>
    </div>
  </div>

  <div class="card">
    <div class="card-label"><span>▸</span> Target Config</div>
    <div class="field">
      <label>Group URL</label>
      <input type="text" name="url"
        placeholder="https://www.instagram.com/direct/t/..."
        value="{{ form.url }}">
    </div>
    <div class="field">
      <label>Group Lock Name</label>
      <input type="text" name="gc_name"
        placeholder="की मां चुदके पागल"
        value="{{ form.gc_name }}">
    </div>
  </div>

  <div class="card">
    <div class="card-label"><span>▸</span> Engine Config</div>
    <div class="g2">
      <div class="field">
        <label>Engine Count</label>
        <input type="number" name="engine_count"
          min="1" max="8" value="{{ form.engine_count }}">
      </div>
      <div class="field">
        <label>Delay (sec)</label>
        <input type="number" name="delay"
          min="0.1" max="5" step="0.1" value="{{ form.delay }}">
      </div>
    </div>
    <div class="tog-row">
      <div class="tog-left">
        <div class="lbl">Name Lock</div>
        <div class="sub">Engine-1 group naam auto-lock karega</div>
      </div>
      <label class="switch" style="margin-left:12px">
        <input type="checkbox" name="lock_enabled"
          {% if form.lock_enabled %}checked{% endif %}>
        <span class="track"></span>
      </label>
    </div>
  </div>

  <div class="card">
    <div class="card-label"><span>▸</span> Strike Messages</div>
    <div class="msg-wrap">
      {% for msg in messages %}
      <div class="msg-row">
        <span class="msg-num">{{ loop.index }}</span>
        <span class="msg-txt">{{ msg }}</span>
        <form method="post" action="/msg/del" style="display:inline">
          <input type="hidden" name="idx" value="{{ loop.index0 }}">
          <button class="del" type="submit">✕</button>
        </form>
      </div>
      {% endfor %}
    </div>
    <textarea class="add-area" id="na"
      placeholder="Naya message likho ..."></textarea>
    <button class="btn-add" type="button" id="ab">+ Add Message</button>
  </div>

  <button class="btn-deploy" type="submit">🔱 &nbsp;deploy engines</button>

</form>

<form id="af" method="post" action="/msg/add" style="display:none">
  <input type="hidden" name="text" id="av">
</form>

{% endif %}
</div>

<script>
document.addEventListener('DOMContentLoaded',function(){
  var ab=document.getElementById('ab');
  if(ab){ab.addEventListener('click',function(){
    var ta=document.getElementById('na');
    if(!ta||!ta.value.trim())return;
    document.getElementById('av').value=ta.value.trim();
    document.getElementById('af').submit();
  });}
});

{% if state.running %}
function poll(){
  fetch('/api/status')
    .then(function(r){return r.json();})
    .then(function(d){
      var t=document.getElementById('total');
      if(t)t.textContent=d.total;
      var g=document.getElementById('eng-grid');
      if(g&&d.engines){
        g.innerHTML=Object.entries(d.engines).map(function(e){
          return '<div class="eng-card"><div class="eng-val">'+e[1]+
                 '</div><div class="eng-key">Engine '+e[0]+'</div></div>';
        }).join('');
      }
      if(!d.running)setTimeout(function(){location.reload();},800);
    }).catch(function(){});
}
setInterval(poll,1500);
{% endif %}
</script>
</body>
</html>"""

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with _state_lock:
        state = dict(_state)
    return render_template_string(HTML,
        state=state, messages=_messages, form=_form,
        error=request.args.get("error",""))

@app.route("/start", methods=["POST"])
def start():
    raw   = request.form.get("sids","").strip()
    url   = request.form.get("url","").strip()
    gc    = request.form.get("gc_name","").strip() or DEFAULT_GC
    n     = int(request.form.get("engine_count") or 4)
    delay = float(request.form.get("delay") or 0.3)
    lock  = bool(request.form.get("lock_enabled"))
    sids  = [s.strip() for s in raw.split(",") if s.strip()]

    _form.update({"sids":raw,"url":url,"gc_name":gc,
                  "engine_count":str(n),"delay":str(delay),"lock_enabled":lock})

    if not sids: return redirect(url_for("index",error="Session ID chahiye."))
    if not url:  return redirect(url_for("index",error="Group URL chahiye."))

    err = start_strike(sids, url, gc, n, delay)
    if err: return redirect(url_for("index",error=err))
    return redirect(url_for("index"))

@app.route("/stop", methods=["POST"])
def stop():
    stop_strike()
    return redirect(url_for("index"))

@app.route("/msg/add", methods=["POST"])
def msg_add():
    t = request.form.get("text","").strip()
    if t: _messages.append(t)
    return redirect(url_for("index"))

@app.route("/msg/del", methods=["POST"])
def msg_del():
    try:
        i = int(request.form.get("idx",-1))
        if 0 <= i < len(_messages): _messages.pop(i)
    except: pass
    return redirect(url_for("index"))

@app.route("/api/status")
def api_status():
    with _state_lock:
        return jsonify(dict(_state))

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("port %d", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
