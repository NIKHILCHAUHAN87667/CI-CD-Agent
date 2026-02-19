import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, Bot, Zap, GitBranch, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAuthStore } from '@/store';
import { githubAuth } from '@/services/api';

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleGithubLogin = () => {
    window.location.href = githubAuth.getAuthUrl();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-secondary/5 px-4">
      <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left Side - Branding */}
        <div className="text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-3 mb-6">
            <Bot className="h-16 w-16 text-primary" />
            <h1 className="text-4xl md:text-5xl font-bold">
              AI DevOps Agent
            </h1>
          </div>
          <p className="text-xl text-muted-foreground mb-8">
            Automated test fixing and deployment agent that intelligently detects, fixes, and commits code errors.
          </p>
          
          <div className="grid gap-4">
            <div className="flex items-start gap-3">
              <Zap className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold">Instant Error Detection</h3>
                <p className="text-sm text-muted-foreground">Automatically detects 6 types of errors including syntax, linting, and logic issues</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <GitBranch className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold">Smart Branch Management</h3>
                <p className="text-sm text-muted-foreground">Creates branches, commits fixes, and pushes changes automatically</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold">Rule-Based Fixes</h3>
                <p className="text-sm text-muted-foreground">Applies intelligent fixes for common errors with detailed commit messages</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Card */}
        <Card className="w-full max-w-md mx-auto">
          <CardHeader className="text-center">
            <CardTitle>Get Started</CardTitle>
            <CardDescription>
              Sign in with GitHub to start using AI DevOps Agent
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              className="w-full h-12 text-lg"
              onClick={handleGithubLogin}
            >
              <Github className="h-5 w-5 mr-2" />
              Continue with GitHub
            </Button>
            
            <div className="mt-6 text-center text-sm text-muted-foreground">
              <p>By continuing, you agree to grant access to:</p>
              <ul className="mt-2 space-y-1">
                <li>• Repository access (read/write)</li>
                <li>• User profile information</li>
                <li>• Commit and branch creation</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
