import http from "./http";

export const getStoresApi = (params) => http.get("/inventory/stores/", { params });
export const createStoreApi = (payload) => http.post("/inventory/stores/", payload);
export const updateStoreApi = (id, payload) => http.put(`/inventory/stores/${id}/`, payload);
export const deleteStoreApi = (id) => http.delete(`/inventory/stores/${id}/`);
export const getInventoryApi = (params) => http.get("/inventory/", { params });
export const createInventoryApi = (payload) => http.post("/inventory/", payload);
export const updateInventoryApi = (id, payload) => http.put(`/inventory/${id}/`, payload);
export const deleteInventoryApi = (id) => http.delete(`/inventory/${id}/`);
