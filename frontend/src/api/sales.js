import http from "./http";

export const getSalesApi = (params) => http.get("/sales/", { params });
export const createSaleApi = (payload) => http.post("/sales/", payload);
