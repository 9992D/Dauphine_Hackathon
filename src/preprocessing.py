import csv
from src.config import CSV_RETAILER, CSV_EXPOS_TV, CSV_EXPOS_PRG, CSV_ID_MAPPING

def preprocess_data_in_chunks():
    """
    Prétraitement en streaming sans pandas pour minimiser l'utilisation mémoire.
    - Charge le mapping device_id->customer_id et dsp_id->customer_id dans des dictionnaires.
    - Parcourt linéairement exposures_tv.csv, exposures_programmatique.csv, et retailer.csv.
    - Pour chaque ligne, récupère customer_id via le mapping, étiquette state et channel, puis écrit dans merged_data.csv.
    Retourne le chemin du fichier consolidé "merged_data.csv".
    """
    map_device = {}
    map_dsp = {}
    with open(CSV_ID_MAPPING, newline='') as mapfile:
        reader = csv.DictReader(mapfile)
        for row in reader:
            cust = row.get('customer_id')
            dev = row.get('device_id')
            dsp = row.get('dsp_id')
            if dev:
                map_device[dev] = cust
            if dsp:
                map_dsp[dsp] = cust

    processed_dir = CSV_RETAILER.parent / 'processed'
    processed_dir.mkdir(exist_ok=True, parents=True)
    output_path = processed_dir / 'merged_data.csv'
    if output_path.exists():
        output_path.unlink()

    with open(CSV_EXPOS_TV, newline='') as tvfile, open(output_path, 'a', newline='') as outfile:
        reader = csv.DictReader(tvfile)
        writer = csv.writer(outfile)
        writer.writerow(['customer_id', 'timestamp', 'state', 'channel'])
        for row in reader:
            dev = row.get('device_id')
            cust = map_device.get(dev)
            if not cust:
                continue
            timestamp = row.get('timestamp_utc')
            writer.writerow([cust, timestamp, 'TV', 'TV'])

    with open(CSV_EXPOS_PRG, newline='') as prgfile, open(output_path, 'a', newline='') as outfile:
        reader = csv.DictReader(prgfile)
        writer = csv.writer(outfile)
        for row in reader:
            dsp = row.get('dsp_id')
            cust = map_dsp.get(dsp)
            if not cust:
                continue
            timestamp = row.get('timestamp_utc')
            camp = row.get('campaign_name') or 'Unknown'
            state = f"Prog_{camp}"
            writer.writerow([cust, timestamp, state, 'Programmatique'])

    with open(CSV_RETAILER, newline='') as retfile, open(output_path, 'a', newline='') as outfile:
        reader = csv.DictReader(retfile)
        writer = csv.writer(outfile)
        for row in reader:
            cust = row.get('customer_id')
            if not cust:
                continue
            timestamp = row.get('timestamp_utc')
            writer.writerow([cust, timestamp, 'Conversion', 'Retailer'])

    return output_path