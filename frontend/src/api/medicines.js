import http from "./http";

export const getMedicinesApi = (params) => http.get("/medicines/", { params });
export const createMedicineApi = (payload) => http.post("/medicines/", payload);
export const updateMedicineApi = (id, payload) => http.put(`/medicines/${id}/`, payload);
export const deleteMedicineApi = (id) => http.delete(`/medicines/${id}/`);

export const getManufacturersApi = (params) => http.get("/medicines/manufacturers/", { params });
export const createManufacturerApi = (payload) => http.post("/medicines/manufacturers/", payload);
export const getCategoriesApi = (params) => http.get("/medicines/categories/", { params });
export const createCategoryApi = (payload) => http.post("/medicines/categories/", payload);
