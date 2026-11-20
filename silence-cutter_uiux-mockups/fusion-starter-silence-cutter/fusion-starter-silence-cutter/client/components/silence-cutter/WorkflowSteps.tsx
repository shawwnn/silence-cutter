import { Check } from "lucide-react";
import type { Phase } from "@/hooks/use-silence-cutter";
import { cn } from "@/lib/utils";

const steps = ["Select video", "Set threshold", "Process", "Done"];

function activeIndex(phase: Phase) {
  switch (phase) {
    case "idle":
      return 0;
    case "selected":
    case "ready":
      return 1;
    case "processing":
    case "failed":
      return 2;
    case "completed":
      return 4;
  }
}

export default function WorkflowSteps({ phase }: { phase: Phase }) {
  const active = activeIndex(phase);
  return (
    <ol className="flex flex-wrap items-center gap-x-2 gap-y-2 text-sm" aria-label="Progress through the workflow">
      {steps.map((label, i) => {
        const done = i < active;
        const current = i === active;
        return (
          <li key={label} className="flex items-center gap-2" aria-current={current ? "step" : undefined}>
            <span
              className={cn(
                "flex size-5 items-center justify-center rounded-full text-[11px] font-semibold transition-colors",
                done && "bg-primary text-primary-foreground",
                current && "border border-primary text-primary",
                !done && !current && "border border-border text-muted-foreground",
              )}
            >
              {done ? <Check className="size-3" strokeWidth={3} /> : i + 1}
            </span>
            <span className={cn("transition-colors", current ? "font-medium text-foreground" : done ? "text-foreground/80" : "text-muted-foreground")}>
              {label}
            </span>
            {i < steps.length - 1 && <span className="mx-1 hidden h-px w-6 bg-border sm:block" aria-hidden="true" />}
          </li>
        );
      })}
    </ol>
  );
}
