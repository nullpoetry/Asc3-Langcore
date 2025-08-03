<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyberweave Unified Core</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        
        body {
            font-family: 'Press Start 2P', monospace;
            margin: 0;
            overflow: hidden;
            background-color: #000;
        }

        #canvas-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
        
        #movable-pane {
            position: absolute;
            top: 10vh;
            left: 10vw;
            width: 300px;
            height: 300px;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00ff41;
            box-shadow: 0 0 15px #00ff41;
            cursor: move;
            z-index: 10;
            display: flex;
            flex-direction: column;
            padding: 10px;
            box-sizing: border-box;
            user-select: none;
            color: #00ff41;
            transform: perspective(600px) rotateX(20deg);
        }

        #pane-header {
            padding: 5px;
            background-color: rgba(0, 0, 0, 0.5);
            cursor: move;
        }

        #pane-content {
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        #pane-controls {
            display: flex;
            flex-direction: column;
            gap: 5px;
            padding: 5px;
            border-top: 2px solid #00ff41;
        }

        .pane-grid {
            display: grid;
            background-color: transparent;
            line-height: 1;
            font-size: 0.5rem;
            width: 100%;
            height: 100%;
            --grid-width: 20;
            --grid-height: 20;
            --cell-size: 10px;
            grid-template-columns: repeat(var(--grid-width), 1fr);
            grid-template-rows: repeat(var(--grid-height), 1fr);
        }

        .pane-cell {
            color: #00ff41;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            height: var(--cell-size);
            width: var(--cell-size);
            opacity: 1; /* Characters are always clear */
        }
        .pane-cell.alive { color: #ff00ff; }

        #render-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <!-- The three.js renderer will append its canvas here -->
    </div>

    <!-- Movable and transparent 2D pane window -->
    <div id="movable-pane">
        <div id="pane-header">
            <h2 class="text-sm">Dynamic Viewport</h2>
        </div>
        <div id="pane-content">
            <div id="pane-grid" class="pane-grid"></div>
        </div>
        <div id="pane-controls">
            <label class="text-xs">Transparency: <span id="opacity-value">70%</span></label>
            <input type="range" id="opacity-slider" min="0" max="100" value="70">
        </div>
    </div>

    <!-- Hidden canvases for WebGL textures -->
    <div style="display:none;">
        <canvas id="hidden-canvas-a"></canvas>
        <canvas id="hidden-canvas-b"></canvas>
        <canvas id="hidden-canvas-c"></canvas>
    </div>

    <!-- three.js library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- OrbitControls for easier viewing -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <!-- TWEEN.js for smooth animations -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.min.js"></script>


    <script>
        // --- Paper Py (Asc3Core) Logic ported to JavaScript ---
        class Asc3Core {
            constructor(canvasWidth = 80, canvasHeight = 24, fillChar = ' ') {
                this.canvasWidth = canvasWidth;
                this.canvasHeight = canvasHeight;
                this.fillChar = fillChar;
                this.styles = {'default': {'color': 'white'}};
                this.fonts = {};
                this.currentStyleName = 'default';
                this.currentStyle = this.styles[this.currentStyleName];
                this.cursorX = 0;
                this.cursorY = 0;
                this.canvas = this._createCanvas();
            }
        
            _createCanvas() {
                return Array.from({ length: this.canvasHeight }, () => 
                    Array.from({ length: this.canvasWidth }, () => this.fillChar)
                );
            }
        
            defineFont(fontName, fontMap) {
                this.fonts[fontName] = fontMap;
            }
        
            setStyle({ styleName = 'default', color = 'white', x = 0, y = 0 }) {
                if (!this.styles[styleName]) {
                    this.styles[styleName] = { color: color };
                }
                this.currentStyleName = styleName;
                this.currentStyle = this.styles[styleName];
                this.cursorX = x;
                this.cursorY = y;
            }
        
            writeText(fontName, text) {
                if (!this.fonts[fontName]) {
                    console.error(`Error: Font '${fontName}' not defined.`);
                    return;
                }
        
                const fontMap = this.fonts[fontName];
                
                for (const char of text) {
                    if (fontMap[char]) {
                        const charArt = fontMap[char];
                        const charWidth = charArt[0].length;
        
                        for (let yOffset = 0; yOffset < charArt.length; yOffset++) {
                            for (let xOffset = 0; xOffset < charArt[yOffset].length; xOffset++) {
                                const pixel = charArt[yOffset][xOffset];
                                const canvasX = this.cursorX + xOffset;
                                const canvasY = this.cursorY + yOffset;
                                
                                if (pixel !== ' ') {
                                    if (canvasX >= 0 && canvasX < this.canvasWidth && canvasY >= 0 && canvasY < this.canvasHeight) {
                                        this.canvas[canvasY][canvasX] = pixel;
                                    }
                                }
                            }
                        }
        
                        this.cursorX += charWidth + 1;
                    } else {
                        console.warn(`Warning: Character '${char}' not in font '${fontName}'.`);
                    }
                }
            }
        
            render() {
                return this.canvas.map(row => row.join('')).join('\n');
            }

            drawToCanvas(targetCanvas, aliveColor, deadColor) {
                const ctx = targetCanvas.getContext('2d');
                const cellSize = 10;
                const charWidth = 6;
                const charHeight = 10;
                targetCanvas.width = this.canvasWidth * charWidth;
                targetCanvas.height = this.canvasHeight * charHeight;

                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, targetCanvas.width, targetCanvas.height);
                ctx.font = `${charHeight * 0.8}px 'Press Start 2P'`;
                ctx.textAlign = 'center';

                for (let y = 0; y < this.canvasHeight; y++) {
                    for (let x = 0; x < this.canvasWidth; x++) {
                        const char = this.canvas[y][x];
                        if (char !== this.fillChar) {
                            ctx.fillStyle = aliveColor;
                            ctx.fillText(char, x * charWidth + charWidth / 2, y * charHeight + charHeight * 0.8);
                        }
                    }
                }
            }
        }

        // --- 3D Scene Setup ---
        let scene, camera, renderer, controls;
        let cubeGroup;
        const subCubeSize = 1;
        const cubeSeparation = 0.05;
        const rubiksCubeSize = subCubeSize * 3 + cubeSeparation * 2;

        const ASC3_FONT = {
            'A': [ "  _  ", " / \\ ", "/___\\", "\\   /", " \\ / " ],
            'S': [ " ____ ", "/ __ \\", "\\___ \\", " ____/", "/____/" ],
            'C': [ "  ___ ", " / __|", "| (__ ", " \\___|", "     " ],
            '3': [ " ____ ", "|___ \\", "  _  |", " ___/ ", "|____/" ],
            ' ': [ "      ", "      ", "      ", "      ", "      " ],
        };
        
        const coreA = new Asc3Core(canvasWidth=15, canvasHeight=5, fillChar='.');
        const coreB = new Asc3Core(canvasWidth=15, canvasHeight=5, fillChar='.');
        const coreC = new Asc3Core(canvasWidth=15, canvasHeight=5, fillChar='.');
        const corePane = new Asc3Core(canvasWidth=20, canvasHeight=20, fillChar='.');

        function initThreeJS() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000000);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 10;

            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);
            const pointLight = new THREE.PointLight(0xffffff, 1);
            pointLight.position.set(5, 5, 5);
            scene.add(pointLight);

            createRubiksCube();

            window.addEventListener('resize', onWindowResize, false);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function createRubiksCube() {
            cubeGroup = new THREE.Group();
            const geometry = new THREE.BoxGeometry(subCubeSize, subCubeSize, subCubeSize);
            
            const hiddenCanvasA = document.getElementById('hidden-canvas-a');
            const hiddenCanvasB = document.getElementById('hidden-canvas-b');
            const hiddenCanvasC = document.getElementById('hidden-canvas-c');

            const faceTextures = [
                new THREE.CanvasTexture(hiddenCanvasA),
                new THREE.CanvasTexture(hiddenCanvasB),
                new THREE.CanvasTexture(hiddenCanvasC),
            ];

            for (let x = 0; x < 3; x++) {
                for (let y = 0; y < 3; y++) {
                    for (let z = 0; z < 3; z++) {
                        const materials = [
                            new THREE.MeshBasicMaterial({ map: faceTextures[0] }), // Right
                            new THREE.MeshBasicMaterial({ map: faceTextures[0] }), // Left
                            new THREE.MeshBasicMaterial({ map: faceTextures[1] }), // Top
                            new THREE.MeshBasicMaterial({ map: faceTextures[1] }), // Bottom
                            new THREE.MeshBasicMaterial({ map: faceTextures[2] }), // Front
                            new THREE.MeshBasicMaterial({ map: faceTextures[2] }), // Back
                        ];
                        const cube = new THREE.Mesh(geometry, materials);
                        cube.position.set(
                            (x - 1) * (subCubeSize + cubeSeparation),
                            (y - 1) * (subCubeSize + cubeSeparation),
                            (z - 1) * (subCubeSize + cubeSeparation)
                        );
                        cubeGroup.add(cube);
                    }
                }
            }
            scene.add(cubeGroup);
        }

        // --- Paper Py Animation Logic ---
        function runAsc3Programs() {
            // Program for core A (Front/Back)
            coreA.canvas = coreA._createCanvas(); // Clear canvas
            coreA.defineFont("basic", ASC3_FONT);
            coreA.setStyle({ x: Math.floor(Math.random() * 5), y: Math.floor(Math.random() * 2) });
            coreA.writeText("basic", "ASC");
            coreA.writeText("basic", "3");
            coreA.drawToCanvas(document.getElementById('hidden-canvas-a'), '#ff00ff', '#00ffff');
            
            // Program for core B (Top/Bottom)
            coreB.canvas = coreB._createCanvas();
            coreB.defineFont("basic", ASC3_FONT);
            coreB.setStyle({ x: Math.floor(Math.random() * 5), y: Math.floor(Math.random() * 2) });
            coreB.writeText("basic", "PY");
            coreB.drawToCanvas(document.getElementById('hidden-canvas-b'), '#ffffff', '#ffaa00');

            // Program for core C (Left/Right)
            coreC.canvas = coreC._createCanvas();
            coreC.defineFont("basic", ASC3_FONT);
            coreC.setStyle({ x: Math.floor(Math.random() * 5), y: Math.floor(Math.random() * 2) });
            coreC.writeText("basic", "C Y B E R");
            coreC.drawToCanvas(document.getElementById('hidden-canvas-c'), '#00ff41', '#ff00ff');

            // Program for Pane
            corePane.canvas = corePane._createCanvas();
            corePane.defineFont("basic", ASC3_FONT);
            corePane.setStyle({ x: 0, y: 0 });
            corePane.writeText("basic", "ASC3");
            corePane.writeText("basic", "PY");
            drawPaneGrid(corePane);
        }

        function drawPaneGrid(core) {
            const cells = document.getElementById('pane-grid').querySelectorAll('.pane-cell');
            cells.forEach(cell => {
                const x = parseInt(cell.dataset.x);
                const y = parseInt(cell.dataset.y);
                const char = core.canvas[y][x];
                if (char !== core.fillChar) {
                    cell.textContent = char;
                    cell.style.color = '#ff00ff';
                } else {
                    cell.textContent = '.';
                    cell.style.color = '#00ff41';
                }
            });
        }
        
        // --- Drag and Drop Logic for the Pane Window ---
        const movablePane = document.getElementById('movable-pane');
        const paneHeader = document.getElementById('pane-header');
        let isDragging = false;
        let offset = { x: 0, y: 0 };
        
        paneHeader.addEventListener('mousedown', (e) => {
            isDragging = true;
            offset.x = e.clientX - movablePane.offsetLeft;
            offset.y = e.clientY - movablePane.offsetTop;
            movablePane.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                movablePane.style.left = `${e.clientX - offset.x}px`;
                movablePane.style.top = `${e.clientY - offset.y}px`;
            }
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
            movablePane.style.cursor = 'move';
        });

        // --- Transparency Slider Logic ---
        const opacitySlider = document.getElementById('opacity-slider');
        const opacityValue = document.getElementById('opacity-value');
        opacitySlider.addEventListener('input', (e) => {
            const opacity = e.target.value / 100;
            movablePane.style.backgroundColor = `rgba(0, 0, 0, ${opacity})`;
            opacityValue.textContent = `${e.target.value}%`;
        });
        
        // --- Animation Loop & Logic ---
        function animate() {
            requestAnimationFrame(animate);

            cubeGroup.rotation.y += 0.005;
            controls.update();
            if(window.TWEEN) TWEEN.update(); // Add a check to prevent errors
            renderer.render(scene, camera);
        }

        function updateTextures() {
            scene.traverse(obj => {
                if (obj.isMesh) {
                    obj.material.forEach(mat => {
                        if (mat.map && mat.map.isCanvasTexture) {
                            mat.map.needsUpdate = true;
                        }
                    });
                }
            });
        }

        function mainLoop() {
            runAsc3Programs();
            updateTextures();
            setTimeout(mainLoop, 1000); // Update every second
        }
        
        function twistCubeFace() {
            const groups = [];
            const allCubes = cubeGroup.children;
            const randomFaceIndex = Math.floor(Math.random() * 6);
            
            let axis, position;
            switch(randomFaceIndex) {
                case 0: axis = new THREE.Vector3(0, 0, 1); position = subCubeSize + cubeSeparation; groups.push(allCubes.filter(c => Math.abs(c.position.z - position) < 0.1)); break;
                case 1: axis = new THREE.Vector3(0, 0, -1); position = -(subCubeSize + cubeSeparation); groups.push(allCubes.filter(c => Math.abs(c.position.z - position) < 0.1)); break;
                case 2: axis = new THREE.Vector3(-1, 0, 0); position = -(subCubeSize + cubeSeparation); groups.push(allCubes.filter(c => Math.abs(c.position.x - position) < 0.1)); break;
                case 3: axis = new THREE.Vector3(1, 0, 0); position = subCubeSize + cubeSeparation; groups.push(allCubes.filter(c => Math.abs(c.position.x - position) < 0.1)); break;
                case 4: axis = new THREE.Vector3(0, 1, 0); position = subCubeSize + cubeSeparation; groups.push(allCubes.filter(c => Math.abs(c.position.y - position) < 0.1)); break;
                case 5: axis = new THREE.Vector3(0, -1, 0); position = -(subCubeSize + cubeSeparation); groups.push(allCubes.filter(c => Math.abs(c.position.y - position) < 0.1)); break;
            }

            if (groups[0] && groups[0].length > 0) {
                const faceGroup = new THREE.Group();
                groups[0].forEach(cube => faceGroup.add(cube));
                
                cubeGroup.add(faceGroup);
                
                if(window.TWEEN) { // Only run if TWEEN is available
                    new TWEEN.Tween(faceGroup.rotation)
                        .to({ x: axis.x * Math.PI / 2, y: axis.y * Math.PI / 2, z: axis.z * Math.PI / 2 }, 1000)
                        .easing(TWEEN.Easing.Quadratic.InOut)
                        .onComplete(() => {
                            faceGroup.children.forEach(cube => {
                                cubeGroup.attach(cube);
                            });
                            cubeGroup.remove(faceGroup);
                        })
                        .start();
                } else {
                    cubeGroup.remove(faceGroup);
                }
            }
        }
        
        // --- Pane Game Initialization ---
        function initPaneGame() {
            const paneElement = document.getElementById('pane-grid');
            paneElement.style.setProperty('--cell-size', `10px`);
            paneElement.style.setProperty('--grid-width', corePane.canvasWidth);
            paneElement.style.setProperty('--grid-height', corePane.canvasHeight);
            
            paneElement.innerHTML = '';
            for (let y = 0; y < corePane.canvasHeight; y++) {
                for (let x = 0; x < corePane.canvasWidth; x++) {
                    const cellElement = document.createElement('span');
                    cellElement.classList.add('pane-cell');
                    cellElement.textContent = corePane.fillChar;
                    cellElement.dataset.x = x;
                    cellElement.dataset.y = y;
                    paneElement.appendChild(cellElement);
                }
            }
        }
        
        // --- Initialization on window load ---
        window.onload = function () {
            initThreeJS();
            initPaneGame();
            animate();
            mainLoop();
            // This is the updated section. The check prevents the error.
            const twistTimer = setInterval(() => {
                if (window.TWEEN) {
                    twistCubeFace();
                }
            }, 5000);
        };
    </script>
</body>
</html>
