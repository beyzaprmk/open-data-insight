import { defineStore } from "pinia";
import { fetchAnalysisById, requestAnalysis } from "../services/analysisApi";

export const useAnalysisStore = defineStore("analysis", {
  state: () => ({
    result: null,
    isLoading: false
  }),
  actions: {
    async runAnalysis(imageId) {
      this.isLoading = true;
      try {
        this.result = await requestAnalysis(imageId);
      } finally {
        this.isLoading = false;
      }
    },
    async loadResult(id) {
      this.isLoading = true;
      try {
        this.result = await fetchAnalysisById(id);
      } finally {
        this.isLoading = false;
      }
    }
  }
});
