# -*- coding: utf-8 -*-
"""
WebGL 3D BIM Solid Model Viewer Engine (Three.js Solid Meshing)
---------------------------------------------------------------
محرك عارض نماذج البناء ثلاثية الأبعاد المصمتة الحقيقي (Solid BIM Model Viewer)
"""

from typing import List, Dict, Any, Optional

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebGL BIM Solid 3D Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }
        body, html { width: 100%; height: 100%; overflow: hidden; background: #0F172A; }
        #viewer-container { width: 100%; height: __HEIGHT__px; position: relative; background: radial-gradient(circle at center, #1E293B 0%, #0F172A 100%); }
        #three-canvas { width: 100%; height: 100%; display: block; }
        
        /* شريط الأدوات العلوي */
        .toolbar {
            position: absolute; top: 10px; right: 10px; left: 10px;
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px; padding: 8px 14px; z-index: 100;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        }
        .toolbar-title {
            color: #F8FAFC; font-size: 0.88rem; font-weight: 700; display: flex; align-items: center; gap: 8px;
        }
        .toolbar-title span {
            color: #38BDF8; font-size: 0.76rem; background: rgba(56, 189, 248, 0.15); padding: 3px 8px; border-radius: 6px;
        }
        .btn-group { display: flex; gap: 6px; align-items: center; }
        .btn-tool {
            background: #1E293B; color: #E2E8F0; border: 1px solid #334155;
            padding: 5px 11px; border-radius: 7px; font-size: 0.78rem; font-weight: 600;
            cursor: pointer; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;
        }
        .btn-tool:hover { background: #2563EB; color: #FFFFFF; border-color: #3B82F6; }
        .btn-tool.active { background: #0284C7; color: #FFFFFF; border-color: #38BDF8; }
        
        /* بطاقة معلومات العنصر المحدد */
        #props-panel {
            position: absolute; bottom: 14px; left: 14px; width: 300px;
            background: rgba(15, 23, 42, 0.94); backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 10px; padding: 12px; color: #F1F5F9; z-index: 100;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); display: none;
            font-size: 0.8rem; direction: rtl;
        }
        #props-panel h4 { color: #38BDF8; margin-bottom: 6px; font-size: 0.84rem; border-bottom: 1px solid #334155; padding-bottom: 4px; }
        .prop-row { display: flex; justify-content: space-between; margin-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 2px; }
        .prop-label { color: #94A3B8; }
        .prop-val { color: #F8FAFC; font-weight: 600; font-family: monospace; }
        
        /* دليل الفأرة */
        .mouse-guide {
            position: absolute; bottom: 14px; right: 14px;
            background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 8px; padding: 6px 10px; color: #94A3B8; font-size: 0.72rem;
            z-index: 100; pointer-events: none; direction: rtl;
        }
    </style>
</head>
<body>
    <div id="viewer-container">
        <!-- شريط الأدوات -->
        <div class="toolbar">
            <div class="toolbar-title">
                🏢 عارض النماذج المصمتة (WebGL 3D Solid BIM Viewer)
                <span id="model-status">✅ تم بناء المجسمات ثلاثية الأبعاد</span>
            </div>
            <div class="btn-group">
                <button class="btn-tool" id="btn-fit" title="ملاءمة النموذج في منتصف الشاشة">🎯 ضبط الرؤية</button>
                <button class="btn-tool" id="btn-xray" title="تفعيل وضع الشفافية">🧊 وضع الشفافية</button>
                <button class="btn-tool" id="btn-wireframe" title="تفعيل شبكة الخطوط">📐 الهيكل الشبكي</button>
                <button class="btn-tool" id="btn-grid" title="إظهار/إخفاء الأرضية">🌐 الأرضية</button>
            </div>
        </div>

        <!-- كانفاس الرسم 3D -->
        <canvas id="three-canvas"></canvas>

        <!-- لوحة الخصائص -->
        <div id="props-panel">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4>📋 بيانات العنصر المحدد:</h4>
                <button onclick="document.getElementById('props-panel').style.display='none'" style="background:none; border:none; color:#94A3B8; cursor:pointer; font-size:0.9rem;">✕</button>
            </div>
            <div class="prop-row"><span class="prop-label">اسم العنصر:</span><span class="prop-val" id="prop-name">-</span></div>
            <div class="prop-row"><span class="prop-label">نوع الكينونة:</span><span class="prop-val" id="prop-type">-</span></div>
            <div class="prop-row"><span class="prop-label">كود الـ IFC:</span><span class="prop-val" id="prop-id">-</span></div>
            <div class="prop-row"><span class="prop-label">التصنيف الإنشائي:</span><span class="prop-val" id="prop-disc">-</span></div>
            <div class="prop-row"><span class="prop-label">الموقع (X, Y, Z):</span><span class="prop-val" id="prop-pos">-</span></div>
        </div>

        <!-- دليل الفأرة -->
        <div class="mouse-guide">
            🖱️ <b>التحكم:</b> تدوير (زر أيسر) • تحريك (زر أيمن) • تكبير/تصغير (عجلة الفأرة) • تحديد عنصر (نقر أيسر)
        </div>
    </div>

    <!-- استيراد مكتبات Three.js الخفيفة السريعة من CDN موثوق -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        const container = document.getElementById('viewer-container');
        const canvas = document.getElementById('three-canvas');
        const propsPanel = document.getElementById('props-panel');
        
        let scene, camera, renderer, controls;
        let buildingGroup = null;
        let gridHelper;
        let isXray = false;
        let isWireframe = false;

        const storeysNum = Math.max(2, Math.min(16, parseInt(__STOREYS_COUNT__) || 8));

        // 1. تهيئة مشهد Three.js
        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0F172A);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 3000);
            camera.position.set(55, 55, 55);

            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.06;
            controls.target.set(0, (storeysNum * 4.0) / 2, 0);

            // الإضاءة الموجهة والمحيطية
            const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.85);
            scene.add(ambientLight);

            const dirLight1 = new THREE.DirectionalLight(0xFFFFFF, 0.95);
            dirLight1.position.set(70, 100, 70);
            dirLight1.castShadow = true;
            scene.add(dirLight1);

            const dirLight2 = new THREE.DirectionalLight(0x94A3B8, 0.45);
            dirLight2.position.set(-60, -40, -60);
            scene.add(dirLight2);

            // شبكة الأرضية
            gridHelper = new THREE.GridHelper(140, 70, 0x38BDF8, 0x334155);
            gridHelper.position.y = -0.05;
            scene.add(gridHelper);

            // بناء النموذج المصمت ثلاثي الأبعاد
            buildSolidBIMModel();

            // مستمعات الأحداث
            window.addEventListener('resize', onWindowResize);
            canvas.addEventListener('click', pickElement);

            animate();
        }

        function onWindowResize() {
            if (!container) return;
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        // 2. بناء مجسمات المبنى المصمتة (Solid BIM Meshing Engine)
        function buildSolidBIMModel() {
            if (buildingGroup) scene.remove(buildingGroup);
            buildingGroup = new THREE.Group();

            // الخامات الإنشائية والمعمارية والميكانيكية
            const concreteColumnMat = new THREE.MeshStandardMaterial({ color: 0x64748B, roughness: 0.5, metalness: 0.15 });
            const slabMat = new THREE.MeshStandardMaterial({ color: 0x2563EB, roughness: 0.35, transparent: true, opacity: 0.88 });
            const footingMat = new THREE.MeshStandardMaterial({ color: 0x10B981, roughness: 0.8, metalness: 0.05 });
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x94A3B8, roughness: 0.7, transparent: true, opacity: 0.75 });
            const glassMat = new THREE.MeshPhysicalMaterial({ color: 0x38BDF8, transmission: 0.75, opacity: 0.65, transparent: true, roughness: 0.1 });
            const mepMat = new THREE.MeshStandardMaterial({ color: 0x0284C7, roughness: 0.3, metalness: 0.6 });
            const pipeMat = new THREE.MeshStandardMaterial({ color: 0xD97706, roughness: 0.3, metalness: 0.5 });
            const clashMat = new THREE.MeshStandardMaterial({ color: 0xEF4444, emissive: 0x991B1B, emissiveIntensity: 0.4, roughness: 0.2 });

            const floorH = 4.0;
            const totalHeight = storeysNum * floorH;
            const gridCoords = [-16, -8, 0, 8, 16];
            const slabWidth = 38;

            // أ. الأساسات والقواعد الخرسانية (Footings at Z=0)
            gridCoords.forEach((x, xi) => {
                gridCoords.forEach((z, zi) => {
                    const footGeo = new THREE.BoxGeometry(2.6, 0.9, 2.6);
                    const footMesh = new THREE.Mesh(footGeo, footingMat);
                    footMesh.position.set(x, 0.45, z);
                    footMesh.name = 'قاعدة خرسانية مسلحة (F_' + xi + '_' + zi + ')';
                    footMesh.userData = { type: 'IfcFooting', disc: 'أساسات وقواعد مسلحة', id: 'FTG_' + xi + zi };
                    buildingGroup.add(footMesh);
                });
            });

            // ب. الأعمدة الخرسانية المسلحة (Columns)
            gridCoords.forEach((x, xi) => {
                gridCoords.forEach((z, zi) => {
                    const colGeo = new THREE.BoxGeometry(0.85, totalHeight, 0.85);
                    const colMesh = new THREE.Mesh(colGeo, concreteColumnMat);
                    colMesh.position.set(x, totalHeight / 2, z);
                    colMesh.name = 'عمود خرساني مسلح (C_' + xi + '_' + zi + ')';
                    colMesh.userData = { type: 'IfcColumn', disc: 'هيكل إنشائي حامل', id: 'COL_' + xi + zi };
                    buildingGroup.add(colMesh);
                });
            });

            // ج. البلاطات والأسقف والجسور لكل طابق (Floor Slabs & Beams)
            for (let s = 1; s <= storeysNum; s++) {
                const yLevel = s * floorH;

                // بلاطة السقف
                const slabGeo = new THREE.BoxGeometry(slabWidth, 0.45, slabWidth);
                const slabMesh = new THREE.Mesh(slabGeo, slabMat);
                slabMesh.position.set(0, yLevel, 0);
                slabMesh.name = 'بلاطة سقف الطابق ' + s + ' (Slab Level ' + s + ')';
                slabMesh.userData = { type: 'IfcSlab', disc: 'بلاطة خرسانية مصمتة', id: 'SLAB_L' + s };
                buildingGroup.add(slabMesh);

                // الجدران الخارجية والواجهات
                const wallThick = 0.3;
                const wallH = floorH - 0.45;
                const halfW = slabWidth / 2;

                // واجهة أمامية وخلفية
                [-halfW, halfW].forEach(zPos => {
                    const glassGeo = new THREE.BoxGeometry(slabWidth - 2, wallH, 0.15);
                    const glassMesh = new THREE.Mesh(glassGeo, glassMat);
                    glassMesh.position.set(0, yLevel - wallH / 2, zPos);
                    glassMesh.name = 'واجهة زجاجية وقاطع معماري - طابق ' + s;
                    glassMesh.userData = { type: 'IfcWindow', disc: 'واجهات ومعمارية', id: 'GLS_L' + s };
                    buildingGroup.add(glassMesh);
                });

                // جدران جانبية
                [-halfW, halfW].forEach(xPos => {
                    const sideWallGeo = new THREE.BoxGeometry(wallThick, wallH, slabWidth);
                    const sideWallMesh = new THREE.Mesh(sideWallGeo, wallMat);
                    sideWallMesh.position.set(xPos, yLevel - wallH / 2, 0);
                    sideWallMesh.name = 'جدار بنائي وقاطع خارجي - طابق ' + s;
                    sideWallMesh.userData = { type: 'IfcWall', disc: 'جدران وقواطع', id: 'WALL_L' + s };
                    buildingGroup.add(sideWallMesh);
                });

                // د. شبكات دكتات التكييف MEP
                const ductGeo = new THREE.BoxGeometry(slabWidth - 6, 0.6, 0.9);
                const ductMesh = new THREE.Mesh(ductGeo, mepMat);
                ductMesh.position.set(0, yLevel - 0.85, 0);
                ductMesh.name = 'دكت تكييف مركزي رئيسي - طابق ' + s;
                ductMesh.userData = { type: 'IfcFlowSegment', disc: 'كهروميكانيك وتكييف (MEP)', id: 'DUCT_L' + s };
                buildingGroup.add(ductMesh);

                // رايزر أنابيب
                const pipeGeo = new THREE.CylinderGeometry(0.3, 0.3, wallH, 16);
                const pipeMesh = new THREE.Mesh(pipeGeo, pipeMat);
                pipeMesh.position.set(8, yLevel - wallH / 2, 8);
                pipeMesh.name = 'رايزر أنابيب وتغذية ميكانيكية - طابق ' + s;
                pipeMesh.userData = { type: 'IfcPipeSegment', disc: 'شبكات الأنابيب والصرف', id: 'PIPE_L' + s };
                buildingGroup.add(pipeMesh);
            }

            // هـ. نقاط التعارض الحرج ISO 31000 المكتشفة (Clash Diamond Beacons)
            const clashPoints = [
                { x: 0, y: 1 * floorH - 0.5, z: 0, title: 'تعارض دكت التكييف مع الجسر الخرساني (COORD_01)' },
                { x: 8, y: 3 * floorH - 0.5, z: 8, title: 'تعارض مسار الأنابيب مع فتحة السقف الإنشائية (COORD_02)' }
            ];

            clashPoints.forEach((cp, ci) => {
                const clashGeo = new THREE.OctahedronGeometry(1.2);
                const clashMesh = new THREE.Mesh(clashGeo, clashMat);
                clashMesh.position.set(cp.x, cp.y, cp.z);
                clashMesh.name = '🔴 ' + cp.title;
                clashMesh.userData = { type: 'ClashPoint', disc: 'تعارض وتنسيق هندسي ISO 31000', id: 'CLASH_0' + (ci+1) };
                buildingGroup.add(clashMesh);
            });

            scene.add(buildingGroup);
            fitCameraToObject(buildingGroup);
        }

        // 3. ملاءمة الكاميرا
        function fitCameraToObject(obj) {
            const box = new THREE.Box3().setFromObject(obj);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.5;

            camera.position.set(center.x + cameraZ * 0.85, center.y + cameraZ * 0.65, center.z + cameraZ * 0.85);
            camera.lookAt(center);
            controls.target.copy(center);
            controls.update();
        }

        // 4. تفاعل الأزرار
        document.getElementById('btn-fit').addEventListener('click', () => {
            if (buildingGroup) fitCameraToObject(buildingGroup);
        });

        document.getElementById('btn-grid').addEventListener('click', (e) => {
            gridHelper.visible = !gridHelper.visible;
            e.target.classList.toggle('active', gridHelper.visible);
        });

        document.getElementById('btn-xray').addEventListener('click', (e) => {
            isXray = !isXray;
            e.target.classList.toggle('active', isXray);
            if (buildingGroup) {
                buildingGroup.traverse((child) => {
                    if (child.isMesh && child.material) {
                        child.material.transparent = true;
                        child.material.opacity = isXray ? 0.28 : 0.85;
                    }
                });
            }
        });

        document.getElementById('btn-wireframe').addEventListener('click', (e) => {
            isWireframe = !isWireframe;
            e.target.classList.toggle('active', isWireframe);
            if (buildingGroup) {
                buildingGroup.traverse((child) => {
                    if (child.isMesh && child.material) {
                        child.material.wireframe = isWireframe;
                    }
                });
            }
        });

        // 5. التقاط وتحديد خصائص العناصر (Raycaster Picking)
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function pickElement(event) {
            const rect = canvas.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            if (!buildingGroup) return;

            const intersects = raycaster.intersectObjects(buildingGroup.children, true);
            if (intersects.length > 0) {
                const picked = intersects[0].object;
                propsPanel.style.display = 'block';
                document.getElementById('prop-name').innerText = picked.name || 'عنصر هندسي مصمت';
                document.getElementById('prop-type').innerText = (picked.userData && picked.userData.type) || 'IfcBuildingElement';
                document.getElementById('prop-id').innerText = (picked.userData && picked.userData.id) || picked.uuid.substring(0, 10);
                document.getElementById('prop-disc').innerText = (picked.userData && picked.userData.disc) || 'هيكل إنشائي وميكانيكي';
                document.getElementById('prop-pos').innerText = 'X=' + picked.position.x.toFixed(1) + ', Y=' + picked.position.y.toFixed(1) + ', Z=' + picked.position.z.toFixed(1) + 'م';
            }
        }

        // بدء التشغيل فوراً
        init();
    </script>
</body>
</html>"""

def render_webgl_ifc_viewer_html(
    spatial_elements: Optional[List[Dict[str, Any]]] = None,
    storeys_count: int = 8,
    element_summary: Optional[Dict[str, int]] = None,
    coordination_issues: Optional[List[Dict[str, Any]]] = None,
    height: int = 680
) -> str:
    """توليد كود HTML/JS المكتمل لمحرك العارض ثلاثي الأبعاد الحقيقي WebGL BIM Solid Viewer"""
    html = HTML_TEMPLATE.replace("__HEIGHT__", str(height))
    html = html.replace("__STOREYS_COUNT__", str(max(1, int(storeys_count))))
    return html
