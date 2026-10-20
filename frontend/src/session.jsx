/**
 * Sesión del usuario: quién está logueado y con qué rol.
 *
 * El token se guarda en localStorage para no tener que iniciar sesión cada
 * vez que se abre la app en el celular. Si el backend dice que el token
 * venció (401), se cierra la sesión y se vuelve al login.
 */

import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { api, getToken, saveToken, setUnauthorizedHandler } from "./api.js";

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(Boolean(getToken()));

  const logout = useCallback(() => {
    saveToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);

    if (!getToken()) return;

    api
      .me()
      .then(setUser)
      .catch(logout)
      .finally(() => setIsLoading(false));
  }, [logout]);

  async function login(email, password) {
    const result = await api.login(email, password);
    saveToken(result.access_token);
    setUser(result.user);
    return result.user;
  }

  return (
    <SessionContext.Provider value={{ user, isLoading, login, logout }}>{children}</SessionContext.Provider>
  );
}

export function useSession() {
  return useContext(SessionContext);
}
