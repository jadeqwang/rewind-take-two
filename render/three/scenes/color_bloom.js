// Scene 3 - "Color bloom". Same mechanic and timeline as rotate_connect, framed wider. The world starts as a
// black-and-white wood engraving (only Jade is in colour); when the turntable locks into the impossible
// joint, colour floods out from the pivot as colored-pencil strokes (orange, sky blue, gold; Klimt gold
// mosaic on the tower and turntable, Kandinsky rings in the sun), while the engraving stays on top.
import { createScene } from './rotate_connect.js';

const inst = createScene({ bloom: true });
export const meta = inst.meta;
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
