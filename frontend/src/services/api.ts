import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 15000,
});

const IGNORAR_LOGOUT = [
  "/auth/login",
  "/notifications/test",
  "/notifications/config",
  "/auth/refresh",
];

api.interceptors.request.use((config) => {
  const isAuthLogin = config.url?.includes("/auth/login");
  const token = localStorage.getItem("access_token");
  if (token && !isAuthLogin) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    const ignorarLogout = IGNORAR_LOGOUT.some(rota =>
      originalRequest.url?.includes(rota)
    );

    if (error.response?.status === 401 && !originalRequest._retry && !ignorarLogout) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");

        if (!refreshToken) {
          localStorage.clear();
          window.location.href = "/login";
          return Promise.reject(error);
        }

        const response = await axios.post("http://localhost:8000/auth/refresh", {
          refresh_token: refreshToken
        });

        const newToken = response.data.access_token;
        localStorage.setItem("access_token", newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);

      } catch {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);