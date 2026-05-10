import { createRouter, createWebHistory } from "vue-router";
import DatasetList from "../pages/DatasetList.vue";
import DatasetDetail from "../pages/DatasetDetail.vue";
import Upload from "../pages/Upload.vue";
import AnalysisResult from "../pages/AnalysisResult.vue";

const routes = [
  { path: "/", name: "datasets", component: DatasetList },
  { path: "/datasets/:id", name: "dataset-detail", component: DatasetDetail },
  { path: "/upload", name: "upload", component: Upload },
  { path: "/analysis/:id", name: "analysis-result", component: AnalysisResult }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
