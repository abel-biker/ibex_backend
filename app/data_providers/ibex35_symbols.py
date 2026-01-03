"""
Símbolos del IBEX 35 con información de las empresas.
Actualizado a 2026.
"""

# Lista completa del IBEX 35 con tickers de Yahoo Finance
IBEX_35_SYMBOLS = {
    # Bancos
    "SAN.MC": {"name": "Banco Santander", "sector": "Financiero", "weight": "high"},
    "BBVA.MC": {"name": "BBVA", "sector": "Financiero", "weight": "high"},
    "CABK.MC": {"name": "CaixaBank", "sector": "Financiero", "weight": "medium"},
    "SAB.MC": {"name": "Banco Sabadell", "sector": "Financiero", "weight": "medium"},
    "BKT.MC": {"name": "Bankinter", "sector": "Financiero", "weight": "low"},
    
    # Energía
    "IBE.MC": {"name": "Iberdrola", "sector": "Energía", "weight": "high"},
    "REE.MC": {"name": "Red Eléctrica", "sector": "Energía", "weight": "medium"},
    "ENG.MC": {"name": "Enagás", "sector": "Energía", "weight": "medium"},
    "NTGY.MC": {"name": "Naturgy", "sector": "Energía", "weight": "medium"},
    "ELE.MC": {"name": "Endesa", "sector": "Energía", "weight": "medium"},
    "REP.MC": {"name": "Repsol", "sector": "Energía", "weight": "high"},
    
    # Telecomunicaciones
    "TEF.MC": {"name": "Telefónica", "sector": "Telecomunicaciones", "weight": "high"},
    
    # Industria y Construcción
    "FER.MC": {"name": "Ferrovial", "sector": "Construcción", "weight": "high"},
    "ACS.MC": {"name": "ACS", "sector": "Construcción", "weight": "high"},
    "SAF.MC": {"name": "Sacyr", "sector": "Construcción", "weight": "low"},
    "ACX.MC": {"name": "Acerinox", "sector": "Industrial", "weight": "low"},
    "ANA.MC": {"name": "Acciona", "sector": "Construcción", "weight": "medium"},
    
    # Retail y Consumo
    "ITX.MC": {"name": "Inditex", "sector": "Retail", "weight": "high"},
    "CLNX.MC": {"name": "Cellnex", "sector": "Telecomunicaciones", "weight": "medium"},
    
    # Inmobiliario
    "COL.MC": {"name": "Colonial", "sector": "Inmobiliario", "weight": "low"},
    "MRL.MC": {"name": "Merlin Properties", "sector": "Inmobiliario", "weight": "low"},
    
    # Seguros
    "MAP.MC": {"name": "Mapfre", "sector": "Seguros", "weight": "medium"},
    
    # Aerolíneas y Turismo
    "IAG.MC": {"name": "IAG", "sector": "Aerolíneas", "weight": "medium"},
    "MEL.MC": {"name": "Meliá Hotels", "sector": "Turismo", "weight": "low"},
    "AENA.MC": {"name": "Aena", "sector": "Aeropuertos", "weight": "medium"},
    
    # Farmacéuticas
    "GRF.MC": {"name": "Grifols", "sector": "Farmacéutico", "weight": "medium"},
    "PHA.MC": {"name": "Pharma Mar", "sector": "Farmacéutico", "weight": "low"},
    
    # Servicios
    "AMS.MC": {"name": "Amadeus", "sector": "Tecnología", "weight": "medium"},
    "FDR.MC": {"name": "Fluidra", "sector": "Industrial", "weight": "low"},
    "LGT.MC": {"name": "Logista", "sector": "Logística", "weight": "low"},
    
    # Alimentación
    "VIS.MC": {"name": "Viscofan", "sector": "Alimentación", "weight": "low"},
    
    # Otros
    "IDR.MC": {"name": "Indra", "sector": "Tecnología", "weight": "low"},
    "SGRE.MC": {"name": "Siemens Gamesa", "sector": "Energía", "weight": "medium"},
    "RJF.MC": {"name": "Rovi", "sector": "Farmacéutico", "weight": "low"},
    "UNI.MC": {"name": "Unicaja", "sector": "Financiero", "weight": "low"},
}

# Lista de sectores
SECTORS = list(set(v["sector"] for v in IBEX_35_SYMBOLS.values()))

# Pesos por capitalización
WEIGHT_MAP = {
    "high": ["SAN.MC", "BBVA.MC", "IBE.MC", "ITX.MC", "TEF.MC", "REP.MC", "FER.MC", "ACS.MC"],
    "medium": ["CABK.MC", "SAB.MC", "REE.MC", "ENG.MC", "NTGY.MC", "ELE.MC", "CLNX.MC", 
               "MAP.MC", "IAG.MC", "AENA.MC", "GRF.MC", "AMS.MC", "ANA.MC", "SGRE.MC"],
    "low": []  # El resto
}

def get_all_symbols():
    """Retorna todos los símbolos del IBEX 35"""
    return list(IBEX_35_SYMBOLS.keys())

def get_symbols_by_sector(sector: str):
    """Retorna símbolos de un sector específico"""
    return [symbol for symbol, info in IBEX_35_SYMBOLS.items() 
            if info["sector"] == sector]

def get_symbols_by_weight(weight: str):
    """Retorna símbolos por peso de capitalización"""
    return [symbol for symbol, info in IBEX_35_SYMBOLS.items() 
            if info["weight"] == weight]

def get_company_info(symbol: str):
    """Retorna información de una empresa"""
    return IBEX_35_SYMBOLS.get(symbol, None)
