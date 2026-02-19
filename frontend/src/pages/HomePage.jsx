import { Link } from 'react-router-dom';
import { Bot, Zap, GitBranch, CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAuthStore } from '@/store';

export function HomePage() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6 py-12">
        <div className="flex justify-center">
          <div className="p-4 rounded-full bg-primary/10">
            <Bot className="h-16 w-16 text-primary" />
          </div>
        </div>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          AI-Powered DevOps Automation
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Automatically detect, fix, and deploy code changes with our intelligent agent.
          Stop wasting time on repetitive debugging tasks.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">
                <Button size="lg">
                  Go to Dashboard
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Link to="/run">
                <Button variant="outline" size="lg">
                  Run Agent
                </Button>
              </Link>
            </>
          ) : (
            <Link to="/login">
              <Button size="lg">
                Get Started
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-8">
        <Card>
          <CardHeader>
            <div className="p-2 w-fit rounded-lg bg-primary/10 mb-4">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <CardTitle>Instant Error Detection</CardTitle>
            <CardDescription>
              Automatically identifies 6 types of common errors: syntax, linting, imports, indentation, logic, and type errors
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <div className="p-2 w-fit rounded-lg bg-primary/10 mb-4">
              <GitBranch className="h-6 w-6 text-primary" />
            </div>
            <CardTitle>Smart Git Integration</CardTitle>
            <CardDescription>
              Creates branches, commits each fix individually, and pushes changes automatically with descriptive messages
            </CardDescription>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <div className="p-2 w-fit rounded-lg bg-primary/10 mb-4">
              <CheckCircle className="h-6 w-6 text-primary" />
            </div>
            <CardTitle>Intelligent Fixes</CardTitle>
            <CardDescription>
              Applies rule-based fixes for common issues with detailed tracking and reporting of all changes
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      {/* How It Works */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold">How It Works</h2>
          <p className="text-muted-foreground mt-2">
            Simple, automated workflow from start to finish
          </p>
        </div>
        
        <Card>
          <CardContent className="pt-6">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center space-y-2">
                <div className="mx-auto w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold">
                  1
                </div>
                <h3 className="font-semibold">Configure & Run</h3>
                <p className="text-sm text-muted-foreground">
                  Enter your repository URL and team details
                </p>
              </div>
              
              <div className="text-center space-y-2">
                <div className="mx-auto w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold">
                  2
                </div>
                <h3 className="font-semibold">Analyze & Fix</h3>
                <p className="text-sm text-muted-foreground">
                  Agent detects errors and applies intelligent fixes
                </p>
              </div>
              
              <div className="text-center space-y-2">
                <div className="mx-auto w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold">
                  3
                </div>
                <h3 className="font-semibold">Review Results</h3>
                <p className="text-sm text-muted-foreground">
                  Get detailed reports and ready-to-merge branches
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* CTA */}
      {!isAuthenticated && (
        <section className="text-center space-y-6 py-12 bg-primary/5 -mx-4 px-4 rounded-lg">
          <h2 className="text-3xl font-bold">Ready to automate your workflow?</h2>
          <p className="text-muted-foreground">
            Join developers who are saving hours of debugging time
          </p>
          <Link to="/login">
            <Button size="lg">
              Get Started for Free
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        </section>
      )}
    </div>
  );
}
