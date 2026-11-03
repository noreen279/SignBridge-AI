export interface Progress {
  detections: Record<string, number>;
  learned: string[];
  quiz: { correct: number; total: number; history: { id: string; ok: boolean; at: number }[] };
}

const KEY = "signbridge-progress";
const empty = (): Progress => ({ detections: {}, learned: [], quiz: { correct: 0, total: 0, history: [] } });

export function loadProgress(): Progress {
  if (typeof window === "undefined") return empty();
  try {
    return { ...empty(), ...JSON.parse(localStorage.getItem(KEY) || "{}") };
  } catch {
    return empty();
  }
}

function save(p: Progress) {
  localStorage.setItem(KEY, JSON.stringify(p));
}

export function recordDetection(id: string) {
  const p = loadProgress();
  p.detections[id] = (p.detections[id] || 0) + 1;
  save(p);
}

export function toggleLearned(id: string) {
  const p = loadProgress();
  p.learned = p.learned.includes(id) ? p.learned.filter((x) => x !== id) : [...p.learned, id];
  save(p);
  return p;
}

export function recordQuiz(id: string, ok: boolean) {
  const p = loadProgress();
  p.quiz.total++;
  if (ok) p.quiz.correct++;
  p.quiz.history = [...p.quiz.history, { id, ok, at: Date.now() }].slice(-100);
  save(p);
}

export function resetProgress() {
  save(empty());
}
