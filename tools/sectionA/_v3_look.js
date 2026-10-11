// look-dev for tools/sectionA/modules/woodcut.js on the v3 keyframes (stills only):
//   node render/engine/render.mjs --timeline tools/sectionA/_v3_look.js --stills 1,3
const WC = 'tools/sectionA/modules/woodcut.js';
export default {
  name: 'A_v3_look', range: [0, 4], background: '#0b0b0c',
  shots: [
    { id: 'lens', start: 0, end: 2, layers: [
      { type: 'image', src: 'media/shots/D5/kf_v3_cu.jpg', fit: 'cover' },
      { type: 'canvas', module: WC, blend: 'screen', params: { text: 'MEN IN\nSHADES', at: 0, box: [560, 400], corners: [275, 335, 835, 335, 835, 735, 275, 735] } },
      { type: 'canvas', module: WC, blend: 'screen', params: { text: 'AND\nSUITS', at: 0, box: [560, 400], corners: [1085, 335, 1645, 335, 1645, 735, 1085, 735] } },
    ], fx: [{ type: 'letterbox', aspect: 2.39, amount: 1 }] },
    { id: 'sign', start: 2, end: 4, layers: [
      { type: 'image', src: 'media/shots/D2/kf_v3_d.jpg', fit: 'cover' },
      { type: 'canvas', module: WC, params: { text: 'A SHADOW', at: 0, reveal: 'bulb', color: '#0b0b0c', flecks: 0, box: [380, 170], corners: [1212, 62, 1592, 62, 1592, 232, 1212, 232] } },
      { type: 'canvas', module: WC, params: { text: 'CHASING ME', at: 0, reveal: 'bulb', color: '#0b0b0c', flecks: 0, box: [400, 210], corners: [1192, 320, 1592, 320, 1592, 530, 1192, 530] } },
    ], fx: [{ type: 'letterbox', aspect: 2.39, amount: 1 }] },
  ],
};
