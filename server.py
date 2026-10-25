#!/usr/bin/env python3
"""Local web server and best-effort live REWE Syke offers reader.
Uses only Python standard library. Public offer pages can change their markup,
so the extraction is intentionally best-effort and errors are reported to UI.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from urllib.error import URLError, HTTPError
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import json, re

BASE = Path(__file__).resolve().parent
OFFERS_URL = "https://www.rewe.de/angebote/syke/540502/rewe-hauptstr-56-58-suurend/"

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"): self.skip += 1
        if tag in ("br", "p", "div", "li", "h1", "h2", "h3", "article"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip: self.skip -= 1
        if tag in ("p", "div", "li", "h1", "h2", "h3", "article"): self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            value=" ".join(data.split())
            if value: self.parts.append(value)

def extract_offers(html):
    parser=TextExtractor(); parser.feed(html)
    text="\n".join(parser.parts)
    lines=[re.sub(r"\s+"," ",x).strip() for x in text.splitlines()]
    lines=[x for x in lines if x]
    found=[]; seen=set()
    # Offer pages typically expose product title and price in nearby text nodes.
    for i,line in enumerate(lines):
        m=re.search(r"(?<!\d)(\d{1,3}[,.]\d{2})\s*€",line)
        if not m: continue
        price=m.group(1).replace('.',',')+' €'
        before=' '.join(lines[max(0,i-5):i+1])
        # Prefer a recognizable product-title line from the nearby context.
        candidates=[]
        for candidate in lines[max(0,i-6):i+1]:
            c=re.sub(r"\s+"," ",candidate).strip()
            if (len(c)>2 and len(c)<100 and not re.search(r"€|kg\s*=|l\s*=|Knaller|Aktion|Bonus|je \d|versch\. Sorten|gültig|Angebote|Prospekt",c,re.I)):
                candidates.append(c)
        name=candidates[-1] if candidates else before[-80:]
        key=(name.lower(),price)
        if key in seen: continue
        seen.add(key)
        detail=''
        if i+1<len(lines) and len(lines[i+1])<100 and not re.search(r"€|Knaller|Aktion",lines[i+1],re.I): detail=lines[i+1]
        found.append({"name":name,"price":price,"detail":detail})
        if len(found)>=30: break
    return found

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(BASE),**kwargs)
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()
    def do_GET(self):
        if self.path.split('?',1)[0] != '/api/offers':
            return super().do_GET()
        try:
            req=Request(OFFERS_URL,headers={"User-Agent":"Mozilla/5.0 (compatible; LocalFoodBudgetCalculator/1.0)","Accept-Language":"de-DE,de;q=0.9,en;q=0.7"})
            with urlopen(req,timeout=15) as resp:
                html=resp.read().decode('utf-8','replace')
            offers=extract_offers(html)
            payload={"offers":offers,"updated_at":datetime.now(ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y %H:%M'),"source":OFFERS_URL,"note":"Nur öffentlich sichtbare Angebotsdaten; keine vollständige Sortiments- oder Regalpreisliste."}
            if not offers: payload["message"]="Die REWE-Seite wurde erreicht, aber ihre aktuelle Darstellung ließ sich nicht automatisch in einzelne Angebote zerlegen. Bitte nutze den offiziellen REWE-Link."
            body=json.dumps(payload,ensure_ascii=False).encode('utf-8')
            self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        except (HTTPError,URLError,TimeoutError,OSError) as e:
            body=json.dumps({"error":f"REWE konnte nicht abgerufen werden ({e}).","offers":[]},ensure_ascii=False).encode('utf-8')
            self.send_response(502);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,fmt,*args): print("[%s] %s"%(self.log_date_time_string(),fmt%args))

if __name__ == '__main__':
    server=ThreadingHTTPServer(('127.0.0.1',8000),Handler)
    print('Food-Rechner läuft: http://127.0.0.1:8000/index.html')
    print('Beenden mit Strg+C')
    try: server.serve_forever()
    except KeyboardInterrupt: print('\nServer beendet.')
    finally: server.server_close()
