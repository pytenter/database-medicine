import http from "./http";

export const getStoresApi = (params) => http.get("/inventory/stores/", { params });
export const createStoreApi = (payload) => http.post("/inventory/stores/", payload);
export const updateStoreApi = (id, payload) => http.put(`/inventory/stores/${id}/`, payload);
export const deleteStoreApi = (id) => http.delete(`/inventory/stores/${id}/`);
export const getInventoryApi = (params) => http.get("/inventory/", { params });
export const createInventoryApi = (payload) => http.post("/inventory/", payload);
export const updateInventoryApi = (id, payload) => http.put(`/inventory/${id}/`, payload);
export const deleteInventoryApi = (id) => http.delete(`/inventory/${id}/`);
export const getPurchaseOrdersApi = (params) => http.get("/inventory/purchase-orders/", { params });
export const getNextPurchaseOrderNoApi = () => http.get("/inventory/purchase-orders/next-code/");
export const createPurchaseOrderApi = (payload) => http.post("/inventory/purchase-orders/", payload);
export const updatePurchaseOrderApi = (id, payload) => http.put(`/inventory/purchase-orders/${id}/`, payload);
export const deletePurchaseOrderApi = (id) => http.delete(`/inventory/purchase-orders/${id}/`);
