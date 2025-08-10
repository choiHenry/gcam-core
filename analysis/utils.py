def convert_to_mt(row):
    val, unit = row['value'], row['Units']
    if unit == 'Tg':
        return val
    elif unit == 'Gg':
        return val * 1e-3
    elif unit == 'MTC':
        return val * (44.009 / 12.011)
    else:
        raise ValueError(f"Unknown unit: {unit}")

# AR5 100‑yr GWP (no climate–carbon feedbacks)
GWP_AR5 = {
    'CO2':      1,      
    'CH4':     28,      
    'CH4_AGR': 28,
    'CH4_AWB': 28,
    'N2O':    265,      
    'N2O_AGR':265,
    'N2O_AWB':265,
    'HFC125': 3170,     
    'HFC134a':1300,     
    'HFC143a':4800,     
    'HFC23': 12400,     
    'HFC32':   677,     
    'HFC43':  1650,     
    'HFC227ea':3350,    
    'HFC236fa':8060,    
    'SF6':   23500,     
    'C2F6':  11100,     
    'CF4':    6630,     
}

def ej_to_twh(ej):
    """
    Convert energy from exajoules (EJ) to terawatt-hours (TWh).

    Parameters:
    ej (float): Energy in exajoules.

    Returns:
    float: Energy in terawatt-hours.
    """
    twh = ej * 277.777778
    return twh