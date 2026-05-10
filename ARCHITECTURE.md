# OpenDataInsight Architecture

## Root
- .env: local secrets and config
- .gitignore: ignored files list
- README.md: project overview
- app/: backend monolith
- frontend/: Vue 3 client
- scripts/: helper scripts

## Backend (app/)
- __init__.py: package marker
- api/: HTTP entry layer
- api/__init__.py: package marker
- api/routes/: route modules
- api/routes/__init__.py: package marker
- api/routes/health.py: health endpoint
- services/: business logic
- services/__init__.py: package marker
- services/dataset_service.py: dataset logic
- services/image_service.py: image logic
- services/analysis_service.py: metrics logic
- services/ai_service.py: AI logic
- repositories/: data access
- repositories/__init__.py: package marker
- repositories/dataset_repository.py: dataset queries
- repositories/image_repository.py: image queries
- integrations/: external adapters
- integrations/__init__.py: package marker
- integrations/cloudinary_client.py: storage client
- integrations/gemini_client.py: LLM client
- integrations/opencv_adapter.py: image metrics

## Frontend (frontend/)
- index.html: app entry
- src/: Vue source
- src/main.js: app bootstrap
- src/App.vue: app shell
- src/router/: routes
- src/router/index.js: route map
- src/pages/: views
- src/pages/DatasetList.vue: dataset list
- src/pages/DatasetDetail.vue: dataset detail
- src/pages/Upload.vue: upload view
- src/pages/AnalysisResult.vue: analysis view
- src/components/: UI blocks
- src/components/ImageCard.vue: dataset card
- src/components/MetricsPanel.vue: metrics grid
- src/components/UploadForm.vue: upload form
- src/components/ResultSummary.vue: AI result
- src/stores/: Pinia state
- src/stores/datasets.js: dataset store
- src/stores/analysis.js: analysis store
- src/services/: API calls
- src/services/apiClient.js: axios base
- src/services/datasetsApi.js: dataset API
- src/services/analysisApi.js: analysis API
- src/styles/: global styles
- src/styles/main.css: base styles

## Scripts (scripts/)
- install_deps.sh: dependency install
