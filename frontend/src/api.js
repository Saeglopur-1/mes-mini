const KEY = "mes_demo_v1";

function read() {
  return JSON.parse(localStorage.getItem(KEY) || "{}");
}
function write(db) {
  localStorage.setItem(KEY, JSON.stringify(db));
}
function ensure() {
  const db = read();
  db.tasks ??= [];
  db.molds ??= [];
  db.materials ??= [];
  db.products ??= [];
  db.inventory ??= [];
  write(db);
  return db;
}
function uid() {
  return Date.now().toString() + Math.random().toString(16).slice(2);
}

export const api = {
  async get(url) {
    const table = url.replace("/api/", "");
    return { data: ensure()[table] };
  },
  async post(url, payload) {
    const table = url.replace("/api/", "");
    const db = ensure();
    const row = { id: uid(), ...payload };
    db[table].unshift(row);
    write(db);
    return { data: row };
  },
  async put(url, payload) {
    const [_, table, id] = url.split("/");
    const db = ensure();
    const index = db[table].findIndex(i => i.id === id);
    if (index !== -1) {
      db[table][index] = { ...db[table][index], ...payload };
      write(db);
    }
    return { data: db[table][index] };
  },
  async delete(url) {
    const [_, table, id] = url.split("/");
    const db = ensure();
    db[table] = db[table].filter(i => i.id !== id);
    write(db);
    return { data: true };
  }
};

export default api;

