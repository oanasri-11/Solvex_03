
## Frontend — React + TypeScript

```mermaid
flowchart TD
    A["frontend/"] --> B["public/"]
    A --> C["src/"]
    A --> D[".env"]
    A --> E["package.json"]

    C --> F["assets/ - Images, logos, fonts"]
    C --> G["components/ - Reusable UI"]
    C --> H["pages/ - Home, Login, Dashboard"]
    C --> I["layouts/ - Shared page layouts"]
    C --> J["services/ - API calls"]
    C --> K["types/ - TypeScript interfaces"]
    C --> L["hooks/ - Reusable React logic"]
    C --> M["App.tsx - App and routes"]
    C --> N["main.tsx - React entry point"]
    C --> O["index.css - Global styles"]
```

## Backend — FastAPI

```mermaid
flowchart TD
    A["backend/"] --> B["app/"]
    A --> C["tests/ - Automated tests"]
    A --> D[".env - Secrets and settings"]
    A --> E["requirements.txt - Dependencies"]

    B --> F["main.py - FastAPI setup"]
    B --> G["api/routes/ - HTTP endpoints"]
    B --> H["schemas/ - Request validation"]
    B --> I["models/ - Database tables"]
    B --> J["services/ - Business logic"]
    B --> K["db/ - Database connection"]
    B --> L["core/ - Configuration and security"]
```

