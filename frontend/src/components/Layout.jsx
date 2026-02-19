import { Header } from './Header';

export function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="border-t py-6 md:py-0">
        <div className="container mx-auto flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row px-4">
          <p className="text-sm text-muted-foreground">
            Built for RIFT PUNE HACK 122 © 2026
          </p>
          <p className="text-sm text-muted-foreground">
            Powered by AI DevOps Agent
          </p>
        </div>
      </footer>
    </div>
  );
}
