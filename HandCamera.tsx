import { useEffect, useRef, useState } from "react";
import { classify, type Sign } from "@/lib/signs";
import { drawHand, getLandmarker } from "@/lib/hand-landmarker";

interface Props {
  onSign?: (sign: Sign | null, stable: boolean) => void;
}

/** Live camera feed with hand landmark overlay; reports a smoothed prediction. */
export function HandCamera({ onSign }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "running" | "error">("idle");
  const [error, setError] = useState("");
  const cb = useRef(onSign);
  cb.current = onSign;
  const stop = useRef<() => void>(() => {});

  useEffect(() => () => stop.current(), []);

  async function start() {
    setStatus("loading");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: 640, height: 480 } });
      const video = videoRef.current!;
      video.srcObject = stream;
      await video.play();
      const lm = await getLandmarker("VIDEO");
      setStatus("running");
      const history: (string | null)[] = [];
      let raf = 0;
      let last = -1;
      const loop = () => {
        const canvas = canvasRef.current;
        if (canvas && video.readyState >= 2 && video.currentTime !== last) {
          last = video.currentTime;
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext("2d")!;
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          const res = lm.detectForVideo(video, performance.now());
          const hand = res.landmarks?.[0];
          if (hand) drawHand(ctx, hand, canvas.width, canvas.height);
          const s = hand ? classify(hand) : null;
          history.push(s?.id ?? null);
          if (history.length > 10) history.shift();
          const stable = history.length === 10 && history.every((h) => h === history[0]);
          cb.current?.(s, stable && !!s);
        }
        raf = requestAnimationFrame(loop);
      };
      loop();
      stop.current = () => {
        cancelAnimationFrame(raf);
        stream.getTracks().forEach((t) => t.stop());
      };
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : "Could not start the camera");
    }
  }

  return (
    <div className="relative aspect-[4/3] w-full overflow-hidden rounded-3xl bg-secondary shadow-soft">
      <video ref={videoRef} playsInline muted className="absolute inset-0 h-full w-full -scale-x-100 object-cover" />
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full -scale-x-100 object-cover" />
      {status !== "running" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 p-6 text-center">
          {status === "error" ? (
            <p className="text-sm text-destructive">{error} — allow camera access and try again.</p>
          ) : (
            <p className="text-sm text-muted-foreground">
              {status === "loading" ? "Loading hand tracking model…" : "Start the camera and place your hand in the frame"}
            </p>
          )}
          {status !== "loading" && (
            <button onClick={start} className="rounded-full bg-primary px-6 py-3 font-semibold text-primary-foreground">
              Start camera
            </button>
          )}
        </div>
      )}
    </div>
  );
}
