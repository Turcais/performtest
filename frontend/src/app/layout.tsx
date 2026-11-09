import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Performetre — Performans Ölçme ve Değerlendirme & Yetenek Seçimi",
  description: "Performetre — Yerli Sunucu (On-Premise) ve KVKK Uyumlu Sporcu Performans Ölçme ve Değerlendirme Platformu",
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

