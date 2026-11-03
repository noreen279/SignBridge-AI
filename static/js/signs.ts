// Small fixed vocabulary of static hand signs, classified from finger states.
export type Fingers = [boolean, boolean, boolean, boolean, boolean]; // thumb, index, middle, ring, pinky

export interface Sign {
  id: string;
  symbol: string;
  meaning: string;
  emoji: string;
  fingers: Fingers;
  howTo: string;
}

export const SIGNS: Sign[] = [
  { id: "hello", symbol: "Hello", meaning: "Greeting", emoji: "🖐️", fingers: [true, true, true, true, true], howTo: "Open your palm with all five fingers extended." },
  { id: "B", symbol: "B", meaning: "Letter B", emoji: "✋", fingers: [false, true, true, true, true], howTo: "Four fingers straight and together, thumb folded across the palm." },
  { id: "A", symbol: "A", meaning: "Letter A", emoji: "✊", fingers: [false, false, false, false, false], howTo: "Make a fist with the thumb resting against the side of the fingers." },
  { id: "D", symbol: "D", meaning: "Letter D / number 1", emoji: "☝️", fingers: [false, true, false, false, false], howTo: "Raise only the index finger; curl the others." },
  { id: "V", symbol: "V", meaning: "Letter V / number 2", emoji: "✌️", fingers: [false, true, true, false, false], howTo: "Raise the index and middle fingers in a V shape." },
  { id: "W", symbol: "W", meaning: "Letter W / number 3", emoji: "3️⃣", fingers: [false, true, true, true, false], howTo: "Raise index, middle and ring fingers; thumb holds the pinky." },
  { id: "L", symbol: "L", meaning: "Letter L", emoji: "👆", fingers: [true, true, false, false, false], howTo: "Extend the thumb and index finger to form an L." },
  { id: "Y", symbol: "Y", meaning: "Letter Y", emoji: "🤙", fingers: [true, false, false, false, true], howTo: "Extend only the thumb and pinky." },
  { id: "I", symbol: "I", meaning: "Letter I", emoji: "🤏", fingers: [false, false, false, false, true], howTo: "Raise only the pinky." },
  { id: "love", symbol: "I love you", meaning: "ILY sign", emoji: "🤟", fingers: [true, true, false, false, true], howTo: "Extend the thumb, index finger and pinky together." },
  { id: "good", symbol: "Good", meaning: "Thumbs up / OK", emoji: "👍", fingers: [true, false, false, false, false], howTo: "Make a fist and raise only the thumb." },
];

export const FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"];

export interface Point { x: number; y: number; z?: number }

const d = (a: Point, b: Point) => Math.hypot(a.x - b.x, a.y - b.y);

/** Decide which fingers are extended from 21 MediaPipe hand landmarks. */
export function fingerStates(lm: Point[]): Fingers {
  const wrist = lm[0];
  const ext = (tip: number, pip: number) => d(lm[tip], wrist) > d(lm[pip], wrist) * 1.1;
  const palm = d(lm[0], lm[9]);
  const thumb = d(lm[4], lm[17]) > d(lm[3], lm[17]) * 1.05 && d(lm[4], lm[5]) > palm * 0.55;
  return [thumb, ext(8, 6), ext(12, 10), ext(16, 14), ext(20, 18)];
}

export function classifyFingers(f: Fingers): Sign | null {
  return SIGNS.find((s) => s.fingers.every((v, i) => v === f[i])) ?? null;
}

export function classify(lm: Point[]): Sign | null {
  if (!lm || lm.length < 21) return null;
  return classifyFingers(fingerStates(lm));
}

export const getSign = (id: string) => SIGNS.find((s) => s.id === id);
