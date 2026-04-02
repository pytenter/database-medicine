import http from "./http";

export const getShiftSchedulesApi = (params) => http.get("/users/shifts/", { params });
export const createShiftScheduleApi = (payload) => http.post("/users/shifts/", payload);
export const updateShiftScheduleApi = (id, payload) => http.put(`/users/shifts/${id}/`, payload);
export const deleteShiftScheduleApi = (id) => http.delete(`/users/shifts/${id}/`);
export const getShiftSalespeopleApi = () => http.get("/users/shifts/salespeople/");
