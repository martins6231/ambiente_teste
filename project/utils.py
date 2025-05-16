import pandas as pd
from datetime import datetime

def format_duration(duration):
    """
    Format a timedelta object to a human-readable string (HH:MM:SS).
    
    Args:
        duration: pandas Timedelta object
    
    Returns:
        Formatted duration string
    """
    if pd.isna(duration):
        return "00:00:00"
    
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_month_name_pt(month_year):
    """
    Convert 'YYYY-MM' format to a readable month name in Portuguese.
    
    Args:
        month_year: String in 'YYYY-MM' format
        
    Returns:
        String with month name and year in Portuguese
    """
    if month_year == 'Todos':
        return 'Todos os Meses'
    
    # Dictionary with Portuguese month names
    meses_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    try:
        # If it's already a month name, return it
        if any(mes in month_year for mes in meses_pt.values()):
            return month_year
        
        # Parse the date
        data = datetime.strptime(month_year, '%Y-%m')
        
        # Format with Portuguese month name
        return f"{meses_pt[data.month]} {data.year}"
    except:
        # If parsing fails, return the original string
        return month_year

def format_number(value, decimals=2):
    """
    Format a number with thousands separator and specified decimal places.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    try:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(value)

def calculate_duration_hours(timedelta_value):
    """
    Convert a timedelta to hours (decimal).
    
    Args:
        timedelta_value: pandas Timedelta object
        
    Returns:
        Hours as float
    """
    if pd.isna(timedelta_value):
        return 0
    
    return timedelta_value.total_seconds() / 3600