// Section file template. Copy to render/timeline/<SECTION>.js (files starting with "_" are ignored).
// render/timeline.js merges every section file; overlapping shots across files are an error, gaps get placeholder slates.
// Layer types, fx, modules and params: render/engine/README.md. Check with:
//   node render/engine/render.mjs --list                       resolved shot table
//   node render/engine/render.mjs --stills 84.9,86.2 --preview  stills
//   node render/engine/render.mjs --range 49:1 51:1 --preview --encode
export default ({ T }) => ({
  section: 'X',
  fx: [],                                     // applied to every shot of this section (before each shot's own fx)
  shots: [
    {
      id: 'V2e', start: '49:1', end: '51:1',  // seconds, "bar:beat", "word:back", "section:verse2", offsets "+2b" ...
      layers: [
        { id: 'plate', type: 'video', src: 'media/shots/V2e1/take_1_engraved.mp4', in: 0.4, rate: 1,
          matte: { src: 'media/shots/V2e1/take_1_matte/', mode: 'luma' }, keepColor: true },
        { type: 'canvas', module: 'slam', stage: 'post', params: { text: 'back on the road', sync: 'lyric', color: '#0b0b0c' } },
      ],
      fx: [{ type: 'isolate', amount: 1, engrave: 0.4 }, { type: 'punch', on: 'downbeat', amount: 0.03 }],
    },
  ],
  overlays: [],                               // HUD clusters spanning several shots, etc.
});
