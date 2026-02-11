from django.shortcuts import render, get_object_or_404
from .utils import screen_stocks, get_available_stocks, load_stock_data, calculate_indicators

def home(request):
    return render(request, 'core/home.html')

def screener(request):
    """
    Stock screener view with filtering capabilities
    """
    results = []
    filters = {}
    total_stocks = len(get_available_stocks())
    
    if request.method == 'GET' and any(key in request.GET for key in [
        'min_price', 'max_price', 'min_pct_1d', 'max_pct_1d', 
        'min_pct_1m', 'max_pct_1m', 'min_pct_3m', 'max_pct_3m',
        'min_rsi', 'max_rsi', 'min_volume_ratio', 'above_ma_20',
        'above_ma_50', 'above_ma_200'
    ]):
        # Extract filters from GET parameters
        filters = {
            'min_price': float(request.GET.get('min_price')) if request.GET.get('min_price') else None,
            'max_price': float(request.GET.get('max_price')) if request.GET.get('max_price') else None,
            'min_pct_1d': float(request.GET.get('min_pct_1d')) if request.GET.get('min_pct_1d') else None,
            'max_pct_1d': float(request.GET.get('max_pct_1d')) if request.GET.get('max_pct_1d') else None,
            'min_pct_1m': float(request.GET.get('min_pct_1m')) if request.GET.get('min_pct_1m') else None,
            'max_pct_1m': float(request.GET.get('max_pct_1m')) if request.GET.get('max_pct_1m') else None,
            'min_pct_3m': float(request.GET.get('min_pct_3m')) if request.GET.get('min_pct_3m') else None,
            'max_pct_3m': float(request.GET.get('max_pct_3m')) if request.GET.get('max_pct_3m') else None,
            'min_rsi': float(request.GET.get('min_rsi')) if request.GET.get('min_rsi') else None,
            'max_rsi': float(request.GET.get('max_rsi')) if request.GET.get('max_rsi') else None,
            'min_volume_ratio': float(request.GET.get('min_volume_ratio')) if request.GET.get('min_volume_ratio') else None,
            'above_ma_20': request.GET.get('above_ma_20') == 'on',
            'above_ma_50': request.GET.get('above_ma_50') == 'on',
            'above_ma_200': request.GET.get('above_ma_200') == 'on',
        }
        
        # Screen stocks
        results = screen_stocks(filters)
        
        # Sort by 1M return (descending) by default
        results.sort(key=lambda x: x['indicators']['pct_1m'] or -999, reverse=True)
    
    context = {
        'results': results,
        'filters': filters,
        'total_stocks': total_stocks,
        'results_count': len(results),
    }
    
    return render(request, 'core/screener.html', context)


def stock_detail(request, symbol):
    """
    Detailed view for a single stock with price/indicator visualizations.
    """
    # Ensure the symbol exists in our downloaded dataset
    available = get_available_stocks()
    if symbol not in available:
        # Try uppercasing as files are saved without extension, e.g. RELIANCE
        symbol_normalized = symbol.upper()
        if symbol_normalized not in available:
            # Use a simple 404-style page
            return render(
                request,
                'core/stock_detail.html',
                {
                    'symbol': symbol,
                    'error': 'No data found for this symbol. Please make sure data is downloaded.',
                },
            )
        symbol = symbol_normalized

    df = load_stock_data(symbol)
    indicators = calculate_indicators(df) if df is not None else None

    # Prepare time series data (last 1 year) for charting
    chart_data = []
    if df is not None and not df.empty:
        df_sorted = df.sort_index()
        # Use roughly last 1 year of data if available
        if len(df_sorted) > 252:
            df_plot = df_sorted.iloc[-252:]
        else:
            df_plot = df_sorted

        for date, row in df_plot.iterrows():
            chart_data.append(
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'close': float(row.get('Close', 0)),
                    'ma20': float(
                        df_plot['Close'].rolling(window=20).mean().loc[date]
                    )
                    if 'Close' in df_plot.columns
                    and df_plot['Close'].rolling(window=20).mean().loc[date]
                    == df_plot['Close'].rolling(window=20).mean().loc[date]
                    else None,
                }
            )

    context = {
        'symbol': symbol,
        'indicators': indicators,
        'chart_data': chart_data,
        'error': None if chart_data else 'No historical data available to plot.',
    }

    return render(request, 'core/stock_detail.html', context)
