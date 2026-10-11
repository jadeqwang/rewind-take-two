// Section B helper: the engine's motes burst on the layer's CONTENT clock (env.t is real time, so tapeStop/hold/time
// remaps would not freeze the stock module). params as modules/motes.js; `at` is layer-local.
import { draw as motesDraw } from '../engine/modules/motes.js';
export function draw(lt, env) { return motesDraw(lt, { ...env, t: env.origin + env.lt }); }
