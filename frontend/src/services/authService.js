import api from "./api";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export const login = async (email, password) => {
  const response = await api.post("/api/auth/login/", {
    email,
    password,
  });

  const { access, refresh, user } = response.data;

  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);

  return user;
};

export const register = async (userData) => {
  const response = await api.post(
    "/api/auth/register/",
    userData
  );

  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get("/api/auth/me/");
  return response.data;
};

export const logout = async () => {
  const refresh = getRefreshToken();

  if (refresh) {
    await api.post("/api/auth/logout/", {
      refresh,
    });
  }

  clearTokens();
};

export const getAccessToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const saveTokens = (access, refresh = null) => {
  if (access) {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
  }

  if (refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }
};

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};
