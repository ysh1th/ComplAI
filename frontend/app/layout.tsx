"use client";

import "./globals.css";
import { ThemeProvider } from "next-themes";
import { Sidebar } from "@/components/layout/Sidebar";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>ComplAi - Compliance Manager</title>
        <meta
          name="description"
          content="AI-powered compliance monitoring for crypto trading"
        />
      </head>
      <body className="antialiased">
        <ThemeProvider attribute="data-theme" defaultTheme="dark">
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-auto">{children}</main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
