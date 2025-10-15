"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/StatusBadge";
import { ConfidenceBar } from "@/components/ConfidenceBar";
import { LevelBadge } from "@/components/LevelBadge";
import { ArrowLeft, Download, RefreshCw } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";


export default function ContractDetailsPage() {
  const router = useRouter();
  const { id } = useParams();
  const [status, setStatus] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  const downloadUrl = useMemo(() => `${API_BASE}/contracts/${id}/download`, [id]);
  const currency = useMemo(() => data?.financial_details?.currency || "USD", [data]);

  useEffect(() => {
    let interval = null;
    const load = async () => {
      try {
        const s = await fetch(`${API_BASE}/contracts/${id}/status`);
        if (s.ok) {
          const sj = await s.json();
          setStatus(sj);
        }
        const r = await fetch(`${API_BASE}/contracts/${id}`);
        if (r.ok) {
          const cj = await r.json();
          setData(cj);
          setLoading(false);
          if (interval) clearInterval(interval);
        } else if (r.status === 404) {
          setLoading(false);
        }
      } catch (e) {
        setErr(e.message ?? "Failed to load");
        setLoading(false);
      }
    };
    load();
    interval = setInterval(load, 2000);
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [id]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.back()} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => router.refresh()} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
          <Button className="gap-2" onClick={() => window.location.href = downloadUrl}>
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </div>

      {(status || loading) && (
        <Card>
          <CardHeader>
            <CardTitle>Processing</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {status && (
              <div className="flex items-center justify-between">
                <StatusBadge status={status.status} />
                <div className="text-sm text-muted-foreground">
                  Updated {new Date(status.updated_at).toLocaleString()}
                </div>
              </div>
            )}
            {status && (
              <div className="space-y-2">
                <Progress value={status.progress} />
                <div className="text-sm">{status.progress}%</div>
                {status.error && <div className="text-sm text-destructive">{status.error}</div>}
              </div>
            )}
            {err && <div className="text-sm text-destructive">{err}</div>}
          </CardContent>
        </Card>
      )}

      {data && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2">
              <Field label="Filename" value={data.filename} mono />
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Overall Score</div>
                <ConfidenceBar value={Number(data.overall_score)} />
              </div>
              <Field label="Uploaded" value={new Date(data.uploaded_at).toLocaleString()} />
              {data.completed_at && <Field label="Completed" value={new Date(data.completed_at).toLocaleString()} />}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Category Scores</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(data.category_scores || {}).map(([k, v]) => (
                <div key={k} className="grid grid-cols-12 items-center gap-3">
                  <div className="col-span-5 md:col-span-3 text-sm">{labelize(k)}</div>
                  <div className="col-span-7 md:col-span-9">
                    <ConfidenceBar value={Number(v)} compact />
                  </div>
                </div>
              ))}
              {!Object.keys(data.category_scores || {}).length && (
                <div className="text-sm text-muted-foreground">No scores</div>
              )}
            </CardContent>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            <EntityCard title="Customer" obj={data.party_identification?.customer} />
            <EntityCard title="Vendor" obj={data.party_identification?.vendor} />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
            </CardHeader>
            <CardContent>
              <KV obj={data.account_information} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Financial Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {Array.isArray(data.financial_details?.line_items) && data.financial_details.line_items.length > 0 && (
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium">Description</th>
                        <th className="px-4 py-2 text-right font-medium">Qty</th>
                        <th className="px-4 py-2 text-right font-medium">Unit Price</th>
                        <th className="px-4 py-2 text-right font-medium">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.financial_details.line_items.map((li, i) => (
                        <tr key={i} className="border-t">
                          <td className="px-4 py-2">{li.description}</td>
                          <td className="px-4 py-2 text-right">{li.quantity}</td>
                          <td className="px-4 py-2 text-right">{fmtMoney(li.unit_price, currency)}</td>
                          <td className="px-4 py-2 text-right">{fmtMoney(li.total, currency)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="border-t">
                        <td className="px-4 py-2 font-medium" colSpan={3}>Subtotal</td>
                        <td className="px-4 py-2 text-right">{fmtMoney(data.financial_details.subtotal ?? 0, currency)}</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2 font-medium" colSpan={3}>Total</td>
                        <td className="px-4 py-2 text-right">{fmtMoney(data.financial_details.total_value ?? 0, currency)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
              {Array.isArray(data.financial_details?.additional_fees) && data.financial_details.additional_fees.length > 0 && (
                <div className="space-y-2">
                  <div className="text-sm font-medium">Additional Fees</div>
                  <ul className="list-disc pl-6 space-y-1">
                    {data.financial_details.additional_fees.map((f, i) => (
                      <li key={i} className="text-sm">
                        <span className="font-medium">{f.description}:</span> {f.amount}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <KV obj={{ currency: currency }} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Payment Structure</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <KV obj={{ payment_terms: data.payment_structure?.payment_terms, payment_method: data.payment_structure?.payment_method }} />
              {Array.isArray(data.payment_structure?.payment_schedule) && data.payment_structure.payment_schedule.length > 0 && (
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium">Description</th>
                        <th className="px-4 py-2 text-left font-medium">Due</th>
                        <th className="px-4 py-2 text-right font-medium">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.payment_structure.payment_schedule.map((p, i) => (
                        <tr key={i} className="border-t">
                          <td className="px-4 py-2">{p.description ?? "-"}</td>
                          <td className="px-4 py-2">{p.due_date ?? "-"}</td>
                          <td className="px-4 py-2 text-right">{typeof p.amount === "number" ? fmtMoney(p.amount, currency) : "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {Array.isArray(data.payment_structure?.due_dates) && data.payment_structure.due_dates.length > 0 && (
                <div className="space-y-2">
                  <div className="text-sm font-medium">Due Dates</div>
                  <ul className="list-disc pl-6 space-y-1">
                    {data.payment_structure.due_dates.map((d, i) => <li key={i} className="text-sm">{d}</li>)}
                  </ul>
                </div>
              )}
              {data.payment_structure?.bank_details && (
                <div>
                  <div className="text-sm font-medium mb-2">Bank Details</div>
                  <KV obj={data.payment_structure.bank_details} />
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Revenue Classification</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {"has_recurring" in data.revenue_classification && (
                  <Badge className={truthy(data.revenue_classification["has_recurring"]) ? "bg-emerald-600 hover:bg-emerald-600" : "bg-gray-500 hover:bg-gray-500"}>
                    Recurring: {truthy(data.revenue_classification["has_recurring"]) ? "Yes" : "No"}
                  </Badge>
                )}
                {"has_one_time" in data.revenue_classification && (
                  <Badge className={truthy(data.revenue_classification["has_one_time"]) ? "bg-emerald-600 hover:bg-emerald-600" : "bg-gray-500 hover:bg-gray-500"}>
                    One-Time: {truthy(data.revenue_classification["has_one_time"]) ? "Yes" : "No"}
                  </Badge>
                )}
                {"auto_renewal" in data.revenue_classification && (
                  <Badge className={truthy(data.revenue_classification["auto_renewal"]) ? "bg-emerald-600 hover:bg-emerald-600" : "bg-gray-500 hover:bg-gray-500"}>
                    Auto-Renewal: {truthy(data.revenue_classification["auto_renewal"]) ? "Yes" : "No"}
                  </Badge>
                )}
              </div>
              <KV obj={{
                billing_cycle: data.revenue_classification["billing_cycle"],
                subscription_model: data.revenue_classification["subscription_model"],
                renewal_terms: data.revenue_classification["renewal_terms"],
              }} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>SLA Terms</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <KV obj={{ uptime_guarantee: data.sla_terms?.uptime_guarantee, response_time: data.sla_terms?.response_time, support_hours: data.sla_terms?.support_hours }} />
              {Array.isArray(data.sla_terms?.performance_metrics) && data.sla_terms.performance_metrics.length > 0 && (
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium">Metric</th>
                        <th className="px-4 py-2 text-left font-medium">Target</th>
                        <th className="px-4 py-2 text-left font-medium">Measurement</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.sla_terms.performance_metrics.map((m, i) => (
                        <tr key={i} className="border-t">
                          <td className="px-4 py-2">{String(m.metric ?? "-")}</td>
                          <td className="px-4 py-2">{String(m.target ?? "-")}</td>
                          <td className="px-4 py-2">{String(m.measurement ?? "-")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {Array.isArray(data.sla_terms?.penalties) && data.sla_terms.penalties.length > 0 && (
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium">Condition</th>
                        <th className="px-4 py-2 text-left font-medium">Penalty</th>
                        <th className="px-4 py-2 text-left font-medium">Calculation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.sla_terms.penalties.map((p, i) => (
                        <tr key={i} className="border-t">
                          <td className="px-4 py-2">{String(p.condition ?? "-")}</td>
                          <td className="px-4 py-2">{String(p.penalty ?? "-")}</td>
                          <td className="px-4 py-2">{String(p.calculation ?? "-")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Missing Fields</CardTitle>
            </CardHeader>
            <CardContent>
              {data.missing_fields?.length ? (
                <ul className="list-disc pl-6 space-y-1">
                  {data.missing_fields.map((m) => (
                    <li key={m} className="text-sm">{m}</li>
                  ))}
                </ul>
              ) : (
                <div className="text-sm text-muted-foreground">None</div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Confidence Levels</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(data.confidence_levels || {}).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between">
                  <div className="text-sm">{labelize(k)}</div>
                  <LevelBadge level={v} />
                </div>
              ))}
              {!Object.keys(data.confidence_levels || {}).length && (
                <div className="text-sm text-muted-foreground">No confidence data</div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function labelize(s) {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function fmtMoney(n, currency) {
  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(n);
  } catch {
    return new Intl.NumberFormat().format(n);
  }
}

function truthy(v) {
  return v === true || v === "true" || v === 1 || v === "1";
}

function Field({ label, value, mono = false }) {
  return (
    <div className="space-y-2">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className={["font-medium break-words", mono ? "font-mono" : ""].join(" ")}>{value}</div>
    </div>
  );
}

function EntityCard({ title, obj }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>{obj ? <KV obj={obj} /> : <div className="text-sm text-muted-foreground">No data</div>}</CardContent>
    </Card>
  );
}

function KV({ obj }) {
  const entries = Object.entries(obj || {}).filter(([, v]) => v !== undefined && v !== null && v !== "");
  if (!entries.length) return <div className="text-sm text-muted-foreground">No data</div>;
  return (
    <dl className="grid gap-3">
      {entries.map(([k, v]) => (
        <div key={k} className="grid grid-cols-3 gap-2">
          <dt className="col-span-1 text-sm text-muted-foreground">{labelize(k)}</dt>
          <dd className="col-span-2 text-sm break-words">{renderVal(v)}</dd>
        </div>
      ))}
    </dl>
  );
}

function renderVal(v) {
  if (typeof v === "boolean") return v ? "Yes" : "No";
  if (Array.isArray(v)) return v.join(", ");
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}
