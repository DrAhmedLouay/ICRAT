import json
import math
import iraq_georisk_engine

def generate_leaflet_map_html(
    selected_gov_key: str = "BAGHDAD",
    project_lat: float = 33.3152,
    project_lon: float = 44.3661,
    project_name: str = "مشروع إنشائي عراقي",
    initial_map_type: str = "SATELLITE",
    height_px: int = 540
) -> str:
    govs_json = json.dumps(iraq_georisk_engine.IRAQ_GOVERNORATES_DB, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خريطة العراق المكانية التفاعلية</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: transparent; overflow: hidden; }}
        #map {{ width: 100%; height: {height_px}px; border-radius: 12px; z-index: 1; border: 1px solid #CBD5E1; }}
        
        /* Floating Info HUD */
        .info-hud {{
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            color: #FFFFFF;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.35);
            border: 1px solid rgba(255,255,255,0.15);
            min-width: 290px;
            max-width: 340px;
            direction: rtl;
            text-align: right;
            transition: all 0.3s ease;
        }}
        .info-hud-title {{
            font-size: 0.95rem;
            font-weight: 800;
            color: #60A5FA;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 6px;
        }}
        .hud-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.82rem;
            margin-bottom: 5px;
        }}
        .hud-lbl {{ color: #94A3B8; font-weight: 600; }}
        .hud-val {{ color: #F8FAFC; font-weight: 700; }}
        .hud-badge-click {{
            background: linear-gradient(135deg, #2563EB, #1D4ED8);
            color: #FFFFFF;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
            text-align: center;
            margin-top: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            animation: pulse-border 2s infinite;
        }}
        @keyframes pulse-border {{
            0% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.6); }}
            70% {{ box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }}
        }}

        /* Custom Project Pin Marker */
        .project-pin-icon {{
            background: #2563EB;
            border: 3px solid #FFFFFF;
            border-radius: 50%;
            width: 28px !important;
            height: 28px !important;
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-weight: 900;
            font-size: 14px;
        }}
        .gov-dot-icon {{
            border: 2px solid #FFFFFF;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }}
        .leaflet-popup-content-wrapper {{
            border-radius: 10px;
            padding: 4px;
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
        }}
        .leaflet-popup-content {{
            font-size: 0.85rem;
            line-height: 1.6;
            margin: 10px 14px;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="info-hud" id="hudBox">
        <div class="info-hud-title">
            <span>🎯 الموقع المحدد بالماوس</span>
            <span style="font-size:0.75rem; background:#334155; padding:2px 6px; border-radius:4px;" id="hudLiveTag">مباشر</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">🌐 خط العرض (Lat):</span>
            <span class="hud-val" id="hudLat">{project_lat:.4f}° N</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">🌐 خط الطول (Lon):</span>
            <span class="hud-val" id="hudLon">{project_lon:.4f}° E</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">🏛️ أقرب محافظة:</span>
            <span class="hud-val" style="color:#FBBF24;" id="hudGov">{iraq_georisk_engine.get_governorate_profile(selected_gov_key)['name_ar']}</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">💧 المياه الجوفية:</span>
            <span class="hud-val" id="hudWater">{iraq_georisk_engine.get_governorate_profile(selected_gov_key)['groundwater_depth_m']} م</span>
        </div>
        <div class="hud-badge-click">
            👆 انقر أو اسحب النجمة في أي مكان بالعراق لتحديد الموقع
        </div>
    </div>

    <script>
        var GOVERNORATES = {govs_json};
        var currentLat = {project_lat};
        var currentLon = {project_lon};
        var selectedGovKey = "{selected_gov_key}";
        
        // 1. تعريف طبقات الخرائط
        var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        }});

        var streetsLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }});

        var topoLayer = L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 17,
            attribution: 'Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap'
        }});

        // 2. إنشاء الخريطة
        var map = L.map('map', {{
            center: [currentLat, currentLon],
            zoom: 6,
            layers: [{ 'satelliteLayer' if initial_map_type == 'SATELLITE' else 'streetsLayer' }]
        }});

        // 3. أداة التبديل بين الطبقات
        var baseMaps = {{
            "🛰️ أقمار صناعية (Satellite)": satelliteLayer,
            "🗺️ شوارع قياسية (OpenStreetMap)": streetsLayer,
            "⛰️ تضاريس (Topography)": topoLayer
        }};
        L.control.layers(baseMaps, null, {{ position: 'topleft' }}).addTo(map);
        L.control.scale({{ metric: true, imperial: false, position: 'bottomleft' }}).addTo(map);

        // 4. دالة حساب أقرب محافظة
        function calculateNearestGov(lat, lon) {{
            var minD = Infinity;
            var bestK = 'BAGHDAD';
            var R = 6371.0;
            for (var k in GOVERNORATES) {{
                var g = GOVERNORATES[k];
                var dlat = (g.lat - lat) * Math.PI / 180.0;
                var dlon = (g.lon - lon) * Math.PI / 180.0;
                var a = Math.sin(dlat/2)*Math.sin(dlat/2) + 
                        Math.cos(lat*Math.PI/180.0) * Math.cos(g.lat*Math.PI/180.0) * 
                        Math.sin(dlon/2)*Math.sin(dlon/2);
                var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                var dist = R * c;
                if (dist < minD) {{
                    minD = dist;
                    bestK = k;
                }}
            }}
            return {{ key: bestK, data: GOVERNORATES[bestK], distKm: minD }};
        }}

        // 5. إضافة نقاط المحافظات الـ 18
        for (var k in GOVERNORATES) {{
            var g = GOVERNORATES[k];
            var dotColor = g.overall_geo_risk_score >= 80 ? '#EF4444' : (g.overall_geo_risk_score >= 65 ? '#F59E0B' : '#10B981');
            
            var govIcon = L.divIcon({{
                className: 'gov-dot-icon',
                html: '<div style=\"background:' + dotColor + '; width:12px; height:12px; border-radius:50%;\"></div>',
                iconSize: [12, 12],
                iconAnchor: [6, 6]
            }});

            var marker = L.marker([g.lat, g.lon], {{ icon: govIcon }}).addTo(map);
            marker.bindTooltip('<b>📍 ' + g.name_ar + '</b><br>المخاطر: ' + g.overall_geo_risk_score + '/100', {{
                direction: 'top',
                className: 'custom-tooltip'
            }});
        }}

        // 6. علامة المشروع الميدانية القابلة للسحب والنقر
        var projectPinIcon = L.divIcon({{
            className: 'project-pin-icon',
            html: '🎯',
            iconSize: [28, 28],
            iconAnchor: [14, 14]
        }});

        var projectMarker = L.marker([currentLat, currentLon], {{
            icon: projectPinIcon,
            draggable: true,
            zIndexOffset: 1000
        }}).addTo(map);

        var radarCircle = L.circle([currentLat, currentLon], {{
            radius: 12000,
            color: '#3B82F6',
            weight: 2,
            fillColor: '#60A5FA',
            fillOpacity: 0.2
        }}).addTo(map);

        function updateProjectPosition(lat, lon) {{
            currentLat = lat;
            currentLon = lon;
            projectMarker.setLatLng([lat, lon]);
            radarCircle.setLatLng([lat, lon]);
            
            var nearest = calculateNearestGov(lat, lon);
            
            document.getElementById('hudLat').innerText = lat.toFixed(4) + '° N';
            document.getElementById('hudLon').innerText = lon.toFixed(4) + '° E';
            document.getElementById('hudGov').innerText = nearest.data.name_ar + ' (' + nearest.distKm.toFixed(1) + ' كم)';
            document.getElementById('hudWater').innerText = nearest.data.groundwater_depth_m + ' م (' + nearest.data.salinity_badge + ')';
            
            projectMarker.bindPopup(
                '<div style=\"font-weight:800; font-size:0.95rem; color:#1E40AF;\">🎯 موقع المشروع المحدد</div>' +
                '<b>المحافظة الأقرب:</b> ' + nearest.data.name_ar + '<br>' +
                '<b>الإحداثيات:</b> ' + lat.toFixed(4) + '° N, ' + lon.toFixed(4) + '° E<br>' +
                '<b>طبيعة التربة:</b> ' + nearest.data.soil_type_ar
            ).openPopup();
        }}

        // النقر على أي مكان في الخريطة لتحريك النجمة فوراً
        map.on('click', function(e) {{
            updateProjectPosition(e.latlng.lat, e.latlng.lng);
        }});

        // سحب النجمة بالماوس
        projectMarker.on('dragend', function(e) {{
            var pos = projectMarker.getLatLng();
            updateProjectPosition(pos.lat, pos.lng);
        }});

        // تهيئة الـ Popup
        updateProjectPosition(currentLat, currentLon);
    </script>
</body>
</html>"""
    return html

html_out = generate_leaflet_map_html()
print("Leaflet HTML generated cleanly, size:", len(html_out))
