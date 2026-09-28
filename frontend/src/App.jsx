import { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import MyLinksPage from './pages/MyLinksPage';

export default function App() {
  const [page, setPage] = useState('home');
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setUser({ token });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setPage('home');
    setError('');
  };

  const handleError = (message) => {
    setError(message);
    if (message.startsWith('✓')) {
      setTimeout(() => setError(''), 3000);
    }
  };

  return (
    <>
      <header>
        <h1>🔗 Shortcuter</h1>
        <nav>
          <button
            className={`nav-btn ${page === 'home' ? 'active' : ''}`}
            onClick={() => setPage('home')}
          >
            Главная
          </button>
          {user ? (
            <>
              <button
                className={`nav-btn ${page === 'my-links' ? 'active' : ''}`}
                onClick={() => setPage('my-links')}
              >
                Мои ссылки
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                Выход
              </button>
            </>
          ) : (
            <button
              className={`nav-btn ${page === 'auth' ? 'active' : ''}`}
              onClick={() => setPage('auth')}
            >
              Вход
            </button>
          )}
        </nav>
      </header>

      <main>
        {error && <div className="error">{error}</div>}

        {page === 'home' && <HomePage user={user} onError={handleError} />}
        {page === 'auth' && (
          <AuthPage
            onAuth={setUser}
            onError={handleError}
            onSuccess={() => setPage('home')}
          />
        )}
        {page === 'my-links' && (
          <MyLinksPage token={user?.token} onError={handleError} />
        )}
      </main>
    </>
  );
}
