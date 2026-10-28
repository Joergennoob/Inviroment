import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Miljøkart California",
  description: "Ti miljøproblemer i California, forklart med vanlige ord, med kilder under.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nb">
      <body>{children}</body>
    </html>
  );
}
