import http from "./http";

export const getSalesApi = (params) => http.get("/sales/", { params });
export const getSaleDetailApi = (id) => http.get(`/sales/${id}/`);
export const createSaleApi = (payload) => http.post("/sales/", payload);
export const addLogisticsApi = (id, payload) => http.post(`/sales/${id}/logistics/`, payload);
export const submitReviewApi = (id, payload) => http.post(`/sales/${id}/review/`, payload);
