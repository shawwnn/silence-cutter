import { AlertCircle, CheckCircle2, FolderOpen, Loader2, Scissors } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import type { Phase } from "@/hooks/use-silence-cutter";
import type { ProcessResult, ProgressUpdate } from "@/lib/silence-cutter/types";

interface Props {
  phase: Phase;
  hasVideo: boolean;
  progress?: ProgressUpdate;
  result?: ProcessResult;
  error?: string;
  isPreview: boolean;
  onStart: () => void;
  onRetry: () => void;
  onOpenFolder: (result: ProcessResult) => Promise<void>;
  onNewVideo: () => void;
}

const hints: Partial<Record<Phase, string>> = {
  idle: "Select a video to get started.",
  selected: "Reading the video…",
};

export default function ProcessPanel({ phase, hasVideo, progress, result, error, isPreview, onStart, onRetry, onOpenFolder, onNewVideo }: Props) {
  if (phase === "processing") {
    const fraction = progress?.fraction;
    return (
      <div className="flex flex-col gap-4" role="status" aria-live="polite">
        <Button size="lg" disabled className="h-12 w-full text-base">
          <Loader2 className="animate-spin" />
          Processing…
        </Button>
        <div className="flex flex-col gap-2.5">
          <div
            className="relative h-1.5 overflow-hidden rounded-full bg-secondary"
            role="progressbar"
            aria-label="Processing progress"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={fraction !== undefined ? Math.round(fraction * 100) : undefined}
          >
            {fraction !== undefined ? (
              <div className="h-full rounded-full bg-primary transition-[width] duration-300" style={{ width: `${fraction * 100}%` }} />
            ) : (
              <div className="absolute inset-y-0 left-0 w-1/3 animate-indeterminate rounded-full bg-primary" />
            )}
          </div>
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="text-foreground">{progress?.message ?? "Working"}…</span>
            {fraction !== undefined && <span className="font-mono text-muted-foreground">{Math.round(fraction * 100)}%</span>}
          </div>
          <p className="text-xs text-muted-foreground">Keep this window open. Longer videos take longer.</p>
        </div>
      </div>
    );
  }

  if (phase === "completed" && result) {
    return (
      <div className="flex flex-col gap-5 animate-fade-up" role="status">
        <div className="flex items-center gap-2.5 text-success">
          <CheckCircle2 className="size-6" />
          <h2 className="font-display text-xl font-bold tracking-tight text-foreground">{isPreview ? "Preview complete" : "Silence removed"}</h2>
        </div>
        <dl className="flex flex-col gap-3 rounded-xl border border-border bg-background/60 p-4 text-sm">
          <div>
            <dt className="text-xs text-muted-foreground">Output file</dt>
            <dd className="mt-0.5 break-all font-medium">{result.outputName}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">Saved in</dt>
            <dd className="mt-0.5 break-all font-mono text-xs text-foreground/80">{result.outputFolder}</dd>
          </div>
        </dl>
        <div className="flex flex-col gap-2">
          <Button
            size="lg"
            className="h-12 w-full text-base"
            onClick={() => onOpenFolder(result).catch((e: Error) => toast.error(e.message))}
          >
            <FolderOpen />
            Open output folder
          </Button>
          <Button variant="ghost" onClick={onNewVideo}>
            Process another video
          </Button>
        </div>
      </div>
    );
  }

  if (phase === "failed") {
    return (
      <div className="flex flex-col gap-4 animate-fade-up">
        <div role="alert" className="flex gap-3 rounded-xl border border-destructive/40 bg-destructive/10 p-4">
          <AlertCircle className="mt-0.5 size-5 shrink-0 text-destructive" />
          <div className="min-w-0">
            <h2 className="text-sm font-semibold">Processing failed</h2>
            <p className="mt-1 break-words text-sm text-foreground/80">{error}</p>
          </div>
        </div>
        <Button size="lg" className="h-12 w-full text-base" onClick={onRetry}>
          Try again
        </Button>
        <Button variant="ghost" onClick={onNewVideo}>
          Choose a different video
        </Button>
      </div>
    );
  }

  const ready = phase === "ready";
  return (
    <div className="flex flex-col gap-3">
      <Button size="lg" className="h-12 w-full text-base font-semibold" disabled={!ready} onClick={onStart}>
        <Scissors />
        Remove silence
      </Button>
      <p className="text-center text-xs text-muted-foreground">
        {ready ? "Your original file is never changed." : hasVideo ? hints.selected : hints.idle}
      </p>
    </div>
  );
}
