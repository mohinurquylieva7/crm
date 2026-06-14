import { useState } from 'react';
import { SignIn } from './SignIn';
import { SignUp } from './SignUp';

type AuthPage = 'signin' | 'signup';

export function AuthRouter() {
  const [page, setPage] = useState<AuthPage>('signin');

  if (page === 'signup') {
    return <SignUp onNavigateToSignIn={() => setPage('signin')} />;
  }
  return <SignIn onNavigateToSignUp={() => setPage('signup')} />;
}
