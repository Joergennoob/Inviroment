import type { Metadata } from "next";
import { Fraunces, Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-outfit",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-fraunces",
});

export const metadata: Metadata = {
  title: "Miljøkart California",
  description: "Ti miljøproblemer i California, forklart med vanlige ord, med kilder under.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nb" className={`${outfit.variable} ${fraunces.variable}`}>
      <body className={outfit.className}>{children}</body>
    </html>
  );
}
