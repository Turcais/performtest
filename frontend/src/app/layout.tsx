import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PerformTest Studio — Biyomekanik Atletik Analiz & Yetenek Seçimi",
  description: "Yerli Sunucu (On-Premise) ve KVKK Uyumlu Sporcu Performans ve Ölçüm Yönetim Platformu",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr" data-theme="dark">
      <body className="antialiased">{children}</body>
    </html>
  );
}

