import { useState } from 'react';
import { authApi } from '../api';

export default function AuthPage({ onAuth, onError, onSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    onError('');

    try {
      if (isLogin) {
        const data = await authApi.login(email, password);
        localStorage.setItem('token', data.token);
        onAuth({ token: data.token });
        onSuccess();
      } else {
        await authApi.register(email, password);
        setIsLogin(true);
        setEmail('');
        setPassword('');
        onError('✓ Регистрация успешна! Теперь войдите в аккаунт.');
      }
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setEmail('');
    setPassword('');
    onError('');
  };

  return (
    <div className="section">
      <h2>{isLogin ? 'Вход в аккаунт' : 'Регистрация'}</h2>
      <form onSubmit={handleSubmit} className="form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль (минимум 8 символов)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Загрузка...' : isLogin ? 'Вход' : 'Регистрация'}
        </button>
      </form>

      <div className="auth-toggle">
        {isLogin ? 'Нет аккаунта? ' : 'Уже есть аккаунт? '}
        <button className="toggle-link" onClick={toggleMode}>
          {isLogin ? 'Зарегистрируйтесь' : 'Войдите'}
        </button>
      </div>
    </div>
  );
}
