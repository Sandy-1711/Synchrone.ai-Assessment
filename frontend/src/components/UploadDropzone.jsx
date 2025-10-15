"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { CloudUpload, FileText, Loader2 } from "lucide-react";
import { StatusBadge } from "./StatusBadge";
import { Link } from "next/link"
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";



export function UploadDropzone({ compact = false }) {
    const router = useRouter();
    const ref = useRef(null);
    const [dragging, setDragging] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [createdId, setCreatedId] = useState(null);
    const [status, setStatus] = useState(null);

    useEffect(() => {
        if (!createdId) return;
        let interval = null;
        const poll = async () => {
            const r = await fetch(`${API_BASE}/contracts/${createdId}/status`);
            if (!r.ok) return;
            const s = await r.json();
            setStatus(s);
            if (s.status === "completed" || s.status === "failed") {
                if (interval) clearInterval(interval);
            }
        };
        poll();
        interval = setInterval(poll, 2000);
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [createdId]);

    const onFiles = async (files) => {
        if (!files || !files[0]) return;
        const f = files[0];
        setFile(f);
        setUploading(true);
        const form = new FormData();
        form.append("file", f);
        const res = await fetch(`${API_BASE}/contracts/upload`, {
            method: "POST",
            body: form,
        });
        setUploading(false);
        if (!res.ok) return;
        const json = await res.json();
        setCreatedId(json.contract_id);
    };

    return (
        <div className="space-y-4">
            <div
                onDragOver={(e) => {
                    e.preventDefault();
                    setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => {
                    e.preventDefault();
                    setDragging(false);
                    onFiles(e.dataTransfer.files);
                }}
                className={[
                    "flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center",
                    dragging ? "border-primary" : "border-muted",
                    compact ? "min-h-40" : "min-h-56",
                ].join(" ")}
            >
                <CloudUpload className="mb-3 h-8 w-8" />
                <div className="text-sm">
                    Drag and drop your PDF here or
                    <span className="mx-1" />
                    <button
                        onClick={() => ref.current?.click()}
                        className="font-medium underline underline-offset-4"
                    >
                        browse
                    </button>
                </div>
                <div className="text-xs text-muted-foreground mt-1">Only PDF files are supported</div>
                <Input
                    ref={ref}
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    onChange={(e) => onFiles(e.target.files)}
                />
            </div>

            {file && (
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                            <FileText className="h-5 w-5" />
                            <div className="flex-1">
                                <div className="text-sm font-medium">{file.name}</div>
                                <div className="text-xs text-muted-foreground">
                                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                                </div>
                            </div>
                            {uploading ? (
                                <Badge variant="secondary" className="gap-2">
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                    Uploading
                                </Badge>
                            ) : createdId ? (
                                <Badge>Uploaded</Badge>
                            ) : null}
                        </div>
                        {uploading && <div className="mt-3"><Progress value={60} /></div>}
                    </CardContent>
                </Card>
            )}

            {createdId && status && (
                <Card>
                    <CardContent className="p-4 space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="text-sm">Processing</div>
                            <StatusBadge status={status.status} />
                        </div>
                        <Progress value={status.progress} />
                        <div className="text-xs text-muted-foreground">{status.progress}%</div>
                        <div className="flex gap-2">
                            <Link href={`${API_BASE}/contracts/${createdId}/download`}>
                                <Button variant="outline" className="w-full">Download PDF</Button>
                            </Link>
                            <Button
                                className="w-full flex-1"
                                onClick={() => {
                                    if (status.status === "completed") {
                                        window.location.href = `/contracts/${createdId}`;
                                    } else {
                                        window.location.href = `/contracts/${createdId}`;
                                    }
                                }}
                            >
                                View Details
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
