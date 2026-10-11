// timing.js: the TimeMap over the song's timing JSON (analysis/cinematic/timing.json, else the engine stub).
// Pure: used by the page (shots, modules) and by render.mjs (to resolve ranges written as bar:beat).
//
// Accepted timing JSON (tolerant; extra fields ignored):
//   { duration, bpm, beats_per_bar (4),
//     beats:     [t, ...]  or [{t|time|start, bar?, beat?}, ...]
//     downbeats: [t, ...]  or [{t|time|start, bar?}]      (or bars: [{bar|n, t|start}])
//     first_bar: 1         (bar number of downbeats[0]; default 1)
//     sections:  [{id|name|label, start, end}]
//     lines | lyrics.lines: [{id?, text, start, end, words?: [{w, start, end}]}]
//     words:     [{w|word|text, start, end, line|line_idx|line_index}]
//     events:    [{start|t, type, label}]   (each type becomes an event list: on: 'impact', T.list('trailer_impact'))
//     kicks/snares/onsets.{name}: [t...], envelopes: {fps, rms:[...], ...} }
//   This is the schema of analysis/cinematic/timing.json (beats[{t,bar,beat,downbeat}], bars[{bar,start,end}], lyrics.lines[].words).
//
// Absolute time expressions (shot start/end, ranges, absolute keyframe times):
//   12.5                     seconds
//   "17:1"  "17:2.5"         bar:beat, both 1-based (beat may be fractional) on the tracked grid
//   "beat:64"                beat index (0-based, fractional ok)
//   "word:rewind"  "word:rewind#2"  "word:stop@40"  "wordEnd:defense"   word onset/offset (#n = n-th, @s = first after s seconds)
//   "line:3" "lineEnd:3"     lyric line (0-based)        "section:drop1" "sectionEnd:drop1"     "event:impact#2"
//   any of these + offsets:  "17:1+0.5b"  "word:rewind-2f"  "section:drop1+1bar"  "33.0+0.25"   (s | b beats | bar | f frames @24)
import { clamp, fin } from './core.js';

const norm = s => String(s).toLowerCase().replace(/[^a-z0-9']/g, '').replace(/'/g, '');
const num = x => (typeof x === 'number' ? x : x && (x.t ?? x.time ?? x.start));
const lastLE = (arr, t) => { let lo = 0, hi = arr.length - 1, ans = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (arr[m] <= t + 1e-9) { ans = m; lo = m + 1; } else hi = m - 1; } return ans; };

export class TimeMap {
  constructor(d = {}, info = {}) {
    this.d = d; this.info = info; this.isStub = !!(d.stub || info.stub);
    this.fps = 24;
    this.duration = fin(d.duration ?? d.source?.duration_s, 228.0);
    this.beatsPerBar = fin(d.beats_per_bar ?? d.time_signature?.[0], 4);
    this.beats = (d.beats || []).map(num).filter(Number.isFinite).sort((a, b) => a - b);
    this.bpm = fin(d.bpm ?? d.tempo?.verified_bpm ?? d.tempo?.nominal_bpm, this.beats.length > 8 ? 60 / median(diffs(this.beats)) : 136);
    this.period = 60 / this.bpm;
    if (!this.beats.length) { const off = fin(d.offset, 0); for (let t = off; t < this.duration + 4; t += this.period) this.beats.push(t); }
    // downbeats / bars
    let downs = (d.downbeats || []).map(num).filter(Number.isFinite);
    this.firstBar = fin(d.first_bar, 1);
    if (!downs.length && Array.isArray(d.bars)) {
      const bars = d.bars.map(b => ({ n: fin(b.bar ?? b.n, NaN), t: num(b) })).filter(b => Number.isFinite(b.t));
      downs = bars.map(b => b.t); if (bars.length && Number.isFinite(bars[0].n)) this.firstBar = bars[0].n;
    }
    if (!downs.length && (d.beats || []).some(b => b && (b.downbeat || b.beat === 1))) downs = d.beats.filter(b => b && (b.downbeat || b.beat === 1)).map(num);
    if (!downs.length) downs = this.beats.filter((_, i) => i % this.beatsPerBar === 0);
    this.downbeats = downs.sort((a, b) => a - b);
    this.downBeatIdx = this.downbeats.map(t => this.beatIndexAt(t));   // fractional beat index of each downbeat (≈ integer)
    this.sections = (d.sections || []).map(s => ({ ...s, name: s.name ?? s.id ?? s.label, start: num(s), end: s.end }));
    // words + lines
    const srcLines = d.lines || d.lyrics?.lines || null;
    let words = d.words || [];
    if (!words.length && Array.isArray(srcLines) && srcLines.some(l => Array.isArray(l.words))) words = srcLines.flatMap((l, li) => (l.words || []).map(w => ({ ...w, line: li })));
    this.words = words.map(w => ({ text: String(w.w ?? w.word ?? w.text ?? '').trim(), start: +w.start, end: +(w.end ?? w.start + 0.3),
      line: w.line ?? w.line_idx ?? w.line_index ?? null, raw: w })).filter(w => w.text && Number.isFinite(w.start)).sort((a, b) => a.start - b.start);
    this.words.forEach((w, i) => { w.i = i; w.key = norm(w.text); });
    if (this.words.length && this.words.every(w => w.line === null)) {        // derive lines from gaps / punctuation
      let li = 0; this.words.forEach((w, i) => { if (i > 0 && (w.start - this.words[i - 1].end > 0.9 || /[.,!?;…]$/.test(this.words[i - 1].text))) li++; w.line = li; });
    }
    const L = Array.isArray(srcLines) && srcLines.length ? srcLines : null;
    const nLines = this.words.length ? Math.max(...this.words.map(w => +w.line)) + 1 : (L ? L.length : 0);
    this.lines = [];
    for (let i = 0; i < Math.max(nLines, L ? L.length : 0); i++) {
      const ws = this.words.filter(w => +w.line === i);
      const src = L && L[i] || {};
      this.lines.push({ i, id: src.id ?? null, section: src.section ?? null, text: src.text ?? ws.map(w => w.text).join(' '), start: fin(+src.start, ws[0]?.start ?? NaN), end: fin(+src.end, ws.length ? ws[ws.length - 1].end : NaN), words: ws });
    }
    this.lines = this.lines.filter(l => Number.isFinite(l.start));
    this.lines.forEach((l, i) => { l.i = i; for (const w of l.words) w.line = i; });
    this.lineStarts = this.lines.map(l => l.start);
    this.wordStarts = this.words.map(w => w.start);
    this.env = d.envelopes || {}; this.envFps = fin(this.env.fps, 24);
    this.events = (d.events || []).map(e => ({ ...e, t: num(e) })).filter(e => Number.isFinite(e.t)).sort((a, b) => a.t - b.t);
    this.lists = {};
    for (const e of this.events) (this.lists[e.type] ||= []).push(e.t);
    if (d.lyrics?.vocal_chops) this.lists.vocal_chops = d.lyrics.vocal_chops.map(num);
    Object.assign(this.lists, { beats: this.beats, downbeats: this.downbeats, kicks: (d.kicks || d.onsets?.kick || []).map(num), snares: (d.snares || d.onsets?.snare || []).map(num), words: this.wordStarts, lines: this.lineStarts });
  }

  // ---- beat grid ----
  // time of fractional beat index x (0-based), extrapolated with the local period outside the tracked list
  beatTime(x) {
    const b = this.beats, n = b.length; if (!n) return x * this.period;
    if (x <= 0) return b[0] + x * (n > 1 ? b[1] - b[0] : this.period);
    if (x >= n - 1) return b[n - 1] + (x - n + 1) * (n > 1 ? b[n - 1] - b[n - 2] : this.period);
    const i = Math.floor(x); return b[i] + (b[i + 1] - b[i]) * (x - i);
  }
  // fractional beat index at time t (inverse of beatTime)
  beatIndexAt(t) {
    const b = this.beats, n = b.length; if (!n) return t / this.period;
    if (t <= b[0]) return (t - b[0]) / (n > 1 ? b[1] - b[0] : this.period);
    if (t >= b[n - 1]) return n - 1 + (t - b[n - 1]) / (n > 1 ? b[n - 1] - b[n - 2] : this.period);
    const i = lastLE(b, t); return i + (t - b[i]) / (b[i + 1] - b[i]);
  }
  // bar:beat (1-based) → seconds
  barBeat(bar, beat = 1) {
    const k = bar - this.firstBar, D = this.downBeatIdx;
    let b0;
    if (k >= 0 && k < D.length) b0 = Math.round(D[k]);
    else if (k < 0) b0 = Math.round(D[0] ?? 0) + k * this.beatsPerBar;
    else b0 = Math.round(D[D.length - 1] ?? 0) + (k - D.length + 1) * this.beatsPerBar;
    return this.beatTime(b0 + (beat - 1));
  }
  // seconds → {bar, beat (1-based, fractional)}
  barBeatAt(t) {
    const x = this.beatIndexAt(t), D = this.downBeatIdx;
    let k = -1; for (let i = 0; i < D.length; i++) if (D[i] <= x + 1e-6) k = i; else break;
    if (k < 0) { const d0 = D[0] ?? 0, kb = Math.floor((x - d0) / this.beatsPerBar); return { bar: this.firstBar + kb, beat: 1 + (x - d0 - kb * this.beatsPerBar) }; }
    if (k === D.length - 1 && x - D[k] >= this.beatsPerBar) { const kb = Math.floor((x - D[k]) / this.beatsPerBar); return { bar: this.firstBar + k + kb, beat: 1 + (x - D[k] - kb * this.beatsPerBar) }; }
    return { bar: this.firstBar + k, beat: 1 + x - Math.round(D[k]) };
  }
  list(name) { return Array.isArray(name) ? name : (this.lists[name] || this.lists.beats); }
  // events in [a, b)
  eventsIn(a, b, name = 'beats') { return this.list(name).filter(x => x >= a - 1e-6 && x < b - 1e-6); }
  countIn(a, b, name = 'beats') { return this.eventsIn(a, b, name).length; }
  lastEvent(t, name = 'beats') { const L = this.list(name), k = lastLE(L, t); return k < 0 ? null : L[k]; }
  nextEvent(t, name = 'beats') { const L = this.list(name), k = lastLE(L, t); return L[k + 1] ?? null; }
  // exponential pulse since the last event (1 at the event, decays with `decay` seconds)
  pulse(t, name = 'beats', decay = 0.12) { const e = this.lastEvent(t, name); return e === null ? 0 : Math.exp(-(t - e) / decay); }
  beatPhase(t) { const x = this.beatIndexAt(t); return { i: Math.floor(x), phase: x - Math.floor(x) }; }
  snap(t, name = 'beats') { const L = this.list(name), k = lastLE(L, t); const a = L[Math.max(0, k)], b = L[Math.min(L.length - 1, k + 1)]; return Math.abs(t - a) <= Math.abs(b - t) ? a : b; }

  // ---- lyrics ----
  // word("rewind") → first occurrence; word("rewind", 2) → second; word("stop", 1, {after: 40}). Throws when missing:
  // a silent fallback would put a cut on the wrong frame.
  word(text, n = 1, opt = {}) {
    const k = norm(text), after = opt.after ?? -1e9; let c = 0;
    for (const w of this.words) if (w.key === k && w.start >= after - 1e-6 && ++c === n) return w;
    throw new Error(`word("${text}"${n > 1 ? ', ' + n : ''}) not in timing (${this.info.source || 'timing'})`);
  }
  section(name, n = 1) { let c = 0; for (const s of this.sections) if ((s.name === name || s.id === name || s.label === name) && ++c === n) return s; throw new Error(`section "${name}" not in timing`); }
  sectionAt(t) { let r = null; for (const s of this.sections) if (t >= s.start - 1e-9 && t < s.end) r = s; return r; }
  event(type, n = 1) { let c = 0; for (const e of this.events) if (e.type === type && ++c === n) return e.t; throw new Error(`event "${type}" #${n} not in timing`); }
  // the word being sung at t (start <= t < end + hold), with progress 0..1 through it
  wordAt(t, hold = 0.12) {
    const k = lastLE(this.wordStarts, t); if (k < 0) return null;
    const w = this.words[k]; if (t >= w.end + hold) return null;
    return { ...w, progress: clamp((t - w.start) / Math.max(0.05, w.end - w.start)) };
  }
  // the lyric line on screen at t: from start - lead until end + hold (or the next line's start - lead)
  lineAt(t, lead = 0.35, hold = 0.6) {
    const k = lastLE(this.lineStarts, t + lead); if (k < 0) return null;
    const l = this.lines[k], next = this.lines[k + 1];
    const until = Math.min(l.end + hold, next ? next.start - lead : 1e9);
    return t < until ? l : null;
  }
  // everything a typography module needs at t
  lyric(t, opt = {}) {
    const lead = opt.lead ?? 0.35, hold = opt.hold ?? 0.6;
    const l = this.lineAt(t, lead, hold);
    const w = this.wordAt(t, opt.wordHold ?? 0.12);
    if (!l) return { line: null, word: w, words: [], lineProgress: 0, next: this.lines[lastLE(this.lineStarts, t + lead) + 1] || null };
    const words = l.words.map(x => ({ text: x.text, start: x.start, end: x.end, i: x.i,
      state: t < x.start ? 'future' : t < x.end ? 'current' : 'past', progress: clamp((t - x.start) / Math.max(0.05, x.end - x.start)) }));
    return { line: l, lineIndex: l.i, text: l.text, word: w, wordIndex: w ? l.words.findIndex(x => x.i === w.i) : -1, words,
      lineProgress: clamp((t - l.start) / Math.max(0.05, l.end - l.start)), appear: clamp((t - (l.start - lead)) / lead),
      vanish: clamp((t - l.end) / hold), next: this.lines[l.i + 1] || null };
  }

  // ---- envelopes ----
  e(key, t) {
    const a = this.env[key]; if (!a || !a.length) return 0;
    const x = t * this.envFps, i = Math.floor(x);
    if (i <= 0) return fin(a[0]); if (i >= a.length - 1) return fin(a[a.length - 1]);
    return fin(a[i] + (a[i + 1] - a[i]) * (x - i));
  }

  // ---- absolute time expressions ----
  time(x) {
    if (x === null || x === undefined) return x;
    if (typeof x === 'number') return x;
    if (typeof x === 'object') {
      if ('bar' in x) return this.barBeat(x.bar, x.beat ?? 1) + fin(x.offset, 0);
      if ('word' in x) return this.word(x.word, x.n ?? 1, x)[x.end ? 'end' : 'start'] + fin(x.offset, 0);
      if ('t' in x) return +x.t;
      throw new Error('bad time ' + JSON.stringify(x));
    }
    const s = String(x).trim();
    const m = s.match(/^(.*?)((?:[+-]\d*\.?\d+(?:bar|b|f|s)?)*)$/);
    let base = m[1], off = m[2];
    if (base === '' && off) { base = off.match(/^[+-]?\d*\.?\d+/)[0]; off = off.slice(base.length); }   // plain "-0.5"
    let t;
    if (/^-?\d*\.?\d+$/.test(base)) t = +base;
    else if (/^\d+:\d*\.?\d+$/.test(base)) { const [b, bt] = base.split(':').map(Number); t = this.barBeat(b, bt); }
    else {
      const p = base.indexOf(':'); if (p < 0) throw new Error(`bad time expression "${s}"`);
      const kind = base.slice(0, p), arg = base.slice(p + 1);
      if (kind === 'beat' || kind === 'b') t = this.beatTime(+arg);
      else if (kind === 'word' || kind === 'wordEnd') {
        const mm = arg.match(/^([^#@]+)(?:#(\d+))?(?:@(\d*\.?\d+))?$/); if (!mm) throw new Error(`bad word ref "${s}"`);
        const w = this.word(mm[1], mm[2] ? +mm[2] : 1, { after: mm[3] !== undefined ? +mm[3] : undefined });
        t = kind === 'word' ? w.start : w.end;
      } else if (kind === 'line' || kind === 'lineEnd') { const l = this.lines[+arg]; if (!l) throw new Error(`line ${arg} not in timing`); t = kind === 'line' ? l.start : l.end; }
      else if (kind === 'section' || kind === 'sectionEnd') { const sc = this.section(arg); t = kind === 'section' ? sc.start : sc.end; }
      else if (kind === 'event') { const mm = arg.match(/^([^#]+)(?:#(\d+))?$/); t = this.event(mm[1], mm[2] ? +mm[2] : 1); }
      else throw new Error(`unknown time kind "${kind}" in "${s}"`);
    }
    for (const o of off.match(/[+-]\d*\.?\d+(?:bar|b|f|s)?/g) || []) {
      const v = parseFloat(o), u = o.replace(/^[+-]\d*\.?\d+/, '');
      if (u === 'b') t = this.beatTime(this.beatIndexAt(t) + v);
      else if (u === 'bar') t = this.beatTime(this.beatIndexAt(t) + v * this.beatsPerBar);
      else if (u === 'f') t += v / this.fps;
      else t += v;
    }
    return t;
  }
  // duration expression relative to a start time: 2.5 | "4b" | "2bar" | "12f" | "2.5s"
  dur(start, x) {
    if (typeof x === 'number') return x;
    const m = String(x).match(/^(\d*\.?\d+)(bar|b|f|s)?$/); if (!m) throw new Error(`bad duration "${x}"`);
    const v = +m[1], u = m[2] || 's';
    if (u === 'b') return this.beatTime(this.beatIndexAt(start) + v) - start;
    if (u === 'bar') return this.beatTime(this.beatIndexAt(start) + v * this.beatsPerBar) - start;
    if (u === 'f') return v / this.fps;
    return v;
  }
}

function diffs(a) { const r = []; for (let i = 1; i < a.length; i++) r.push(a[i] - a[i - 1]); return r; }
function median(a) { const s = [...a].sort((x, y) => x - y); return s[s.length >> 1] || 0.44; }

// candidate timing files, first that exists wins (paths relative to the repo root)
export const TIMING_PATHS = ['analysis/cinematic/timing.json', 'render/engine/data/timing.stub.json'];
