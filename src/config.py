from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
CSV_RETAILER = DATA_DIR / "retailer.csv"      
CSV_EXPOS_TV = DATA_DIR / "tv_publisher.csv"         
CSV_EXPOS_PRG = DATA_DIR / "programmatic_publisher.csv"  
CSV_ID_MAPPING = DATA_DIR / "mapping_transac_tv.csv"          
CSV_DEMOGRAPHICS = DATA_DIR / "socio_demo.csv"       

RESULTS_DIR = ROOT_DIR / "results"
MATRICES_DIR = RESULTS_DIR / "matrices"
FIGURES_DIR = RESULTS_DIR / "figures"
LOGS_DIR = RESULTS_DIR / "logs"

MARKOV_ORDER = 1