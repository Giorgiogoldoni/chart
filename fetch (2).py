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
  {"ticker": "TSLQ", "name": "Leverage Shares -3x Short Tesla Etp Securities"},
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
  {"ticker": "GBE3", "name": "WisdomTree Short GBP Long EUR 3x Daily"},
  {"ticker": "3STS", "name": "GraniteShares 3x Short Tesla Daily Etp"},
  {"ticker": "3EMS", "name": "WisdomTree Emerging Markets 3x Daily Short"},
  {"ticker": "CHE3", "name": "WisdomTree Short CHF Long EUR 3x Daily"},
  {"ticker": "SGB3", "name": "WisdomTree Short GBP Long USD 3x Daily"},
  {"ticker": "3MST", "name": "Leverage Shares 3x Long MicroStrategy Etp"},
  {"ticker": "3SMS", "name": "GraniteShares 3x Short Microsoft Daily Etp"},
  {"ticker": "SBA3", "name": "Leverage Shares -3x Short Alibaba Etp Securities"},
  {"ticker": "3OIL", "name": "WisdomTree WTI Crude Oil 3x Daily Leveraged"},
  {"ticker": "PCRD", "name": "WisdomTree WTI Crude Oil - GBP Daily Hedged"},
  {"ticker": "3SAA", "name": "GraniteShares 3x Short Alibaba Daily Etp"},
  {"ticker": "SEU3", "name": "WisdomTree Short EUR Long USD 3x Daily"},
  {"ticker": "3LNI", "name": "GraniteShares 3x Long NIO Daily Etp"},
  {"ticker": "PBRT", "name": "WisdomTree Brent Crude Oil - GBP Daily Hedged"},
  {"ticker": "USP3", "name": "WisdomTree Long USD Short GBP 3x Daily"},
  {"ticker": "PUS3", "name": "WisdomTree Short USD Long GBP 3x Daily"},
  {"ticker": "3NIO", "name": "Leverage Shares 3x NIO Etp Securities"},
  {"ticker": "SUP3", "name": "WisdomTree Short EUR Long GBP 3x Daily"},
  {"ticker": "3NFL", "name": "Leverage Shares 3x Netflix Etp Securities"},
  {"ticker": "EUUS", "name": "WisdomTree Long USD Short EUR"},
  {"ticker": "WCOA", "name": "WisdomTree Enhanced Commodity UCITS ETF USD Acc"},
  {"ticker": "ARM3", "name": "Leverage Shares 3x Arm Etp Securities"},
  {"ticker": "SNIK", "name": "WisdomTree Nickel 1x Daily Short"},
  {"ticker": "EIMT", "name": "WisdomTree Industrial Metals - EUR Daily Hedged"},
  {"ticker": "WCOM", "name": "WisdomTree Enhanced Commodity UCITS ETF - GBP Hedged Acc"},
  {"ticker": "SSIL", "name": "WisdomTree Silver 1x Daily Short"},
  {"ticker": "SEUR", "name": "WisdomTree Short EUR Long USD"},
  {"ticker": "3SAP", "name": "GraniteShares 3x Short Apple Daily Etp"},
  {"ticker": "AIGE", "name": "WisdomTree Energy"},
  {"ticker": "3BAS", "name": "WisdomTree EURO STOXX Banks 3x Daily Short"},
  {"ticker": "WTI",  "name": "Leverage Shares Wti Oil Etc"},
  {"ticker": "LWEA", "name": "WisdomTree Wheat 2x Daily Leveraged"},
  {"ticker": "SFNG", "name": "GraniteShares 1x Short Faang Etp"},
  {"ticker": "3BUS", "name": "WisdomTree Bund 10Y 3x Daily Short"},
  {"ticker": "3EUS", "name": "WisdomTree EURO STOXX 50 3x Daily Short"},
  {"ticker": "3AMD", "name": "Leverage Shares 3x AMD Etp Securities"},
  {"ticker": "3DES", "name": "WisdomTree DAX 3x Daily Short"},
  {"ticker": "BRENT","name": "Leverage Shares Brent Oil Etc"},
  {"ticker": "3GIS", "name": "WisdomTree Gilts 10Y 3x Daily Short"},
  {"ticker": "LOIL", "name": "WisdomTree WTI Crude Oil 2x Daily Leveraged"},
  {"ticker": "3MG7", "name": "WisdomTree Magnificent 7 3x Daily Leveraged"},
  {"ticker": "3TYS", "name": "WisdomTree US Treasuries 10Y 3x Daily Short"},
  {"ticker": "3BRL", "name": "WisdomTree Brent Crude Oil 3x Daily Leveraged"},
  {"ticker": "3WHL", "name": "WisdomTree Wheat 3x Daily Leveraged"},
  {"ticker": "3LAM", "name": "GraniteShares 3x Long AMD Daily Etp"},
  {"ticker": "3USS", "name": "WisdomTree S&P 500 3x Daily Short"},
  {"ticker": "3CAC", "name": "WisdomTree CAC 40 3x Daily Leveraged"},
  {"ticker": "SJP3", "name": "WisdomTree Short JPY Long USD 3x Daily"},
  {"ticker": "JPE3", "name": "WisdomTree Short JPY Long EUR 3x Daily"},
  {"ticker": "1PAS", "name": "WisdomTree Palladium 1x Daily Short"},
  {"ticker": "3GOO", "name": "Leverage Shares 3x Alphabet Etp Securities"},
  {"ticker": "SC3S", "name": "WisdomTree PHLX Semiconductor 3x Daily Short"},
  {"ticker": "3BTS", "name": "WisdomTree BTP 10Y 3x Daily Short"},
  {"ticker": "3NGS", "name": "WisdomTree Natural Gas 3x Daily Short"},
  {"ticker": "CORN", "name": "WisdomTree Corn"},
  {"ticker": "3LSP", "name": "GraniteShares 3x Long Intesa Sanpaolo Daily Etp"},
  {"ticker": "MAGS", "name": "Leverage Shares -3x Short Magnificent 7 Etp"},
  {"ticker": "EUP3", "name": "WisdomTree Long EUR Short GBP 3x Daily"},
  {"ticker": "3EDS", "name": "WisdomTree STOXX Europe Aerospace & Defence 3x Daily Short"},
  {"ticker": "CPER", "name": "Leverage Shares Copper Etc"},
  {"ticker": "3SRA", "name": "Leverage Shares 3x Short Ferrari (RACE) Etp"},
  {"ticker": "5EUL", "name": "WisdomTree EURO STOXX 50 5x Daily Leveraged"},
  {"ticker": "2MCL", "name": "WisdomTree FTSE 250 2x Daily Leveraged"},
  {"ticker": "3LPP", "name": "GraniteShares 3x Long PayPal Daily Etp"},
  {"ticker": "3BAL", "name": "WisdomTree EURO STOXX Banks 3x Daily Leveraged"},
  {"ticker": "2TRV", "name": "WisdomTree STOXX Europe Travel & Leisure 2x Daily Leveraged"},
  {"ticker": "3SCR", "name": "GraniteShares 3x Short Unicredit Daily Etp"},
  {"ticker": "3M7S", "name": "WisdomTree Magnificent 7 3x Daily Short"},
  {"ticker": "3FNG", "name": "GraniteShares 3x Long Faang Etp"},
  {"ticker": "LCOP", "name": "WisdomTree Copper 2x Daily Leveraged"},
  {"ticker": "2STR", "name": "WisdomTree STOXX Europe Travel & Leisure 2x Daily Short"},
  {"ticker": "3EUL", "name": "WisdomTree EURO STOXX 50 3x Daily Leveraged"},
  {"ticker": "3SMO", "name": "GraniteShares 3x Short Moderna Daily Etp"},
  {"ticker": "WS5X", "name": "WisdomTree EURO STOXX 50"},
  {"ticker": "3LAL", "name": "GraniteShares 3x Long Alphabet Daily Etp"},
  {"ticker": "5SIT", "name": "GraniteShares 5x Short Mib Daily Etp"},
  {"ticker": "WRTY", "name": "WisdomTree Russell 2000"},
  {"ticker": "3SEM", "name": "WisdomTree PHLX Semiconductor 3x Daily Leveraged"},
  {"ticker": "3LSQ", "name": "GraniteShares 3x Long Square Daily Etp"},
  {"ticker": "SQQQ", "name": "Leverage Shares -5x Short Nasdaq 100 Etp"},
  {"ticker": "3LPO", "name": "GraniteShares 3x Long Spotify Daily Etp"},
  {"ticker": "EUS3", "name": "WisdomTree Long USD Short EUR 3x Daily"},
  {"ticker": "3LCO", "name": "GraniteShares 3x Long Coinbase Daily Etp"},
  {"ticker": "ECOF", "name": "WisdomTree Coffee - EUR Daily Hedged"},
  {"ticker": "SUGA", "name": "WisdomTree Sugar"},
  {"ticker": "EGB3", "name": "WisdomTree Long GBP Short EUR 3x Daily"},
  {"ticker": "3SSQ", "name": "GraniteShares 3x Short Square Daily Etp"},
  {"ticker": "3CON", "name": "Leverage Shares 3x Long Coinbase Etp Securities"},
  {"ticker": "3LMI", "name": "GraniteShares 3x Long MicroStrategy Daily Etp"},
  {"ticker": "3LMS", "name": "GraniteShares 3x Long Microsoft Daily Etp"},
  {"ticker": "S3CO", "name": "Leverage Shares -3x Short Coinbase Etp"},
  {"ticker": "AIGS", "name": "WisdomTree Softs"},
  {"ticker": "3AMZ", "name": "Leverage Shares 3x Amazon Etp Securities"},
  {"ticker": "ENIK", "name": "WisdomTree Nickel - EUR Daily Hedged"},
  {"ticker": "3CAS", "name": "WisdomTree CAC 40 3x Daily Short"},
  {"ticker": "3RAC", "name": "Leverage Shares 3x Long Ferrari (RACE) Etp"},
  {"ticker": "ECH3", "name": "WisdomTree Long CHF Short EUR 3x Daily"},
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
  {"ticker": "2OIG", "name": "WisdomTree STOXX Europe Oil & Gas 2x Daily Short"},
  {"ticker": "3SFB", "name": "GraniteShares 3x Short Facebook Daily Etp"},
  {"ticker": "3LAP", "name": "GraniteShares 3x Long Apple Daily Etp"},
  {"ticker": "3SSP", "name": "GraniteShares 3x Short Intesa Sanpaolo Daily Etp"},
  {"ticker": "3ITS", "name": "WisdomTree FTSE MIB 3x Daily Short"},
  {"ticker": "3LUB", "name": "GraniteShares 3x Long Uber Daily Etp"},
  {"ticker": "3LPA", "name": "GraniteShares 3x Long Palantir Daily Etp"},
  {"ticker": "3SMI", "name": "GraniteShares 3x Short MicroStrategy Daily Etp"},
  {"ticker": "SMST", "name": "Leverage Shares -3x Short MicroStrategy Etp"},
  {"ticker": "5SPY", "name": "Leverage Shares 5x Long S&P 500 Etp"},
  {"ticker": "LGB3", "name": "WisdomTree Long GBP Short USD 3x Daily"},
  {"ticker": "3UBR", "name": "Leverage Shares 3x Uber Etp Securities"},
  {"ticker": "3GIL", "name": "WisdomTree Gilts 10Y 3x Daily Leveraged"},
  {"ticker": "3DEL", "name": "WisdomTree DAX 3x Daily Leveraged"},
  {"ticker": "3LAA", "name": "GraniteShares 3x Long Alibaba Daily Etp"},
  {"ticker": "3FB",  "name": "Leverage Shares 3x Facebook Etp Securities"},
  {"ticker": "UL3S", "name": "WisdomTree US Treasuries 30Y 3x Daily Short"},
  {"ticker": "3LCR", "name": "GraniteShares 3x Long Unicredit Daily Etp"},
  {"ticker": "3UKS", "name": "WisdomTree FTSE 100 3x Daily Short"},
  {"ticker": "USE3", "name": "WisdomTree Short USD Long EUR 3x Daily"},
  {"ticker": "2UKS", "name": "WisdomTree FTSE 100 2x Daily Short"},
  {"ticker": "WNAS", "name": "WisdomTree NASDAQ-100"},
  {"ticker": "3SPA", "name": "GraniteShares 3x Short Palantir Daily Etp"},
  {"ticker": "3EML", "name": "WisdomTree Emerging Markets 3x Daily Leveraged"},
  {"ticker": "3BAB", "name": "Leverage Shares 3x Alibaba Etp Securities"},
  {"ticker": "3SNF", "name": "GraniteShares 3x Short Netflix Daily Etp"},
  {"ticker": "3AAP", "name": "Leverage Shares 3x Apple Etp Securities"},
  {"ticker": "QQQ3", "name": "WisdomTree NASDAQ 100 3x Daily Leveraged"},
  {"ticker": "3SNI", "name": "WisdomTree Nickel 3x Daily Short"},
  {"ticker": "WSPX", "name": "WisdomTree S&P 500"},
  {"ticker": "3LFB", "name": "GraniteShares 3x Long Facebook Daily Etp"},
  {"ticker": "3CFL", "name": "WisdomTree Coffee 3x Daily Leveraged"},
  {"ticker": "3LNV", "name": "GraniteShares 3x Long NVIDIA Daily Etp"},
  {"ticker": "GAS",  "name": "Leverage Shares Natural Gas Etc"},
  {"ticker": "3SUL", "name": "WisdomTree Sugar 3x Daily Leveraged"},
  {"ticker": "3OIS", "name": "WisdomTree WTI Crude Oil 3x Daily Short"},
  {"ticker": "PHPT", "name": "WisdomTree Physical Platinum"},
  {"ticker": "3NGL", "name": "WisdomTree Natural Gas 3x Daily Leveraged"},
  {"ticker": "3HCS", "name": "WisdomTree Copper 3x Daily Short"},
  {"ticker": "5EUS", "name": "WisdomTree EURO STOXX 50 5x Daily Short"},
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
  {"ticker": "SOIL", "name": "WisdomTree WTI Crude Oil 1x Daily Short"},
  {"ticker": "3SIL", "name": "WisdomTree Silver 3x Daily Leveraged"},
  {"ticker": "LCFE", "name": "WisdomTree Coffee 2x Daily Leveraged"},
  {"ticker": "5QQQ", "name": "Leverage Shares 5x Long Nasdaq 100 Etp"},
  {"ticker": "3MRN", "name": "Leverage Shares 3x Long Moderna Etp Securities"},
  {"ticker": "3LZN", "name": "GraniteShares 3x Long Amazon Daily Etp"},
  {"ticker": "3GOL", "name": "WisdomTree Gold 3x Daily Leveraged"},
  {"ticker": "3LMO", "name": "GraniteShares 3x Long Moderna Daily Etp"},
  {"ticker": "3UBS", "name": "WisdomTree Bund 30Y 3x Daily Short"},
  {"ticker": "SCOP", "name": "WisdomTree Copper 1x Daily Short"},
  {"ticker": "NCLR", "name": "WisdomTree Uranium and Nuclear Energy UCITS ETF - USD Acc"},
  {"ticker": "3BRS", "name": "WisdomTree Brent Crude Oil 3x Daily Short"},
  {"ticker": "SNV3", "name": "Leverage Shares -3x Short NVIDIA Etp Securities"},
  {"ticker": "3SQ",  "name": "Leverage Shares 3x Square Etp Securities"},
  {"ticker": "FANG", "name": "GraniteShares Faang Etp"},
  {"ticker": "3EDF", "name": "WisdomTree STOXX Europe Aerospace & Defence 3x Daily Leveraged"},
  {"ticker": "3SAL", "name": "GraniteShares 3x Short Alphabet Daily Etp"},
  {"ticker": "GPTS", "name": "Leverage Shares -3x Short Artificial Intelligence (AI) Etp"},
  {"ticker": "3SIS", "name": "WisdomTree Silver 3x Daily Short"},
  {"ticker": "3SZN", "name": "GraniteShares 3x Short Amazon Daily Etp"},
  {"ticker": "SOXS", "name": "Leverage Shares -4x Short Semiconductors Etp"},
  {"ticker": "LJP3", "name": "WisdomTree Long JPY Short USD 3x Daily"},
  {"ticker": "EJP3", "name": "WisdomTree Long JPY Short EUR 3x Daily"},
  {"ticker": "SMCI", "name": "Leverage Shares 2x Super Micro Computer Etp"},
  {"ticker": "3GOS", "name": "WisdomTree Gold 3x Daily Short"},
  {"ticker": "3SNV", "name": "GraniteShares 3x Short NVIDIA Daily Etp"},
  {"ticker": "3BTL", "name": "WisdomTree BTP 10Y 3x Daily Leveraged"},
  {"ticker": "LEU3", "name": "WisdomTree Long EUR Short USD 3x Daily"},
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

def calc_signal(i, closes, kama_f, kama_s, er, sar_b, ao, scores):
    """
    Logica segnali v2 — miglioramenti rispetto a v1:
    1. Filtro KAMA Lenta: BUY solo se prezzo > KAMA Lenta (trend strutturale)
    2. ER minimo alzato: BUY2 richiede ER > 0.50, BUY3 richiede ER > 0.65
    3. Score minimo alzato: BUY2/BUY3 richiedono score >= 70 (era 65)
    4. EXIT3 grace period gestita in simulate_trades (primi 3 gg protetti)
    """
    if i < 35: return 'NONE'
    kfv = kama_f[i]; ksv = kama_s[i]; erv = er[i]; erp = er[i-1]
    aov = ao[i]; aop = ao[i-1]
    sb = sar_b[i]; sc = scores[i]; scp = scores[i-1]
    if kfv is None or ksv is None or erv is None or aov is None: return 'NONE'
    p = closes[i]

    above_kf  = p > kfv
    above_ks  = p > ksv          # ← NUOVO: filtro trend strutturale
    er_grow   = erv > (erp or 0)
    ao_grow   = aov > (aop or 0)
    ao_pos    = aov > 0
    sc_grow   = sc > scp

    # EXIT — condizioni negative (invariate, EXIT non filtrate da KAMA Lenta)
    neg = sum([not above_kf, not ao_pos, erv < 0.3, not sb])
    if sc < 35 or neg >= 2: return 'EXIT3'
    if sc < 50 and erv < 0.5:   return 'EXIT2'
    if not sb or (not ao_pos and sc < 70): return 'EXIT1'

    # BUY — richiedono TUTTI: prezzo sopra KAMA Lenta + soglie alzate
    if not above_ks: return 'WATCH'   # blocco strutturale

    if sb and ao_pos and above_kf and sc >= 70 and er_grow and sc_grow and erv > 0.65:
        return 'BUY3'
    if sb and ao_pos and above_kf and sc >= 70 and er_grow and erv > 0.50:
        return 'BUY2'
    if above_kf and erv > 0.45 and ao_grow and sb and above_ks:
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
        sar_v, sar_b = calc_sar(highs, lows, closes)
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

        # ER trend
        er_trend = '▲' if (er[last] or 0) > (er[last-1] or 0) else '▼'

        # Variazione oggi
        today_chg = round((bars[last]['close']-bars[last-1]['close'])/bars[last-1]['close']*100, 2) if last > 0 else 0

        result = {
            'ticker':        ticker,
            'name':          name,
            'updated':       datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'bars':          bars,
            'signal':        current_signal,
            'score':         scores[last],
            'er':            round(er[last],4) if er[last] is not None else None,
            'er_trend':      er_trend,
            'ao':            round(ao[last],4) if ao[last] is not None else None,
            'sar_bull':      bool(sar_b[last]) if sar_b[last] is not None else False,
            'kama_fast':     round(kama_f[last],4) if kama_f[last] is not None else None,
            'kama_slow':     round(kama_s[last],4) if kama_s[last] is not None else None,
            'sar':           round(sar_v[last],4) if sar_v[last] is not None else None,
            'rsi':           round(rsi[last],2) if rsi[last] is not None else None,
            'close':         bars[last]['close'],
            'today_chg':     today_chg,
            'momentum_days': momentum_days,
            'perf':          perf,
            'trades':        trades[-20:],  # ultimi 20 trade per risparmio spazio
        }
        return result

    except Exception as e:
        log.error(f"  {ticker}: errore — {e}")
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

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
                'ticker':        result['ticker'],
                'name':          result['name'],
                'signal':        result['signal'],
                'score':         result['score'],
                'er':            result['er'],
                'er_trend':      result['er_trend'],
                'ao':            result['ao'],
                'sar_bull':      result['sar_bull'],
                'close':         result['close'],
                'today_chg':     result['today_chg'],
                'momentum_days': result['momentum_days'],
                'perf':          result['perf'],
                'updated':       result['updated'],
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
    log.info(f"File salvati in: {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
