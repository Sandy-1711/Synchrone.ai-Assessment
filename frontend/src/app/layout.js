import "@/app/globals.css";
import { ReactNode } from "react";
import Link from "next/link";
export const metadata = {
  title: "Contract Console",
  description: "Smart contract processing console",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-dvh bg-background text-foreground antialiased">
        <div className="mx-auto max-w-6xl px-4">
          <header className="sticky top-0 z-40 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center justify-between py-4">
              <Link href="/" className="text-xl font-semibold">Contract Console</Link>
              <nav className="flex items-center gap-2">
                <Link href="/" className="text-sm font-medium hover:underline">Home</Link>
                <Link href="/upload" className="text-sm font-medium hover:underline">Upload</Link>
              </nav>
            </div>
          </header>
          <main className="py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
