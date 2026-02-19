import { Link, useNavigate } from 'react-router-dom';
import { Github, LogOut, Bot, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '@/store';
import { Button } from './ui/Button';

export function Header() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl">
          <Bot className="h-6 w-6 text-primary" />
          <span>AI DevOps Agent</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="text-sm font-medium hover:text-primary transition-colors">
                Dashboard
              </Link>
              <Link to="/run" className="text-sm font-medium hover:text-primary transition-colors">
                Run Agent
              </Link>
              <Link to="/history" className="text-sm font-medium hover:text-primary transition-colors">
                History
              </Link>
              <div className="flex items-center gap-3 ml-4 pl-4 border-l">
                <div className="flex items-center gap-2">
                  <img 
                    src={user?.avatar_url || `https://github.com/${user?.login}.png`} 
                    alt={user?.login}
                    className="h-8 w-8 rounded-full"
                  />
                  <span className="text-sm font-medium">{user?.login}</span>
                </div>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </>
          ) : (
            <Link to="/login">
              <Button>
                <Github className="h-4 w-4 mr-2" />
                Login with GitHub
              </Button>
            </Link>
          )}
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t bg-background">
          <nav className="container mx-auto flex flex-col gap-4 p-4">
            {isAuthenticated ? (
              <>
                <Link 
                  to="/dashboard" 
                  className="text-sm font-medium hover:text-primary"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link 
                  to="/run" 
                  className="text-sm font-medium hover:text-primary"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Run Agent
                </Link>
                <Link 
                  to="/history" 
                  className="text-sm font-medium hover:text-primary"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  History
                </Link>
                <div className="flex items-center gap-2 pt-4 border-t">
                  <img 
                    src={user?.avatar_url || `https://github.com/${user?.login}.png`} 
                    alt={user?.login}
                    className="h-8 w-8 rounded-full"
                  />
                  <span className="text-sm font-medium flex-1">{user?.login}</span>
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              </>
            ) : (
              <Link to="/login">
                <Button className="w-full">
                  <Github className="h-4 w-4 mr-2" />
                  Login with GitHub
                </Button>
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
