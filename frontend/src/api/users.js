import http from "./http";

export const getUsersApi = (params) => http.get("/users/", { params });
export const createUserApi = (payload) => http.post("/users/", payload);
export const updateUserApi = (id, payload) => http.put(`/users/${id}/`, payload);
export const deleteUserApi = (id) => http.delete(`/users/${id}/`);
export const resetPasswordApi = (id) => http.post(`/users/${id}/reset_password/`);
