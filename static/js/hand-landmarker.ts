// Browser-only: lazily loads MediaPipe Hand Landmarker.
import type { HandLandmarker } from "@mediapipe/tasks-vision";

let instance: HandLandmarker | null = null;
let currentMode: "IMAGE" | "VIDEO" = "VIDEO";
let loading: Promise<HandLandmarker> | null = null;

export async function getLandmarker(mode: "IMAGE" | "VIDEO"): Promise<HandLandmarker> {
  if (!loading) {
    loading = (async () => {
      const { FilesetResolver, HandLandmarker } = await import("@mediapipe/tasks-vision");
      const fileset = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.2.0/wasm",
      );
      const opts = (delegate: "GPU" | "CPU") => ({
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
          delegate,
        },
        runningMode: mode,
        numHands: 1,
      });
      try {
        instance = await HandLandmarker.createFromOptions(fileset, opts("GPU"));
      } catch {
        instance = await HandLandmarker.createFromOptions(fileset, opts("CPU"));
      }
      currentMode = mode;
      return instance;
    })();
  }
  const lm = await loading;
  if (currentMode !== mode) {
    await lm.setOptions({ runningMode: mode });
    currentMode = mode;
  }
  return lm;
}

export const HAND_CONNECTIONS: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8], [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16], [13, 17], [17, 18], [18, 19], [19, 20], [0, 17],
];

export function drawHand(ctx: CanvasRenderingContext2D, lm: { x: number; y: number }[], w: number, h: number) {
  const styles = getComputedStyle(document.documentElement);
  ctx.lineWidth = 4;
  ctx.strokeStyle = styles.getPropertyValue("--accent").trim() || "orange";
  for (const [a, b] of HAND_CONNECTIONS) {
    ctx.beginPath();
    ctx.moveTo(lm[a].x * w, lm[a].y * h);
    ctx.lineTo(lm[b].x * w, lm[b].y * h);
    ctx.stroke();
  }
  ctx.fillStyle = styles.getPropertyValue("--primary").trim() || "teal";
  for (const p of lm) {
    ctx.beginPath();
    ctx.arc(p.x * w, p.y * h, 5, 0, Math.PI * 2);
    ctx.fill();
  }
}
