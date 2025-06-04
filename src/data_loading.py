import pandas as pd
from src.config import CSV_RETAILER, CSV_EXPOS_TV, CSV_EXPOS_PRG, CSV_ID_MAPPING, CSV_DEMOGRAPHICS


def load_retailer_events():
    """Charge le fichier Retailer contenant les transactions/événements.</n    Colonnes attendues : ['customer_id', 'timestamp_utc', 'event_name', 'brand', 'product_name', 'sales', 'quantity']
    """
    df = pd.read_csv(CSV_RETAILER, parse_dates=['timestamp_utc'])
    return df


def load_exposures_tv():
    """Charge le fichier d'expositions TV.
    Colonnes attendues : ['device_id', 'timestamp_utc', 'cost_milli_cent']
    """
    df = pd.read_csv(CSV_EXPOS_TV, parse_dates=['timestamp_utc'])
    return df


def load_exposures_programmatique():
    """Charge le fichier d'expositions programmatiques.
    Colonnes attendues : ['dsp_id', 'timestamp_utc', 'campaign_name', 'device_type', 'cost_milli_cent']
    """
    df = pd.read_csv(CSV_EXPOS_PRG, parse_dates=['timestamp_utc'])
    return df


def load_id_mapping():
    """Charge le fichier de mapping entre customer_id, device_id et dsp_id.
    Colonnes attendues : ['customer_id', 'device_id', 'dsp_id']
    """
    df = pd.read_csv(CSV_ID_MAPPING)
    return df


def load_demographics():
    """Charge le fichier des données socio-démographiques.
    Colonnes attendues : ['customer_id', 'breed', 'age', 'income']
    """
    df = pd.read_csv(CSV_DEMOGRAPHICS)
    return df