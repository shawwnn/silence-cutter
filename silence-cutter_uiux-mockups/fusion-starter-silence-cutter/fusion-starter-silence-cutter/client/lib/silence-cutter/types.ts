export const SUPPORTED_EXTENSIONS = ["mp4", "mov", "mkv", "avi", "webm", "m4v"] as const;

export const THRESHOLD_MIN_DB = -60;
export const THRESHOLD_MAX_DB = -10;
export const THRESHOLD_DEFAULT_DB = -35;

export interface VideoFile {
  name: string;
  extension: string;
  sizeBytes: number;
  durationSeconds?: number;
  path?: string;
  source?: File;
}

export interface ProgressUpdate {
  /** 0..1. Leave undefined when the backend cannot report real progress. */
  fraction?: number;
  message?: string;
}

export interface ProcessResult {
  outputName: string;
  outputPath: string;
  outputFolder: string;
}

export interface SilenceCutterBridge {
  /** Opens a file dialog, or resolves a dropped file when one is given. Resolves null if cancelled. */
  selectVideo(file?: File): Promise<VideoFile | null>;
  processVideo(
    video: VideoFile,
    thresholdDb: number,
    onProgress: (update: ProgressUpdate) => void,
  ): Promise<ProcessResult>;
  openOutputFolder(result: ProcessResult): Promise<void>;
}

declare global {
  interface Window {
    silenceCutter?: SilenceCutterBridge;
  }
}
