frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── types/
│   ├── hooks/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── .env
└── package.json


Folder / file	What to put inside
public/	Static files used directly, such as a favicon.
assets/	Images, logos, fonts and illustrations.
components/	Reusable UI elements: buttons, navbar, cards, input fields.
pages/	Full screens: Home, Login, Dashboard, Results.
layouts/	Shared page structure, such as a sidebar and header.
services/	API calls to FastAPI, such as authService.ts or patientService.ts.
types/	TypeScript interfaces for users, requests and responses.
hooks/	Reusable React logic, e.g. useAuth.ts.
App.tsx	Main application component and route setup.
main.tsx	React entry point that renders the app.
index.css	Global styles, fonts and CSS resets.
.env	Frontend configuration, such as VITE_API_URL.
package.json	Dependencies and commands to run the fronten






backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   ├── schemas/
│   ├── models/
│   ├── services/
│   ├── db/
│   └── core/
├── tests/
├── .env
└── requirements.txt


Folder / file	What to put inside
main.py	Create the FastAPI app, register routes and configure CORS.
api/routes/	API endpoints, e.g. auth.py, patients.py, analysis.py.
schemas/	Pydantic models validating incoming requests and outgoing responses.
models/	Database table definitions, if you use a database.
services/	Business logic, such as appointment scheduling or medical-data processing.
db/	Database connection, session and initialization code.
core/	Configuration, environment settings and shared security utilities.
tests/	Tests for important endpoints and business logic.
.env	Backend secrets and configuration; never commit this file.
requirements.txt	Python dependencies needed to run the backend.