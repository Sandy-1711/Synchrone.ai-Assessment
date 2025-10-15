"use client";

import { Progress } from "@/components/ui/progress";

export function ConfidenceBar({ value, compact = false }) {
    const v = Math.max(0, Math.min(100, value));
    return (
        <div className="space-y-1">
            <Progress value={v} />
            {!compact && <div className="text-xs text-muted-foreground">{v.toFixed(0)}%</div>}
        </div>
    );
}
