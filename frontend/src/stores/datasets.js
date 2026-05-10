import { defineStore } from "pinia";
import { fetchDatasets, fetchDatasetById } from "../services/datasetsApi";

export const useDatasetsStore = defineStore("datasets", {
  state: () => ({
    items: [],
    selected: null,
    isLoading: false
  }),
  actions: {
    async loadAll() {
      this.isLoading = true;
      try {
        this.items = await fetchDatasets();
      } finally {
        this.isLoading = false;
      }
    },
    async loadById(id) {
      this.isLoading = true;
      try {
        this.selected = await fetchDatasetById(id);
      } finally {
        this.isLoading = false;
      }
    }
  }
});
