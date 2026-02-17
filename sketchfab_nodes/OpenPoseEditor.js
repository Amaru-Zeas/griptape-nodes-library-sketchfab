/**
 * OpenPoseEditor - 3D OpenPose skeleton editor with full camera orbit and joint dragging.
 * Left-drag empty space = orbit camera
 * Left-drag joint = move joint
 * Scroll = zoom
 * Front/Side/Top = preset views
 */

export default function OpenPoseEditor(container, props) {
  const { value, onChange, disabled, height } = props;

  const canvasHeight = height && height > 0 ? Math.max(300, height - 90) : 450;

  var JOINT_NAMES = [
    'nose', 'neck',
    'right_shoulder', 'right_elbow', 'right_wrist',
    'left_shoulder', 'left_elbow', 'left_wrist',
    'right_hip', 'right_knee', 'right_ankle',
    'left_hip', 'left_knee', 'left_ankle',
    'right_eye', 'left_eye', 'right_ear', 'left_ear'
  ];

  var BONES = [
    ['nose', 'neck'],
    ['neck', 'right_shoulder'], ['right_shoulder', 'right_elbow'], ['right_elbow', 'right_wrist'],
    ['neck', 'left_shoulder'], ['left_shoulder', 'left_elbow'], ['left_elbow', 'left_wrist'],
    ['neck', 'right_hip'], ['right_hip', 'right_knee'], ['right_knee', 'right_ankle'],
    ['neck', 'left_hip'], ['left_hip', 'left_knee'], ['left_knee', 'left_ankle'],
    ['nose', 'right_eye'], ['right_eye', 'right_ear'],
    ['nose', 'left_eye'], ['left_eye', 'left_ear'],
    ['right_hip', 'left_hip']
  ];

  var JOINT_COLORS = {
    nose: 0xff0000, neck: 0xff5500,
    right_shoulder: 0xffaa00, right_elbow: 0xffff00, right_wrist: 0xaaff00,
    left_shoulder: 0x00ff00, left_elbow: 0x00ffaa, left_wrist: 0x00ffff,
    right_hip: 0x0055ff, right_knee: 0x0000ff, right_ankle: 0x5500ff,
    left_hip: 0xaa00ff, left_knee: 0xff00ff, left_ankle: 0xff00aa,
    right_eye: 0xff3333, left_eye: 0x33ff33, right_ear: 0xff6666, left_ear: 0x66ff66
  };

  var DEFAULT_POS = {
    nose: {x:0,y:1.7,z:0}, neck: {x:0,y:1.5,z:0},
    right_shoulder: {x:-0.3,y:1.5,z:0}, right_elbow: {x:-0.55,y:1.5,z:0}, right_wrist: {x:-0.8,y:1.5,z:0},
    left_shoulder: {x:0.3,y:1.5,z:0}, left_elbow: {x:0.55,y:1.5,z:0}, left_wrist: {x:0.8,y:1.5,z:0},
    right_hip: {x:-0.15,y:1.0,z:0}, right_knee: {x:-0.15,y:0.55,z:0}, right_ankle: {x:-0.15,y:0.1,z:0},
    left_hip: {x:0.15,y:1.0,z:0}, left_knee: {x:0.15,y:0.55,z:0}, left_ankle: {x:0.15,y:0.1,z:0},
    right_eye: {x:-0.06,y:1.75,z:0.05}, left_eye: {x:0.06,y:1.75,z:0.05},
    right_ear: {x:-0.12,y:1.73,z:-0.02}, left_ear: {x:0.12,y:1.73,z:-0.02}
  };

  // Load positions from value
  var jointPositions = {};
  var joints = (value && value.joints) ? value.joints : {};
  JOINT_NAMES.forEach(function (n) {
    var j = joints[n], d = DEFAULT_POS[n];
    jointPositions[n] = (j && typeof j.x === 'number') ? {x:j.x,y:j.y,z:j.z} : {x:d.x,y:d.y,z:d.z};
  });

  // Build DOM
  container.innerHTML =
    '<div class="openpose-widget nodrag nowheel" style="' +
      'display:flex;flex-direction:column;gap:6px;padding:8px;' +
      'background:#1a1a1a;border-radius:6px;user-select:none;width:100%;box-sizing:border-box;">' +
      '<div class="three-wrapper" style="width:100%;height:' + canvasHeight + 'px;position:relative;border-radius:4px;overflow:hidden;background:#111;">' +
        '<div class="view-label" style="position:absolute;top:6px;left:8px;font-size:10px;color:#555;z-index:10;pointer-events:none;">Front View</div>' +
      '</div>' +
      '<div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap;">' +
        '<button class="btn-front" style="padding:4px 10px;font-size:11px;background:#2a2a4a;border:1px solid #444;border-radius:4px;color:#ccc;cursor:pointer;">Front</button>' +
        '<button class="btn-side" style="padding:4px 10px;font-size:11px;background:#2a2a4a;border:1px solid #444;border-radius:4px;color:#ccc;cursor:pointer;">Side</button>' +
        '<button class="btn-top" style="padding:4px 10px;font-size:11px;background:#2a2a4a;border:1px solid #444;border-radius:4px;color:#ccc;cursor:pointer;">Top</button>' +
        '<button class="btn-reset" style="padding:4px 10px;font-size:11px;background:#6b1a1a;border:1px solid #8b2a2a;border-radius:4px;color:#ccc;cursor:pointer;">Reset Pose</button>' +
        '<div style="flex:1;"></div>' +
        '<span class="joint-label" style="font-size:10px;color:#888;">Drag joints to pose | Drag empty to orbit</span>' +
      '</div>' +
    '</div>';

  var widgetEl = container.querySelector('.openpose-widget');
  var wrapper = container.querySelector('.three-wrapper');
  var viewLabel = container.querySelector('.view-label');
  var jointLabel = container.querySelector('.joint-label');

  var scene, camera, renderer, raycaster, mouse;
  var jointMeshes = {}, boneMeshes = [];
  var animationId;

  // Interaction state
  var mode = 'none'; // 'none', 'orbit', 'drag_joint'
  var dragTarget = null;
  var dragPlane = null;
  var dragOffset = null;
  var prevMouse = {x: 0, y: 0};

  // Camera orbit state (spherical coords)
  var orbitCenter = {x: 0, y: 0.9, z: 0};
  var orbitRadius = 3.5;
  var orbitTheta = 0;        // horizontal angle (radians)
  var orbitPhi = Math.PI / 6; // vertical angle (radians, 0 = horizontal, PI/2 = top)

  function updateCameraFromOrbit() {
    if (!camera) return;
    var x = orbitCenter.x + orbitRadius * Math.cos(orbitPhi) * Math.sin(orbitTheta);
    var y = orbitCenter.y + orbitRadius * Math.sin(orbitPhi);
    var z = orbitCenter.z + orbitRadius * Math.cos(orbitPhi) * Math.cos(orbitTheta);
    camera.position.set(x, y, z);
    camera.lookAt(orbitCenter.x, orbitCenter.y, orbitCenter.z);
    viewLabel.textContent = 'Free View';
  }

  function loadThree() {
    return new Promise(function (resolve, reject) {
      if (window.THREE) { resolve(window.THREE); return; }
      var s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
      s.onload = function () { resolve(window.THREE); };
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function emitChange() {
    if (disabled || !onChange) return;
    var out = {joints: {}};
    JOINT_NAMES.forEach(function (n) {
      var p = jointPositions[n];
      out.joints[n] = {x: Math.round(p.x*1000)/1000, y: Math.round(p.y*1000)/1000, z: Math.round(p.z*1000)/1000};
    });
    onChange(out);
  }

  function updateBones() {
    var THREE = window.THREE;
    boneMeshes.forEach(function (bone) {
      var from = jointMeshes[bone.userData.from];
      var to = jointMeshes[bone.userData.to];
      if (!from || !to) return;
      var start = from.position, end = to.position;
      var mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
      var dir = new THREE.Vector3().subVectors(end, start);
      var len = dir.length();
      bone.position.copy(mid);
      bone.scale.set(1, len, 1);
      if (len > 0.001) {
        bone.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir.normalize());
      }
    });
  }

  async function initScene() {
    var THREE = await loadThree();

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    camera = new THREE.PerspectiveCamera(45, wrapper.clientWidth / wrapper.clientHeight, 0.1, 100);
    updateCameraFromOrbit();

    renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setSize(wrapper.clientWidth, wrapper.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    wrapper.insertBefore(renderer.domElement, wrapper.firstChild);

    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    var dl = new THREE.DirectionalLight(0xffffff, 0.5);
    dl.position.set(3, 5, 3);
    scene.add(dl);

    scene.add(new THREE.GridHelper(4, 16, 0x333333, 0x222222));

    // Joints
    var jointGeo = new THREE.SphereGeometry(0.04, 12, 12);
    JOINT_NAMES.forEach(function (name) {
      var c = JOINT_COLORS[name] || 0xffffff;
      var mat = new THREE.MeshStandardMaterial({color: c, emissive: c, emissiveIntensity: 0.4});
      var mesh = new THREE.Mesh(jointGeo.clone(), mat);
      mesh.userData.jointName = name;
      var p = jointPositions[name];
      mesh.position.set(p.x, p.y, p.z);
      scene.add(mesh);
      jointMeshes[name] = mesh;
    });

    // Bones
    var boneGeo = new THREE.CylinderGeometry(0.012, 0.012, 1, 6);
    BONES.forEach(function (pair) {
      var mat = new THREE.MeshBasicMaterial({color: 0xcccccc, transparent: true, opacity: 0.7});
      var bone = new THREE.Mesh(boneGeo, mat);
      bone.userData.from = pair[0];
      bone.userData.to = pair[1];
      scene.add(bone);
      boneMeshes.push(bone);
    });
    updateBones();

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    dragPlane = new THREE.Plane();
    dragOffset = new THREE.Vector3();

    // Animation
    function animate() {
      animationId = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    }
    animate();

    // --- Pointer events ---
    var canvas = renderer.domElement;

    function getMouseNDC(e) {
      var rect = canvas.getBoundingClientRect();
      return {
        x: ((e.clientX - rect.left) / rect.width) * 2 - 1,
        y: -((e.clientY - rect.top) / rect.height) * 2 + 1
      };
    }

    function onPointerDown(e) {
      e.stopPropagation();
      e.preventDefault();

      var m = getMouseNDC(e);
      mouse.set(m.x, m.y);
      prevMouse = {x: e.clientX, y: e.clientY};

      if (disabled) return;

      // Check if we hit a joint
      raycaster.setFromCamera(mouse, camera);
      var allJoints = JOINT_NAMES.map(function (n) { return jointMeshes[n]; });
      var intersects = raycaster.intersectObjects(allJoints);

      if (intersects.length > 0) {
        // Drag joint mode
        mode = 'drag_joint';
        dragTarget = intersects[0].object;

        var camDir = new THREE.Vector3();
        camera.getWorldDirection(camDir);
        dragPlane.setFromNormalAndCoplanarPoint(camDir, dragTarget.position);

        var intersection = new THREE.Vector3();
        raycaster.ray.intersectPlane(dragPlane, intersection);
        dragOffset.subVectors(dragTarget.position, intersection);

        dragTarget.material.emissiveIntensity = 1.0;
        dragTarget.scale.setScalar(1.8);

        jointLabel.textContent = dragTarget.userData.jointName.replace(/_/g, ' ');
        jointLabel.style.color = '#' + dragTarget.material.color.getHexString();
      } else {
        // Orbit mode
        mode = 'orbit';
      }

      canvas.setPointerCapture(e.pointerId);
      canvas.style.cursor = mode === 'orbit' ? 'grabbing' : 'crosshair';
    }

    function onPointerMove(e) {
      e.stopPropagation();
      e.preventDefault();

      if (mode === 'none') return;

      if (mode === 'orbit') {
        var dx = e.clientX - prevMouse.x;
        var dy = e.clientY - prevMouse.y;
        prevMouse = {x: e.clientX, y: e.clientY};

        orbitTheta -= dx * 0.01;
        orbitPhi += dy * 0.01;
        // Clamp phi to avoid flipping
        orbitPhi = Math.max(-Math.PI * 0.45, Math.min(Math.PI * 0.45, orbitPhi));
        updateCameraFromOrbit();
      }

      if (mode === 'drag_joint' && dragTarget) {
        var m = getMouseNDC(e);
        mouse.set(m.x, m.y);
        raycaster.setFromCamera(mouse, camera);
        var intersection = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(dragPlane, intersection)) {
          dragTarget.position.copy(intersection.add(dragOffset));
          updateBones();
        }
      }
    }

    function onPointerUp(e) {
      e.stopPropagation();
      e.preventDefault();

      if (canvas.hasPointerCapture(e.pointerId)) {
        canvas.releasePointerCapture(e.pointerId);
      }

      if (mode === 'drag_joint' && dragTarget) {
        dragTarget.material.emissiveIntensity = 0.4;
        dragTarget.scale.setScalar(1.0);
        // Sync positions and emit
        JOINT_NAMES.forEach(function (n) {
          if (jointMeshes[n]) {
            var p = jointMeshes[n].position;
            jointPositions[n] = {x: p.x, y: p.y, z: p.z};
          }
        });
        emitChange();
      }

      mode = 'none';
      dragTarget = null;
      canvas.style.cursor = 'grab';
      jointLabel.textContent = 'Drag joints to pose | Drag empty to orbit';
      jointLabel.style.color = '#888';
    }

    function onWheel(e) {
      e.stopPropagation();
      e.preventDefault();
      orbitRadius += e.deltaY * 0.003;
      orbitRadius = Math.max(1.5, Math.min(10, orbitRadius));
      updateCameraFromOrbit();
    }

    canvas.addEventListener('pointerdown', onPointerDown);
    canvas.addEventListener('pointermove', onPointerMove);
    canvas.addEventListener('pointerup', onPointerUp);
    canvas.addEventListener('pointercancel', onPointerUp);
    canvas.addEventListener('wheel', onWheel, {passive: false});
    canvas.style.cursor = 'grab';

    wrapper._cleanup = function () {
      canvas.removeEventListener('pointerdown', onPointerDown);
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerup', onPointerUp);
      canvas.removeEventListener('pointercancel', onPointerUp);
      canvas.removeEventListener('wheel', onWheel);
      if (animationId) cancelAnimationFrame(animationId);
      if (renderer) renderer.dispose();
    };
  }

  // View presets
  function setOrbitView(theta, phi, label) {
    orbitTheta = theta;
    orbitPhi = phi;
    orbitRadius = 3.5;
    updateCameraFromOrbit();
    viewLabel.textContent = label;
  }

  var btnFront = container.querySelector('.btn-front');
  var btnSide = container.querySelector('.btn-side');
  var btnTop = container.querySelector('.btn-top');
  var btnReset = container.querySelector('.btn-reset');

  function hFront(e) { e.stopPropagation(); e.preventDefault(); setOrbitView(0, Math.PI/6, 'Front View'); }
  function hSide(e) { e.stopPropagation(); e.preventDefault(); setOrbitView(Math.PI/2, Math.PI/6, 'Side View'); }
  function hTop(e) { e.stopPropagation(); e.preventDefault(); setOrbitView(0, Math.PI/2.1, 'Top View'); }
  function hReset(e) {
    if (disabled) return;
    e.stopPropagation(); e.preventDefault();
    JOINT_NAMES.forEach(function (n) {
      var d = DEFAULT_POS[n];
      jointPositions[n] = {x:d.x,y:d.y,z:d.z};
      if (jointMeshes[n]) jointMeshes[n].position.set(d.x, d.y, d.z);
    });
    updateBones();
    emitChange();
  }

  btnFront.addEventListener('click', hFront);
  btnSide.addEventListener('click', hSide);
  btnTop.addEventListener('click', hTop);
  btnReset.addEventListener('click', hReset);

  function stopEvent(e) { e.stopPropagation(); }
  widgetEl.addEventListener('pointerdown', stopEvent);
  widgetEl.addEventListener('mousedown', stopEvent);

  initScene().catch(function (err) {
    console.error('OpenPose init failed:', err);
    wrapper.innerHTML = '<div style="color:#a44;padding:16px;text-align:center;">Failed to load 3D scene</div>';
  });

  return function () {
    if (wrapper._cleanup) wrapper._cleanup();
    btnFront.removeEventListener('click', hFront);
    btnSide.removeEventListener('click', hSide);
    btnTop.removeEventListener('click', hTop);
    btnReset.removeEventListener('click', hReset);
    widgetEl.removeEventListener('pointerdown', stopEvent);
    widgetEl.removeEventListener('mousedown', stopEvent);
  };
}
