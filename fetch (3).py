#!/usr/bin/env python3
"""
RAPTOR Chart Engine — fetch.py
Scarica dati OHLC da Yahoo Finance per tutti i ticker RAPTOR Leva
e salva un file JSON per ticker nella cartella data/
Eseguito da GitHub Actions 2x al giorno
"""

import os
import json
import time
import math
import logging
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── CONFIGURAZIONE ──────────────────────────────────────────
OUTPUT_DIR = "data"
PERIOD     = "2y"
INTERVAL   = "1d"
DELAY      = 0.5   # secondi tra richieste (evita rate limit)

TICKERS = [
  {"ticker": "EZNC", "name": "WisdomTree Zinc - EUR Daily Hedged"},
  {"ticker": "ZINC", "name": "WisdomTree Zinc"},
  {"ticker": "2CAR", "name": "WisdomTree STOXX Europe Automobiles 2x Daily Leveraged"},
  {"ticker": "AIGL", "name": "WisdomTree Livestock"},
  {"ticker": "2UKL", "name": "WisdomTree FTSE 100 2x Daily Leveraged"},
  {"ticker": "3LNF", "name": "GraniteShares 3x Long Netflix Daily Etp"},
  {"ticker": "PIMT", "name": "WisdomTree Industrial Metals - GBP Daily Hedged"},
  {"ticker": "COTN", "name": "WisdomTree Cotton"},
  {"ticker": "ECTN", "name": "WisdomTree Cotton - EUR Daily Hedged"},
  {"ticker": "EALU", "name": "WisdomTree Aluminium - EUR Daily Hedged"},
  {"ticker": "5MIB", "name": "GraniteShares 5x Long Mib Daily Etp"},
  {"ticker": "LALU", "name": "WisdomTree Aluminium 2x Daily Leveraged"},
  {"ticker": "ALUM", "name": "WisdomTree Aluminium"},
  {"ticker": "3UKL", "name": "WisdomTree FTSE 100 3x Daily Leveraged"},
  {"ticker": "3ITL", "name": "WisdomTree FTSE MIB 3x Daily Leveraged"},
  {"ticker": "SOYO", "name": "WisdomTree Soybean Oil"},
  {"ticker": "UNH3", "name": "Leverage Shares 3x Long Unitedhealth (Unh) Etp Securities"},
  {"ticker": "3MST", "name": "Leverage Shares 3x Long MicroStrategy Etp"},
  {"ticker": "3OIL", "name": "WisdomTree WTI Crude Oil 3x Daily Leveraged"},
  {"ticker": "PCRD", "name": "WisdomTree WTI Crude Oil - GBP Daily Hedged"},
  {"ticker": "3LNI", "name": "GraniteShares 3x Long NIO Daily Etp"},
  {"ticker": "PBRT", "name": "WisdomTree Brent Crude Oil - GBP Daily Hedged"},
  {"ticker": "3NIO", "name": "Leverage Shares 3x NIO Etp Securities"},
  {"ticker": "3NFL", "name": "Leverage Shares 3x Netflix Etp Securities"},
  {"ticker": "WCOA", "name": "WisdomTree Enhanced Commodity UCITS ETF USD Acc"},
  {"ticker": "ARM3", "name": "Leverage Shares 3x Arm Etp Securities"},
  {"ticker": "EIMT", "name": "WisdomTree Industrial Metals - EUR Daily Hedged"},
  {"ticker": "WCOM", "name": "WisdomTree Enhanced Commodity UCITS ETF - GBP Hedged Acc"},
  {"ticker": "AIGE", "name": "WisdomTree Energy"},
  {"ticker": "WTI", "name": "Leverage Shares Wti Oil Etc"},
  {"ticker": "LWEA", "name": "WisdomTree Wheat 2x Daily Leveraged"},
  {"ticker": "3AMD", "name": "Leverage Shares 3x AMD Etp Securities"},
  {"ticker": "BRENT", "name": "Leverage Shares Brent Oil Etc"},
  {"ticker": "LOIL", "name": "WisdomTree WTI Crude Oil 2x Daily Leveraged"},
  {"ticker": "3MG7", "name": "WisdomTree Magnificent 7 3x Daily Leveraged"},
  {"ticker": "3BRL", "name": "WisdomTree Brent Crude Oil 3x Daily Leveraged"},
  {"ticker": "3WHL", "name": "WisdomTree Wheat 3x Daily Leveraged"},
  {"ticker": "3LAM", "name": "GraniteShares 3x Long AMD Daily Etp"},
  {"ticker": "3CAC", "name": "WisdomTree CAC 40 3x Daily Leveraged"},
  {"ticker": "3GOO", "name": "Leverage Shares 3x Alphabet Etp Securities"},
  {"ticker": "CORN", "name": "WisdomTree Corn"},
  {"ticker": "3LSP", "name": "GraniteShares 3x Long Intesa Sanpaolo Daily Etp"},
  {"ticker": "CPER", "name": "Leverage Shares Copper Etc"},
  {"ticker": "5EUL", "name": "WisdomTree EURO STOXX 50 5x Daily Leveraged"},
  {"ticker": "2MCL", "name": "WisdomTree FTSE 250 2x Daily Leveraged"},
  {"ticker": "3LPP", "name": "GraniteShares 3x Long PayPal Daily Etp"},
  {"ticker": "3BAL", "name": "WisdomTree EURO STOXX Banks 3x Daily Leveraged"},
  {"ticker": "2TRV", "name": "WisdomTree STOXX Europe Travel & Leisure 2x Daily Leveraged"},
  {"ticker": "3FNG", "name": "GraniteShares 3x Long Faang Etp"},
  {"ticker": "LCOP", "name": "WisdomTree Copper 2x Daily Leveraged"},
  {"ticker": "3EUL", "name": "WisdomTree EURO STOXX 50® 3x Daily Leveraged"},
  {"ticker": "WS5X", "name": "WisdomTree EURO STOXX 50"},
  {"ticker": "3LAL", "name": "GraniteShares 3x Long Alphabet Daily Etp"},
  {"ticker": "WRTY", "name": "WisdomTree Russell 2000"},
  {"ticker": "3SEM", "name": "WisdomTree PHLX Semiconductor 3x Daily Leveraged"},
  {"ticker": "3LSQ", "name": "GraniteShares 3x Long Square Daily Etp"},
  {"ticker": "3LPO", "name": "GraniteShares 3x Long Spotify Daily Etp"},
  {"ticker": "3LCO", "name": "GraniteShares 3x Long Coinbase Daily Etp"},
  {"ticker": "ECOF", "name": "WisdomTree Coffee - EUR Daily Hedged"},
  {"ticker": "SUGA", "name": "WisdomTree Sugar"},
  {"ticker": "3CON", "name": "Leverage Shares 3x Long Coinbase Etp Securities"},
  {"ticker": "3LMI", "name": "GraniteShares 3x Long MicroStrategy Daily Etp"},
  {"ticker": "3LMS", "name": "GraniteShares 3x Long Microsoft Daily Etp"},
  {"ticker": "AIGS", "name": "WisdomTree Softs"},
  {"ticker": "3AMZ", "name": "Leverage Shares 3x Amazon Etp Securities"},
  {"ticker": "ENIK", "name": "WisdomTree Nickel - EUR Daily Hedged"},
  {"ticker": "3RAC", "name": "Leverage Shares 3x Long Ferrari (RACE) Etp"},
  {"ticker": "3LTS", "name": "GraniteShares 3x Long Tesla Daily Etp"},
  {"ticker": "CARB", "name": "WisdomTree Carbon"},
  {"ticker": "COCO", "name": "WisdomTree Cocoa"},
  {"ticker": "3BUL", "name": "WisdomTree Bund 10Y 3x Daily Leveraged"},
  {"ticker": "LCOC", "name": "WisdomTree Cocoa 2x Daily Leveraged"},
  {"ticker": "LPLA", "name": "WisdomTree Platinum 2x Daily Leveraged"},
  {"ticker": "ECOP", "name": "WisdomTree Copper - EUR Daily Hedged"},
  {"ticker": "3HCL", "name": "WisdomTree Copper 3x Daily Leveraged"},
  {"ticker": "3MSF", "name": "Leverage Shares 3x Microsoft Etp Securities"},
  {"ticker": "3TSL", "name": "Leverage Shares 3x Tesla Etp"},
  {"ticker": "3LAP", "name": "GraniteShares 3x Long Apple Daily Etp"},
  {"ticker": "3LUB", "name": "GraniteShares 3x Long Uber Daily Etp"},
  {"ticker": "3LPA", "name": "GraniteShares 3x Long Palantir Daily Etp"},
  {"ticker": "5SPY", "name": "Leverage Shares 5x Long S&P 500 Etp"},
  {"ticker": "3UBR", "name": "Leverage Shares 3x Uber Etp Securities"},
  {"ticker": "3GIL", "name": "WisdomTree Gilts 10Y 3x Daily Leveraged"},
  {"ticker": "3DEL", "name": "WisdomTree DAX 3x Daily Leveraged"},
  {"ticker": "3LAA", "name": "GraniteShares 3x Long Alibaba Daily Etp"},
  {"ticker": "3FB", "name": "Leverage Shares 3x Facebook Etp Securities"},
  {"ticker": "3LCR", "name": "GraniteShares 3x Long Unicredit Daily Etp"},
  {"ticker": "WNAS", "name": "WisdomTree NASDAQ-100"},
  {"ticker": "3EML", "name": "WisdomTree Emerging Markets 3x Daily Leveraged"},
  {"ticker": "3BAB", "name": "Leverage Shares 3x Alibaba Etp Securities"},
  {"ticker": "3AAP", "name": "Leverage Shares 3x Apple Etp Securities"},
  {"ticker": "QQQ3", "name": "WisdomTree NASDAQ 100 3x Daily Leveraged"},
  {"ticker": "WSPX", "name": "WisdomTree S&P 500"},
  {"ticker": "3LFB", "name": "GraniteShares 3x Long Facebook Daily Etp"},
  {"ticker": "3CFL", "name": "WisdomTree Coffee 3x Daily Leveraged"},
  {"ticker": "3LNV", "name": "GraniteShares 3x Long NVIDIA Daily Etp"},
  {"ticker": "GAS", "name": "Leverage Shares Natural Gas Etc"},
  {"ticker": "3SUL", "name": "WisdomTree Sugar 3x Daily Leveraged"},
  {"ticker": "3OIS", "name": "WisdomTree WTI Crude Oil 3x Daily Short"},
  {"ticker": "PHPT", "name": "WisdomTree Physical Platinum"},
  {"ticker": "3NGL", "name": "WisdomTree Natural Gas 3x Daily Leveraged"},
  {"ticker": "3USL", "name": "WisdomTree S&P 500 3x Daily Leveraged"},
  {"ticker": "3TYL", "name": "WisdomTree US Treasuries 10Y 3x Daily Leveraged"},
  {"ticker": "LSUG", "name": "WisdomTree Sugar 2x Daily Leveraged"},
  {"ticker": "SLVR", "name": "WisdomTree Silver"},
  {"ticker": "FAAN", "name": "Leverage Shares Faang+ Etp"},
  {"ticker": "3PYP", "name": "Leverage Shares 3x PayPal Etp Securities"},
  {"ticker": "ESOY", "name": "WisdomTree Soybeans - EUR Daily Hedged"},
  {"ticker": "SOXL", "name": "Leverage Shares 4x Long Semiconductors Etp"},
  {"ticker": "3NVD", "name": "Leverage Shares 3x NVIDIA Etp Securities"},
  {"ticker": "LCOR", "name": "WisdomTree Corn 2x Daily Leveraged"},
  {"ticker": "GPT3", "name": "Leverage Shares 3x Long Artificial Intelligence (AI) Etp"},
  {"ticker": "2PAL", "name": "WisdomTree Palladium 2x Daily Leveraged"},
  {"ticker": "3SIL", "name": "WisdomTree Silver 3x Daily Leveraged"},
  {"ticker": "LCFE", "name": "WisdomTree Coffee 2x Daily Leveraged"},
  {"ticker": "5QQQ", "name": "Leverage Shares 5x Long Nasdaq 100 Etp"},
  {"ticker": "3MRN", "name": "Leverage Shares 3x Long Moderna Etp Securities"},
  {"ticker": "3LZN", "name": "GraniteShares 3x Long Amazon Daily Etp"},
  {"ticker": "3GOL", "name": "WisdomTree Gold 3x Daily Leveraged"},
  {"ticker": "3LMO", "name": "GraniteShares 3x Long Moderna Daily Etp"},
  {"ticker": "NCLR", "name": "WisdomTree Uranium and Nuclear Energy UCITS ETF - USD Acc"},
  {"ticker": "3SQ", "name": "Leverage Shares 3x Square Etp Securities"},
  {"ticker": "FANG", "name": "GraniteShares Faang Etp"},
  {"ticker": "3EDF", "name": "WisdomTree STOXX Europe Aerospace & Defence 3x Daily Leveraged"},
  {"ticker": "SMCI", "name": "Leverage Shares 2x Super Micro Computer Etp"},
  {"ticker": "3BTL", "name": "WisdomTree BTP 10Y 3x Daily Leveraged"},
]

# ── INDICATORI ──────────────────────────────────────────────
def calc_kama(closes, n=10, fast=5, slow=20):
    fsc = 2/(fast+1); ssc = 2/(slow+1)
    k = [None]*len(closes)
    if len(closes) <= n: return k
    k[n-1] = closes[n-1]
    for i in range(n, len(closes)):
        direction = abs(closes[i] - closes[i-n])
        noise = sum(abs(closes[j]-closes[j-1]) for j in range(i-n+1, i+1))
        er = direction/noise if noise else 0
        sc = (er*(fsc-ssc)+ssc)**2
        k[i] = k[i-1] + sc*(closes[i]-k[i-1])
    return k

def calc_er(closes, period=10):
    er = [None]*len(closes)
    for i in range(period, len(closes)):
        direction = abs(closes[i]-closes[i-period])
        noise = sum(abs(closes[j]-closes[j-1]) for j in range(i-period+1, i+1))
        er[i] = direction/noise if noise else 0
    return er

def calc_atr(highs, lows, closes, period=14):
    """Average True Range — True Range = max(H-L, |H-Cprev|, |L-Cprev|)"""
    atr = [None]*len(closes)
    if len(closes) < period+1: return atr
    # Prima TR semplice
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        trs.append(tr)
    # Prima ATR = media semplice dei primi period TR
    atr[period] = sum(trs[:period]) / period
    # ATR successivi = Wilder smoothing
    for i in range(period+1, len(closes)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        atr[i] = (atr[i-1]*(period-1) + tr) / period
    return atr

def get_sar_step(highs, lows, closes, atr_vals, lookback=60):
    """
    Determina lo step SAR adattivo basato su ATR% medio degli ultimi lookback giorni.
    ATR% = ATR / prezzo × 100
    """
    last = len(closes)-1
    start = max(0, last-lookback)
    valid = [(atr_vals[i]/closes[i]*100) for i in range(start, last+1) if atr_vals[i] is not None and closes[i]>0]
    if not valid: return 0.02, 0.0
    atr_pct_avg = sum(valid)/len(valid)
    if atr_pct_avg < 1.5:   step = 0.020   # Materie prime lente
    elif atr_pct_avg < 3.0: step = 0.015   # ETP indici standard
    elif atr_pct_avg < 5.0: step = 0.012   # ETP leva tech
    else:                   step = 0.008   # ETP leva estrema
    return step, round(atr_pct_avg, 3)

def calc_sar(highs, lows, closes, step=0.02, max_af=0.2):
    n = len(closes)
    sar_vals = [None]*n; sar_bull = [None]*n
    if n < 2: return sar_vals, sar_bull
    bull = closes[1] > closes[0]
    af = step; ep = highs[0] if bull else lows[0]; sar = lows[0] if bull else highs[0]
    for i in range(1, n):
        sar_vals[i] = sar; sar_bull[i] = bull
        if bull:
            if lows[i] < sar:
                bull=False; sar=ep; af=step; ep=lows[i]
            else:
                if highs[i] > ep: ep=highs[i]; af=min(af+step, max_af)
                sar += af*(ep-sar)
                sar = min(sar, lows[i-1], lows[i-2] if i>1 else lows[i-1])
        else:
            if highs[i] > sar:
                bull=True; sar=ep; af=step; ep=highs[i]
            else:
                if lows[i] < ep: ep=lows[i]; af=min(af+step, max_af)
                sar += af*(ep-sar)
                sar = max(sar, highs[i-1], highs[i-2] if i>1 else highs[i-1])
    return sar_vals, sar_bull

def calc_ao(highs, lows):
    mid = [(h+l)/2 for h,l in zip(highs,lows)]
    ao = [None]*len(mid)
    for i in range(33, len(mid)):
        sma5  = sum(mid[i-4:i+1])/5
        sma34 = sum(mid[i-33:i+1])/34
        ao[i] = sma5 - sma34
    return ao

def calc_rsi(closes, period=14):
    rsi = [None]*len(closes)
    if len(closes) <= period: return rsi
    gains = losses = 0
    for i in range(1, period+1):
        d = closes[i]-closes[i-1]
        if d>0: gains+=d
        else: losses+=abs(d)
    ag = gains/period; al = losses/period
    rsi[period] = 100 if al==0 else 100-100/(1+ag/al)
    for i in range(period+1, len(closes)):
        d = closes[i]-closes[i-1]
        ag = (ag*(period-1)+max(d,0))/period
        al = (al*(period-1)+max(-d,0))/period
        rsi[i] = 100 if al==0 else 100-100/(1+ag/al)
    return rsi

def calc_score(i, closes, kama_f, er, sar_b, ao):
    s = 50
    if kama_f[i] is not None and closes[i] > kama_f[i]: s += 10
    if er[i] is not None:
        if er[i] > 0.6: s += 15
        elif er[i] > 0.4: s += 8
        elif er[i] < 0.3: s -= 10
    if sar_b[i]: s += 10
    if ao[i] is not None and ao[i] > 0: s += 10
    if ao[i] is not None and ao[i] < 0: s -= 5
    return max(0, min(100, s))

def kama_derivative(kama_arr, i, n=1):
    """
    Calcola la derivata della KAMA — quante barre consecutive sta salendo.
    Ritorna: numero positivo = barre consecutive in salita, 0 = piatta, -1 = scende
    """
    if i < 1 or kama_arr[i] is None or kama_arr[i-1] is None: return 0
    # Conta barre consecutive in salita
    count = 0
    for j in range(i, max(0, i-5), -1):
        if kama_arr[j] is None or kama_arr[j-1] is None: break
        diff = kama_arr[j] - kama_arr[j-1]
        pct  = abs(diff) / kama_arr[j-1] if kama_arr[j-1] else 0
        if diff > 0 and pct > 0.0001:  # soglia minima 0.01% per escludere piatto
            count += 1
        else:
            break
    if count == 0:
        # controlla se scende
        diff = kama_arr[i] - kama_arr[i-1]
        return -1 if diff < 0 else 0
    return count

def calc_signal(i, closes, kama_f, kama_s, er, sar_b, ao, scores):
    """
    Logica segnali v3:
    1. BUY1: SAR bull + KAMA Veloce in salita 2+ barre + ER > 0.35 + prezzo > KAMA Lenta
    2. BUY2: SAR bull + KAMA Veloce in salita 2+ barre + AO > 0 + ER > 0.50 + score >= 70 + prezzo > KAMA Lenta
    3. BUY3: tutto BUY2 + KAMA Veloce in salita 3+ barre + ER > 0.65 + score crescente
    4. EXIT: invariate rispetto a v2
    5. Filtro strutturale: prezzo > KAMA Lenta obbligatorio per tutti i BUY
    """
    if i < 35: return 'NONE'
    kfv = kama_f[i]; ksv = kama_s[i]; erv = er[i]; erp = er[i-1]
    aov = ao[i]; aop = ao[i-1]
    sb = sar_b[i]; sc = scores[i]; scp = scores[i-1]
    if kfv is None or ksv is None or erv is None or aov is None: return 'NONE'
    p = closes[i]

    above_kf  = p > kfv
    above_ks  = p > ksv
    er_grow   = erv > (erp or 0)
    ao_grow   = aov > (aop or 0)
    ao_pos    = aov > 0
    sc_grow   = sc > scp

    # Derivata KAMA Veloce — quante barre consecutive in salita
    kf_deriv  = kama_derivative(kama_f, i)
    kf_rising2 = kf_deriv >= 2   # sale da almeno 2 barre
    kf_rising3 = kf_deriv >= 3   # sale da almeno 3 barre

    # EXIT — non filtrate da KAMA Lenta
    neg = sum([not above_kf, not ao_pos, erv < 0.3, not sb])
    if sc < 35 or neg >= 2: return 'EXIT3'
    if sc < 50 and erv < 0.5:   return 'EXIT2'
    if not sb or (not ao_pos and sc < 70): return 'EXIT1'

    # BUY — filtro strutturale obbligatorio
    if not above_ks: return 'WATCH'

    # BUY3: SAR + KAMA sale 3+ barre + AO>0 + ER>0.65 + score>=70 + crescente + prezzo>KAMAl
    if sb and kf_rising3 and ao_pos and erv > 0.65 and sc >= 70 and sc_grow and above_ks:
        return 'BUY3'
    # BUY2: SAR + KAMA sale 2+ barre + AO>0 + ER>0.50 + score>=70 + prezzo>KAMAl
    if sb and kf_rising2 and ao_pos and erv > 0.50 and sc >= 70 and above_ks:
        return 'BUY2'
    # BUY1: SAR + KAMA sale 2+ barre + ER>0.35 + prezzo>KAMAl
    if sb and kf_rising2 and erv > 0.35 and above_ks:
        return 'BUY1'
    return 'WATCH'

GRACE_PERIOD = 3   # giorni dall'entrata in cui EXIT3 è ignorata

def simulate_trades(bars, signals):
    trades = []
    in_trade = False; ent_i = -1; ent_p = 0; ent_sig = ''; days = 0
    for i, (bar, sig) in enumerate(zip(bars, signals)):
        price = bar['close']
        if not in_trade:
            if sig in ('BUY1','BUY2','BUY3'):
                in_trade=True; ent_i=i; ent_p=price; ent_sig=sig; days=0
        else:
            days += 1
            # Grace period: EXIT3 ignorata nei primi GRACE_PERIOD giorni
            effective_sig = sig
            if sig == 'EXIT3' and days <= GRACE_PERIOD:
                effective_sig = 'HOLD'   # non uscire ancora
            time_stop = ent_sig=='BUY1' and days>=7 and effective_sig not in ('BUY2','BUY3')
            is_exit = effective_sig in ('EXIT1','EXIT2','EXIT3') or time_stop or i==len(bars)-1
            if is_exit:
                exit_sig = 'EXIT1a' if time_stop else ('OPEN' if (i==len(bars)-1 and effective_sig not in ('EXIT1','EXIT2','EXIT3')) else effective_sig)
                pnl = (price - ent_p)/ent_p*100
                trades.append({'entSig':ent_sig,'exitSig':exit_sig,'pnlPct':round(pnl,4),'isOpen':exit_sig=='OPEN','days':days})
                in_trade = False
    return trades

def perf_stats(trades):
    closed = [t for t in trades if not t['isOpen']]
    if not closed: return {'trades':len(trades),'closed':0,'wins':0,'wr':0,'totalPnl':0,'best':0,'worst':0,'avg':0,'dd':0}
    wins = [t for t in closed if t['pnlPct']>0]
    pnls = [t['pnlPct'] for t in closed]
    total_pnl = sum(pnls)
    # max drawdown
    peak=eq=dd=0
    for p in pnls:
        eq+=p
        if eq>peak: peak=eq
        if peak-eq>dd: dd=peak-eq
    return {
        'trades': len(trades), 'closed': len(closed), 'wins': len(wins),
        'wr': round(len(wins)/len(closed)*100,1) if closed else 0,
        'totalPnl': round(total_pnl,2),
        'best': round(max(pnls),2), 'worst': round(min(pnls),2),
        'avg': round(total_pnl/len(closed),2) if closed else 0,
        'dd': round(dd,2)
    }

# ── MAIN ────────────────────────────────────────────────────
def flatten_df(df, symbol):
    """Appiattisce il MultiIndex colonne di yfinance >= 0.2.x"""
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance nuovo stile: (Price, Ticker) → prendi solo il livello Price
        df.columns = df.columns.get_level_values(0)
    # normalizza nomi colonne (a volte minuscolo)
    df.columns = [c.capitalize() for c in df.columns]
    return df

def download_symbol(symbol):
    """Scarica con yf.download e gestisce sia vecchio che nuovo stile colonne"""
    df = yf.download(symbol, period=PERIOD, interval=INTERVAL,
                     progress=False, auto_adjust=True, timeout=20)
    if df is None or len(df) == 0:
        return None
    df = flatten_df(df, symbol)
    return df

def process_ticker(entry):
    ticker = entry['ticker']
    name   = entry['name']

    # Prova prima con .MI (Borsa Italiana), poi senza suffisso come fallback
    symbols_to_try = [ticker + '.MI', ticker]
    if '.' in ticker:
        symbols_to_try = [ticker]

    df = None
    used_symbol = None
    for sym in symbols_to_try:
        try:
            df = download_symbol(sym)
            if df is not None and len(df) >= 30:
                used_symbol = sym
                break
            log.warning(f"  {ticker}: {sym} → {len(df) if df is not None else 0} barre")
        except Exception as e:
            log.warning(f"  {ticker}: {sym} → errore {e}")

    try:
        if df is None or len(df) < 30:
            log.warning(f"  {ticker}: dati insufficienti dopo tutti i tentativi")
            return None

        df = df.dropna(subset=['Close'])
        df = df.sort_index()

        bars = []
        for ts, row in df.iterrows():
            try:
                vol = int(row['Volume']) if not math.isnan(float(row['Volume'])) else 0
            except:
                vol = 0
            bars.append({
                'time':  int(ts.timestamp()),
                'open':  round(float(row['Open']),4),
                'high':  round(float(row['High']),4),
                'low':   round(float(row['Low']),4),
                'close': round(float(row['Close']),4),
                'volume': vol
            })

        closes = [b['close'] for b in bars]
        highs  = [b['high']  for b in bars]
        lows   = [b['low']   for b in bars]

        kama_f  = calc_kama(closes, 10, 5, 20)
        kama_s  = calc_kama(closes, 10, 2, 30)
        er      = calc_er(closes)
        # ATR prima del SAR — calibra lo step
        atr_vals          = calc_atr(highs, lows, closes, period=14)
        sar_step, atr_pct = get_sar_step(highs, lows, closes, atr_vals, lookback=60)
        sar_v, sar_b      = calc_sar(highs, lows, closes, step=sar_step)
        ao      = calc_ao(highs, lows)
        rsi     = calc_rsi(closes)

        scores  = [calc_score(i, closes, kama_f, er, sar_b, ao) for i in range(len(closes))]
        signals = [calc_signal(i, closes, kama_f, kama_s, er, sar_b, ao, scores) for i in range(len(closes))]
        trades  = simulate_trades(bars, signals)
        perf    = perf_stats(trades)

        last = len(bars)-1
        current_signal = signals[last]

        # Momentum — giorni consecutivi in segnale BUY
        momentum_days = 0
        for s in reversed(signals):
            if s in ('BUY1','BUY2','BUY3'): momentum_days += 1
            else: break

        # Data ultimo segnale BUY (quando è scattato)
        signal_date = None
        for i in range(last, -1, -1):
            if signals[i] in ('BUY1','BUY2','BUY3'):
                if i == 0 or signals[i-1] not in ('BUY1','BUY2','BUY3'):
                    signal_date = bars[i]['time']
                    break
            elif signals[i] not in ('BUY1','BUY2','BUY3'):
                break

        # ER trend
        er_trend = '▲' if (er[last] or 0) > (er[last-1] or 0) else '▼'

        # Variazione oggi
        today_chg = round((bars[last]['close']-bars[last-1]['close'])/bars[last-1]['close']*100, 2) if last > 0 else 0

        # Rendimento 6 mesi (circa 126 barre)
        idx_6m = max(0, last - 126)
        ret_6m = round((closes[last] - closes[idx_6m]) / closes[idx_6m] * 100, 2) if closes[idx_6m] else 0

        # Filtro downtrend strutturale permanente:
        # prezzo sotto KAMA Lenta da > 30 giorni E rendimento 6m < -25%
        days_below_ks = 0
        for i in range(last, -1, -1):
            if kama_s[i] is not None and closes[i] < kama_s[i]:
                days_below_ks += 1
            else:
                break
        structural_downtrend = (days_below_ks > 30 and ret_6m < -25)

        # Score composito per candidati (ER × score × log(momentum+1))
        import math as _math
        er_last = er[last] or 0
        composite_score = round(er_last * scores[last] * _math.log(momentum_days + 1 + 1), 4)

        # Posizione aperta — cerca l'ultimo trade con isOpen=True
        open_trade = None
        last_trade = trades[-1] if trades else None
        if last_trade and last_trade['isOpen']:
            ent_idx  = last_trade.get('entIdx', 0)
            ent_p    = last_trade['entPrice'] if 'entPrice' in last_trade else bars[ent_idx]['close']
            cur_p    = bars[last]['close']
            # Stop dinamico: MAX(SAR corrente, KAMA Lenta corrente)
            sar_now  = sar_v[last] or 0
            ks_now   = kama_s[last] or 0
            stop_dyn = round(max(sar_now, ks_now), 4)
            risk     = abs(ent_p - stop_dyn)
            tgt_dyn  = round(ent_p + risk * 2, 4) if risk > 0 else round(ent_p * 1.05, 4)
            pnl_pct  = round((cur_p - ent_p) / ent_p * 100, 2) if ent_p else 0
            pnl_abs  = round(cur_p - ent_p, 4)
            days_open= last_trade.get('days', 0)
            # Distanza % dallo stop e dal target
            dist_stop = round((cur_p - stop_dyn) / stop_dyn * 100, 2) if stop_dyn else 0
            dist_tgt  = round((tgt_dyn - cur_p) / cur_p * 100, 2) if tgt_dyn else 0
            # Alert: vicino allo stop (<3%) o in perdita >5%
            alert = 'stop' if dist_stop < 3 else ('loss' if pnl_pct < -5 else None)
            open_trade = {
                'entSig':    last_trade.get('entSig',''),
                'entTime':   bars[ent_idx]['time'] if ent_idx < len(bars) else bars[0]['time'],
                'entPrice':  round(ent_p, 4),
                'curPrice':  round(cur_p, 4),
                'stopDyn':   stop_dyn,
                'targetDyn': tgt_dyn,
                'pnlPct':    pnl_pct,
                'pnlAbs':    pnl_abs,
                'daysOpen':  days_open,
                'distStop':  dist_stop,
                'distTgt':   dist_tgt,
                'alert':     alert,
            }

        # Classificazione volatilità
        if atr_pct < 1.5:   vol_class = 'BASSA'
        elif atr_pct < 3.0: vol_class = 'MEDIA'
        elif atr_pct < 5.0: vol_class = 'ALTA'
        else:               vol_class = 'ESTREMA'

        # ATR ultimo valore assoluto e percentuale
        atr_last = round(atr_vals[last], 4) if atr_vals[last] is not None else None
        atr_pct_last = round(atr_vals[last]/closes[last]*100, 3) if atr_vals[last] and closes[last] else None

        result = {
            'ticker':               ticker,
            'name':                 name,
            'updated':              datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'bars':                 bars,
            'signal':               current_signal,
            'score':                scores[last],
            'er':                   round(er[last],4) if er[last] is not None else None,
            'er_trend':             er_trend,
            'ao':                   round(ao[last],4) if ao[last] is not None else None,
            'sar_bull':             bool(sar_b[last]) if sar_b[last] is not None else False,
            'kama_fast':            round(kama_f[last],4) if kama_f[last] is not None else None,
            'kama_slow':            round(kama_s[last],4) if kama_s[last] is not None else None,
            'sar':                  round(sar_v[last],4) if sar_v[last] is not None else None,
            'rsi':                  round(rsi[last],2) if rsi[last] is not None else None,
            'atr':                  atr_last,
            'atr_pct':              atr_pct_last,
            'atr_pct_avg60':        atr_pct,
            'sar_step':             sar_step,
            'vol_class':            vol_class,
            'close':                bars[last]['close'],
            'today_chg':            today_chg,
            'ret_6m':               ret_6m,
            'momentum_days':        momentum_days,
            'signal_date':          signal_date,
            'structural_downtrend': structural_downtrend,
            'days_below_ks':        days_below_ks,
            'composite_score':      composite_score,
            'open_trade':           open_trade,
            'perf':                 perf,
            'trades':               trades[-20:],
        }
        return result

    except Exception as e:
        log.error(f"  {ticker}: errore — {e}")
        return None


# ── SOTTOSTANTI ─────────────────────────────────────────────
UNDERLYINGS = [
    # Single stock USA
    {'ticker':'GOOGL','name':'Alphabet (Google)','etps':['3LAL','3GOO'],'market':'US'},
    {'ticker':'NVDA', 'name':'NVIDIA',           'etps':['3NVD','3LNV'],'market':'US'},
    {'ticker':'TSLA', 'name':'Tesla',            'etps':['3TSL','3LTS'],'market':'US'},
    {'ticker':'AAPL', 'name':'Apple',            'etps':['3AAP','3LAP'],'market':'US'},
    {'ticker':'AMZN', 'name':'Amazon',           'etps':['3AMZ','3LZN'],'market':'US'},
    {'ticker':'MSFT', 'name':'Microsoft',        'etps':['3MSF','3LMS','3SMS'],'market':'US'},
    {'ticker':'META', 'name':'Meta (Facebook)',  'etps':['3FB','3LFB'],'market':'US'},
    {'ticker':'NFLX', 'name':'Netflix',          'etps':['3NFL','3LNF'],'market':'US'},
    {'ticker':'AMD',  'name':'AMD',              'etps':['3AMD','3LAM'],'market':'US'},
    {'ticker':'UBER', 'name':'Uber',             'etps':['3UBR','3LUB'],'market':'US'},
    {'ticker':'PYPL', 'name':'PayPal',           'etps':['3PYP','3LPP'],'market':'US'},
    {'ticker':'COIN', 'name':'Coinbase',         'etps':['3CON','3LCO'],'market':'US'},
    {'ticker':'MSTR', 'name':'MicroStrategy',    'etps':['3MST','3LMI'],'market':'US'},
    {'ticker':'ARM',  'name':'ARM Holdings',     'etps':['ARM3'],'market':'US'},
    {'ticker':'SPOT', 'name':'Spotify',          'etps':['3LPO'],'market':'US'},
    {'ticker':'UNH',  'name':'UnitedHealth',     'etps':['UNH3'],'market':'US'},
    {'ticker':'BABA', 'name':'Alibaba',          'etps':['3BAB','3LAA'],'market':'US'},
    {'ticker':'NIO',  'name':'NIO',              'etps':['3NIO','3LNI'],'market':'US'},
    {'ticker':'SQ',   'name':'Block (Square)',   'etps':['3SQ','3LSQ'],'market':'US'},
    {'ticker':'PLTR', 'name':'Palantir',         'etps':['3LPA'],'market':'US'},
    {'ticker':'SMCI', 'name':'Super Micro Computer','etps':['SMCI'],'market':'US'},
    # Indici USA
    {'ticker':'SPY',  'name':'S&P 500',          'etps':['3USL','5SPY','WSPX'],'market':'US'},
    {'ticker':'QQQ',  'name':'Nasdaq 100',       'etps':['QQQ3','5QQQ','WNAS'],'market':'US'},
    {'ticker':'IWM',  'name':'Russell 2000',     'etps':['WRTY'],'market':'US'},
    {'ticker':'SOXX', 'name':'Semiconductors',   'etps':['3SEM','SOXL'],'market':'US'},
    # Indici Europa
    {'ticker':'^GDAXI','name':'DAX',             'etps':['3DEL'],'market':'EU'},
    {'ticker':'FTSEMIB.MI','name':'FTSE MIB',    'etps':['3ITL','5MIB'],'market':'EU'},
    {'ticker':'^FCHI','name':'CAC 40',           'etps':['3CAC'],'market':'EU'},
    {'ticker':'^FTSE','name':'FTSE 100',         'etps':['3UKL','2UKL'],'market':'EU'},
    {'ticker':'^STOXX50E','name':'Euro Stoxx 50','etps':['3EUL','5EUL','WS5X'],'market':'EU'},
    {'ticker':'^STOXX','name':'STOXX Europe Banks','etps':['3BAL'],'market':'EU'},
    # Titoli europei
    {'ticker':'UCG.MI','name':'Unicredit',       'etps':['3LCR'],'market':'EU'},
    {'ticker':'ISP.MI','name':'Intesa Sanpaolo', 'etps':['3LSP'],'market':'EU'},
    {'ticker':'RACE.MI','name':'Ferrari',        'etps':['3RAC'],'market':'EU'},
    # Materie prime (già in lista come ETP senza leva)
    {'ticker':'CL=F', 'name':'WTI Crude Oil',   'etps':['3OIL','LOIL','WTI','3OIS','PCRD'],'market':'CMD'},
    {'ticker':'BZ=F', 'name':'Brent Crude Oil', 'etps':['3BRL','BRENT','PBRT'],'market':'CMD'},
    {'ticker':'NG=F', 'name':'Natural Gas',      'etps':['3NGL','GAS'],'market':'CMD'},
    {'ticker':'GC=F', 'name':'Gold',             'etps':['3GOL'],'market':'CMD'},
    {'ticker':'SI=F', 'name':'Silver',           'etps':['3SIL','SLVR'],'market':'CMD'},
    {'ticker':'HG=F', 'name':'Copper',           'etps':['3HCL','LCOP','CPER','ECOP'],'market':'CMD'},
    {'ticker':'ZW=F', 'name':'Wheat',            'etps':['3WHL','LWEA'],'market':'CMD'},
    {'ticker':'ZC=F', 'name':'Corn',             'etps':['CORN','LCOR'],'market':'CMD'},
    {'ticker':'ZS=F', 'name':'Soybeans',         'etps':['ESOY'],'market':'CMD'},
    {'ticker':'SB=F', 'name':'Sugar',            'etps':['SUGA','3SUL','LSUG'],'market':'CMD'},
    {'ticker':'KC=F', 'name':'Coffee',           'etps':['3CFL','LCFE','ECOF'],'market':'CMD'},
    {'ticker':'CC=F', 'name':'Cocoa',            'etps':['COCO','LCOC'],'market':'CMD'},
    {'ticker':'PA=F', 'name':'Palladium',        'etps':['2PAL'],'market':'CMD'},
    {'ticker':'PL=F', 'name':'Platinum',         'etps':['LPLA','PHPT'],'market':'CMD'},
    {'ticker':'AL=F', 'name':'Aluminium',        'etps':['LALU','ALUM','EALU'],'market':'CMD'},
    {'ticker':'UX=F', 'name':'Uranium',          'etps':['NCLR'],'market':'CMD'},
]

def process_underlying(entry):
    """Scarica e processa un sottostante — calcola solo indicatori, no segnali operativi"""
    ticker = entry['ticker']
    name   = entry['name']
    market = entry['market']
    etps   = entry['etps']

    try:
        df = download_symbol(ticker)
        if df is None or len(df) < 30:
            log.warning(f"  UNDER {ticker}: dati insufficienti")
            return None
        df = df.dropna(subset=['Close']).sort_index()

        bars = []
        for ts, row in df.iterrows():
            try: vol = int(row['Volume']) if not math.isnan(float(row['Volume'])) else 0
            except: vol = 0
            bars.append({'time':int(ts.timestamp()),'open':round(float(row['Open']),4),'high':round(float(row['High']),4),'low':round(float(row['Low']),4),'close':round(float(row['Close']),4),'volume':vol})

        closes = [b['close'] for b in bars]
        highs  = [b['high']  for b in bars]
        lows   = [b['low']   for b in bars]
        last   = len(bars)-1

        kama_f = calc_kama(closes, 10, 5, 20)
        kama_s = calc_kama(closes, 10, 2, 30)
        er     = calc_er(closes)
        atr_v  = calc_atr(highs, lows, closes, 14)
        sar_step, atr_pct = get_sar_step(highs, lows, closes, atr_v, 60)
        sar_v, sar_b = calc_sar(highs, lows, closes, step=sar_step)
        ao_v   = calc_ao(highs, lows)
        rsi_v  = calc_rsi(closes)

        # Derivata KAMA Veloce
        kf_deriv = kama_derivative(kama_f, last)

        # Score e segnale (stesso sistema degli ETP)
        scores  = [calc_score(i, closes, kama_f, er, sar_b, ao_v) for i in range(len(closes))]
        signals = [calc_signal(i, closes, kama_f, kama_s, er, sar_b, ao_v, scores) for i in range(len(closes))]
        trades  = simulate_trades(bars, signals)
        perf    = perf_stats(trades)

        today_chg = round((closes[last]-closes[last-1])/closes[last-1]*100,2) if last>0 else 0
        er_last   = er[last] or 0
        atr_last  = atr_v[last]
        atr_pct_last = round(atr_last/closes[last]*100,3) if atr_last and closes[last] else None

        if atr_pct < 1.5:   vol_class='BASSA'
        elif atr_pct < 3.0: vol_class='MEDIA'
        elif atr_pct < 5.0: vol_class='ALTA'
        else:                vol_class='ESTREMA'

        return {
            'ticker':    ticker,
            'name':      name,
            'market':    market,
            'etps':      etps,
            'updated':   datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'signal':    signals[last],
            'score':     scores[last],
            'er':        round(er_last,4),
            'kf_deriv':  kf_deriv,
            'sar_bull':  bool(sar_b[last]) if sar_b[last] is not None else False,
            'sar':       round(sar_v[last],4) if sar_v[last] else None,
            'kama_fast': round(kama_f[last],4) if kama_f[last] else None,
            'kama_slow': round(kama_s[last],4) if kama_s[last] else None,
            'ao':        round(ao_v[last],4) if ao_v[last] else None,
            'rsi':       round(rsi_v[last],2) if rsi_v[last] else None,
            'atr_pct':   atr_pct_last,
            'vol_class': vol_class,
            'close':     closes[last],
            'today_chg': today_chg,
            'perf':      perf,
            'trades':    trades[-20:],
        }
    except Exception as e:
        log.error(f"  UNDER {ticker}: errore — {e}")
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR + '/underlying', exist_ok=True)

    ok = 0; fail = 0; skipped = 0
    index = []   # per il ranking

    for i, entry in enumerate(TICKERS):
        ticker = entry['ticker']
        log.info(f"[{i+1}/{len(TICKERS)}] {ticker} — {entry['name'][:40]}")

        result = process_ticker(entry)
        if result:
            # Salva file individuale
            path = os.path.join(OUTPUT_DIR, f"{ticker}.json")
            with open(path, 'w') as f:
                json.dump(result, f, separators=(',',':'))
            log.info(f"  ✅ {ticker}: {len(result['bars'])} barre | signal={result['signal']} | pnl={result['perf']['totalPnl']}%")

            # Aggiungi al ranking index (senza bars per leggerezza)
            index.append({
                'ticker':               result['ticker'],
                'name':                 result['name'],
                'signal':               result['signal'],
                'score':                result['score'],
                'er':                   result['er'],
                'er_trend':             result['er_trend'],
                'ao':                   result['ao'],
                'sar_bull':             result['sar_bull'],
                'rsi':                  result['rsi'],
                'close':                result['close'],
                'today_chg':            result['today_chg'],
                'ret_6m':               result['ret_6m'],
                'momentum_days':        result['momentum_days'],
                'signal_date':          result['signal_date'],
                'structural_downtrend': result['structural_downtrend'],
                'days_below_ks':        result['days_below_ks'],
                'composite_score':      result['composite_score'],
                'atr':                  result['atr'],
                'atr_pct':              result['atr_pct'],
                'atr_pct_avg60':        result['atr_pct_avg60'],
                'sar_step':             result['sar_step'],
                'vol_class':            result['vol_class'],
                'open_trade':           result['open_trade'],
                'perf':                 result['perf'],
                'updated':              result['updated'],
            })
            ok += 1
        else:
            fail += 1

        time.sleep(DELAY)

    # Salva index per la classifica
    index_path = os.path.join(OUTPUT_DIR, 'index.json')
    with open(index_path, 'w') as f:
        json.dump({
            'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'tickers': index
        }, f, separators=(',',':'))

    log.info(f"\n{'='*50}")
    log.info(f"✅ OK: {ok} | ❌ Fail: {fail} | Index: {len(index)} ticker")

    # ── SOTTOSTANTI ─────────────────────────────────────────
    log.info(f"\n{'='*50}")
    log.info(f"Inizio download {len(UNDERLYINGS)} sottostanti...")
    under_index = []
    ok_u = 0; fail_u = 0

    for i, entry in enumerate(UNDERLYINGS):
        ticker = entry['ticker']
        log.info(f"[U {i+1}/{len(UNDERLYINGS)}] {ticker} — {entry['name']}")
        result = process_underlying(entry)
        if result:
            path = os.path.join(OUTPUT_DIR, 'underlying', f"{ticker.replace('=','_').replace('^','_')}.json")
            with open(path, 'w') as f:
                json.dump(result, f, separators=(',',':'))
            log.info(f"  ✅ {ticker}: signal={result['signal']} | kf_deriv={result['kf_deriv']} | pnl={result['perf']['totalPnl']}%")
            under_index.append({
                'ticker':    result['ticker'],
                'name':      result['name'],
                'market':    result['market'],
                'etps':      result['etps'],
                'signal':    result['signal'],
                'score':     result['score'],
                'er':        result['er'],
                'kf_deriv':  result['kf_deriv'],
                'sar_bull':  result['sar_bull'],
                'atr_pct':   result['atr_pct'],
                'vol_class': result['vol_class'],
                'close':     result['close'],
                'today_chg': result['today_chg'],
                'perf':      result['perf'],
                'updated':   result['updated'],
            })
            ok_u += 1
        else:
            fail_u += 1
        time.sleep(DELAY)

    # Salva index sottostanti
    under_path = os.path.join(OUTPUT_DIR, 'underlying', 'index.json')
    with open(under_path, 'w') as f:
        json.dump({
            'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'underlyings': under_index
        }, f, separators=(',',':'))

    log.info(f"✅ Sottostanti OK: {ok_u} | ❌ Fail: {fail_u}")
    log.info(f"File salvati in: {OUTPUT_DIR}/underlying/")


if __name__ == '__main__':
    main()
