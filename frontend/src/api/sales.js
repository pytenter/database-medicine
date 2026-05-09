import http from "./http";

export const getSalesApi = (params) => http.get("/sales/", { params });
export const getSaleDetailApi = (id) => http.get(`/sales/${id}/`);
export const createSaleApi = (payload) => http.post("/sales/", payload);
