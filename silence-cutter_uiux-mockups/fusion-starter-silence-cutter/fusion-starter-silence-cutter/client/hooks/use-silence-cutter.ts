import { useCallback, useReducer, useRef } from "react";
import { previewBridge } from "@/lib/silence-cutter/preview-bridge";
import {
  SUPPORTED_EXTENSIONS,
  THRESHOLD_DEFAULT_DB,
  type ProcessResult,
  type ProgressUpdate,
  type VideoFile,
} from "@/lib/silence-cutter/types";

export type Phase = "idle" | "selected" | "ready" | "processing" | "completed" | "failed";

interface State {
  phase: Phase;
  video?: VideoFile;
  thresholdDb: number;
  progress?: ProgressUpdate;
  result?: ProcessResult;
  error?: string;
  selectionError?: string;
}

type Action =
  | { type: "selecting"; video: VideoFile }
  | { type: "ready"; video: VideoFile }
  | { type: "selectionError"; message: string }
  | { type: "threshold"; value: number }
  | { type: "start" }
  | { type: "progress"; update: ProgressUpdate }
  | { type: "completed"; result: ProcessResult }
  | { type: "failed"; message: string }
  | { type: "retry" };

const initial: State = { phase: "idle", thresholdDb: THRESHOLD_DEFAULT_DB };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "selecting":
      return { ...state, phase: "selected", video: action.video, result: undefined, error: undefined, progress: undefined, selectionError: undefined };
    case "ready":
      return state.video === action.video ? { ...state, phase: "ready" } : state;
    case "selectionError":
      return { ...state, selectionError: action.message };
    case "threshold":
      return state.phase === "processing" ? state : { ...state, thresholdDb: action.value };
    case "start":
      return { ...state, phase: "processing", progress: { message: "Starting" }, error: undefined };
    case "progress":
      return state.phase === "processing" ? { ...state, progress: action.update } : state;
    case "completed":
      return { ...state, phase: "completed", result: action.result, progress: undefined };
    case "failed":
      return { ...state, phase: "failed", error: action.message, progress: undefined };
    case "retry":
      return { ...state, phase: "ready", error: undefined };
  }
}

function validate(video: VideoFile) {
  if (!(SUPPORTED_EXTENSIONS as readonly string[]).includes(video.extension)) {
    return `".${video.extension || "?"}" files aren't supported. Choose ${SUPPORTED_EXTENSIONS.map((e) => e.toUpperCase()).join(", ")}.`;
  }
  if (video.sizeBytes === 0) return "This file is empty.";
  return null;
}

export function useSilenceCutter() {
  const [state, dispatch] = useReducer(reducer, initial);
  const busy = useRef(false);
  const bridge = typeof window !== "undefined" && window.silenceCutter ? window.silenceCutter : previewBridge;
  const isPreview = bridge === previewBridge;

  const selectVideo = useCallback(
    async (file?: File) => {
      if (busy.current) return;
      try {
        const video = await bridge.selectVideo(file);
        if (!video) return;
        const problem = validate(video);
        if (problem) {
          dispatch({ type: "selectionError", message: problem });
          return;
        }
        dispatch({ type: "selecting", video });
        await new Promise((r) => setTimeout(r, 350));
        dispatch({ type: "ready", video });
      } catch (e) {
        dispatch({ type: "selectionError", message: e instanceof Error ? e.message : "Couldn't read that file." });
      }
    },
    [bridge],
  );

  const setThreshold = useCallback((value: number) => dispatch({ type: "threshold", value }), []);

  const start = useCallback(async () => {
    if (busy.current || state.phase !== "ready" || !state.video) return;
    busy.current = true;
    dispatch({ type: "start" });
    try {
      const result = await bridge.processVideo(state.video, state.thresholdDb, (update) =>
        dispatch({ type: "progress", update }),
      );
      dispatch({ type: "completed", result });
    } catch (e) {
      dispatch({ type: "failed", message: e instanceof Error ? e.message : "Processing stopped unexpectedly." });
    } finally {
      busy.current = false;
    }
  }, [bridge, state.phase, state.video, state.thresholdDb]);

  const retry = useCallback(() => dispatch({ type: "retry" }), []);
  const openOutputFolder = useCallback(
    (result: ProcessResult) => bridge.openOutputFolder(result),
    [bridge],
  );

  return { state, isPreview, selectVideo, setThreshold, start, retry, openOutputFolder };
}
