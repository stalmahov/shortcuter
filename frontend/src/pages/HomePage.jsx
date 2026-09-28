import { useState } from 'react';
import { linksApi } from '../api';

export default function HomePage({ user, onError }) {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    onError('');

    try {
      const data = await linksApi.create(url, user?.token);
      setResult(data);
      setUrl('');
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result?.short_url) {
      navigator.clipboard.writeText(result.short_url);
      onError('✓ Ссылка скопирована в буфер обмена');
    }
  };

  return (
    <div className="section">
      <h2>Сократить URL</h2>
      <form onSubmit={handleSubmit} className="form">
        <input
          type="url"
          placeholder="https://example.com/long/path"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Сократить'}
        </button>
      </form>

      {result && (
        <div className="result">
          <p>
            <strong>Оригинальная ссылка:</strong>
            {result.url}
          </p>

          <p>
            <strong>Код:</strong>
            <code>{result.code}</code>
          </p>

          <p>
            <strong>Короткая ссылка:</strong>
          </p>
          <div style={{ display: 'flex', gap: '0.5em', alignItems: 'center' }}>
            <input
              type="text"
              value={result.short_url}
              readOnly
              className="result-input"
            />
            <button className="btn-success" onClick={copyToClipboard}>
              Копировать
            </button>
          </div>

          {result.owner_id && (
            <div className="success-msg">
              ✓ Ссылка сохранена в вашем кабинете
            </div>
          )}
        </div>
      )}
    </div>
  );
}
