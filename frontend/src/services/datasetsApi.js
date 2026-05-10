import apiClient from "./apiClient";

export async function fetchDatasets() {
  const response = await apiClient.get("/datasets");
  return response.data;
}

export async function fetchDatasetById(id) {
  const response = await apiClient.get(`/datasets/${id}`);
  return response.data;
}
