import asyncio
from ib_insync import *

# CONFIGURACIÓN
IP_LOCAL = '127.0.0.1'
PUERTO = 4002
CLIENT_ID = 2  # Cambiamos ID por si el otro script se quedó colgado

async def main():
    ib = IB()
    try:
        await ib.connectAsync(IP_LOCAL, PUERTO, clientId=CLIENT_ID)
        print("✅ Conectado. Buscando cadena de opciones...")
        
        # IMPORTANTE: Pedir datos retrasados para que no te de error 10089
        ib.reqMarketDataType(3)

        # 1. Definir el subyacente (El Stock)
        symbol = 'AAPL'
        stock = Stock(symbol, 'SMART', 'USD')
        
        # Necesitamos "cualificar" el contrato para obtener su ID único (conid)
        # Esto rellena los detalles faltantes del objeto stock
        await ib.qualifyContractsAsync(stock)
        print(f"Stock ID para {symbol}: {stock.conId}")

        # 2. Obtener fechas de vencimiento disponibles
        # reqSecDefOptParams nos da los parámetros de las opciones disponibles
        chains = await ib.reqSecDefOptParamsAsync(stock.symbol, '', stock.secType, stock.conId)
        
        # Filtramos para usar el exchange 'SMART' que es el que nos interesa
        chain = next(c for c in chains if c.exchange == 'SMART')
        
        # Tomamos la primera fecha de vencimiento disponible (la más próxima)
        expiration = sorted(chain.expirations)[0]
        print(f"\n📅 Próximo vencimiento encontrado: {expiration}")
        
        # Tomamos unos pocos strikes alrededor del precio actual (para no saturar)
        strikes = [s for s in chain.strikes if s % 5 == 0] # Filtro simple: solo múltiplos de 5
        # Seleccionamos un rango medio (esto es solo para demo)
        middle_index = len(strikes) // 2
        selected_strikes = strikes[middle_index-2 : middle_index+2]
        print(f"🎯 Strikes seleccionados para demo: {selected_strikes}")

        # 3. Crear los contratos de opciones específicos
        contracts = []
        for strike in selected_strikes:
            # CALLs
            contracts.append(Option(symbol, expiration, strike, 'C', 'SMART'))
            # PUTs
            contracts.append(Option(symbol, expiration, strike, 'P', 'SMART'))
        
        # Cualificamos los contratos (obtener sus IDs reales)
        contracts = await ib.qualifyContractsAsync(*contracts)
        print(f"✅ Se generaron {len(contracts)} contratos de opciones válidos.")

        # 4. (DEMO) Pedir datos de mercado para la primera opción de la lista
        option = contracts[0]
        print(f"\n📡 Escuchando flujo para: {option.localSymbol} (Strike {option.strike} {option.right})")
        
        ticker = ib.reqMktData(option, '', False, False)
        
        for i in range(5):
            await asyncio.sleep(1)
            print(f"   Precio Opción: {ticker.last if ticker.last else '---'} "
                  f"| Vol: {ticker.volume} | Bid: {ticker.bid} | Ask: {ticker.ask}")

    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        ib.disconnect()

if __name__ == '__main__':
    asyncio.run(main())