"""
Management command to download NSE stock data from Yahoo Finance
"""
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings

# List of popular NSE stocks (Top 200+ stocks)
NSE_STOCKS = [
    # Large Cap - Banking
    'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS',
    'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'BANDHANBNK.NS', 'FEDERALBNK.NS', 'RBLBANK.NS',
    'YESBANK.NS', 'SOUTHBANK.NS', 'UNIONBANK.NS', 'CANBK.NS', 'PNB.NS',
    'BANKBARODA.NS', 'INDIANB.NS', 'CENTRALBK.NS', 'UCOBANK.NS', 'IOB.NS',
    # Large Cap - IT
    'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS',
    # Large Cap - FMCG
    'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'DABUR.NS',
    'MARICO.NS', 'GODREJCP.NS', 'COLPAL.NS', 'EMAMILTD.NS', 'JYOTHYLAB.NS',
    # Large Cap - Auto
    'MARUTI.NS', 'M&M.NS', 'TATAMOTORS.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS',
    'EICHERMOT.NS', 'TVSMOTOR.NS', 'ASHOKLEY.NS', 'ESCORTS.NS', 'FORCEMOT.NS',
    # Large Cap - Pharma
    'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'LUPIN.NS', 'TORNTPHARM.NS',
    'GLENMARK.NS', 'ALKEM.NS', 'AUROPHARMA.NS', 'ZYDUSLIFE.NS', 'BIOCON.NS',
    # Large Cap - Energy
    'RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS', 'GAIL.NS',
    'PETRONET.NS', 'MGL.NS', 'IGL.NS', 'ADANIGREEN.NS', 'ADANITRANS.NS',
    # Large Cap - Infrastructure
    'LT.NS', 'ADANIPORTS.NS', 'ADANIENT.NS', 'ADANIWILMAR.NS', 'TATAPOWER.NS',
    'NTPC.NS', 'POWERGRID.NS', 'NHPC.NS', 'SJVN.NS', 'IRCTC.NS',
    # Large Cap - Metals
    'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'JINDALSTEL.NS',
    'SAIL.NS', 'NMDC.NS', 'MOIL.NS', 'RATNAMANI.NS', 'APARINDS.NS',
    # Large Cap - Cement
    'ULTRACEMCO.NS', 'SHREECEM.NS', 'AMBUJACEM.NS', 'ACC.NS', 'DALBHARAT.NS',
    'RAMCOCEM.NS', 'JKLAKSHMI.NS', 'ORIENTCEM.NS', 'JKCEMENT.NS', 'HEIDELBERG.NS',
    # Large Cap - Finance
    'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'ICICIPRULI.NS',
    'LICI.NS', 'MUTHOOTFIN.NS', 'MANAPPURAM.NS', 'IIFL.NS', 'MOTILALOFS.NS',
    # Large Cap - Others
    'BHARTIARTL.NS', 'ASIANPAINT.NS', 'TITAN.NS', 'DIVISLAB.NS', 'GRASIM.NS',
    'COALINDIA.NS', 'ZOMATO.NS', 'PAYTM.NS', 'NYKAA.NS', 'POLICYBZR.NS',
    # Mid Cap - Tech
    'MINDTREE.NS', 'LTTS.NS', 'MPHASIS.NS', 'PERSISTENT.NS', 'COFORGE.NS',
    'ZENSAR.NS', 'SONATA.NS', 'NEWGEN.NS', 'INTELLECT.NS', 'CYIENT.NS',
    # Mid Cap - Pharma
    'NATCOPHARM.NS', 'LAURUSLABS.NS', 'APLLTD.NS', 'JBCHEPHARM.NS', 'REDDY.NS',
    'CADILAHC.NS', 'FORTIS.NS', 'MAXHEALTH.NS', 'NARAYANA.NS', 'APOLLOHOSP.NS',
    # Mid Cap - Auto Components
    'MOTHERSON.NS', 'BOSCHLTD.NS', 'MOTHERSON.NS', 'BAJAJHLDNG.NS', 'SCHAEFFLER.NS',
    'BALKRISIND.NS', 'MRF.NS', 'APOLLOTYRE.NS', 'CEAT.NS', 'JKTYRE.NS',
    # Mid Cap - Consumer
    'HAVELLS.NS', 'CROMPTON.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 'WHIRLPOOL.NS',
    'PIDILITIND.NS', 'BERGEPAINT.NS', 'AKZOINDIA.NS', 'KANSAINER.NS', 'INDIGOPAINT.NS',
    # Mid Cap - Others
    'SIEMENS.NS', 'ABB.NS', 'SCHNEIDER.NS', 'LARSEN.NS', 'BHEL.NS',
    'THERMAX.NS', 'BLUEDART.NS', 'DELHIVERY.NS', 'MAHINDRA.NS', 'EICHER.NS',
]

# Remove duplicates and get unique stocks
NSE_STOCKS = sorted(list(set(NSE_STOCKS)))

class Command(BaseCommand):
    help = 'Download NSE stock data from Yahoo Finance for the last 5 years'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of stocks to download (for testing)',
        )

    def handle(self, *args, **options):
        # Create data directory
        data_dir = os.path.join(settings.BASE_DIR, 'stock_data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Calculate date range (last 5 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        stocks_to_download = NSE_STOCKS
        if options['limit']:
            stocks_to_download = NSE_STOCKS[:options['limit']]
        
        self.stdout.write(f'Starting download of {len(stocks_to_download)} stocks...')
        self.stdout.write(f'Date range: {start_date.date()} to {end_date.date()}')
        
        successful = 0
        failed = 0
        
        for i, symbol in enumerate(stocks_to_download, 1):
            try:
                self.stdout.write(f'[{i}/{len(stocks_to_download)}] Downloading {symbol}...', ending=' ')
                
                # Download data
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
                
                if data.empty:
                    self.stdout.write(self.style.WARNING('No data available'))
                    failed += 1
                    continue
                
                # Save to CSV
                filename = f"{symbol.replace('.NS', '')}.csv"
                filepath = os.path.join(data_dir, filename)
                data.to_csv(filepath)
                
                self.stdout.write(self.style.SUCCESS(f'✓ Saved {len(data)} records'))
                successful += 1
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
                failed += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\nDownload complete! Successful: {successful}, Failed: {failed}'
        ))
        self.stdout.write(f'Data saved to: {data_dir}')
