"use client";

import { UploadDropzone } from "@/components/UploadDropzone";
import { ContractTable } from "@/components/ContractTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Quick Upload</CardTitle>
        </CardHeader>
        <CardContent>
          <UploadDropzone compact />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>All Contracts</CardTitle>
        </CardHeader>
        <CardContent>
          <ContractTable />
        </CardContent>
      </Card>
    </div>
  );
}
