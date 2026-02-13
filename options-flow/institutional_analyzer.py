import asyncio
from ib_insync import *
from datetime import datetime
import pandas as pd
import logging

# --- CONFIGURACIÓN ESTABLE ---
IP_LOCAL = '127.0.0.1'
PUERTO = 4001
CLIENT_ID = 30
# WATCHLIST = ['GOOGL', 'JNJ', 'CELH', 'HGRAF', 'RBLX', 'NBIS']
# WATCHLIST = ['META', 'AMZN', 'GOOGL', 'AAPL', 'MSFT', 'NVDA', 'TSLA']
WATCHLIST = ['GOOGL', 'META', 'NBIS', 'ASTS', 'EOSE', 'ONDAS', 'NVDA']

MIN_PREMIUM = 20000 # Bajamos un poco la vara para ver datos seguro

# Silenciar logs internos pero permitir errores críticos
util.logToConsole(logging.CRITICAL) 
pd.set_option('display.max_rows', None)

def get_best_expiration(chains):
    today = datetime.now()
    all_expirations = set()
    for chain in chains:
        for exp in chain.expirations: all_expirations.add(exp)
    sorted_exps = sorted(list(all_expirations))
    
    # Buscamos vencimiento entre 10 y 45 días
    for exp in sorted_exps:
        try:
            exp_date = datetime.strptime(exp, '%Y%m%d')
            days_diff = (exp_date - today).days
            if 10 <= days_diff <= 45: return exp
        except: continue
    return sorted_exps[-1] if sorted_exps else None

async def analyze_ticker_v7(ib, symbol):
    print(f"\n🧠 Analizando {symbol}...", end="")
    
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        
        # 1. TIMEOUT MÁS LARGO (10s)
        await asyncio.wait_for(ib.qualifyContractsAsync(stock), timeout=10.0)
        
        # Esto funciona GRATIS en Live (precio de cierre/último trade)
        bars = await asyncio.wait_for(
            ib.reqHistoricalDataAsync(stock, '', '1 D', '1 day', 'TRADES', True),
            timeout=10.0
        )

        if not bars: 
            print(" ❌ (Error: No llega precio del stock)")
            return None
        price = bars[-1].close
        print(f" ${price:.2f}", end="")

        chains = await ib.reqSecDefOptParamsAsync(stock.symbol, '', stock.secType, stock.conId)
        smart_chains = [c for c in chains if c.exchange == 'SMART']
        expiration = get_best_expiration(smart_chains)
        if not expiration: return None
        print(f" | 📅 {expiration}")

        # Recolección de strikes
        universe_strikes = set()
        for chain in smart_chains:
            if expiration in chain.expirations:
                for strike in chain.strikes: universe_strikes.add(strike)
        
        # Filtro: Rango 4% y solo enteros (o .5 para IWM/QQQ que son ETFs)
        valid_strikes = sorted([s for s in universe_strikes if price*0.96 < s < price*1.04])
        # Tomamos los 4 más cercanos al precio
        targets = sorted(valid_strikes, key=lambda x: abs(x - price))[:4]

        data_points = []
        print(f"   🔎 Escaneando strikes {targets}: ", end="")

        for strike in targets:
            for right in ['C', 'P']:
                contract = Option(symbol, expiration, strike, right, 'SMART')
                try:
                    await asyncio.wait_for(ib.qualifyContractsAsync(contract), timeout=5.0)
                    
                    # 2. INTENTO DE DESCARGA CON MÁS TIEMPO (15s)
                    trades = await asyncio.wait_for(
                        ib.reqHistoricalDataAsync(contract, '', '2 D', '5 mins', 'TRADES', True),
                        timeout=15.0
                    )
                    
                    if trades:
                        df = util.df(trades)
                        # Cálculo simple para verificar datos
                        df['premium'] = df['volume'] * df['average'] * 100
                        big_money = df[df['premium'] > MIN_PREMIUM]
                        
                        if not big_money.empty:
                            total_premium = big_money['premium'].sum()
                            data_points.append({
                                'Type': 'CALL' if right == 'C' else 'PUT',
                                'Premium': total_premium,
                                'Strike': strike
                            })
                            print("✅", end="", flush=True) # Encontró Whales
                        else:
                            print(".", end="", flush=True) # Encontró datos pero eran pequeños
                    else:
                        print("x", end="", flush=True) # Datos vacíos (común en opciones lejanas)
                            
                except asyncio.TimeoutError:
                    print("⌛", end="", flush=True) # Timeout real
                except Exception:
                    print("!", end="", flush=True) # Otro error

        print("") # Salto de línea

        if not data_points: return None

        # Resumen
        df = pd.DataFrame(data_points)
        call_vol = df[df['Type']=='CALL']['Premium'].sum()
        put_vol = df[df['Type']=='PUT']['Premium'].sum()
        net_flow = call_vol - put_vol
        
        pcr = put_vol / call_vol if call_vol > 0 else 10.0
        
        sentiment = "NEUTRO"
        if net_flow > 100000: sentiment = "🟢 BULLISH"
        elif net_flow < -100000: sentiment = "🔴 BEARISH"

        return {
            'symbol': symbol,
            'sentiment': sentiment,
            'net_flow': net_flow,
            'pcr': pcr,
            'top_strike': df.loc[df['Premium'].idxmax()]
        }

    except Exception as e:
        print(f"\n   ⚠️ Skip {symbol}: {e}")
        return None

async def main():
    ib = IB()
    try:
        await ib.connectAsync(IP_LOCAL, PUERTO, clientId=CLIENT_ID)
        
        # --- CORRECCIÓN CRÍTICA ---
        # Tipo 3 = Datos Retrasados (Gratis). Vital para Paper Trading sin subscripción.
        ib.reqMarketDataType(3) 
        
        print("🚀 SENTIMENT ENGINE V7 (CORREGIDO)\n")
        
        results = []
        for ticker in WATCHLIST:
            res = await analyze_ticker_v7(ib, ticker)
            if res: results.append(res)
        
        print("\n" + "="*75)
        print(f"{'TICKER':<8} {'SENTIMIENTO':<15} {'FLUJO NETO ($)':<15} {'PCR':<6} {'TOP FLOW'}")
        print("="*75)
        
        for r in results:
            strike_str = f"{r['top_strike']['Type']} {r['top_strike']['Strike']} (${r['top_strike']['Premium']:,.0f})"
            print(f"{r['symbol']:<8} {r['sentiment']:<15} {r['net_flow']:,.0f}        {r['pcr']:.2f}   {strike_str}")
            
    except Exception as e:
        print(f"Error Fatal: {e}")
    finally:
        ib.disconnect()

if __name__ == '__main__':
    asyncio.run(main())