import asyncio
from ib_insync import *

# Esta es la dirección de tu Gateway local
IP_LOCAL = '127.0.0.1'
PUERTO = 4002  # Coincide con tu captura de pantalla
CLIENT_ID = 1  # Un identificador cualquiera

async def main():
    ib = IB()
    try:
        print(f"📡 Intentando conectar a {IP_LOCAL}:{PUERTO}...")
        await ib.connectAsync(IP_LOCAL, PUERTO, clientId=CLIENT_ID)
        print("✅ ¡CONEXIÓN EXITOSA!")
        print("El Gateway te ha dejado entrar.")

        # Prueba de fuego: Pedir el precio de una acción (ej. Apple)
        print("\n🔍 Consultando precio de AAPL para verificar datos...")
        stock = Stock('AAPL', 'SMART', 'USD')
        
        # Solicitamos datos de mercado en tiempo real
        ticker = ib.reqMktData(stock, '', False, False)
        
        # Esperamos unos segundos a que lleguen los datos
        for i in range(5):
            await asyncio.sleep(1)
            if ticker.last != float('nan') or ticker.bid != float('nan'):
                print(f"   Precio actual AAPL: ${ticker.last if ticker.last else ticker.marketPrice()}")
                print(f"   Bid: {ticker.bid} / Ask: {ticker.ask}")
                break
            else:
                print("   Esperando datos...")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Si el error es 'Connection Refused', verifica que el Gateway siga abierto.")
    
    finally:
        ib.disconnect()
        print("\n🔌 Desconectado.")

if __name__ == '__main__':
    asyncio.run(main())