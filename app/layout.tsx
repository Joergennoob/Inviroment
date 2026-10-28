import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Miljøkart California",
  description: "Kildebelagte miljøproblemer i California, med kart og kort.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nb">
      <body>{children}</body>
    </html>
  );
}
