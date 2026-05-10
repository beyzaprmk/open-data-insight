import apiClient from "./apiClient";

export async function requestAnalysis(imageId) {
  const response = await apiClient.post("/analysis", { imageId });
  return response.data;
}

export async function fetchAnalysisById(id) {
  const response = await apiClient.get(`/analysis/${id}`);
  return response.data;
}
