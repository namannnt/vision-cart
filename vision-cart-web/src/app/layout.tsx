import type { Metadata } from 'next';
import { Space_Grotesk } from 'next/font/google';
import './globals.css';
import AnimatedBackground from '@/components/AnimatedBackground';

const space = Space_Grotesk({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VisionCart',
  description: 'AI-Powered Smart Billing System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${space.className} min-h-screen bg-slate-950 text-slate-50 antialiased selection:bg-blue-500/30 font-light`}>
        <AnimatedBackground />
        <main className="relative flex min-h-screen flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
