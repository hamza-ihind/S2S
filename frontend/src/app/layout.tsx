import type { Metadata } from "next";
import { Capriola } from "next/font/google";
import "./globals.css";

const capriola = Capriola({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-capriola",
});

export const metadata: Metadata = {
  title: "Sheet2Sound — PDF Sheet Music → Audio Converter",
  description: "Convert piano PDF sheet music into MIDI, WAV audio, and MusicXML scores with oemer OMR & FluidSynth.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${capriola.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
