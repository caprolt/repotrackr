import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'RepoTrackr - Project Tracking Dashboard',
  description: 'Automated project tracking system for developers',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation Header */}
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">RepoTrackr</h1>
                </div>
                <nav className="flex items-center space-x-4">
                  <a 
                    href="/dashboard" 
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Dashboard
                  </a>
                  <a 
                    href="/projects/new" 
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Add Project
                  </a>
                </nav>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-white border-t border-gray-200 mt-16">
            <div className="container mx-auto px-4 py-6">
              <div className="text-center text-sm text-gray-600">
                <p>&copy; 2024 RepoTrackr. Automated project tracking for developers.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
