"use client";

import { Badge } from "@/components/ui/badge";

export function LevelBadge({ level }) {
    if (typeof level === "number") return <Badge className="bg-blue-600 hover:bg-blue-600">{Math.round(level)}%</Badge>;
    const v = String(level).toLowerCase();
    if (v === "high") return <Badge className="bg-emerald-600 hover:bg-emerald-600">High</Badge>;
    if (v === "medium") return <Badge className="bg-amber-600 hover:bg-amber-600">Medium</Badge>;
    if (v === "low") return <Badge variant="destructive">Low</Badge>;
    return <Badge variant="secondary">{level}</Badge>;
}
