import { Link, Outlet } from "react-router-dom";

export function LogoMark({ className = "size-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="9" fill="hsl(var(--primary))" />
      <g fill="hsl(var(--primary-foreground))">
        <rect x="6" y="12" width="3.5" height="8" rx="1.75" />
        <rect x="11.5" y="8" width="3.5" height="16" rx="1.75" />
        <rect x="17" y="12" width="3.5" height="8" rx="1.75" opacity="0.35" />
        <rect x="22.5" y="9.5" width="3.5" height="13" rx="1.75" />
      </g>
    </svg>
  );
}

export default function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-10 border-b border-border/70 bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-5 sm:px-8">
          <Link to="/" className="flex items-center gap-2.5 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <LogoMark />
            <span className="font-display text-lg font-bold tracking-tight">Silence Cutter</span>
          </Link>
          <span className="hidden text-xs text-muted-foreground sm:block">Powered by FFmpeg · runs on your computer</span>
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-5 py-6 sm:px-8 sm:py-8">
        <Outlet />
      </main>
    </div>
  );
}
