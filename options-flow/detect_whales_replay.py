import asyncio
from ib_insync import *
from datetime import datetime

# --- CONFIGURACIÓN ---
IP_LOCAL = '127.0.0.1'
PUERTO = 4002
CLIENT_ID = 10
WATCHLIST = ['SPY', 'QQQ', 'IGV', 'IWM']
MIN_PREMIUM = 20000 

def get_best_expiration(chains):
    """
    Busca una fecha de vencimiento óptima (2-4 semanas) que exista
    en ALGUNA de las cadenas disponibles.
    """
    today = datetime.now()
    all_expirations = set()
    
    # 1. Recolectar TODAS las fechas posibles de todas las cadenas
    for chain in chains:
        for exp in chain.expirations:
            all_expirations.add(exp)
            
    sorted_exps = sorted(list(all_expirations))
    
    # 2. Elegir la mejor fecha (evitando 0DTE y lejanas)
    for exp in sorted_exps:
        try:
            exp_date = datetime.strptime(exp, '%Y%m%d')
            days_diff = (exp_date - today).days
            if 10 <= days_diff <= 35: # Rango ideal: 2 semanas a 1 mes
                return exp
        except:
            continue
            
    # Fallback: Si no hay nada ideal, devolver la última
    return sorted_exps[-1] if sorted_exps else None

async def analyze_ticker(ib, symbol):
    print(f"\n📡 --- Analizando {symbol} ---")
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        await ib.qualifyContractsAsync(stock)
        
        # 1. Precio Referencia
        bars = await ib.reqHistoricalDataAsync(stock, '', '1 D', '1 day', 'MIDPOINT', True)
        if not bars: return []
        price = bars[-1].close
        print(f"   💲 Precio: ${price:.2f}")

        # 2. Obtener TODAS las Cadenas
        chains = await ib.reqSecDefOptParamsAsync(stock.symbol, '', stock.secType, stock.conId)
        if not chains: return []
        
        # Filtramos solo las que cotizan en SMART para evitar duplicados raros
        smart_chains = [c for c in chains if c.exchange == 'SMART']
        
        # 3. Elegir UNA fecha común para analizar
        expiration = get_best_expiration(smart_chains)
        if not expiration: return []
        print(f"   📅 Vencimiento Maestro: {expiration}")

        # 4. RECOLECTAR STRIKES (El Arreglo Clave)
        # Iteramos por TODAS las cadenas y guardamos los strikes que coincidan con la fecha
        universe_strikes = set()
        
        for chain in smart_chains:
            # Solo si esta cadena incluye nuestra fecha elegida
            if expiration in chain.expirations:
                for strike in chain.strikes:
                    universe_strikes.add(strike)
        
        # 5. FILTRADO (Ahora sobre el universo completo)
        # Ampliamos un poco el rango al 3% por seguridad
        rango_min = price * 0.97
        rango_max = price * 1.03
        
        valid_strikes = [
            s for s in universe_strikes 
            if rango_min < s < rango_max  # Rango Precio
            and s % 1 == 0                # Solo Enteros
        ]
        
        # Ordenar y tomar los 3 más cercanos al precio (ATM)
        valid_strikes.sort(key=lambda x: abs(x - price))
        targets = valid_strikes[:3]
        
        print(f"   🎯 Strikes ATM encontrados: {targets}")
        
        if not targets:
            print("   ⚠️ No se encontraron strikes cercanos (Data incompleta en Paper?)")
            return []

        # 6. ESCANEO DE WHALES
        whales_found = []
        for strike in targets:
            for right in ['C', 'P']:
                # Creamos el contrato
                contract = Option(symbol, expiration, strike, right, 'SMART')
                try:
                    await ib.qualifyContractsAsync(contract)
                    
                    # Pedimos los trades
                    trades = await ib.reqHistoricalDataAsync(
                        contract, '', '2 D', '5 mins', 'TRADES', True
                    )
                    
                    if trades:
                        df = util.df(trades)
                        # Calcular dinero movido
                        df['money'] = df['volume'] * df['average'] * 100
                        
                        max_row = df.loc[df['money'].idxmax()]
                        max_money = max_row['money']
                        
                        if max_money > MIN_PREMIUM:
                            tipo = "CALL 🐂" if right == 'C' else "PUT 🐻"
                            print(f"      🐋 {symbol} {tipo} {strike} | ${max_money:,.0f} | {max_row['date']}")
                            
                            whales_found.append({
                                'Symbol': symbol,
                                'Type': tipo,
                                'Strike': strike,
                                'Money': max_money
                            })
                            
                except Exception:
                    continue # Si un contrato falla, seguimos
        
        return whales_found

    except Exception as e:
        print(f"❌ Error en {symbol}: {e}")
        return []

async def main():
    ib = IB()
    try:
        await ib.connectAsync(IP_LOCAL, PUERTO, clientId=CLIENT_ID)
        print("🚀 Iniciando Universe Scanner...")
        
        for ticker in WATCHLIST:
            await analyze_ticker(ib, ticker)
            
    except Exception as e:
        print(f"Error Global: {e}")
    finally:
        ib.disconnect()

if __name__ == '__main__':
    asyncio.run(main())