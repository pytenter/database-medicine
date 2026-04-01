import http from "./http";

export const loginApi = (payload) => http.post("/auth/login/", payload);
export const currentUserApi = () => http.get("/auth/me/");
