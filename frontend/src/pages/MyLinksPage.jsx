import { useState, useEffect } from 'react';
import { linksApi } from '../api';

export default function MyLinksPage({ token, onError }) {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editId, setEditId] = useState(null);
  const [newAlias, setNewAlias] = useState('');

  useEffect(() => {
    loadLinks();
  }, [token]);

  const loadLinks = async () => {
    setLoading(true);
    try {
      const data = await linksApi.getMyLinks(token);
      setLinks(data.links);
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены? Эту ссылку больше нельзя будет восстановить.')) {
      return;
    }

    try {
      await linksApi.delete(id, token);
      setLinks(links.filter((l) => l.id !== id));
    } catch (err) {
      onError(err.message);
    }
  };

  const handleSetAlias = async (id, alias) => {
    try {
      const data = await linksApi.setAlias(id, alias, token);
      setLinks(links.map((l) => (l.id === id ? data : l)));
      setEditId(null);
      setNewAlias('');
    } catch (err) {
      onError(err.message);
    }
  };

  const copyToClipboard = (url) => {
    navigator.clipboard.writeText(url);
    onError('✓ Ссылка скопирована');
  };

  if (loading) return <div className="section loading">Загрузка ваших ссылок...</div>;

  return (
    <div className="section">
      <h2>Мои ссылки ({links.length})</h2>

      {links.length === 0 ? (
        <p className="empty">У вас пока нет ни одной ссылки. Создайте первую!</p>
      ) : (
        <div className="links-list">
          {links.map((link) => (
            <div key={link.id} className="link-card">
              <div className="link-info">
                <p className="link-url">{link.short_url}</p>
                <p className="link-original">{link.url}</p>

                {editId === link.id ? (
                  <div className="alias-form">
                    <input
                      type="text"
                      placeholder="Новый алиас (3-32 символа)"
                      value={newAlias}
                      onChange={(e) => setNewAlias(e.target.value)}
                      maxLength={32}
                    />
                    <button
                      className="btn-primary"
                      onClick={() => handleSetAlias(link.id, newAlias)}
                    >
                      Сохранить
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => {
                        setEditId(null);
                        setNewAlias('');
                      }}
                    >
                      Отмена
                    </button>
                  </div>
                ) : (
                  <p className="link-alias">
                    <strong>Алиас:</strong> {link.alias || '—'}
                  </p>
                )}

                {link.created_at && (
                  <p
                    style={{
                      fontSize: '0.8em',
                      color: '#999',
                      marginTop: '0.5em',
                    }}
                  >
                    Создано: {new Date(link.created_at).toLocaleString('ru-RU')}
                  </p>
                )}
              </div>

              <div className="link-actions">
                <button
                  className="btn-secondary"
                  onClick={() => copyToClipboard(link.short_url)}
                >
                  Копировать
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => {
                    setEditId(link.id);
                    setNewAlias('');
                  }}
                >
                  Алиас
                </button>
                <button
                  className="btn-danger"
                  onClick={() => handleDelete(link.id)}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
