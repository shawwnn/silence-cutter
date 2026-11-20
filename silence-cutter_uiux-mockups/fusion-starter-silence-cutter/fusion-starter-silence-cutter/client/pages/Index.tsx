import { Info } from "lucide-react";
import ProcessPanel from "@/components/silence-cutter/ProcessPanel";
import ThresholdControl from "@/components/silence-cutter/ThresholdControl";
import VideoStage from "@/components/silence-cutter/VideoStage";
import WorkflowSteps from "@/components/silence-cutter/WorkflowSteps";
import { useSilenceCutter } from "@/hooks/use-silence-cutter";

export default function Index() {
  const { state, isPreview, selectVideo, setThreshold, start, retry, openOutputFolder } = useSilenceCutter();
  const { phase, video, thresholdDb, progress, result, error, selectionError } = state;
  const processing = phase === "processing";

  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      {isPreview && (
        <p className="flex items-start gap-2 rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0 text-primary" />
          <span>
            Preview mode. The Python/FFmpeg backend isn't connected, so no video is processed and no file is written.
          </span>
        </p>
      )}

      <section className="flex max-w-xl flex-col gap-2.5">
        <h1 className="font-display text-3xl font-extrabold leading-[1.05] tracking-tight sm:text-4xl">
          Cut the dead air.
          <br />
          <span className="text-primary">Keep the video.</span>
        </h1>
        <p className="text-base leading-relaxed text-muted-foreground">
          Silence Cutter finds the silent stretches in a video and removes them, so you get a tighter cut without opening an editor.
        </p>
      </section>

      <WorkflowSteps phase={phase} />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
        <VideoStage
          video={video}
          loading={phase === "selected"}
          locked={processing}
          error={selectionError}
          onSelect={selectVideo}
        />

        <aside className="flex flex-col gap-7 rounded-2xl border border-border bg-card p-6">
          <ThresholdControl value={thresholdDb} disabled={processing || phase === "completed"} onChange={setThreshold} />
          <div className="h-px bg-border" />
          <ProcessPanel
            phase={phase}
            hasVideo={!!video}
            progress={progress}
            result={result}
            error={error}
            isPreview={isPreview}
            onStart={start}
            onRetry={retry}
            onOpenFolder={openOutputFolder}
            onNewVideo={() => selectVideo()}
          />
        </aside>
      </div>
    </div>
  );
}
