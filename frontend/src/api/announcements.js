import http from "./http";

export const getAnnouncementsApi = (params) => http.get("/announcements/", { params });
export const createAnnouncementApi = (payload) => http.post("/announcements/", payload);
export const updateAnnouncementApi = (id, payload) => http.put(`/announcements/${id}/`, payload);
export const deleteAnnouncementApi = (id) => http.delete(`/announcements/${id}/`);
