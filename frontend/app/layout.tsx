import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'AI Recruitment Copilot', description: 'Recruiter workspace for resume screening and candidate matching.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
