// iso_test.js: reference Three.js scene module (a tiny isometric "Monument Valley" diorama) showing the module contract.
//   export async function init(renderer, params, env) → state      build scene/camera once (env.THREE, env.loadImage, env.T)
//   export function draw(lt, env)                                   pose everything from lt/env.t only, then
//                                                                   env.renderer.render(scene, camera) into the bound target
// The engine binds a transparent, multisampled render target before draw() and composites it as a layer (linear → sRGB).
// Never call renderer.setRenderTarget() or rely on the previous frame.
//   params: rotate (deg, keyframable: Monument Valley quarter turns), zoom (ortho half-height in world units), marker (bool)
import * as THREE from 'three';

export async function init(renderer, params, env) {
  const scene = new THREE.Scene();
  const zoom = params.zoom ?? 6.5, aspect = 16 / 9;
  const cam = new THREE.OrthographicCamera(-zoom * aspect, zoom * aspect, zoom, -zoom, -100, 100);
  cam.position.set(10, 10 * Math.SQRT1_2 * 1.15, 10); cam.lookAt(0, 0.6, 0);        // true isometric-ish
  scene.add(new THREE.HemisphereLight('#ffffff', '#5a5650', 1.3));
  const sun = new THREE.DirectionalLight('#ffffff', 2.2); sun.position.set(6, 12, 3); scene.add(sun);
  const paper = new THREE.MeshLambertMaterial({ color: '#ece7dc' }), shade = new THREE.MeshLambertMaterial({ color: '#b9b3a6' });
  const inkLine = new THREE.LineBasicMaterial({ color: '#0b0b0c' });
  const pivot = new THREE.Group(); scene.add(pivot);
  const box = (w, h, d, x, y, z, m = paper) => {
    const geo = new THREE.BoxGeometry(w, h, d), mesh = new THREE.Mesh(geo, m); mesh.position.set(x, y + h / 2, z);
    mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), inkLine)); pivot.add(mesh); return mesh;
  };
  box(8, 0.6, 8, 0, -0.6, 0, shade);                         // plinth
  box(2, 4, 2, -2.5, 0, -2.5); box(2, 2.5, 2, -0.5, 0, -2.5); box(2, 1, 2, 1.5, 0, -2.5);   // stepped towers
  for (let k = 0; k < 6; k++) box(1.2, 0.35 * (k + 1), 0.8, 2.6, 0, -1.4 + k * 0.8);       // stairs (Ascending and Descending, nearly)
  box(1, 3, 1, -2.8, 0, 2.2); box(1, 3, 1, -0.8, 0, 2.2); box(3, 0.6, 1, -1.8, 3, 2.2);    // an arch (the Loop's el track)
  box(6.5, 0.25, 1.1, 0, 3.6, 0.2, shade);                    // elevated walkway
  const marker = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.9, 0.42), new THREE.MeshLambertMaterial({ color: '#ff7a1a', emissive: '#ff7a1a', emissiveIntensity: 0.35 }));
  marker.visible = params.marker !== false; pivot.add(marker);
  return { scene, cam, pivot, marker };
}

export function draw(lt, env) {
  const { scene, cam, pivot, marker } = env.state;
  pivot.rotation.y = env.val(env.params.rotate, 0) * Math.PI / 180;
  // the marker walks the walkway and back (a function of time only)
  const u = (Math.sin(lt * 1.3) + 1) / 2;
  marker.position.set(-2.8 + 5.6 * u, 3.85 + 0.45, 0.2);
  env.renderer.render(scene, cam);
}
