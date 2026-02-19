import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Play, History, TrendingUp, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { useAuthStore, useAgentStore } from '@/store';
import { agentAPI } from '@/services/api';
import { formatDate, getStatusColor } from '@/lib/utils';

export function DashboardPage() {
  const { user } = useAuthStore();
  const { runs, setRuns } = useAgentStore();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalRuns: 0,
    successRate: 0,
    totalFixes: 0,
    avgIterations: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await agentAPI.getRuns();
      setRuns(data);
      calculateStats(data);
    } catch (error) {
      console.error('Failed to load runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (runsData) => {
    const totalRuns = runsData.length;
    const passed = runsData.filter(r => r.status === 'PASSED').length;
    const totalFixes = runsData.reduce((sum, r) => sum + (r.total_fixes || 0), 0);
    const avgIterations = totalRuns > 0 
      ? (runsData.reduce((sum, r) => sum + (r.iterations || 0), 0) / totalRuns).toFixed(1)
      : 0;

    setStats({
      totalRuns,
      successRate: totalRuns > 0 ? Math.round((passed / totalRuns) * 100) : 0,
      totalFixes,
      avgIterations,
    });
  };

  const recentRuns = runs.slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.login}!</h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage your AI DevOps Agent runs
          </p>
        </div>
        <Link to="/run">
          <Button size="lg">
            <Play className="h-4 w-4 mr-2" />
            Run New Agent
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
                <History className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalRuns}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  All time executions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.successRate}%</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Passed vs total runs
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Fixes</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalFixes}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Errors automatically fixed
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Iterations</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.avgIterations}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Per successful run
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Runs */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Runs</CardTitle>
                  <CardDescription>Your latest agent executions</CardDescription>
                </div>
                <Link to="/history">
                  <Button variant="outline" size="sm">
                    View All
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {recentRuns.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No runs yet. Start by running your first agent!</p>
                  <Link to="/run">
                    <Button className="mt-4">
                      <Play className="h-4 w-4 mr-2" />
                      Run Agent
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentRuns.map((run) => (
                    <Link
                      key={run.id}
                      to={`/results/${run.id}`}
                      className="block p-4 rounded-lg border hover:bg-accent transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{run.repo_name}</p>
                          <p className="text-sm text-muted-foreground mt-1">
                            {formatDate(run.created_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <p className="text-sm font-medium">{run.total_fixes} fixes</p>
                            <p className="text-xs text-muted-foreground">{run.iterations} iterations</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(run.status)}`}>
                            {run.status}
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
