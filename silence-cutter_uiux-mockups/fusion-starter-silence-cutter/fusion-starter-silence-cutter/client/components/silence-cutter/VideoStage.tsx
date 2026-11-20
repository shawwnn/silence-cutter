import { useRef, useState, type DragEvent } from "react";
import { AlertCircle, FileVideo, Loader2, RefreshCw, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatBytes, formatDuration } from "@/lib/silence-cutter/format";
import { SUPPORTED_EXTENSIONS, type VideoFile } from "@/lib/silence-cutter/types";
import { cn } from "@/lib/utils";

interface Props {
  video?: VideoFile;
  loading: boolean;
  locked: boolean;
  error?: string;
  onSelect: (file?: File) => void;
}

export default function VideoStage({ video, loading, locked, error, onSelect }: Props) {
  const [dragging, setDragging] = useState(false);
  const depth = useRef(0);

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    depth.current = 0;
    setDragging(false);
    if (locked) return;
    const file = e.dataTransfer.files?.[0];
    if (file) onSelect(file);
  };

  const dragProps = {
    onDragEnter: (e: DragEvent) => {
      e.preventDefault();
      depth.current++;
      if (!locked) setDragging(true);
    },
    onDragLeave: () => {
      depth.current = Math.max(0, depth.current - 1);
      if (depth.current === 0) setDragging(false);
    },
    onDragOver: (e: DragEvent) => e.preventDefault(),
    onDrop: handleDrop,
  };

  if (!video) {
    return (
      <div className="flex flex-col gap-3">
        <button
          type="button"
          onClick={() => onSelect()}
          {...dragProps}
          className={cn(
            "group flex min-h-[320px] w-full flex-col items-center justify-center gap-5 rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-all",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
            dragging ? "border-primary bg-primary/10" : error ? "border-destructive/60 bg-destructive/5" : "border-input bg-card/50 hover:border-primary/60 hover:bg-card",
          )}
        >
          <span className={cn("flex size-16 items-center justify-center rounded-2xl transition-colors", dragging ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground group-hover:bg-primary group-hover:text-primary-foreground")}>
            <UploadCloud className="size-7" />
          </span>
          <span className="flex flex-col gap-1.5">
            <span className="font-display text-xl font-bold tracking-tight">{dragging ? "Drop to select" : "Drop a video here"}</span>
            <span className="text-sm text-muted-foreground">
              or <span className="font-medium text-primary underline-offset-4 group-hover:underline">browse your files</span>
            </span>
          </span>
          <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            {SUPPORTED_EXTENSIONS.join(" · ")}
          </span>
        </button>
        {error && <ErrorLine message={error} />}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div
        {...dragProps}
        className={cn(
          "flex min-h-[320px] flex-col justify-between gap-8 rounded-2xl border bg-card p-6 transition-colors sm:p-8",
          dragging ? "border-primary bg-primary/10" : "border-border",
        )}
      >
        <div className="flex items-start gap-4">
          <span className="flex size-14 shrink-0 items-center justify-center rounded-xl bg-secondary text-primary">
            <FileVideo className="size-7" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Selected video</p>
            <p className="mt-1 break-all font-display text-xl font-bold leading-snug tracking-tight sm:text-2xl" title={video.name}>
              {video.name}
            </p>
          </div>
        </div>

        <dl className="grid grid-cols-3 gap-4 border-t border-border pt-6">
          <Meta label="Format" value={video.extension.toUpperCase()} />
          <Meta label="Size" value={formatBytes(video.sizeBytes)} />
          <Meta label="Duration" value={loading ? undefined : video.durationSeconds ? formatDuration(video.durationSeconds) : "—"} />
        </dl>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-muted-foreground" aria-live="polite">
            {loading ? "Reading video details…" : locked ? "Locked while processing." : "Drop another video here to replace it."}
          </p>
          <Button variant="secondary" onClick={() => onSelect()} disabled={locked}>
            <RefreshCw className="size-4" />
            Choose a different video
          </Button>
        </div>
      </div>
      {error && <ErrorLine message={error} />}
    </div>
  );
}

function Meta({ label, value }: { label: string; value?: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 font-mono text-base font-medium">
        {value ?? <Loader2 className="size-4 animate-spin text-muted-foreground" aria-label="Loading" />}
      </dd>
    </div>
  );
}

function ErrorLine({ message }: { message: string }) {
  return (
    <p role="alert" className="flex items-start gap-2 text-sm text-destructive animate-fade-up">
      <AlertCircle className="mt-0.5 size-4 shrink-0" />
      {message}
    </p>
  );
}
