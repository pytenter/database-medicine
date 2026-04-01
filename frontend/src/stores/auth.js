import { defineStore } from "pinia";

import { currentUserApi, loginApi } from "../api/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("current_user") || "null"),
  }),
  getters: {
    isAuthenticated: (state) => Boolean(localStorage.getItem("access_token") && state.user),
    role: (state) => state.user?.role || "",
  },
  actions: {
    async login(payload) {
      const { data } = await loginApi(payload);
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("current_user", JSON.stringify(data.user));
      this.user = data.user;
      return data.user;
    },
    async refreshUser() {
      if (!localStorage.getItem("access_token")) return null;
      const { data } = await currentUserApi();
      localStorage.setItem("current_user", JSON.stringify(data));
      this.user = data;
      return data;
    },
    logout() {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("current_user");
      this.user = null;
    },
  },
});
