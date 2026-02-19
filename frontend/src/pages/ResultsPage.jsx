import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, GitBranch, Calendar, RefreshCw, CheckCircle2, XCircle, Clock, Play } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { agentAPI } from '@/services/api';
import { formatDate, getStatusColor, getErrorTypeColor } from '@/lib/utils';

export function ResultsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRun();
  }, [id]);

  const loadRun = async () => {
    try {
      const data = await agentAPI.getRun(id);
      setRun(data);
    } catch (error) {
      console.error('Failed to load run:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!run) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Run not found</p>
        <Link to="/dashboard">
          <Button className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/dashboard">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{run.repo_name}</h1>
          <p className="text-muted-foreground mt-1">Run #{run.id}</p>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(run.status)}`}>
          {run.status}
        </span>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Failures</CardTitle>
            <XCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.total_failures}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fixes Applied</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.total_fixes}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Iterations</CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{run.iterations}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {run.total_failures > 0 
                ? Math.round((run.total_fixes / run.total_failures) * 100)
                : 0}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Run Details */}
      <Card>
        <CardHeader>
          <CardTitle>Run Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Repository</p>
              <p className="font-medium break-all">{run.repo}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Branch</p>
              <div className="flex items-center gap-2">
                <GitBranch className="h-4 w-4" />
                <p className="font-medium">{run.branch}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Team</p>
              <p className="font-medium">{run.team || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Leader</p>
              <p className="font-medium">{run.leader || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Started At</p>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <p className="font-medium">{formatDate(run.created_at)}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Duration</p>
              <p className="font-medium">{run.duration || 'N/A'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Fixes Applied */}
      <Card>
        <CardHeader>
          <CardTitle>Fixes Applied ({run.fixes?.length || 0})</CardTitle>
          <CardDescription>
            Detailed breakdown of all fixes applied by the agent
          </CardDescription>
        </CardHeader>
        <CardContent>
          {run.fixes && run.fixes.length > 0 ? (
            <div className="space-y-3">
              {run.fixes.map((fix, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getErrorTypeColor(fix.type)}`}>
                          {fix.type}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {fix.file}:{fix.line}
                        </span>
                      </div>
                      <p className="text-sm font-mono bg-muted p-2 rounded">
                        {fix.commit_message}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      {fix.status === 'Fixed' ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No fixes were applied during this run
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button 
          className="flex-1" 
          onClick={() => navigate('/run', { 
            state: { 
              repo_url: run.repo,
              team: run.team || '',
              leader: run.leader || '',
              max_retries: 5
            } 
          })}
        >
          <Play className="h-4 w-4 mr-2" />
          Run Again on This Repo
        </Button>
        <Link to="/history">
          <Button variant="outline">View All Runs</Button>
        </Link>
      </div>
    </div>
  );
}
