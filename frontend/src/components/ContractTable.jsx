"use client";

import { useEffect, useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/StatusBadge";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { Download, Eye, RefreshCw, Search } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";



const sortables = [
    { key: "uploaded_at", label: "Uploaded" },
    { key: "filename", label: "Filename" },
    { key: "status", label: "Status" },
    { key: "overall_score", label: "Score" },
];

export function ContractTable() {
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");
    const [sortBy, setSortBy] = useState("uploaded_at");
    const [order, setOrder] = useState("desc");
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);

    const params = useMemo(() => {
        const p = new URLSearchParams();
        p.set("page", String(page));
        p.set("limit", String(limit));
        p.set("sort_by", sortBy);
        p.set("order", order);
        if (status) p.set("status", status);
        return p.toString();
    }, [page, limit, sortBy, order, status]);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            const res = await fetch(`${API_BASE}/contracts?${params}`);
            if (res.ok) {
                const json = await res.json();
                setData(json);
            }
            setLoading(false);
        };
        load();
    }, [params]);

    const filtered = useMemo(() => {
        if (!data) return [];
        if (!search) return data.items;
        const q = search.toLowerCase();
        return data.items.filter((i) => i.filename.toLowerCase().includes(q));
    }, [data, search]);

    return (
        <div className="space-y-4">
            <div className="grid gap-2 md:grid-cols-4">
                <div className="md:col-span-2 flex items-center gap-2">
                    <div className="relative w-full">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search filename"
                            className="pl-8"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                    <Button variant="outline" className="gap-2" onClick={() => window.location.reload()}>
                        <RefreshCw className="h-4 w-4" />
                        Refresh
                    </Button>
                </div>
                <div className="flex items-center gap-2">
                    <Select value={status} onValueChange={(v) => { setPage(1); setStatus(v); }}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="All statuses" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value={undefined}>All</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                            <SelectItem value="processing">Processing</SelectItem>
                            <SelectItem value="completed">Completed</SelectItem>
                            <SelectItem value="failed">Failed</SelectItem>
                        </SelectContent>
                    </Select>
                    <Select value={sortBy} onValueChange={(v) => setSortBy(v)}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="Sort by" />
                        </SelectTrigger>
                        <SelectContent>
                            {sortables.map((s) => (
                                <SelectItem key={s.key} value={s.key}>{s.label}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Select value={order} onValueChange={(v) => setOrder(v)}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="Order" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="asc">Asc</SelectItem>
                            <SelectItem value="desc">Desc</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="overflow-x-auto rounded-md border">
                <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                        <tr>
                            <th className="px-4 py-3 text-left font-medium">Filename</th>
                            <th className="px-4 py-3 text-left font-medium">Status</th>
                            <th className="px-4 py-3 text-left font-medium">Uploaded</th>
                            <th className="px-4 py-3 text-left font-medium">Score</th>
                            <th className="px-4 py-3 text-right font-medium">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td colSpan={5} className="px-4 py-6 text-center text-muted-foreground">Loading</td>
                            </tr>
                        )}
                        {!loading && filtered.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-4 py-6 text-center text-muted-foreground">No results</td>
                            </tr>
                        )}
                        {filtered.map((c) => (
                            <tr key={c.contract_id} className="border-t">
                                <td className="px-4 py-3 align-top">
                                    <div className="font-medium break-all">{c.filename}</div>
                                    <div className="text-xs text-muted-foreground">
                                        {(c.file_size ? c.file_size / (1024 * 1024) : 0).toFixed(2)} MB
                                    </div>
                                </td>
                                <td className="px-4 py-3 align-top">
                                    <StatusBadge status={c.status} />
                                </td>
                                <td className="px-4 py-3 align-top">
                                    {new Date(c.uploaded_at).toLocaleString()}
                                </td>
                                <td className="px-4 py-3 align-top w-52">
                                    {typeof c.overall_score === "number" ? (
                                        <ConfidenceBar value={c.overall_score} compact />
                                    ) : (
                                        <Badge variant="secondary">N/A</Badge>
                                    )}
                                </td>
                                <td className="px-4 py-3 align-top">
                                    <div className="flex justify-end gap-2">
                                        <a href={`${API_BASE}/contracts/${c.contract_id}/download`}>
                                            <Button variant="outline" size="sm" className="gap-2">
                                                <Download className="h-4 w-4" />
                                                Download
                                            </Button>
                                        </a>
                                        <a href={`/contracts/${c.contract_id}`}>
                                            <Button size="sm" className="gap-2">
                                                <Eye className="h-4 w-4" />
                                                Details
                                            </Button>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    {data && data.pages > 1 && (
                        <tfoot>
                            <tr>
                                <td colSpan={5} className="px-4 py-3">
                                    <div className="flex items-center justify-between">
                                        <div className="text-xs text-muted-foreground">
                                            Page {data.page} of {data.pages} • {data.total} items
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                disabled={data.page <= 1}
                                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                                            >
                                                Prev
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                disabled={data.page >= data.pages}
                                                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                                            >
                                                Next
                                            </Button>
                                            <Select value={String(limit)} onValueChange={(v) => { setPage(1); setLimit(Number(v)); }}>
                                                <SelectTrigger className="w-24">
                                                    <SelectValue placeholder="Page size" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="5">5</SelectItem>
                                                    <SelectItem value="10">10</SelectItem>
                                                    <SelectItem value="20">20</SelectItem>
                                                    <SelectItem value="50">50</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </tfoot>
                    )}
                </table>
            </div>
        </div>
    );
}
