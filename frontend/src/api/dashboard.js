import http from "./http";

export const getDashboardOverviewApi = () => http.get("/dashboard/overview/");
