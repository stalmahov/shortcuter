import { useEffect, useState } from 'react';
import { adminApi, api } from '../api';

export default function AdminPage({ token }) {
  const [users, setUsers] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    setUsers([]);
    setLinks([]);
    Promise.all([adminApi.getUsers(token), api.get('/api/admin/links', token)])
      .then(([userData, linkData]) => {
        if (!active) return;
        setUsers(userData.users);
        setLinks(linkData.links);
      })
      .catch((err) => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [token]);

  const toggleBlock = async (user) => {
    setSaving(true);
    setError('');
    try {
      const updated = await adminApi.blockUser(user.id, !user.is_blocked, token);
      setUsers((current) => current.map((item) => (
        item.id === updated.id ? updated : item
      )));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const deleteLink = async (link) => {
    if (!window.confirm(`Удалить ссылку «${link.code}»?`)) return;
    setSaving(true);
    setError('');
    try {
      await api.delete(`/api/admin/links/${link.id}`, token);
      setLinks((current) => current.filter((item) => item.id !== link.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="section">
      <h2>Пользователи</h2>
      {error && <p className="error" role="alert">{error}</p>}
      {loading ? <p>Загрузка...</p> : (
        <div className="links-list">
          {users.map((user) => (
            <div className="link-card" key={user.id}>
              <div className="link-info">
                <p>{user.email}</p>
                <p>{user.role} · {user.is_blocked ? 'Заблокирован' : 'Активен'}</p>
                {user.blocked_at && <p>С {new Date(user.blocked_at).toLocaleString('ru-RU')}</p>}
              </div>
              <button className="btn-secondary" disabled={saving}
                onClick={() => toggleBlock(user)}>
                {user.is_blocked ? 'Разблокировать' : 'Заблокировать'}
              </button>
            </div>
          ))}
        </div>
      )}
      {!loading && users.length > 0 && (
        <>
          <h2>Все ссылки</h2>
          {links.length === 0 && <p>Ссылок пока нет.</p>}
          <div className="links-list">
            {links.map((link) => (
              <div className="link-card" key={link.id}>
                <div className="link-info">
                  <p>{link.code}</p>
                  <p className="link-original">{link.url}</p>
                  <p>{link.owner_id === null ? 'Гостевая' : `Пользователь №${link.owner_id}`}</p>
                </div>
                <button className="btn-secondary" disabled={saving}
                  onClick={() => deleteLink(link)}>
                  Удалить
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
