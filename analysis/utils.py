import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

dfExc = pd.read_csv("./extdata/DEXKOUS.csv")
dfExc['date'] = pd.to_datetime(dfExc['observation_date'])
dfExcAnnual = dfExc.groupby(dfExc['date'].dt.year)['DEXKOUS'].mean()

def krw_to_usd(year):
    return 1 / dfExcAnnual[year]

def convert_price_co2_to_c(price_per_tco2):
    """
    Convert carbon price from $/tCO2 to $/tC.

    Parameters:
    - price_per_tco2 (float): Carbon price in dollars per tonne of CO₂

    Returns:
    - float: Carbon price in dollars per tonne of carbon (tC)
    """
    CONVERSION_FACTOR = 3.664  # 1 tC = 3.664 tCO2
    return price_per_tco2 * CONVERSION_FACTOR

dfDef = pd.read_csv("./extdata/gdpdef.csv")
dfDef.head()
dfDef['Year'] = dfDef['date'].str.split('-').str[0].astype(int)
arrDef = dfDef.set_index('Year')['gdpdef']
arrDef[2024] = (139.71495 / 136.41462) * arrDef[2023]

def gcam_deflator(value, from_year=2023, to_year=1975):
    return float(value * arrDef[to_year] / arrDef[from_year])

gwpAr5_CaT = {
    # CO2 and related gases
    'CO2': 1,  # Carbon Dioxide,
    'CO2_CaT': -1,  # Carbon Dioxide
    'CO2_CCfD': -1,  # Carbon Dioxide
    'CO2_FUG': 1,
    'CO2_LUC': 1,
    'CO': np.nan,  # Carbon Monoxide (indirect GWP)
    'CO_AWB': np.nan,  # Carbon Monoxide from Agricultural Waste Burning (indirect GWP)
    
    # Methane and related gases
    'CH4': 28,  # Methane
    'CH4_AGR': 28,  # Methane from Agriculture
    'CH4_AWB': 28,  # Methane from Agricultural Waste Burning

    # Nitrous Oxide and related gases
    'N2O': 265,  # Nitrous Oxide
    'N2O_AGR': 265,  # Nitrous Oxide from Agriculture
    'N2O_AWB': 265,  # Nitrous Oxide from Agricultural Waste Burning

    # Fluorinated gases (F-gases)
    'C2F6': 11100,  # Perfluoroethane
    'CF4': 6630,  # Perfluoromethane
    'HFC125': 3170,  # Hydrofluorocarbon-125
    'HFC134a': 1300,  # Hydrofluorocarbon-134a
    'HFC143a': 4800,  # Hydrofluorocarbon-143a
    'HFC152a': 138,  # Hydrofluorocarbon-152a
    'HFC227ea': 3350,  # Hydrofluorocarbon-227ea
    'HFC23': 12400,  # Hydrofluorocarbon-23
    'HFC245fa': 858,  # Hydrofluorocarbon-245fa
    'HFC32': 677,  # Hydrofluorocarbon-32
    'HFC365mfc': 804,  # Hydrofluorocarbon-365mfc
    'HFC43': 1650,  # Hydrofluorocarbon-43-10mee (closest match)
    'SF6': 23500,  # Sulfur Hexafluoride
    'HFC236fa': 8060,  # Hydrofluorocarbon-236fa

    # Other gases
    'BC': np.nan,  # Black Carbon
    'BC_AWB': np.nan,  # Black Carbon from Agricultural Waste Burning
    'H2': np.nan,  # Hydrogen
    'H2_AWB': np.nan,  # Hydrogen from Agricultural Waste Burning
    'NH3': np.nan,  # Ammonia
    'NH3_AGR': np.nan,  # Ammonia from Agriculture
    'NH3_AWB': np.nan,  # Ammonia from Agricultural Waste Burning
    'NMVOC': np.nan,  # Non-Methane Volatile Organic Compounds
    'NMVOC_AGR': np.nan,  # NMVOC from Agriculture
    'NMVOC_AWB': np.nan,  # NMVOC from Agricultural Waste Burning
    'NOx': np.nan,  # Nitrogen Oxides
    'NOx_AGR': np.nan,  # Nitrogen Oxides from Agriculture
    'NOx_AWB': np.nan,  # Nitrogen Oxides from Agricultural Waste Burning
    'OC': np.nan,  # Organic Carbon
    'OC_AWB': np.nan,  # Organic Carbon from Agricultural Waste Burning
    'SO2_3': np.nan,  # Sulfur Dioxide compound
    'SO2_3_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'SO2_1': np.nan,  # Sulfur Dioxide compound
    'SO2_1_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'SO2_2': np.nan,  # Sulfur Dioxide compound
    'SO2_2_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'SO2_4': np.nan,  # Sulfur Dioxide compound
    'SO2_4_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'PM10': np.nan,  # Particulate Matter 10 micrometers or less
    'PM2.5': np.nan,  # Particulate Matter 2.5 micrometers or less
}


def convert_xkm_to_ej(output, load_factor, year, dict_intensity):
    return (output / load_factor / 1e6) * dict_intensity[year]

def twh_to_ej(twh):
    """
    Convert Terawatt-hours (TWh) to Exajoules (EJ).

    Parameters:
    twh (float): Energy in Terawatt-hours.

    Returns:
    float: Energy in Exajoules.
    """
    conversion_factor = 0.0036
    return twh * conversion_factor

def gw_to_ej(gigawatts, utilization_rate=1.0, hours=8760):
    """
    Convert power in gigawatts (GW) to energy in exajoules (EJ) over a specified number of hours,
    taking into account the utilization rate.
    
    Parameters:
    gigawatts (float): The power in gigawatts (GW).
    utilization_rate (float): The utilization rate or capacity factor (e.g., 0.5 for 50%).
    hours (float): The time period in hours. Default is 8760 hours (1 year).
    
    Returns:
    float: The energy in exajoules (EJ).
    """
    # Convert gigawatts to watts, adjust for utilization rate, then to joules, and finally to exajoules
    joules = gigawatts * 1e9 * hours * utilization_rate * 3600  # Convert hours to seconds
    exajoules = joules * 1e-18  # Convert joules to exajoules
    
    return exajoules

def string_to_xml_file(xml_string, file_name):
    """
    Converts a string into a well-formatted (indented) XML file, without unnecessary newlines.

    Parameters:
    xml_string (str): The XML content as a string.
    file_name (str): The desired filename for the XML file.
    """
    try:
        # Parse the XML string
        root = ET.ElementTree(ET.fromstring(xml_string))
        
        # Convert ElementTree to a string
        rough_string = ET.tostring(root.getroot(), encoding="utf-8")
        
        # Use minidom to pretty-print the XML
        parsed = minidom.parseString(rough_string)
        pretty_xml_as_string = parsed.toprettyxml(indent="  ")
        
        # Remove unnecessary blank lines created by toprettyxml()
        pretty_xml_as_string = "\n".join([line for line in pretty_xml_as_string.splitlines() if line.strip()])
        
        # Write the formatted XML to a file
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(pretty_xml_as_string)
        
        print(f"XML file '{file_name}' created successfully with proper indentation and no extra newlines.")
    except ET.ParseError as e:
        print("Error parsing XML string:", e)

def catTech(x):
    if x in ['PV']:
        return 'Solar'
    elif x in ['wind', 'wind_offshore', 'wind_storage']:
        return 'Onshore Wind'
    elif x in ['wind_offshore']:
        return 'Offshore Wind'
    elif x in ['PV_storage', 'wind_storage', 'refined liquids (CC CCS)', 'refined liquids (CC)', 'refined liquids (steam/CT)']:
        return '*Etc.'
    elif x in ['hydro']:
        return 'Hydro'
    elif x in ['Gen_III', 'Gen_II_LWR']:
        return 'Nuclear'
    elif x in ['biomass (IGCC CCS)', 'biomass (conv CCS)']:
        return 'Biomass w/ CCS'
    elif x in ['biomass (IGCC)', 'biomass (conv)']:
        return 'Biomass'
    elif x in ['coal (conv pul ammonia blend 20%)']:
        return 'Coal Ammonia Blend (20%)'
    elif x in ['gas (CC H2 blend 50%)']:
        return 'Gas H2 Blend (50%)'
    elif x in ['gas (CC CCS)']:
        return 'Gas w/ CCS'
    elif x in ['gas (CC)', 'gas (steam/CT)']:
        return 'Gas'
    elif x in ['coal (IGCC CCS)', 'coal (conv pul CCS)']:
        return 'Coal'
    elif x in ['coal (IGCC)', 'coal (conv pul)']:
        return 'Coal w/o CCS'
    
def catTechRe(x):
    if x in ['PV']:
        return 'PV'
    elif x in ['wind']:
        return 'Onshore Wind'
    elif x in ['rooftop_pv']:
        return 'Rooftop PV'
    elif x in ['wind_offshore']:
        return 'Offshore Wind'
    elif x in ['wind_storage', 'PV_storage', 'CSP_storage']:
        return 'Energy Storage System'
    elif x in ['hydro']:
        return 'Hydro'
    elif x in ['biomass (conv)', 'biomass (IGCC)']:
        return 'Biomass'
    
# Define custom colors for each class
custom_colors_re = {
'Wind Storage': 'rgb(203,213,232)', 'Offshore Wind': 'rgb(141,160,203)', 'Onshore Wind': 'rgb(117,112,179)', 'Rooftop PV': 'rgb(255,217,47)', 'PV': 'rgb(230,171,2)', # 'PV Storage': 'rgb(255,242,174)', 
'Hydro': '#3366CC', 'Biomass': 'rgb(15, 133, 84)', 'Energy Storage System': 'rgb(255, 255, 179)'
}

stack_order_re = ['Hydro', 'Biomass', 'Energy Storage System', 'Offshore Wind', 'Onshore Wind', 'Rooftop PV', 'PV']
    
# Define custom colors for each class
custom_colors = {
    'Solar': '#FECB52',  # Yellow
    'Wind': 'rgb(136,204,238)',  # Light blue
    'Hydro': 'rgb(95, 70, 144)',  # Dark blue
    'Nuclear': '#EB663B',  # Orange
    'Biomass w/o CCS': 'rgb(15, 133, 84)',  # Dark green
    'Gas w/ CCS': '#DEA0FD',     # Pink
    'Gas w/o CCS': '#AB63FA',    # Purple
    'Coal w/ CCS': '#E48F72',    # Maroon
    'Coal w/o CCS': 'rgb(136,34,85)',   # Red
    'Oil w/o CCS': '#DA16FF',      # Dark orange
    'Gas H2 Blend (50%)': "rgb(102,197,204)",
    'Coal Ammonia Blend (20%)': "rgb(57, 105, 172)",
}

stack_order = [
    'Coal Ammonia Blend (20%)', 'Coal w/ CCS', 'Coal w/o CCS', 'Oil w/ CCS', 'Oil w/o CCS', 'Gas H2 Blend (50%)', 'Gas w/ CCS', 
    'Gas w/o CCS',  'Biomass w/o CCS', 'Nuclear', 'Hydro', 'Wind', 'Solar'
]

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


def twh_to_ej(twh):

    ej = twh / 277.777778
    return ej

def convert_to_mt(row):
    if row['Units'] == 'Tg':
        return row['value']
    elif row['Units'] == 'Gg':
        return row['value'] / 1_000
    elif row['Units'] == 'MTC':
        return row['value'] * (44/12)
    
def classify_ghg(ghg):
    if ghg in ['CO2']:
        return 'CO2'
    elif ghg in ['CH4', 'CH4_AGR', 'CH4_AWB']:
        return 'CH4'
    elif ghg in ['N2O', 'N2O_AGR', 'N2O_AWB']:
        return 'N2O'
    elif ghg in ['C2F6', 'CF4', 'HFC125', 'HFC134a', 'HFC143a', 'HFC152a', 'HFC227ea', 'HFC23', 'HFC245fa', 'HFC32', 'HFC365mfc', 'HFC43', 'SF6', 'HFC236fa']:
        return 'F-Gas'
    
gwpAr5 = {
    # CO2 and related gases
    'CO2': 1,  # Carbon Dioxide,
    'CO2_CaT': -1,  # Carbon Dioxide
    'CO2_CCfD': -1,  # Carbon Dioxide
    'CO2_Chemical': -1,
    'CO2_IronSteel': -1,
    'CO2_FUG': 1,
    'CO2_LUC': 1,
    'CO': np.nan,  # Carbon Monoxide (indirect GWP)
    'CO_AWB': np.nan,  # Carbon Monoxide from Agricultural Waste Burning (indirect GWP)
    
    # Methane and related gases
    'CH4': 28,  # Methane
    'CH4_AGR': 28,  # Methane from Agriculture
    'CH4_AWB': 28,  # Methane from Agricultural Waste Burning

    # Nitrous Oxide and related gases
    'N2O': 265,  # Nitrous Oxide
    'N2O_AGR': 265,  # Nitrous Oxide from Agriculture
    'N2O_AWB': 265,  # Nitrous Oxide from Agricultural Waste Burning

    # Fluorinated gases (F-gases)
    'C2F6': 11100,  # Perfluoroethane
    'CF4': 6630,  # Perfluoromethane
    'HFC125': 3170,  # Hydrofluorocarbon-125
    'HFC134a': 1300,  # Hydrofluorocarbon-134a
    'HFC143a': 4800,  # Hydrofluorocarbon-143a
    'HFC152a': 138,  # Hydrofluorocarbon-152a
    'HFC227ea': 3350,  # Hydrofluorocarbon-227ea
    'HFC23': 12400,  # Hydrofluorocarbon-23
    'HFC245fa': 858,  # Hydrofluorocarbon-245fa
    'HFC32': 677,  # Hydrofluorocarbon-32
    'HFC365mfc': 804,  # Hydrofluorocarbon-365mfc
    'HFC43': 1650,  # Hydrofluorocarbon-43-10mee (closest match)
    'SF6': 23500,  # Sulfur Hexafluoride
    'HFC236fa': 8060,  # Hydrofluorocarbon-236fa

    # Other gases
    'BC': np.nan,  # Black Carbon
    'BC_AWB': np.nan,  # Black Carbon from Agricultural Waste Burning
    'H2': np.nan,  # Hydrogen
    'H2_AWB': np.nan,  # Hydrogen from Agricultural Waste Burning
    'NH3': np.nan,  # Ammonia
    'NH3_AGR': np.nan,  # Ammonia from Agriculture
    'NH3_AWB': np.nan,  # Ammonia from Agricultural Waste Burning
    'NMVOC': np.nan,  # Non-Methane Volatile Organic Compounds
    'NMVOC_AGR': np.nan,  # NMVOC from Agriculture
    'NMVOC_AWB': np.nan,  # NMVOC from Agricultural Waste Burning
    'NOx': np.nan,  # Nitrogen Oxides
    'NOx_AGR': np.nan,  # Nitrogen Oxides from Agriculture
    'NOx_AWB': np.nan,  # Nitrogen Oxides from Agricultural Waste Burning
    'OC': np.nan,  # Organic Carbon
    'OC_AWB': np.nan,  # Organic Carbon from Agricultural Waste Burning
    'SO2_3': np.nan,  # Sulfur Dioxide compound
    'SO2_3_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'SO2_1': np.nan,  # Sulfur Dioxide compound
    'SO2_1_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'SO2_2': np.nan,  # Sulfur Dioxide compound
    'SO2_2_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'SO2_4': np.nan,  # Sulfur Dioxide compound
    'SO2_4_AWB': np.nan,  # Sulfur Dioxide compound from Agricultural Waste Burning
    'PM10': np.nan,  # Particulate Matter 10 micrometers or less
    'PM2.5': np.nan,  # Particulate Matter 2.5 micrometers or less
}

gwpAr6 = {
    # CO2 and related gases
    'CO2': 1,  # Carbon Dioxide
    'CO2_FUG': 1,
    'CO2_LUC': 1,
    
    # Methane and related gases
    'CH4': 27,  # Methane
    'CH4_AGR': 27,  # Methane from Agriculture
    'CH4_AWB': 27,  # Methane from Agricultural Waste Burning

    # Nitrous Oxide and related gases
    'N2O': 273,  # Nitrous Oxide
    'N2O_AGR': 273,  # Nitrous Oxide from Agriculture
    'N2O_AWB': 273,  # Nitrous Oxide from Agricultural Waste Burning

    # Fluorinated gases (F-gases)
    'C2F6': 12400,  # Perfluoroethane
    'CF4': 7380,  # Perfluoromethane
    'HFC125': 3740,  # Hydrofluorocarbon-125
    'HFC134a': 1530,  # Hydrofluorocarbon-134a
    'HFC143a': 5810,  # Hydrofluorocarbon-143a
    'HFC152a': 164,  # Hydrofluorocarbon-152a
    'HFC227ea': 3600,  # Hydrofluorocarbon-227ea
    'HFC23': 14600,  # Hydrofluorocarbon-23
    'HFC245fa': 962,  # Hydrofluorocarbon-245fa
    'HFC32': 771,  # Hydrofluorocarbon-32
    'HFC365mfc': 914,  # Hydrofluorocarbon-365mfc
    'HFC43': 1600,  # Hydrofluorocarbon-43-10mee (closest match)
    'SF6': 24300,  # Sulfur Hexafluoride
    'HFC236fa': 8690,  # Hydrofluorocarbon-236fa
}

def visualize_xml_tree(element, level=0, max_depth=2):
    """
    Recursively print the structure of the XML tree up to a given depth.
    :param element: The XML element to visualize
    :param level: Current depth level
    :param max_depth: Maximum depth to visualize
    """
    if level > max_depth:
        return

    indent = "  " * level  # Indentation based on level   
    if element.attrib:
        print(f"{indent}- {element.tag} (Attributes: {element.attrib})")
    elif element.text and element.text.strip():
        print(f"{indent}- {element.tag} (Text: {element.text})")
    else:
        print(f"{indent}- {element.tag}")

    for child in element:
        visualize_xml_tree(child, level + 1, max_depth)

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element without empty new lines."""
    rough_string = ET.tostring(elem, encoding='utf-8')
    parsed = minidom.parseString(rough_string)
    pretty_xml = parsed.toprettyxml(indent="  ", newl="\n")
    
    # Remove empty lines
    cleaned_xml = "\n".join(line for line in pretty_xml.splitlines() if line.strip())
    
    return cleaned_xml

def copy_element(element):
    """Recursively copy an XML element."""
    # Create a new element with the same tag and attributes
    new_element = ET.Element(element.tag, attrib=element.attrib)
    
    # Copy the text and tail
    new_element.text = element.text
    new_element.tail = element.tail
    
    # Recursively copy child elements
    for child in element:
        new_element.append(copy_element(child))
    
    return new_element

# Helper function to recursively copy an element and modify specific children
def copy_and_modify_element(element, name):
    # Create a new element with the same tag and attributes
    new_element = ET.Element(element.tag, attrib=element.attrib)
    
    # Modify text if the element is "coefficient" or "input-cost"
    if element.tag == "technology":
        new_element.set('name', name)  # Example modification
    elif element.tag == "minicam-energy-input":
        new_element.set('name', 'elect_td_ind')  # Example modification
    elif element.tag == 'CO2':
        new_element.set('name', 'CO2_CCfD')
    else:
        new_element.text = element.text  # Copy text as is
    
    # Recursively process child elements
    for child in element:
        new_child = copy_and_modify_element(child, name)
        new_element.append(new_child)
    
    return new_element

# Helper function to recursively copy an element and modify specific children
def copy_and_modify_element_korea(element, name):
    # Create a new element with the same tag and attributes
    new_element = ET.Element(element.tag, attrib=element.attrib)
    
    # Modify text if the element is "coefficient" or "input-cost"
    if element.tag == "stub-technology":
        new_element.set('name', name)  # Example modification
    elif element.tag == "minicam-energy-input":
        new_element.set('name', 'elect_td_ind')  # Example modification
    elif element.tag == 'CO2':
        new_element.set('name', 'CO2_CCfD')
    else:
        new_element.text = element.text  # Copy text as is
    
    # Recursively process child elements
    for child in element:
        new_child = copy_and_modify_element(child, name)
        new_element.append(new_child)
    
    return new_element

def subsidize(period, subsidy, attrib):
    minicam_non_energy_input = ET.SubElement(period, "minicam-non-energy-input", attrib=attrib)
    input_cost = ET.SubElement(minicam_non_energy_input, 'input-cost')
    input_cost.text = str(-subsidy)

def make_constraint_value_file(dictConst: dict, polNm: str, outFileFp, yearsDetermined=[], tax=True, regionNm="South Korea", marketNm="South Korea"):
    dictConstSorted = dict(sorted(dictConst.items()))
    dictConstSorted = {k: v for k, v in dictConstSorted.items() if k % 5 == 0}

    new_root = ET.Element("scenario")
    new_world = ET.SubElement(new_root, "world")
    new_region = ET.SubElement(new_world, "region", {'name': regionNm})
    policy_portfolio_standard = ET.SubElement(new_region, 'policy-portfolio-standard', {'name': polNm})
    policyType = ET.SubElement(policy_portfolio_standard, 'policyType')
    policyType.text = ('tax' if tax else 'subsidy')
    market = ET.SubElement(policy_portfolio_standard, 'market')
    market.text = marketNm

    for year in dictConstSorted.keys():
        min_price = ET.SubElement(policy_portfolio_standard, 'min-price', {'year': str(year)})
        min_price.text = ("-10000" if year in yearsDetermined else "0")

    for year, value in dictConstSorted.items():
        constraint = ET.SubElement(policy_portfolio_standard, 'constraint', {'year': str(year)})
        constraint.text = str(round(value, 6))

    xml_string = ET.tostring(new_root, encoding="unicode")
    string_to_xml_file(xml_string, outFileFp)

def make_constraint_techs_file(dictConst: dict, polNm: str, supplysectorNm: str, subsectorNm: str, stub_technologyNms: list, outFileFp, tax=True, regionNm="South Korea"):
    dictConstSorted = dict(sorted(dictConst.items()))
    dictConstSorted = {k: v for k, v in dictConstSorted.items() if k % 5 == 0}

    new_root = ET.Element("scenario")
    new_world = ET.SubElement(new_root, "world")
    new_region = ET.SubElement(new_world, "region", {'name': regionNm})
    new_supplysector = ET.SubElement(new_region, 'supplysector', {'name': supplysectorNm})
    new_subsector = ET.SubElement(new_supplysector, 'subsector', {'name': subsectorNm})
    for stub_technologyNm in stub_technologyNms:
        new_stub_technology = ET.SubElement(new_subsector, 'stub-technology', {'name': stub_technologyNm})
        for year in dictConstSorted.keys():
            new_period = ET.SubElement(new_stub_technology, 'period', {'year': str(year)})
            constElemNm = ("input-tax" if tax else "input-subsidy")
            ET.SubElement(new_period, constElemNm, {'name': polNm})

    xml_string = ET.tostring(new_root, encoding="unicode")
    string_to_xml_file(xml_string, outFileFp)

def make_constraint_techs_file_multi_subsector(dictConst: dict, polNm: str, supplysectorNm: str, subsectorNms: list, stub_technologyNms: list, outFileFp, tax=True, regionNm="South Korea"):
    dictConstSorted = dict(sorted(dictConst.items()))
    dictConstSorted = {k: v for k, v in dictConstSorted.items() if k % 5 == 0}

    new_root = ET.Element("scenario")
    new_world = ET.SubElement(new_root, "world")
    new_region = ET.SubElement(new_world, "region", {'name': regionNm})
    new_supplysector = ET.SubElement(new_region, 'supplysector', {'name': supplysectorNm})
    for subsectorNm in subsectorNms:
        new_subsector = ET.SubElement(new_supplysector, 'subsector', {'name': subsectorNm})
        for stub_technologyNm in stub_technologyNms:
            new_stub_technology = ET.SubElement(new_subsector, 'stub-technology', {'name': stub_technologyNm})
            for year in dictConstSorted.keys():
                new_period = ET.SubElement(new_stub_technology, 'period', {'year': str(year)})
                constElemNm = ("input-tax" if tax else "input-subsidy")
                ET.SubElement(new_period, constElemNm, {'name': polNm})

    xml_string = ET.tostring(new_root, encoding="unicode")
    string_to_xml_file(xml_string, outFileFp)

def make_constraint_fixedOutput_file(dictConst: dict, supplysectorNm: str, subsectorNm: str, stub_technologyNms: list, outFileFp, regionNm="South Korea"):
    dictConstSorted = dict(sorted(dictConst.items()))
    dictConstSorted = {k: v for k, v in dictConstSorted.items() if k % 5 == 0}

    new_root = ET.Element("scenario")
    new_world = ET.SubElement(new_root, "world")
    new_region = ET.SubElement(new_world, "region", {'name': regionNm})
    new_supplysector = ET.SubElement(new_region, 'supplysector', {'name': supplysectorNm})
    new_subsector = ET.SubElement(new_supplysector, 'subsector', {'name': subsectorNm})
    for stub_technologyNm in stub_technologyNms:
        new_stub_technology = ET.SubElement(new_subsector, 'stub-technology', {'name': stub_technologyNm})
        for year in dictConstSorted.keys():
            new_period = ET.SubElement(new_stub_technology, 'period', {'year': str(year)})
            fixedOutput = ET.SubElement(new_period, 'fixedOutput')
            fixedOutput.text = str(round(dictConstSorted[year], 3))

    xml_string = ET.tostring(new_root, encoding="unicode")
    string_to_xml_file(xml_string, outFileFp)

def make_new_element(regionNm, supplysectorNm, subsectorNm, stub_technologyNms, time_range, elementName, elementAttrs, elementTextVal, outFileFp):
    new_root = ET.Element("scenario")
    new_world = ET.SubElement(new_root, "world")
    new_region = ET.SubElement(new_world, "region", {'name': regionNm})
    new_supplysector = ET.SubElement(new_region, 'supplysector', {'name': supplysectorNm})
    new_subsector = ET.SubElement(new_supplysector, 'subsector', {'name': subsectorNm})
    for stub_technologyNm in stub_technologyNms:
        new_stub_technology = ET.SubElement(new_subsector, 'stub-technology', {'name': stub_technologyNm})
        for year in time_range:
            new_period = ET.SubElement(new_stub_technology, 'period', {'year': str(year)})
            newElem = ET.SubElement(new_period, elementName, elementAttrs[year])
            newElem.text = elementTextVal[year]

    xml_string = ET.tostring(new_root, encoding="unicode")
    string_to_xml_file(xml_string, outFileFp)