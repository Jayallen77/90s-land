const PASSPORT_KEY = "90sLand.passport.v1";
const SURPRISE_KEY = "90sLand.surprise.v1";

const memory = new Map();

function storageAdapter(kind) {
  let storage;
  try {
    storage = window[kind];
    const probe = `90sLand.${kind}.probe`;
    storage.setItem(probe, "1");
    storage.removeItem(probe);
    return {
      persistent: true,
      read(key) {
        return storage.getItem(key);
      },
      write(key, value) {
        storage.setItem(key, value);
      },
      remove(key) {
        storage.removeItem(key);
      },
    };
  } catch {
    return {
      persistent: false,
      read(key) {
        return memory.get(`${kind}:${key}`) ?? null;
      },
      write(key, value) {
        memory.set(`${kind}:${key}`, value);
      },
      remove(key) {
        memory.delete(`${kind}:${key}`);
      },
    };
  }
}

export const localStore = storageAdapter("localStorage");
export const sessionStore = storageAdapter("sessionStorage");

export function readJson(adapter, key, fallback) {
  try {
    const raw = adapter.read(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function writeJson(adapter, key, value) {
  try {
    adapter.write(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}

export { PASSPORT_KEY, SURPRISE_KEY };
