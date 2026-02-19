import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Play, Loader2, GitBranch, Search } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input, Label } from '@/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAgentStore } from '@/store';
import { agentAPI } from '@/services/api';
import { useAgentProgress } from '@/hooks/useAgentProgress';
import AgentProgress from '@/components/AgentProgress';

export function RunAgentPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setCurrentRun, setIsRunning } = useAgentStore();
  const [loading, setLoading] = useState(false);
  const [currentRunId, setCurrentRunId] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showRepoList, setShowRepoList] = useState(false);
  
  // WebSocket progress tracking
  const { progress, currentStatus, isConnected } = useAgentProgress(currentRunId);
  
  // Auto-navigate when agent completes
  useEffect(() => {
    if (currentStatus === 'completed' && currentRunId) {
      toast.success('🎉 Agent completed successfully!');
      setTimeout(() => {
        setLoading(false);
        setIsRunning(false);
        navigate(`/results/${currentRunId}`);
      }, 2000);
    } else if (currentStatus === 'error') {
      toast.error('❌ Agent encountered an error');
      setLoading(false);
      setIsRunning(false);
    }
  }, [currentStatus, currentRunId, navigate]);
  
  // Check if we have pre-filled data from navigation (Run Again)
  const initialFormData = location.state || {
    repo_url: '',
    team: '',
    leader: '',
    max_retries: 5,
  };
  
  const [formData, setFormData] = useState(initialFormData);
  
  // Show toast if this is a re-run
  useEffect(() => {
    if (location.state?.repo_url) {
      toast.success('📋 Form pre-filled from previous run. Review and submit!');
    }
  }, []);

  // Fetch user's repositories on mount
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        const data = await agentAPI.getRepos();
        setRepositories(data.repositories || []);
      } catch (error) {
        console.error('Failed to fetch repositories:', error);
        toast.error('Could not load repositories');
      } finally {
        setLoadingRepos(false);
      }
    };

    fetchRepositories();
  }, []); // Only run once on mount

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showRepoList && !e.target.closest('.repo-selector')) {
        setShowRepoList(false);
      }
    };

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setShowRepoList(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [showRepoList]);

  // Filter repositories based on search
  const filteredRepos = searchQuery
    ? repositories.filter(repo =>
        repo.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        repo.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : repositories;

  const handleRepoSelect = (repo) => {
    setFormData(prev => ({
      ...prev,
      repo_url: repo.clone_url,
    }));
    setSearchQuery('');
    setShowRepoList(false);
    toast.success(`Selected: ${repo.full_name}`);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'max_retries' ? parseInt(value) || 5 : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.repo_url || !formData.team || !formData.leader) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (!formData.repo_url.includes('github.com')) {
      toast.error('Please enter a valid GitHub repository URL');
      return;
    }

    setLoading(true);
    setIsRunning(true);

    try {
      // Start the agent run async (returns immediately with run_id)
      toast.loading('🚀 Starting agent run...');
      
      const response = await agentAPI.runAgentAsync(formData);
      console.log('🔍 Agent started:', response);
      console.log('🆔 Run ID:', response?.id);
      
      if (!response?.id) {
        console.error('❌ No ID in response:', response);
        toast.error('Failed to start agent run');
        return;
      }
      
      // Set run ID to connect WebSocket
      setCurrentRunId(response.id.toString());
      toast.success(`✅ Agent running! ID: ${response.id}`);
      
      // The component will now show real-time progress via WebSocket
      // We'll navigate to results when we receive the "completed" status
      // or user can manually navigate using the run ID
      
    } catch (error) {
      console.error('Agent run failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to start agent. Please try again.');
      setLoading(false);
      setIsRunning(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Run AI DevOps Agent</h1>
        <p className="text-muted-foreground mt-2">
          Configure and execute the agent on your repository
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Agent Configuration</CardTitle>
          <CardDescription>
            Enter your repository details and team information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Repository Selector */}
            <div className="space-y-2">
              <Label>Select Repository from Your Account</Label>
              <div className="relative repo-selector">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Click to see all repositories or type to search..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setShowRepoList(true);
                    }}
                    onFocus={() => setShowRepoList(true)}
                    disabled={loading || loadingRepos}
                    className="pl-10"
                  />
                </div>
                
                {/* Repository Dropdown List */}
                {showRepoList && (
                  <div className="absolute z-10 w-full mt-1 bg-background border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
                    {loadingRepos ? (
                      <div className="p-4 text-center text-muted-foreground">
                        <Loader2 className="h-5 w-5 animate-spin mx-auto mb-2" />
                        Loading repositories...
                      </div>
                    ) : filteredRepos.length > 0 ? (
                      <div className="py-2">
                        {filteredRepos.map((repo) => (
                          <button
                            key={repo.id}
                            type="button"
                            onClick={() => handleRepoSelect(repo)}
                            className="w-full px-4 py-3 text-left hover:bg-secondary/50 transition-colors"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-sm truncate">{repo.full_name}</p>
                                {repo.description && (
                                  <p className="text-xs text-muted-foreground truncate mt-1">
                                    {repo.description}
                                  </p>
                                )}
                                <div className="flex items-center gap-2 mt-1">
                                  {repo.language && (
                                    <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded">
                                      {repo.language}
                                    </span>
                                  )}
                                  {repo.private && (
                                    <span className="text-xs px-2 py-0.5 bg-yellow-500/10 text-yellow-600 rounded">
                                      Private
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-center text-muted-foreground text-sm">
                        No repositories found
                      </div>
                    )}
                  </div>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {loadingRepos
                  ? 'Loading your repositories...'
                  : `Found ${repositories.length} repositories in your account`}
              </p>
            </div>

            {/* Manual Repository URL Input */}
            <div className="space-y-2">
              <Label htmlFor="repo_url">Repository URL *</Label>
              <Input
                id="repo_url"
                name="repo_url"
                type="url"
                placeholder="https://github.com/username/repository.git"
                value={formData.repo_url}
                onChange={handleChange}
                required
                disabled={loading}
              />
              <p className="text-xs text-muted-foreground">
                Selected repository or enter a GitHub URL manually
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="team">Team Name *</Label>
                <Input
                  id="team"
                  name="team"
                  placeholder="TeamAlpha"
                  value={formData.team}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
                <p className="text-xs text-muted-foreground">
                  Your team name for branch creation
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="leader">Team Leader *</Label>
                <Input
                  id="leader"
                  name="leader"
                  placeholder="John"
                  value={formData.leader}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
                <p className="text-xs text-muted-foreground">
                  Team leader name for branch creation
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max_retries">Max Retries</Label>
              <Input
                id="max_retries"
                name="max_retries"
                type="number"
                min="1"
                max="10"
                value={formData.max_retries}
                onChange={handleChange}
                disabled={loading}
              />
              <p className="text-xs text-muted-foreground">
                Maximum number of fix iterations (1-10)
              </p>
            </div>

            <div className="bg-secondary/50 p-4 rounded-lg space-y-2">
              <div className="flex items-center gap-2 font-medium">
                <GitBranch className="h-4 w-4" />
                <span>Branch Preview</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {formData.team && formData.leader
                  ? `${formData.team.toUpperCase().replace(/\s/g, '_')}_${formData.leader.toUpperCase().replace(/\s/g, '_')}_AI_FIX`
                  : 'TEAM_LEADER_AI_FIX'}
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                type="submit"
                className="flex-1"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Running Agent...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Run Agent
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/dashboard')}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Real-time Progress Display */}
      {loading && currentRunId && (
        <div className="space-y-4">
          <AgentProgress progress={progress} currentStatus={currentStatus} isConnected={isConnected} />
          
          {/* Manual Navigation Button */}
          {currentRunId && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">
                      {isConnected ? 'Agent is running...' : 'Connection lost. Agent may still be running.'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Run ID: {currentRunId}
                    </p>
                  </div>
                  <Button
                    onClick={() => {
                      navigate(`/results/${currentRunId}`);
                    }}
                    variant="outline"
                  >
                    View Results →
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>What happens when you run the agent?</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3 text-sm">
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                1
              </span>
              <span>Clones your repository to a secure workspace</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                2
              </span>
              <span>Installs dependencies from requirements.txt</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                3
              </span>
              <span>Runs pytest to detect errors and failures</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                4
              </span>
              <span>Analyzes errors and applies intelligent fixes</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                5
              </span>
              <span>Creates commits for each fix with descriptive messages</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                6
              </span>
              <span>Pushes all changes to a new branch</span>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-medium">
                7
              </span>
              <span>Generates detailed results and statistics</span>
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
