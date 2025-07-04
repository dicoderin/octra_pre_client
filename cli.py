#!/usr/bin/env python3
import json, base64, hashlib, time, sys, re, random, string, os, shutil, asyncio, aiohttp, threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import nacl.signing

c = {'r': '\033[0m', 'b': '\033[94m', 'c': '\033[96m', 'g': '\033[92m', 'y': '\033[93m', 'R': '\033[91m', 'B': '\033[1m', 'bg': '\033[44m', 'bgr': '\033[41m', 'bgg': '\033[42m', 'w': '\033[97m'}

priv, addr, rpc = None, None, None
sk, pub = None, None
b58 = re.compile(r"^oct[1-9A-HJ-NP-Za-km-z]{44}$")
μ = 1_000_000
h = []
cb, cn, lu, lh = None, None, 0, 0
session = None
executor = ThreadPoolExecutor(max_workers=1)
stop_flag = threading.Event()
spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
spinner_idx = 0

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def sz():
    return shutil.get_terminal_size((80, 25))

def at(x, y, t, cl=''):
    print(f"\033[{y};{x}H{c['bg']}{cl}{t}{c['bg']}", end='')

def inp(x, y):
    print(f"\033[{y};{x}H{c['bg']}{c['B']}{c['w']}", end='', flush=True)
    return input()

async def ainp(x, y):
    print(f"\033[{y};{x}H{c['bg']}{c['B']}{c['w']}", end='', flush=True)
    try:
        return await asyncio.get_event_loop().run_in_executor(executor, input)
    except:
        stop_flag.set()
        return ''

def wait():
    cr = sz()
    msg = "press enter to continue..."
    msg_len = len(msg)
    y_pos = cr[1] - 2
    x_pos = max(2, (cr[0] - msg_len) // 2)
    at(x_pos, y_pos, msg, c['y'])
    print(f"\033[{y_pos};{x_pos + msg_len}H", end='', flush=True)
    input()

async def awaitkey():
    cr = sz()
    msg = "press enter to continue..."
    msg_len = len(msg)
    y_pos = cr[1] - 2
    x_pos = max(2, (cr[0] - msg_len) // 2)
    at(x_pos, y_pos, msg, c['y'])
    print(f"\033[{y_pos};{x_pos + msg_len}H{c['bg']}", end='', flush=True)
    try:
        await asyncio.get_event_loop().run_in_executor(executor, input)
    except:
        stop_flag.set()

def ld():
    global priv, addr, rpc, sk, pub
    try:
        with open('wallet.json', 'r') as f:
            d = json.load(f)
        priv = d.get('priv')
        addr = d.get('addr')
        r极 = d.get('rpc', 'https://octra.network')
        sk = nacl.signing.SigningKey(base64.b64decode(priv))
        pub = base64.b64encode(sk.verify_key.encode()).decode()
        return True
    except:
        return False

def fill():
    cr = sz()
    print(f"{c['bg']}", end='')
    for _ in range(cr[1]):
        print(" " * cr[0])
    print("\033[H", end='')

def box(x, y, w, h, t=""):
    print(f"\033[{y};{x}H{c['bg']}{c['w']}┌{'─' * (w - 2)}┐{c['bg']}")
    if t:
        print(f"\033[{y};{x}H{c['bg']}{c['w']}┤ {c['B']}{t} {c['w']}├{c['bg']}")
    for i in range(1, h - 1):
        print(f"\033[{y + i};{x}H{c['bg']}{c['w']}│{' ' * (w - 2)}│{c['bg']}")
    print(f"\033[{y + h - 1};{x}H{c['bg']}{c['w']}└{'─' * (w - 2)}┘{c['bg']}")

async def spin_animation(x, y, msg):
    global spinner_idx
    try:
        while True:
            at(x, y, f"{c['c']}{spinner_frames[spinner_idx]} {msg}", c['c'])
            spinner_idx = (spinner_idx + 1) % len(spinner_frames)
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        at(x, y, " " * (len(msg) + 3), "")

async def req(m, p, d=None, t=10):
    global session
    if not session:
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=t))
    try:
        url = f"{rpc}{p}"
        async with getattr(session, m.lower())(url, json=d if m == 'POST' else None) as resp:
            text = await resp.text()
            try:
                j = json.loads(text) if text else None
            except:
                j = None
            return resp.status, text, j
    except asyncio.CancelledError:
        raise
    except asyncio.TimeoutError:
        return 0, "timeout", None
    except Exception as e:
        return 0, str(e), None

async def st():
    global cb, cn, lu
    now = time.time()
    if cb is not None and (now - lu) < 30:
        return cn, cb
    
    results = await asyncio.gather(
        req('GET', f'/balance/{addr}'),
        req('GET', '/staging', 5),
        return_exceptions=True
    )
    
    s, t, j = results[0] if not isinstance(results[0], Exception) else (0, str(results[0]), None)
    s2, _, j2 = results[1] if not isinstance(results[1], Exception) else (0, None, None)
    
    if s == 200 and j:
        cn = int(j.get('nonce', 0))
        cb = float(j.get('balance', 0))
        lu = now
        if s2 == 200 and j2:
            our = [tx for tx in j2.get('staged_transactions', []) if tx.get('from') == addr]
            if our:
                nonces = [int(tx.get('nonce', 0)) for tx in our]
                max_nonce = max(nonces) if nonces else cn
                cn = max(cn, max_nonce)
    elif s == 404:
        cn, cb, lu = 0, 0.0, now
    elif s == 200 and t and not j:
        try:
            parts = t.strip().split()
            if len(parts) >= 2:
                cb = float(parts[0]) if parts[0].replace('.', '').isdigit() else 0.0
                cn = int(parts[1]) if parts[1].isdigit() else 0
                lu = now
            else:
                cn, cb = None, None
        except:
            cn, cb = None, None
    return cn, cb

async def gh():
    global h, lh
    now = time.time()
    if now - lh < 60 and h:
        return
    s, t, j = await req('GET', f'/address/{addr}?limit=20')
    if s != 200 or (not j and not t):
        return
    
    if j and 'recent_transactions' in j:
        tx_hashes = [ref["hash"] for ref in j.get('recent_transactions', [])]
        tx_results = await asyncio.gather(*[req('GET', f'/tx/{hsh}', 5) for hsh in tx_hashes], return_exceptions=True)
        
        existing_hashes = {tx['hash'] for tx in h}
        nh = []
        
        for i, (ref, result) in enumerate(zip(j.get('recent_transactions', []), tx_results)):
            if isinstance(result, Exception):
                continue
            s2, _, j2 = result
            if s2 == 200 and j2 and 'parsed_tx' in j2:
                p = j2['parsed_tx']
                tx_hash = ref['hash']
                
                if tx_hash in existing_hashes:
                    continue
                
                ii = p.get('to') == addr
                ar = p.get('amount_raw', p.get('amount', '0'))
                a = float(ar) if '.' in str(ar) else int(ar) / μ
                nh.append({
                    'time': datetime.fromtimestamp(p.get('timestamp', 0)),
                    'hash': tx_hash,
                    'amt': a,
                    'to': p.get('to') if not ii else p.get('from'),
                    'type': 'in' if ii else 'out',
                    'ok': True,
                    'nonce': p.get('nonce', 0),
                    'epoch': ref.get('epoch', 0)
                })
        
        oh = datetime.now() - timedelta(hours=1)
        h[:] = sorted(nh + [tx for tx in h if tx.get('time', datetime.now()) > oh], key=lambda x: x['time'], reverse=True)[:50]
        lh = now
    elif s == 404 or (s == 200 and t and 'no transactions' in t.lower()):
        h.clear()
        lh = now

def mk(to, a, n):
    tx = {
        "from": addr,
        "to_": to,
        "amount": str(int(a * μ)),
        "nonce": int(n),
        "ou": "1" if a < 1000 else "3",
        "timestamp": time.time() + random.random() * 0.01
    }
    bl = json.dumps(tx, separators=(",", ":"))
    sig = base64.b64encode(sk.sign(bl.encode()).signature).decode()
    tx.update(signature=sig, public_key=pub)
    return tx, hashlib.sha256(bl.encode()).hexdigest()

async def snd(tx):
    t0 = time.time()
    s, t, j = await req('POST', '/send-tx', tx)
    dt = time.time() - t0
    if s == 200:
        if j and j.get('status') == 'accepted':
            return True, j.get('tx_hash', ''), dt, j
        elif t.lower().startswith('ok'):
            return True, t.split()[-1], dt, None
    return False, json.dumps(j) if j else t, dt, j

async def expl(x, y, w, hb):
    at(x, y, "TRANSACTION HISTORY", c['B'] + c['c'])
    at(x, y + 1, "─" * 19, c['c'])
    y_offset = y + 2
    
    at(x + 2, y_offset, "address:", c['c'])
    at(x + 11, y_offset, addr, c['w'])
    at(x + 2, y_offset + 1, "balance:", c['c'])
    n, b = await st()
    at(x + 11, y_offset + 1, f"{b:.6f} oct" if b is not None else "---", c['B'] + c['g'] if b else c['w'])
    at(x + 2, y_offset + 2, "nonce:  ", c['c'])
    at(x + 11, y_offset + 2, str(n) if n is not None else "---", c['w'])
    at(x + 2, y_offset + 3, "public: ", c['c'])
    at(x + 11, y_offset + 3, pub, c['w'])
    _, _, j = await req('GET', '/staging', 2)
    sc = len([tx for tx in j.get('staged_transactions', []) if tx.get('from') == addr]) if j else 0
    at(x + 2, y_offset + 4, "staging:", c['c'])
    at(x + 11, y_offset + 4, f"{sc} pending" if sc else "none", c['y'] if sc else c['w'])
    at(x + 1, y_offset + 5, "─" * (w - 2), c['w'])
    
    at(x + 2, y_offset + 6, "recent transactions:", c['B'] + c['c'])
    if not h:
        at(x + 2, y_offset + 8, "no transactions yet", c['y'])
    else:
        at(x + 2, y_offset + 8, "time     type  amount      address", c['c'])
        at(x + 2, y_offset + 9, "─" * (w - 4), c['w'])
        seen_hashes = set()
        display_count = 0
        sorted_h = sorted(h, key=lambda x: x['time'], reverse=True)
        for tx in sorted_h:
            if tx['hash'] in seen_hashes:
                continue
            seen_hashes.add(tx['hash'])
            if display_count >= min(len(h), hb - 15):
                break
            is_pending = not tx.get('epoch')
            time_color = c['y'] if is_pending else c['w']
            at(x + 2, y_offset + 10 + display_count, tx['time'].strftime('%H:%M:%S'), time_color)
            at(x + 11, y_offset + 10 + display_count, " in" if tx['type'] == 'in' else "out", c['g'] if tx['type'] == 'in' else c['R'])
            at(x + 16, y_offset + 10 + display_count, f"{float(tx['amt']):>10.6f}", c['w'])
            at(x + 28, y_offset + 10 + display_count, str(tx.get('to', '---')), c['y'])
            status_text = "pen" if is_pending else f"e{tx.get('epoch', 0)}"
            status_color = c['y'] + c['B'] if is_pending else c['c']
            at(x + w - 6, y_offset + 10 + display_count, status_text, status_color)
            display_count += 1

def menu(x, y, w, h):
    at(x, y, "COMMANDS", c['B'] + c['c'])
    at(x, y + 1, "────────", c['c'])
    at(x, y + 3, "[1] send tx", c['w'])
    at(x, y + 5, "[2] refresh balance", c['w'])
    at(x, y + 7, "[3] multi send", c['w'])
    at(x, y + 9, "[4] export keys", c['w'])
    at(x, y + 11, "[5] clear history", c['w'])
    at(x, y + 13, "[6] send to list", c['w'])
    at(x, y + 15, "[7] fetch oct addresses", c['w'])
    at(x, y + 17, "[8] clear wallet list", c['w'])
    at(x, y + 19, "[0] exit", c['w'])
    at(x, y + 21, "─" * (w - 2), c['c'])
    at(x, y + 22, "select option: ", c['B'] + c['y'])

async def clear_wallet_list():
    cr = sz()
    w, hb = 70, 10
    x = (cr[0] - w) // 2
    y = (cr[1] - hb) // 2
    box(x, y, w, hb, "clear wallet list")
    
    at(x + 2, y + 2, "this will remove all addresses from list.txt", c['y'])
    at(x + 2, y + 3, "are you sure? [y/n]: ", c['B'] + c['y'])
    confirm = await ainp(x + 25, y + 3)
    
    if confirm.strip().lower() == 'y':
        try:
            with open('list.txt', 'w') as f:
                pass
            at(x + 2, y + 5, "list.txt has been cleared.", c['g'])
        except Exception as e:
            at(x + 2, y + 5, f"error: {str(e)}", c['R'])
    else:
        at(x + 2, y + 5, "operation canceled.", c['y'])
    
    at(x + 2, y + 7, "press enter to continue...", c['y'])
    await awaitkey()

async def fetch_oct_addresses():
    """Fetch oct addresses from API and save to list.txt"""
    try:
        api_url = "https://octrascan.io/api/txs?offset=100"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return f"API error: HTTP {response.status}"
                
                data = await response.json()
                addresses = set()
                
                # Extract addresses from transactions with better validation
                for tx in data.get('transactions', []):
                    # Handle both 'from' and 'to' addresses
                    for field in ['from', 'to']:
                        addr_val = tx.get(field)
                        if addr_val and b58.match(addr_val):
                            addresses.add(addr_val)
                
                # Filter valid addresses
                valid_addresses = list(addresses)
                
                # Save to file
                with open('list.txt', 'w') as f:
                    for addr in valid_addresses:
                        f.write(addr + '\n')
                
                return len(valid_addresses)
    
    except aiohttp.ClientError as e:
        return f"Network error: {str(e)}"
    except json.JSONDecodeError:
        return "Invalid API response format"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

async def fetch_oct_addresses_screen():
    """Display screen for fetching oct addresses"""
    cr = sz()
    cls()
    fill()
    w, hb = 70, 12  # Increased height for better message display
    x = (cr[0] - w) // 2
    y = (cr[1] - hb) // 2
    box(x, y, w, hb, "fetch oct addresses")
    
    # Create spinner animation
    spin_task = asyncio.create_task(spin_animation(x + 2, y + 3, "fetching addresses from octrascan.io..."))
    
    # Run fetch operation
    result = await fetch_oct_addresses()
    
    # Cancel spinner
    spin_task.cancel()
    try:
        await spin_task
    except asyncio.CancelledError:
        pass
    
    # Display results
    if isinstance(result, int):
        if result > 0:
            at(x + 2, y + 4, f"✓ Found {result} valid OCT addresses", c['g'])
            at(x + 2, y + 5, "Saved to list.txt", c['g'])
        else:
            at(x + 2, y + 4, "No valid addresses found in recent transactions", c['y'])
            at(x + 2, y + 5, "Try increasing the offset parameter", c['y'])
    else:
        at(x + 2, y + 4, "✗ Failed to fetch addresses:", c['R'])
        at(x + 2, y + 5, result, c['R'])
    
    at(x + 2, y + 7, "Press enter to continue...", c['y'])
    await awaitkey()

async def scr():
    cr = sz()
    cls()
    fill()
    t = f" octra wallet v0.0.12 │ {datetime.now().strftime('%H:%M:%S')} "
    at((cr[0] - len(t)) // 2, 1, t, c['B'] + c['c'])
    at(1, 2, "─" * cr[0], c['c'])
    
    sidebar_w = 28
    menu(2, 4, sidebar_w, 23)
    
    info_y = 28
    at(2, info_y, "INFORMATION", c['B'] + c['c'])
    at(2, info_y + 1, "───────────", c['c'])
    at(4, info_y + 3, "testnet environment", c['y'])
    at(4, info_y + 4, "tokens have no value", c['y'])
    at(4, info_y + 5, "use for testing only", c['y'])
    
    explorer_x = sidebar_w + 4
    explorer_w = cr[0] - explorer_x - 2
    await expl(explorer_x, 4, explorer_w, cr[1] - 6)
    
    at(2, cr[1] - 1, " ready ", c['g'])
    return await ainp(18, 25)

async def tx():
    cr = sz()
    cls()
    fill()
    w, hb = 85, 22
    x = (cr[0] - w) // 2
    y = (cr[1] - hb) // 2
    box(x, y, w, hb, "send transaction")
    at(x + 2, y + 2, "to address: (or [esc] to cancel)", c['y'])
    at(x + 2, y + 3, "─" * (w - 4), c['w'])
    to = await ainp(x + 2, y + 4)
    if not to or to.lower() == 'esc':
        return
    if not b58.match(to):
        at(x + 2, y + 14, "invalid address!", c['bgr'] + c['w'])
        at(x + 2, y + 15, "press enter to go back...", c['y'])
        await ainp(x + 2, y + 16)
        return
    at(x + 2, y + 5, f"to: {to}", c['g'])
    at(x + 2, y + 7, "amount: (or [esc] to cancel)", c['y'])
    at(x + 2, y + 8, "─" * (w - 4), c['w'])
    a = await ainp(x + 2, y + 9)
    if not a or a.lower() == 'esc':
        return
    if not re.match(r"^\d+(\.\d+)?$", a) or float(a) <= 0:
        at(x + 2, y + 14, "invalid amount!", c['bgr'] + c['w'])
        at(x + 2, y + 15, "press enter to go back...", c['y'])
        await ainp(x + 2, y + 16)
        return
    a = float(a)
    global lu
    lu = 0
    n, b = await st()
    if n is None:
        at(x + 2, y + 14, "failed to get nonce!", c['bgr'] + c['w'])
        at(x + 2, y + 15, "press enter to go back...", c['y'])
        await ainp(x + 2, y + 16)
        return
    if not b or b < a:
        at(x + 2, y + 14, f"insufficient balance ({b:.6f} < {a})", c['bgr'] + c['w'])
        at(x + 2, y + 15, "press enter to go back...", c['y'])
        await ainp(x + 2, y + 16)
        return
    at(x + 2, y + 11, "─" * (w - 4), c['w'])
    at(x + 2, y + 12, f"send {a:.6f} oct", c['B'] + c['g'])
    at(x + 2, y + 13, f"to:  {to}", c['g'])
    at(x + 2, y + 14, f"fee: {'0.001' if a < 1000 else '0.003'} oct (nonce: {n + 1})", c['y'])
    at(x + 2, y + 15, "[y]es / [n]o: ", c['B'] + c['y'])
    if (await ainp(x + 16, y + 15)).strip().lower() != '极y':
        return
    
    spin_task = asyncio.create_task(spin_animation(x + 2, y + 16, "sending transaction"))
    
    t, _ = mk(to, a, n + 1)
    ok, hs, dt, r = await snd(t)
    
    spin_task.cancel()
    try:
        await spin_task
    except asyncio.CancelledError:
        pass
    
    if ok:
        for i in range(16, 21):
            at(x + 2, y + i, " " * (w - 4), c['bg'])
        at(x + 2, y + 16, f"✓ transaction accepted!", c['bgg'] + c['w'])
        at(x + 2, y + 17, f"hash: {hs[:64]}...", c['g'])
        at(x + 2, y + 18, f"      {hs[64:]}", c['g'])
        at(x + 2, y + 19, f"time: {dt:.2f}s", c['w'])
        if r and 'pool_info' in r:
            at(x + 2, y + 20, f"pool: {r['pool_info'].get('total_pool_size', 0)} txs pending", c['y'])
        h.append({
            'time': datetime.now(),
            'hash': hs,
            'amt': a,
            'to': to,
            'type': 'out',
            'ok': True
        })
        lu = 0
    else:
        at(x + 2, y + 16, f"✗ transaction failed!", c['bgr'] + c['w'])
        at(x + 2, y + 17, f"error: {str(hs)[:w - 10]}", c['R'])
    await awaitkey()

async def multi():
    cr = sz()
    cls()
    fill()
    w, hb = 70, cr[1] - 4
    x = (cr[0] - w) // 2
    y = 2
    box(x, y, w, hb, "multi send")
    at(x + 2, y + 2, "enter recipients (address amount), empty line to finish:", c['y'])
    at(x + 2, y + 3, "type [esc] to cancel", c['c'])
    at(x + 2, y + 4, "─" * (w - 4), c['w'])
    rcp = []
    tot = 0
    ly = y + 5
    while ly < y + hb - 8:
        at(x + 2, ly, f"[{len(rcp) + 1}] ", c['c'])
        l = await ainp(x + 7, ly)
        if l.lower() == 'esc':
            return
        if not l:
            break
        p = l.split()
        if len(p) == 2 and b58.match(p[0]) and re.match(r"^\d+(\.\d+)?$", p[1]) and float(p[1]) > 0:
            a = float(p[1])
            rcp.append((p[0], a))
            tot += a
            at(x + 50, ly, f"+{a:.6f}", c['g'])
            ly += 1
        else:
            at(x + 50, ly, "invalid!", c['R'])
    if not rcp:
        return
    at(x + 2, y + hb - 7, "─" * (w - 4), c['w'])
    at(x + 2, y + hb - 6, f"total: {tot:.6f} oct to {len(rcp)} addresses", c['B'] + c['y'])
    global lu
    lu = 0
    n, b = await st()
    if n is None:
        at(x + 2, y + hb - 5, "failed to get nonce!", c['bgr'] + c['w'])
        at(x + 2, y + hb - 4, "press enter to go back...", c['y'])
        await ainp(x + 2, y + hb - 3)
        return
    if not b or b < tot:
        at(x + 2, y + hb - 5, f"insufficient balance! ({b:.6f} < {tot})", c['bgr'] + c['w'])
        at(x + 2, y + hb - 4, "press enter to go back...", c['y'])
        await ainp(x + 2, y + hb - 3)
        return
    at(x + 2, y + hb - 5, f"send all? [y/n] (starting nonce: {n + 1}): ", c['y'])
    if (await ainp(x + 48, y + hb - 5)).strip().lower() != 'y':
        return
    
    spin_task = asyncio.create_task(spin_animation(x + 2, y + hb - 3, "sending transactions"))
    
    batch_size = 5
    batches = [rcp[i:i+batch_size] for i in range(0, len(rcp), batch_size)]
    s_total, f_total = 0, 0
    
    for batch_idx, batch in enumerate(batches):
        tasks = []
        for i, (to, a) in enumerate(batch):
            idx = batch_idx * batch_size + i
            at(x + 2, y + hb - 2, f"[{idx + 1}/{len(rcp)}] preparing batch...", c['c'])
            t, _ = mk(to, a, n + 1 + idx)
            tasks.append(snd(t))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (result, (to, a)) in enumerate(zip(results, batch)):
            idx = batch_idx * batch_size + i
            if isinstance(result, Exception):
                f_total += 1
                at(x + 55, y + hb - 2, "✗ fail ", c['R'])
            else:
                ok, hs, _, _ = result
                if ok:
                    s_total += 1
                    at(x + 55, y + hb - 2, "✓ ok   ", c['g'])
                    h.append({
                        'time': datetime.now(),
                        'hash': hs,
                        'amt': a,
                        'to': to,
                        'type': 'out',
                        'ok': True
                    })
                else:
                    f_total += 1
                    at(x + 55, y + hb - 2, "✗ fail ", c['R'])
            at(x + 2, y + hb - 2, f"[{idx + 1}/{len(rcp)}] {a:.6f} to {to[:20]}...", c['c'])
            await asyncio.sleep(0.05)
    
    spin_task.cancel()
    try:
        await spin_task
    except asyncio.CancelledError:
        pass
    
    lu = 0
    at(x + 2, y + hb - 2, " " * 65, c['bg'])
    at(x + 2, y + hb - 2, f"completed: {s_total} success, {f_total} failed", c['bgg'] + c['w'] if f_total == 0 else c['bgr'] + c['w'])
    await awaitkey()

async def send_to_list():
    cr = sz()
    cls()
    fill()
    w, hb = 70, cr[1] - 4
    x = (cr[0] - w) // 2
    y = 2
    
    addresses = []
    try:
        with open('list.txt', 'r') as f:
            addresses = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        box(x, y, w, 8, "error")
        at(x + 2, y + 3, "file 'list.txt' not found!", c['R'])
        at(x + 2, y + 5, "create a file named list.txt with", c['y'])
        at(x + 2, y + 6, "one address per line", c['y'])
        await awaitkey()
        return
    
    valid_addresses = [addr for addr in addresses if b58.match(addr)]
    invalid_count = len(addresses) - len(valid_addresses)
    
    if not valid_addresses:
        box(x, y, w, 8, "error")
        at(x + 2, y + 3, "no valid addresses found in list.txt", c['R'])
        at(x + 2, y + 5, "all addresses must be valid OCT addresses", c['y'])
        await awaitkey()
        return
    
    box(x, y, w, hb, "send 1 OCT to list")
    at(x + 2, y + 2, f"found {len(valid_addresses)} valid addresses in list.txt", c['g'])
    if invalid_count > 0:
        at(x + 2, y + 3, f"{invalid_count} invalid addresses skipped", c['y'])
    
    amount_per = 1.0
    total_amount = len(valid_addresses) * amount_per
    fee_per = 0.001
    total_fee = len(valid_addresses) * fee_per
    total_required = total_amount + total_fee
    
    at(x + 2, y + 5, "each address will receive:", c['c'])
    at(x + 2, y + 6, f"  {amount_per:.6f} OCT", c['w'])
    at(x + 2, y + 7, f"total to send: {total_amount:.6f} OCT", c['c'])
    at(x + 2, y + 8, f"estimated fees: {total_fee:.6f} OCT", c['c'])
    at(x + 2, y + 9, f"total required: {total_required:.6f} OCT", c['B'] + c['y'])
    
    global lu
    lu = 0
    n, b = await st()
    if n is None:
        at(x + 2, y + 12, "failed to get nonce!", c['bgr'] + c['w'])
        await awaitkey()
        return
    
    if b < total_required:
        at(x + 2, y + 11, "─" * (w - 4), c['w'])
        at(x + 2, y + 12, f"insufficient balance! ({b:.6f} < {total_required:.6f})", c['bgr'] + c['w'])
        at(x + 2, y + 13, "press enter to go back...", c['y'])
        await ainp(x + 2, y + 14)
        return
    
    at(x + 2, y + 11, "─" * (w - 4), c['w'])
    at(x + 2, y + 12, f"your balance: {b:.6f} OCT", c['g'])
    at(x + 2, y + 13, f"nonce: {n + 1}", c['g'])
    
    at(x + 2, y + 15, "confirm sending? [y/n]: ", c['B'] + c['y'])
    if (await ainp(x + 27, y + 15)).strip().lower() != 'y':
        return
    
    spin_task = asyncio.create_task(spin_animation(x + 2, y + 17, "sending transactions"))
    
    batch_size = 5
    batches = [valid_addresses[i:i+batch_size] for i in range(0, len(valid_addresses), batch_size)]
    s_total, f_total = 0, 0
    
    for batch_idx, batch in enumerate(batches):
        tasks = []
        for i, addr in enumerate(batch):
            idx = batch_idx * batch_size + i
            at(x + 2, y + 18, f"[{idx + 1}/{len(valid_addresses)}] preparing...", c['c'])
            t, _ = mk(addr, amount_per, n + 1 + idx)
            tasks.append(snd(t))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (result, addr) in enumerate(zip(results, batch)):
            idx = batch_idx * batch_size + i
            if isinstance(result, Exception):
                f_total += 1
                at(x + 55, y + 18, "✗ fail ", c['R'])
            else:
                ok, hs, _, _ = result
                if ok:
                    s_total += 1
                    at(x + 55, y + 18, "✓ ok   ", c['g'])
                    h.append({
                        'time': datetime.now(),
                        'hash': hs,
                        'amt': amount_per,
                        'to': addr,
                        'type': 'out',
                        'ok': True
                    })
                else:
                    f_total += 1
                    at(x + 55, y + 18, "✗ fail ", c['R'])
            at(x + 2, y + 18, f"[{idx + 1}/{len(valid_addresses)}] sent 1 OCT to {addr[:20]}...", c['c'])
            await asyncio.sleep(0.5)
    
    spin_task.cancel()
    try:
        await spin_task
    except asyncio.CancelledError:
        pass
    
    lu = 0
    at(x + 2, y + 18, " " * 65, c['bg'])
    at(x + 2, y + 18, f"completed: {s_total} success, {f_total} failed", 
       c['bgg'] + c['w'] if f_total == 0 else c['bgr'] + c['w'])
    
    if f_total > 0:
        failed_addresses = [addr for i, addr in enumerate(valid_addresses) 
                          if i < len(results) and (isinstance(results[i], Exception) or not results[i][0])]
        with open('failed.txt', 'w') as f:
            for addr in failed_addresses:
                f.write(addr + '\n')
        at(x + 2, y + 19, f"failed addresses saved to failed.txt", c['y'])
    
    await awaitkey()

async def exp():
    cr = sz()
    cls()
    fill()
    w, hb = 70, 15
    x = (cr[0] - w) // 2
    y = (cr[1] - hb) // 2
    box(x, y, w, hb, "export keys")
    
    at(x + 2, y + 2, "current wallet info:", c['c'])
    at(x + 2, y + 4, "address:", c['c'])
    at(x + 11, y + 4, addr[:32] + "...", c['w'])
    at(x + 2, y + 5, "balance:", c['c'])
    n, b = await st()
    at(x + 11, y + 5, f"{b:.6f} oct" if b is not None else "---", c['g'])
    
    at(x + 2, y + 7, "export options:", c['y'])
    at(x + 2, y + 8, "[1] show private key", c['w'])
    at(x + 2, y + 9, "[2] save full wallet to file", c['w'])
    at(x + 2, y + 10, "[3] copy address to clipboard", c['w'])
    at(x + 2, y + 11, "[0] cancel", c['w'])
    at(x + 2, y + 13, "choice: ", c['B'] + c['y'])
    
    choice = await ainp(x + 10, y + 13)
    choice = choice.strip()
    
    if choice == '1':
        at(x + 2, y + 7, " " * (w - 4), c['bg'])
        at(x + 2, y + 8, " " * (w - 4), c['bg'])
        at(x + 2, y + 9, " " * (w - 4), c['bg'])
        at(x + 2, y + 10, " " * (w - 4), c['bg'])
        at(x + 2, y + 11, " " * (w - 4), c['bg'])
        at(x + 2, y + 13, " " * (w - 4), c['bg'])
        
        at(x + 2, y + 7, "private key (keep secret!):", c['R'])
        at(x + 2, y + 8, priv[:32], c['R'])
        at(x + 2, y + 9, priv[32:], c['R'])
        at(x + 2, y + 11, "public key:", c['g'])
        at(x + 2, y + 12, pub[:44] + "...", c['g'])
        await awaitkey()
        
    elif choice == '2':
        fn = f"octra_wallet_{int(time.time())}.json"
        wallet_data = {
            'priv': priv,
            'addr': addr,
            'rpc': rpc
        }
        with open(fn, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        at(x + 2, y + 7, " " * (w - 4), c['bg'])
        at(x + 2, y + 8, " " * (w - 4), c['bg'])
        at(x + 2, y + 9, " " * (w - 4), c['bg'])
        at(x + 2, y + 10, " " * (w - 4), c['bg'])
        at(x + 2, y + 11, " " * (w - 4), c['bg'])
        at(x + 2, y + 13, " " * (w - 4), c['bg'])
        at(x + 2, y + 9, f"saved to {fn}", c['g'])
        at(x + 2, y + 11, "file contains private key - keep safe!", c['R'])
        await awaitkey()
        
    elif choice == '3':
        try:
            import pyperclip
            pyperclip.copy(addr)
            at(x + 2, y + 7, " " * (w - 4), c['bg'])
            at(x + 2, y + 9, "address copied to clipboard!", c['g'])
        except:
            at(x + 2, y + 7, " " * (w - 4), c['bg'])
            at(x + 2, y + 9, "clipboard not available", c['R'])
        at(x + 2, y + 11, " " * (w - 4), c['bg'])
        await awaitkey()

async def main():
    global session
    
    if not ld():
        sys.exit("[!] wallet.json error")
    if not addr:
        sys.exit("[!] wallet.json not configured")
    
    try:
        await st()
        await gh()
        
        while not stop_flag.is_set():
            cmd = await scr()
            if cmd == '1':
                await tx()
            elif cmd == '2':
                global lu, lh
                lu = lh = 0
                await st()
                await gh()
            elif cmd == '3':
                await multi()
            elif cmd == '4':
                await exp()
            elif cmd == '5':
                h.clear()
                lh = 0
            elif cmd == '6':
                await send_to_list()
            elif cmd == '7':
                await fetch_oct_addresses_screen()
            elif cmd == '8':
                await clear_wallet_list()
            elif cmd in ['0', 'q', '']:
                break
    except:
        pass
    finally:
        if session:
            await session.close()
        executor.shutdown(wait=False)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        asyncio.run(main())
    except:
        pass
    finally:
        cls()
        print(f"{c['r']}")
        os._exit(0)
