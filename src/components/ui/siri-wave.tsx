"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

const VERTEX_SHADER = `
attribute vec2 aPos;
void main() {
  gl_Position = vec4(aPos, 0.0, 1.0);
}
`;

const FLUID_DOTS_FRAGMENT = `
precision highp float;
uniform vec2 iResolution;
uniform float iTime;
uniform float uSpeaking;
const float TAU = 6.28318530718;
const int N = 6;
const float SMOOTH_K = 0.08;
const float INTENSITY = 0.0025;
const float FALLOFF_P = 1.35;
const float FADE_START = 0.02;
const float FADE_END = 0.56;
const float ABERR = 0.005;
const vec3 SPECTRAL = vec3(0.0, 0.5, 1.0) * ABERR;
const float HUE_SPEED = 0.06;
const float COLOR_K = 0.5;
const float SAT = 0.01;
const float HUE_SPAN = 0.667;

float hash11(float n) {
  return fract(sin(n * 127.1 + 311.7) * 43758.5453);
}

float settle(float tau) {
  if (tau <= 0.0) return 0.0;
  return 1.0 - exp(-3.2 * tau) * cos(4.6 * tau);
}

float smin(float a, float b, float k) {
  float h = max(k - abs(a - b), 0.0) / k;
  return min(a, b) - h * h * k * 0.25;
}

vec3 hue2rgb(float h) {
  h = fract(h);
  float r = clamp(abs(h * 6.0 - 3.0) - 1.0, 0.0, 1.0);
  float g = clamp(2.0 - abs(h * 6.0 - 2.0), 0.0, 1.0);
  float b = clamp(2.0 - abs(h * 6.0 - 4.0), 0.0, 1.0);
  return vec3(r, g, b);
}

float dotR(float fi, float seed, float t) {
  return 0.036 + 0.010 * sin(t * 1.3 + seed * TAU) + 0.005 * sin(t * 2.4 + fi * 1.3);
}

float dotSD(vec2 p, vec2 pos, float r, float t, float fi, float shapeDamp) {
  vec2 d = p - pos;
  float sq = 0.075 * (0.5 + 0.5 * sin(t * 0.9 + fi * 2.0)) * shapeDamp;
  float ca = cos(t * 0.35 + fi);
  float sa = sin(t * 0.35 + fi);
  d = mat2(ca, -sa, sa, ca) * d;
  d *= vec2(1.0 + sq, 1.0 - sq);
  return length(d) - r;
}

vec3 scene(vec2 p, float t) {
  float k = floor(t / 6.0);
  float u = fract(t / 6.0);
  float te = u * 6.0;
  float tg = mod(t, 12.0);
  float g = settle((tg - 9.2) * 1.8) - settle((tg - 9.2 - 0.8) * 6.5);
  float gC = clamp(g, 0.0, 1.0);
  vec3 total3 = vec3(1e5);
  vec3 cAcc = vec3(0.0);
  float wAcc = 1e-6;
  float speak = clamp(uSpeaking, 0.0, 1.0);

  for (int i = 0; i < N; i++) {
    float fi = float(i);
    float seed = hash11(fi);
    float ang = fi / float(N) * TAU + t * 0.35;
    vec2 dir = vec2(cos(ang), sin(ang));

    float R = 0.17 + 0.010 * sin(t * 1.0) + 0.007 * sin(t * 1.3 + seed * TAU);
    float pairId = mod(fi, 3.0);
    float moverLow = mod(k + pairId, 2.0);
    float isMover = (fi < 2.5) ? step(moverLow, 0.5) : step(0.5, moverLow);
    float goStart = pairId * 0.33;
    float retStart = 3.0 * 0.33 + 0.0 + pairId * 0.33;
    float m = (settle(te - goStart) - settle(te - retStart)) * isMover;
    float rec = (settle(te - goStart - 0.11) - settle(te - retStart - 0.11)) * (1.0 - isMover);
    float rSelf = dotR(fi, seed, t);
    rSelf = mix(rSelf, 0.036, gC);
    float fj = mod(fi + 3.0, 6.0);
    float rPart = dotR(fj, hash11(fj), t);
    float deep = -(R + 0.035) - 0.12 * rPart;
    float radial = mix(R, deep, m) + 0.035 * rec;
    radial = mix(radial, 0.008, g);
    vec2 pos = radial * dir;

    float activeSpread = mix(1.0, 0.08, speak);
    pos *= activeSpread;
    pos += dir * 0.18 * (1.0 - speak);

    float sdR = dotSD(p - SPECTRAL.r * dir, pos, rSelf, t, fi, 1.0 - gC);
    float sdG = dotSD(p - SPECTRAL.g * dir, pos, rSelf, t, fi, 1.0 - gC);
    float sdB = dotSD(p - SPECTRAL.b * dir, pos, rSelf, t, fi, 1.0 - gC);

    total3 = vec3(
      smin(total3.r, sdR, SMOOTH_K),
      smin(total3.g, sdG, SMOOTH_K),
      smin(total3.b, sdB, SMOOTH_K)
    );

    float hue = fract(fi / float(N) + t * HUE_SPEED) * HUE_SPAN;
    vec3 dotCol = mix(vec3(1.0), hue2rgb(hue), SAT);
    float w = exp(-sdG * COLOR_K);
    cAcc += w * dotCol;
    wAcc += w;
  }

  vec3 sd3 = max(total3, vec3(0.0)) + 1e-4;
  vec3 core3 = clamp(INTENSITY / pow(sd3, vec3(FALLOFF_P)), 0.0, 1.0);
  vec3 edge3 = 1.0 - smoothstep(vec3(FADE_START), vec3(FADE_END), sd3);
  vec3 bright = core3 * edge3 * mix(1.0, 0.8, speak);
  return bright * (cAcc / wAcc);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 res = iResolution.xy;
  vec2 p = (2.0 * fragCoord - res) / min(res.x, res.y);
  float t = iTime;
  float speak = clamp(uSpeaking, 0.0, 1.0);
  p /= mix(1.0, 1.8, speak);
  vec3 col = scene(p, t);
  col *= 1.0 + 0.05 * sin(t * 1.0 + 1.0);
  col = pow(col, vec3(1.0 / 1.2));
  col = min(col, 1.0);
  float n = fract(sin(dot(fragCoord, vec2(12.9898, 78.233))) * 43758.5453);
  col += (n - 0.5) / 255.0;
  fragColor = vec4(col, 1.0);
}

void main() {
  mainImage(gl_FragColor, gl_FragCoord.xy);
}
`;

const WAVE_FRAGMENT = `
precision highp float;
uniform vec2 iResolution;
uniform float iTime;
const float PI = 3.14159265359;
const float AMPLITUDE = 0.32;
const float FREQ = 1.1;
const float ABER_FREQ = 1.0;
const float SPEED = 2.4;
const float WAVE_SCALE = 0.6;
const float ABERRATION = 2.6;
const float THICKNESS = 3.0;
const float INTENSITY = 2.0;
const float FALLOFF = 1.7;
const float EDGE_MASK = 0.4;
const float EDGE_INSET = 0.0;
const float BAND_FILL = 30000.0;
const float BAND_THICK = 0.08;
const float SOFTNESS = 2.5;
const float LOW_AMP = 6.0;
const float LOW_INT = 1.5;
const float MID_ABER = 0.8;
const float MID_ABAMP = 0.05;
const float MID_BAND = 20.0;
const float MID_SOFT = 0.4;
const float HIGH_ABER = 0.5;
const float HIGH_ABAMP = 0.06;
const float RESOLVED = 1.0;
const float UNRES_SCALE = 0.14;

vec3 spectral4(int s) {
  float x = float(s);
  return clamp(vec3(abs(x - 3.0) - 1.0, 2.0 - abs(x - 2.0), 2.0 - abs(x - 4.0)), 0.0, 1.0);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  vec2 R = iResolution.xy;
  float aspect = R.x / R.y;
  vec2 p = (fragCoord + 0.5) * 2.0 / R - 1.0;
  p.x *= aspect;
  float yScreen = p.y;
  p /= max(WAVE_SCALE, 0.1);
  float t = iTime;
  float low = clamp(0.45 + 0.45 * sin(t * 0.8) * sin(t * 0.37 + 1.0), 0.0, 1.0);
  float mid = clamp(0.40 + 0.40 * sin(t * 1.7 + 2.0) * sin(t * 0.53), 0.0, 1.0);
  float high = clamp(0.30 + 0.30 * sin(t * 2.9 + 4.0) * sin(t * 0.71 + 2.0), 0.0, 1.0);
  float res = clamp(RESOLVED, 0.0, 1.0);
  float drift = mod(t, 20.0 * PI) * SPEED;
  float xN = p.x / max(aspect, 1.0);
  float env = cos(PI * 0.5 * min(abs(0.9 * xN), 1.0));
  env *= env;
  float A1 = AMPLITUDE + 0.01 * low * LOW_AMP;
  float A2 = A1 + mid * MID_ABAMP + high * HIGH_ABAMP;
  float AB = (ABERRATION + mid * MID_ABER + high * HIGH_ABER) * res;
  float th = mix(0.1, 0.01 * THICKNESS, res);
  float inten = mix(0.1, 0.01 * (INTENSITY + low * LOW_INT), res);
  float soft = 0.01 * res * max(0.0, SOFTNESS + mid * MID_SOFT);
  float dUnres = max(length(p) - mix(0.14, UNRES_SCALE, res), 0.0);
  float yMain = A1 * env * res * sin(p.x * FREQ + drift);
  float bandFillTh = max(BAND_THICK, 1e-4);
  float bandAmt = 1e-4 * BAND_FILL * inten;
  vec3 num = vec3(0.0);
  vec3 den = vec3(0.0);

  for (int s = 0; s < 4; s++) {
    vec3 hue = mix(vec3(1.0), spectral4(s), res);
    den += hue;
    float ab = mix(-AB, AB, float(s) / 3.0);
    float yL = A2 * env * res * sin(p.x * ABER_FREQ + drift + ab);
    float d = mix(dUnres, abs(p.y - yL), res);
    float lor = mix(1.0 / (1.0 + (0.02 * d) * (0.02 * d)), 1.0, res);
    float line = inten / (sqrt(d * d + soft * soft) + th);
    float lo = min(yMain, yL);
    float hi = max(yMain, yL);
    float dBand = max(0.0, max(p.y - hi, lo - p.y));
    float band = bandAmt / (dBand + bandFillTh);
    num += hue * lor * (line + band);
  }

  vec3 col = num / den;
  float dM = mix(dUnres, abs(p.y - yMain), res);
  float lorM = mix(1.0 / (1.0 + (0.02 * dM) * (0.02 * dM)), 1.0, res);
  float boost = (1.0 - res) * (14.0 * low + 4.0);
  col += 0.5 * inten * (lorM + boost) / (sqrt(dM * dM + soft * soft) + th);
  col = pow(max(col, 0.0), vec3(1.5));
  float emT = clamp((abs(yScreen) - 1.0 + EDGE_INSET) / (-max(EDGE_MASK, 1e-4)), 0.0, 1.0);
  float em = emT * emT * (3.0 - 2.0 * emT);
  float gauss = exp(-pow(xN * FALLOFF, 2.0));
  col *= mix(1.0, em * gauss, res);
  col *= res;
  fragColor = vec4(col, 1.0);
}

void main() {
  mainImage(gl_FragColor, gl_FragCoord.xy);
}
`;

type SiriWaveVariant = "wave" | "fluid-dots";

interface SiriWaveProps {
  variant?: SiriWaveVariant;
  size?: number;
  className?: string;
  active?: boolean;
  speaking?: boolean;
}

function compileShader(gl: WebGLRenderingContext, type: number, source: string) {
  const shader = gl.createShader(type);
  if (!shader) throw new Error("Failed to create shader");
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(log ?? "Shader compile error");
  }
  return shader;
}

function createProgram(gl: WebGLRenderingContext, fragmentSource: string) {
  const program = gl.createProgram();
  if (!program) throw new Error("Failed to create program");

  const vs = compileShader(gl, gl.VERTEX_SHADER, VERTEX_SHADER);
  const fs = compileShader(gl, gl.FRAGMENT_SHADER, fragmentSource);
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    throw new Error(gl.getProgramInfoLog(program) ?? "Program link error");
  }

  gl.deleteShader(vs);
  gl.deleteShader(fs);
  return program;
}

export function SiriWave({
  variant = "fluid-dots",
  size = 360,
  className,
  active = false,
  speaking = false,
}: SiriWaveProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const activeRef = useRef(active);
  const speakingRef = useRef(speaking);
  const speakingValueRef = useRef(0);

  useEffect(() => {
    activeRef.current = active;
  }, [active]);

  useEffect(() => {
    speakingRef.current = speaking;
  }, [speaking]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl");
    if (!gl) return;

    const fragmentSource = variant === "fluid-dots" ? FLUID_DOTS_FRAGMENT : WAVE_FRAGMENT;
    let program: WebGLProgram;

    try {
      program = createProgram(gl, fragmentSource);
    } catch {
      return;
    }

    gl.useProgram(program);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

    const aPos = gl.getAttribLocation(program, "aPos");
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

    const uResolution = gl.getUniformLocation(program, "iResolution");
    const uTime = gl.getUniformLocation(program, "iTime");
    const uSpeaking = gl.getUniformLocation(program, "uSpeaking");

    const renderScale = 0.75;
    canvas.width = Math.round(size * renderScale);
    canvas.height = Math.round(size * renderScale);
    gl.viewport(0, 0, canvas.width, canvas.height);

    const start = performance.now();
    let frameId = 0;

    const frame = () => {
      const speed = activeRef.current ? 1.6 : 1.0;
      const t = ((performance.now() - start) / 1000) * speed;
      const targetSpeaking = speakingRef.current ? 1 : 0;
      speakingValueRef.current += (targetSpeaking - speakingValueRef.current) * 0.08;
      const bob = speakingValueRef.current > 0.1 ? Math.sin(t * 6.5) * 8 : 0;
      if (canvas.style) {
        canvas.style.transform = speakingValueRef.current > 0.1 ? `translateY(${bob}px)` : "translateY(0px)";
      }
      gl.uniform2f(uResolution, canvas.width, canvas.height);
      gl.uniform1f(uTime, t);
      gl.uniform1f(uSpeaking, speakingValueRef.current);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      frameId = requestAnimationFrame(frame);
    };

    frameId = requestAnimationFrame(frame);

    return () => {
      cancelAnimationFrame(frameId);
      gl.deleteProgram(program);
      gl.deleteBuffer(buffer);
    };
  }, [variant, size]);

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      className={cn("block rounded-full", className)}
      style={{
        width: size,
        height: size,
        display: "block",
        borderRadius: "9999px",
        transformOrigin: "center center",
        willChange: "transform",
      }}
      aria-hidden
    />
  );
}
