import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { LoadingOverlay } from '@/components/ui/Spinner';
import { useAuthStore } from '@/store';
import { githubAuth } from '@/services/api';

export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuthStore();

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        toast.error('Authentication failed. Please try again.');
        navigate('/login');
        return;
      }

      if (!code) {
        toast.error('No authorization code received.');
        navigate('/login');
        return;
      }

      try {
        const data = await githubAuth.handleCallback(code);
        login(data.user, data.token);
        toast.success('Successfully logged in!');
        navigate('/dashboard');
      } catch (error) {
        console.error('Auth error:', error);
        toast.error('Authentication failed. Please try again.');
        navigate('/login');
      }
    };

    handleCallback();
  }, [searchParams, navigate, login]);

  return <LoadingOverlay message="Authenticating with GitHub..." />;
}
