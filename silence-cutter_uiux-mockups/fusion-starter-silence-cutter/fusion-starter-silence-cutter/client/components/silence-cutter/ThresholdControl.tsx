import { Slider } from "@/components/ui/slider";
import {
  THRESHOLD_DEFAULT_DB,
  THRESHOLD_MAX_DB,
  THRESHOLD_MIN_DB,
} from "@/lib/silence-cutter/types";
import { cn } from "@/lib/utils";

interface Props {
  value: number;
  disabled: boolean;
  onChange: (value: number) => void;
}

function describe(db: number) {
  if (db <= -45) return "Cuts only near-total silence. Keeps quiet speech and room tone.";
  if (db <= -25) return "Balanced. Cuts pauses and quiet gaps between speech.";
  return "Cuts aggressively. Soft speech and background sound may be removed.";
}

export default function ThresholdControl({ value, disabled, onChange }: Props) {
  return (
    <section aria-labelledby="threshold-label" className={cn("flex flex-col gap-4", disabled && "opacity-60")}>
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 id="threshold-label" className="font-display text-base font-bold tracking-tight">Silence threshold</h2>
          <p className="mt-1 text-sm text-muted-foreground">Audio quieter than this is cut.</p>
        </div>
        <output className="font-mono text-2xl font-medium tabular-nums text-primary" aria-live="off">
          {value} <span className="text-sm text-muted-foreground">dB</span>
        </output>
      </div>

      <Slider
        aria-labelledby="threshold-label"
        min={THRESHOLD_MIN_DB}
        max={THRESHOLD_MAX_DB}
        step={1}
        value={[value]}
        disabled={disabled}
        onValueChange={([v]) => onChange(v)}
      />

      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Gentle</span>
        <span>Aggressive</span>
      </div>

      <p className="min-h-10 text-sm leading-relaxed text-foreground/80">{describe(value)}</p>

      <button
        type="button"
        onClick={() => onChange(THRESHOLD_DEFAULT_DB)}
        disabled={disabled || value === THRESHOLD_DEFAULT_DB}
        className="self-start text-xs font-medium text-muted-foreground underline-offset-4 transition-colors hover:text-foreground hover:underline disabled:pointer-events-none disabled:opacity-0"
      >
        Reset to default ({THRESHOLD_DEFAULT_DB} dB)
      </button>
    </section>
  );
}
