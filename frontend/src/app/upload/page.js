"use client";

import { UploadDropzone } from "@/components/UploadDropzone";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function UploadPage() {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Upload Contract</CardTitle>
            </CardHeader>
            <CardContent>
                <UploadDropzone />
            </CardContent>
        </Card>
    );
}
