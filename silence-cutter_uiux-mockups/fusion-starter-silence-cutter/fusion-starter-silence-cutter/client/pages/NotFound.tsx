import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 py-20 text-center">
      <p className="font-mono text-sm text-primary">404</p>
      <h1 className="font-display text-3xl font-bold tracking-tight">Nothing here</h1>
      <p className="max-w-sm text-muted-foreground">This page doesn't exist. Head back to the workspace to cut a video.</p>
      <Button asChild>
        <Link to="/">Back to workspace</Link>
      </Button>
    </div>
  );
}
