import json
import math
import iraq_georisk_engine

def find_nearest_governorate(lat: float, lon: float):
    min_d = float('inf')
    best_k = 'BAGHDAD'
    for k, data in iraq_georisk_engine.IRAQ_GOVERNORATES_DB.items():
        R = 6371.0
        dlat = math.radians(data['lat'] - lat)
        dlon = math.radians(data['lon'] - lon)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(data['lat'])) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist_km = R * c
        if dist_km < min_d:
            min_d = dist_km
            best_k = k
    return best_k, min_d

govs_json = json.dumps(iraq_georisk_engine.IRAQ_GOVERNORATES_DB, ensure_ascii=False)
print("Govs JSON length:", len(govs_json))
