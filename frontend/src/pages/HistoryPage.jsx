import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Filter, Calendar, GitBranch, Play, Eye } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { useAgentStore } from '@/store';
import { agentAPI } from '@/services/api';
import { formatDate, getStatusColor } from '@/lib/utils';

export function HistoryPage() {
  const navigate = useNavigate();
  const { runs, setRuns } = useAgentStore();
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const data = await agentAPI.getRuns();
      setRuns(data);
    } catch (error) {
      console.error('Failed to load runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRuns = runs.filter(run => {
    const matchesSearch = run.repo_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         run.repo?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || run.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Run History</h1>
        <p className="text-muted-foreground mt-2">
          View and manage all your agent execution history
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search repositories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'PASSED' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('PASSED')}
              >
                Passed
              </Button>
              <Button
                variant={filter === 'PARTIAL' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('PARTIAL')}
              >
                Partial
              </Button>
              <Button
                variant={filter === 'FAILED' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setFilter('FAILED')}
              >
                Failed
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : filteredRuns.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground">
              {searchTerm || filter !== 'all' 
                ? 'No runs found matching your filters'
                : 'No runs yet. Start by running your first agent!'}
            </p>
            <Link to="/run">
              <Button className="mt-4">Run Agent</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredRuns.map((run) => (
            <Card key={run.id} className="hover:bg-accent/50 transition-colors">
              <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row md:items-center gap-4">
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold truncate">{run.repo_name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(run.status)}`}>
                        {run.status}
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <GitBranch className="h-4 w-4" />
                        <span className="truncate">{run.branch}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(run.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-6 text-center">
                    <div>
                      <p className="text-2xl font-bold">{run.total_failures}</p>
                      <p className="text-xs text-muted-foreground">Failures</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-600">{run.total_fixes}</p>
                      <p className="text-xs text-muted-foreground">Fixes</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-600">{run.iterations}</p>
                      <p className="text-xs text-muted-foreground">Iterations</p>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 min-w-fit">
                    <Link to={`/results/${run.id}`}>
                      <Button variant="outline" size="sm" className="w-full">
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                    </Link>
                    <Button 
                      variant="default" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate('/run', { 
                          state: { 
                            repo_url: run.repo,
                            team: run.team || '',
                            leader: run.leader || '',
                            max_retries: 5
                          } 
                        });
                      }}
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Run Again
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
