# BingePal Backend API

A FastAPI backend serving as the brain of BingePal.

🔗 Base URL: https://bingepal.onrender.com

### Endpoints

- '/api/search?query=...&type=movie|series|anime'
  → Search for content

- '/api/detail?id=external_id&type=movie|series|anime'  
  → Fetch detailed info

- '/api/log' 
  → Log a view (POST JSON)

- '/api/trending?type=...&days=0|7|30|365' 
  → Trending titles by type and range

- '/api/history?limit=50'
  → List recent search/view logs