import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trader Alpha - Stock Scanner",
  description: "Automated stock analysis with technical indicators",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center">
                <h1 className="text-xl font-bold">📈 Trader Alpha</h1>
              </div>
              <div className="flex space-x-4">
                <a href="/lists" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                  Lists
                </a>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}