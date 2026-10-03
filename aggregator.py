#!/usr/bin/env python3
"""
Mining & Mobile Whitelist Proxy Aggregator
Aggregates VLESS Reality, Trojan, and Hysteria configurations from curated
Russian mobile whitelist bypass sources with mirror failover.
Outputs optimized Clash Meta (Mihomo) configuration with exactly 150-200 proxies.
"""

import os
import re
import sys
import copy
import urllib.parse
import yaml
import requests

TEST_URL = os.environ.get("LATENCY_TEST_URL", "https://pitbit.com")
FALLBACK_TEST_URL = "https://ya.ru"
MIN_PROXIES = 150
MAX_PROXIES = 200

SOURCES = [
    {
        "id": "igareck_mobile",
        "type": "clash_yaml",
        "mirrors": [
            "https://fastly.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/Export/Clash/GLOBAL/Vless-Reality-White-Lists-Rus-Mobile-clash-global.yaml",
            "https://cdn.jsdelivr.net/gh/igareck/vpn-configs-for-russia@main/Export/Clash/GLOBAL/Vless-Reality-White-Lists-Rus-Mobile-clash-global.yaml",
            "https://ghproxy.net/https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Export/Clash/GLOBAL/Vless-Reality-White-Lists-Rus-Mobile-clash-global.yaml",
            "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Export/Clash/GLOBAL/Vless-Reality-White-Lists-Rus-Mobile-clash-global.yaml"
        ]
    },
    {
        "id": "rkp_clash",
        "type": "clash_yaml",
        "mirrors": [
            "https://fastly.jsdelivr.net/gh/RKPchannel/RKP_bypass_configs@main/whitelist.yaml",
            "https://cdn.jsdelivr.net/gh/RKPchannel/RKP_bypass_configs@main/whitelist.yaml",
            "https://ghproxy.net/https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/main/whitelist.yaml",
            "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/main/whitelist.yaml"
        ]
    },
    {
        "id": "zieng2_wl",
        "type": "uris",
        "mirrors": [
            "https://gitverse.ru/api/repos/zieng2/wl/raw/branch/master/list_universal.txt",
            "https://hub.mos.ru/zieng2/wl/raw/main/list_universal.txt",
            "https://fastly.jsdelivr.net/gh/zieng2/wl@main/vless_universal.txt",
            "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt"
        ]
    },
    {
        "id": "flat447_white",
        "type": "uris",
        "mirrors": [
            "https://fastly.jsdelivr.net/gh/FLAT447/v2ray-lists@main/WHITE_FULL.txt",
            "https://fastly.jsdelivr.net/gh/FLAT447/v2ray-lists@main/WHITE_LITE.txt",
            "https://raw.githubusercontent.com/FLAT447/v2ray-lists/main/WHITE_FULL.txt"
        ]
    },
    {
        "id": "whoahaow_bypass",
        "type": "uris",
        "mirrors": [
            "https://fastly.jsdelivr.net/gh/whoahaow/rjsxrd@main/githubmirror/bypass/bypass-all.txt",
            "https://cdn.jsdelivr.net/gh/whoahaow/rjsxrd@main/githubmirror/bypass/bypass-all.txt",
            "https://ghproxy.net/https://raw.githubusercontent.com/whoahaow/rjsxrd/main/githubmirror/bypass/bypass-all.txt"
        ]
    },
    {
        "id": "solovyov_cidr",
        "type": "uris",
        "mirrors": [
            "https://fastly.jsdelivr.net/gh/solovyov-jenya2004/all_subs@main/final_sorted",
            "https://cdn.jsdelivr.net/gh/solovyov-jenya2004/all_subs@main/final_sorted",
            "https://raw.githubusercontent.com/solovyov-jenya2004/all_subs/main/final_sorted"
        ]
    },
    {
        "id": "vansfenix_white",
        "type": "uris",
        "mirrors": [
            "https://fastly.jsdelivr.net/gh/VansFenix/vpnparser@main/white.txt",
            "https://cdn.jsdelivr.net/gh/VansFenix/vpnparser@main/white.txt"
        ]
    }
]

def fetch_with_mirrors(mirror_list, timeout=12):
    headers = {
        "User-Agent": "ClashMeta/v1.18.10 (Mihomo; Linux)",
        "Accept": "*/*"
    }
    for url in mirror_list:
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200 and len(resp.text) > 100:
                return resp.text, url
        except Exception:
            continue
    return None, None

def parse_vless_uri(uri):
    try:
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != 'vless':
            return None
        uuid = parsed.username
        server = parsed.hostname
        port = parsed.port
        if not (uuid and server and port):
            return None
        
        name = urllib.parse.unquote(parsed.fragment).strip() if parsed.fragment else f"VLESS-{server}:{port}"
        query = urllib.parse.parse_qs(parsed.query)
        
        security = query.get('security', ['none'])[0]
        net_type = query.get('type', ['tcp'])[0]
        sni = query.get('sni', [query.get('serverName', [''])[0]])[0]
        fp = query.get('fp', ['chrome'])[0]
        flow = query.get('flow', [''])[0]
        pbk = query.get('pbk', [query.get('publicKey', [''])[0]])[0]
        sid = query.get('sid', [query.get('shortId', [''])[0]])[0]
        spx = query.get('spx', ['/'])[0]
        
        proxy = {
            'name': name,
            'type': 'vless',
            'server': server,
            'port': int(port),
            'uuid': uuid,
            'udp': True,
            'client-fingerprint': fp or 'chrome'
        }
        
        if security == 'reality':
            proxy['tls'] = True
            proxy['servername'] = sni
            proxy['reality-opts'] = {
                'public-key': pbk,
                'short-id': sid
            }
            if spx and spx != '/':
                proxy['reality-opts']['spider-x'] = spx
        elif security == 'tls':
            proxy['tls'] = True
            if sni:
                proxy['servername'] = sni
                
        if flow:
            proxy['flow'] = flow
            
        if net_type == 'grpc':
            proxy['network'] = 'grpc'
            service_name = query.get('serviceName', [''])[0]
            if service_name:
                proxy['grpc-opts'] = {'grpc-service-name': service_name}
        elif net_type == 'ws':
            proxy['network'] = 'ws'
            path = query.get('path', ['/'])[0]
            proxy['ws-opts'] = {'path': path}
            if sni:
                proxy['ws-opts']['headers'] = {'Host': sni}
                
        return proxy
    except Exception:
        return None

def parse_trojan_uri(uri):
    try:
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != 'trojan':
            return None
        password = parsed.username
        server = parsed.hostname
        port = parsed.port
        if not (password and server and port):
            return None
            
        name = urllib.parse.unquote(parsed.fragment).strip() if parsed.fragment else f"Trojan-{server}:{port}"
        query = urllib.parse.parse_qs(parsed.query)
        sni = query.get('sni', [''])[0]
        
        return {
            'name': name,
            'type': 'trojan',
            'server': server,
            'port': int(port),
            'password': password,
            'udp': True,
            'sni': sni,
            'skip-cert-verify': True
        }
    except Exception:
        return None

def parse_hysteria2_uri(uri):
    try:
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme not in ('hysteria2', 'hy2'):
            return None
        password = parsed.username
        server = parsed.hostname
        port = parsed.port
        if not (password and server and port):
            return None
            
        name = urllib.parse.unquote(parsed.fragment).strip() if parsed.fragment else f"Hy2-{server}:{port}"
        query = urllib.parse.parse_qs(parsed.query)
        sni = query.get('sni', [''])[0]
        
        return {
            'name': name,
            'type': 'hysteria2',
            'server': server,
            'port': int(port),
            'password': password,
            'udp': True,
            'sni': sni,
            'skip-cert-verify': True
        }
    except Exception:
        return None

def is_russian_node(proxy):
    name = proxy.get('name', '').lower()
    sni = proxy.get('servername', '') or proxy.get('sni', '')
    sni = str(sni).lower()
    
    ru_keywords = ['🇷🇺', 'russia', 'россия', 'ru ', '[ru', 'moscow', 'spb', 'москва', 'санкт-петербург']
    if any(k in name for k in ru_keywords):
        return True
    
    white_sni_patterns = ['yandex', 'vk.com', 'userapi', 'mail.ru', 'x5.ru', 'sber', 'gosuslugi', 'cdnvideo', 'beeline']
    if any(p in sni for p in white_sni_patterns):
        return True
        
    return False

def clean_and_normalize_name(name, server, port, index):
    clean = re.sub(r'[\r\n\t]+', ' ', name).strip()
    clean = re.sub(r'^(GB【机场推荐.*?】\d*|🇬🇧\[openproxylist.*?\])\s*', '', clean).strip()
    if not clean or len(clean) < 3:
        clean = f"Node-{server}:{port}"
    return f"{clean} #{index:03d}"

def collect_proxies():
    raw_proxies = []
    
    for src in SOURCES:
        content, mirror_url = fetch_with_mirrors(src["mirrors"])
        if not content:
            print(f"[-] Warning: Failed to fetch {src['id']} from all mirrors.")
            continue
        print(f"[+] Fetched {src['id']} from {mirror_url}")
        
        if src["type"] == "clash_yaml":
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict) and "proxies" in data:
                    for p in data["proxies"]:
                        if isinstance(p, dict) and p.get("server") and p.get("port"):
                            raw_proxies.append(p)
            except Exception as e:
                print(f"[-] YAML parse error for {src['id']}: {e}")
        elif src["type"] == "uris":
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                p = None
                if line.startswith("vless://"):
                    p = parse_vless_uri(line)
                elif line.startswith("trojan://"):
                    p = parse_trojan_uri(line)
                elif line.startswith("hysteria2://") or line.startswith("hy2://"):
                    p = parse_hysteria2_uri(line)
                if p and p.get("server") and p.get("port"):
                    raw_proxies.append(p)
                    
    print(f"[*] Total raw proxies harvested: {len(raw_proxies)}")
    
    # Deduplication by (server, port)
    seen_endpoints = set()
    deduped = []
    for p in raw_proxies:
        endpoint = f"{str(p['server']).strip()}:{p['port']}"
        if endpoint in seen_endpoints:
            continue
        seen_endpoints.add(endpoint)
        deduped.append(p)
        
    print(f"[*] Unique proxies after endpoint deduplication: {len(deduped)}")
    
    # Classify into foreign and RU reserve
    foreign_nodes = []
    ru_nodes = []
    for p in deduped:
        if is_russian_node(p):
            ru_nodes.append(p)
        else:
            foreign_nodes.append(p)
            
    print(f"[*] Classified: {len(foreign_nodes)} foreign nodes, {len(ru_nodes)} RU reserve nodes")
    
    # Smart Capping to 150-200 nodes
    # Balance: up to 135 foreign nodes + up to 55 RU reserve nodes
    target_foreign = min(len(foreign_nodes), 135)
    target_ru = min(len(ru_nodes), 55)
    
    selected = foreign_nodes[:target_foreign] + ru_nodes[:target_ru]
    
    # If total selected is less than MIN_PROXIES, take remaining foreign or RU
    if len(selected) < MIN_PROXIES:
        remainder_foreign = foreign_nodes[target_foreign:]
        remainder_ru = ru_nodes[target_ru:]
        needed = MIN_PROXIES - len(selected)
        selected += remainder_foreign[:needed]
        needed = MIN_PROXIES - len(selected)
        if needed > 0:
            selected += remainder_ru[:needed]
        
    # If still more than MAX_PROXIES, hard cap at MAX_PROXIES (e.g. 190)
    if len(selected) > MAX_PROXIES:
        selected = selected[:MAX_PROXIES]
        
    print(f"[*] Final curated node count: {len(selected)} (target: {MIN_PROXIES}-{MAX_PROXIES})")
    
    # Assign unique clean names
    final_proxies = []
    used_names = set()
    for idx, p in enumerate(selected, 1):
        item = copy.deepcopy(p)
        base_name = clean_and_normalize_name(item.get("name", "Node"), item["server"], item["port"], idx)
        name = base_name
        counter = 1
        while name in used_names:
            name = f"{base_name}-{counter}"
            counter += 1
        used_names.add(name)
        item["name"] = name
        final_proxies.append(item)
        
    return final_proxies

def build_clash_config(proxies):
    proxy_names = [p["name"] for p in proxies]
    foreign_names = [p["name"] for p in proxies if not is_russian_node(p)]
    ru_names = [p["name"] for p in proxies if is_russian_node(p)]
    
    if not foreign_names:
        foreign_names = proxy_names[:]
    if not ru_names:
        ru_names = proxy_names[:]

    config = {
        "port": 7890,
        "socks-port": 7891,
        "mixed-port": 7893,
        "allow-lan": True,
        "mode": "rule",
        "log-level": "info",
        "unified-delay": True,
        "tcp-concurrent": True,
        "external-controller": "127.0.0.1:9090",
        "profile": {
            "store-selected": True,
            "store-fake-ip": True
        },
        "dns": {
            "enable": True,
            "ipv6": False,
            "enhanced-mode": "fake-ip",
            "fake-ip-range": "198.18.0.1/16",
            "nameserver": [
                "1.1.1.1",
                "8.8.8.8",
                "77.88.8.8",
                "https://cloudflare-dns.com/dns-query"
            ]
        },
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "🚀 VIP-Auto-Select",
                "type": "url-test",
                "url": TEST_URL,
                "interval": 180,
                "tolerance": 50,
                "timeout": 3000,
                "proxies": foreign_names
            },
            {
                "name": "🛡️ Emergency-Fallback",
                "type": "fallback",
                "url": TEST_URL,
                "interval": 120,
                "timeout": 3000,
                "proxies": ["🚀 VIP-Auto-Select", "🇷🇺 Russian-Reserve"]
            },
            {
                "name": "🇷🇺 Russian-Reserve",
                "type": "url-test",
                "url": FALLBACK_TEST_URL,
                "interval": 300,
                "tolerance": 100,
                "timeout": 3000,
                "proxies": ru_names
            },
            {
                "name": "🌐 Manual-Select",
                "type": "select",
                "proxies": ["🚀 VIP-Auto-Select", "🛡️ Emergency-Fallback", "🇷🇺 Russian-Reserve"] + proxy_names
            },
            {
                "name": "GLOBAL",
                "type": "select",
                "proxies": ["🚀 VIP-Auto-Select", "🛡️ Emergency-Fallback", "🌐 Manual-Select"]
            }
        ],
        "rules": [
            # Russian Whitelist & Domestic Services (Direct without proxy)
            "DOMAIN-SUFFIX,yandex.ru,DIRECT",
            "DOMAIN-SUFFIX,ya.ru,DIRECT",
            "DOMAIN-SUFFIX,vk.com,DIRECT",
            "DOMAIN-SUFFIX,userapi.com,DIRECT",
            "DOMAIN-SUFFIX,gosuslugi.ru,DIRECT",
            "DOMAIN-SUFFIX,sberbank.ru,DIRECT",
            "DOMAIN-SUFFIX,tbank.ru,DIRECT",
            "GEOSITE,category-ru,DIRECT",
            "GEOIP,RU,DIRECT",

            # Stratum Mining Pools and ASIC Pitbit MUST route through VIP Proxy!
            "DOMAIN-KEYWORD,trustpool,🚀 VIP-Auto-Select",
            "DOMAIN-KEYWORD,stratum,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,trustpool.ru,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,trustpool.cc,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,viabtc.com,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,emcd.io,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,antpool.com,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,f2pool.com,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,binance.com,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,pitbit.com,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,pitbit.io,🚀 VIP-Auto-Select",
            "DOMAIN-SUFFIX,pitbit.ru,🚀 VIP-Auto-Select",
            "DST-PORT,3333,🚀 VIP-Auto-Select",
            "DST-PORT,4433,🚀 VIP-Auto-Select",
            "DST-PORT,25,🚀 VIP-Auto-Select",
            "DST-PORT,8000,🚀 VIP-Auto-Select",
            "DST-PORT,8888,🚀 VIP-Auto-Select",
            
            # Default Routing
            "MATCH,🚀 VIP-Auto-Select"
        ]
    }
    return config

def main():
    print(f"[*] Starting Whitelist Proxy Aggregator...")
    print(f"[*] Latency test target: {TEST_URL}")
    
    proxies = collect_proxies()
    if len(proxies) < 10:
        print("[-] Critical Error: Less than 10 proxies collected. Aborting generation.")
        sys.exit(1)
        
    config = build_clash_config(proxies)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clash.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
    print(f"[+] Successfully generated {output_path} with {len(proxies)} proxies.")
    
    # Also generate plain nodes list
    nodes_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nodes.txt")
    with open(nodes_txt_path, "w", encoding="utf-8") as f:
        for p in proxies:
            f.write(f"# {p['name']}\n")
            f.write(f"{p['type']}://{p.get('uuid', p.get('password', ''))}@{p['server']}:{p['port']}\n\n")
    print(f"[+] Successfully generated {nodes_txt_path}")

if __name__ == "__main__":
    main()
