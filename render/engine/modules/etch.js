// etch.js: mirror-etch text ("OBJECTS IN MIRROR…" style), i.e. pin.js with style 'etch'. Same params as pin.js
// (corners to lay it along the mirror's edge; text + sync: 'lyric' for word timing). Use blend: 'screen' over dark glass.
import { draw as pinDraw } from './pin.js';
export function draw(lt, env) { return pinDraw(lt, { ...env, params: { style: 'etch', ...env.params } }); }
