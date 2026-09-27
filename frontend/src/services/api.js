import axios from "axios";

const API_URL =
  process.env.REACT_APP_API_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const accessToken =
      localStorage.getItem("access_token");

    if (accessToken) {
      config.headers.Authorization =
        `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      !originalRequest?.url?.includes(
        "/api/auth/login/"
      ) &&
      !originalRequest?.url?.includes(
        "/api/auth/refresh/"
      )
    ) {
      originalRequest._retry = true;

      const refreshToken =
        localStorage.getItem("refresh_token");

      if (!refreshToken) {
        localStorage.removeItem("access_token");
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(
          `${API_URL}/api/auth/refresh/`,
          {
            refresh: refreshToken,
          }
        );

        const {
          access,
          refresh,
        } = response.data;

        localStorage.setItem(
          "access_token",
          access
        );

        // Important :
        // Django effectue une rotation du refresh token.
        if (refresh) {
          localStorage.setItem(
            "refresh_token",
            refresh
          );
        }

        originalRequest.headers.Authorization =
          `Bearer ${access}`;

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
EOF
