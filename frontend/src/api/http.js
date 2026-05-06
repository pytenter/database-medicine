import axios from "axios";
import { finishRequest, startRequest } from "../stores/requestState";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
});

http.interceptors.request.use(
  (config) => {
    startRequest();
    config.__counted = true;

    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    if (error.config?.__counted) {
      finishRequest();
    }
    return Promise.reject(error);
  }
);

http.interceptors.response.use(
  (response) => {
    if (response.config?.__counted) {
      finishRequest();
    }
    return response;
  },
  (error) => {
    if (error.config?.__counted) {
      finishRequest();
    }
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("current_user");
      if (location.pathname !== "/login") {
        location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default http;
