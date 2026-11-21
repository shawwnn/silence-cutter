import type { SilenceCutterBridge, VideoFile } from "./types";

const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

function extensionOf(name: string) {
  const i = name.lastIndexOf(".");
  return i === -1 ? "" : name.slice(i + 1).toLowerCase();
}

function readDuration(file: File): Promise<number | undefined> {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const video = document.createElement("video");
    const done = (value?: number) => {
      URL.revokeObjectURL(url);
      resolve(value);
    };
    const timer = setTimeout(() => done(), 4000);
    video.preload = "metadata";
    video.onloadedmetadata = () => {
      clearTimeout(timer);
      done(Number.isFinite(video.duration) ? video.duration : undefined);
    };
    video.onerror = () => {
      clearTimeout(timer);
      done();
    };
    video.src = url;
  });
}

function pickFile(): Promise<File | null> {
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "video/*,.mkv,.avi,.m4v";
    input.onchange = () => resolve(input.files?.[0] ?? null);
    input.oncancel = () => resolve(null);
    input.click();
  });
}

/**
 * Used when no desktop shell has injected `window.silenceCutter`.
 * It cannot run FFmpeg, so it reports no percentage and writes no file.
 */
export const previewBridge: SilenceCutterBridge = {
  async selectVideo(dropped) {
    const file = dropped ?? (await pickFile());
    if (!file) return null;
    const video: VideoFile = {
      name: file.name,
      extension: extensionOf(file.name),
      sizeBytes: file.size,
      source: file,
    };
    video.durationSeconds = await readDuration(file);
    return video;
  },

  async processVideo(video, _thresholdDb, onProgress) {
    onProgress({ message: "Detecting silent sections" });
    await wait(2200);
    onProgress({ message: "Rendering the trimmed video" });
    await wait(2200);
    const base = video.name.replace(/\.[^.]+$/, "");
    const outputName = `${base}_silence-cut.${video.extension}`;
    const outputFolder = "Preview mode (no file written)";
    return { outputName, outputFolder, outputPath: `${outputFolder}/${outputName}` };
  },

  async openOutputFolder() {
    throw new Error("Opening folders needs the desktop app.");
  },
};
