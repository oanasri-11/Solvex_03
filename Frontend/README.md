# روض — Frontend

A pixel-perfect, fully responsive, and modular React frontend for the **روض** Clinical Telemonitoring Platform, based on the design system in `assets/UI`.

---

## 🚀 Tech Stack

- **Framework:** React 19 (Functional Components, TypeScript, Hooks)
- **Bundler & Tooling:** Vite 8 + TypeScript (Strict Type Safety, `verbatimModuleSyntax`)
- **Styling:** Tailwind CSS v4 (`@tailwindcss/vite`) matching exact Figma spacing, color tokens, and border radii
- **Icons:** [Lucide React](https://lucide.dev/) + Authentic Arabic Calligraphic Brand SVG Vector Logo
- **State Management:** Centralized React Context (`AppContext`) with global navigation, interactive state handlers, filter states, and live telemetry simulation

---

## 📐 Implemented Screens & Mockup Mapping

| Mockup Image | Component | Description |
| :--- | :--- | :--- |
| `Splash.png` | `SplashScreen.tsx` | Centered Rawd logo, animated spinner, "Getting things ready" |
| `Log in.png` | `LoginScreen.tsx` | Welcome back form, password toggle, quick demo switches |
| `sign up doctor.png` | `SignUpDoctorScreen.tsx` | Doctor registration with RPPS/license, specialty, telemonitoring protocols |
| `sign up patient.png` | `SignUpPatientScreen.tsx` | Patient registration with DOB, emergency contact info, consent |
| `Home — Doctor workspace.png` | `DoctorDashboard.tsx` | 3 metric summary cards (148 patients, 12 urgent, 18 alerts), prioritized care queue, inbox callout |
| `Patients — Doctor workspace.png` | `DoctorPatients.tsx` | Search by patient name or ID, clinical status dropdown filter, sorted priority table, pagination |
| `Alerts — Doctor workspace.png` | `DoctorAlerts.tsx` | Master-detail clinical inbox, acknowledgement and resolution workflows, contact modal |
| `Marc Dupuis — Patient detail.png` | `DoctorPatientDetail.tsx` | 10-day worsening BP banner, interactive trend chart with tooltips, recent readings, active alerts |
| `Marc Dupuis — Patient review.png` | `DoctorPatientReview.tsx` | 14-day patient review summary, core clinical findings, morning vs evening reading analysis |
| `Patient Home.png` | `PatientHome.tsx` | Latest reading (128/82), 7-day trend chart with target range shading, weekly summary |
| `Patient Blood Pressure Tracking.png` | `PatientRecordReading.tsx` | Manual reading entry, symptom checklist (1–7), medication taken toggle, HAS protocol guide |
| `P2_ Patient Record Measurement.png` | `PatientRecordReading.tsx` | Continuous monitoring mode, streaming simulation, AI prediction |
| `Patient.png` | `PatientHistoryTrends.tsx` | Multi-interval trend filters (7d/14d/30d), SYS/DIA chart with time-of-day filters, reading log, consultation summary |
| `Alerts & Actions — Overview.png` | `PatientAlertsActions.tsx` | Emergency hotline banner, filtered example alerts table, priority & status guidance cards |
| `Information Alert — Device.png` | `PatientAlertDetail.tsx` | Step-by-step Bluetooth sync troubleshooting guide, interactive retry sync simulation |
| `P7_ Patient Settings — Desktop.png` | `PatientSettings.tsx` | Dynamic font scaling (14px/18px/22px), theme selection, Arabic RTL toggle, connected BLE device test, caregiver access |

---

## 📁 Modular Folder Structure

```
Frontend/src/
├── assets/
│   ├── logo/
│   │   └── Logo.svg                # High-res authentic Rawd (روض) brand mark
│   └── UI/                         # Design references
├── components/
│   ├── auth/                       # Splash, Login, Sign Up (Doctor & Patient)
│   ├── common/                     # BrandLogo, Badge, DevNavBar showcase bar
│   ├── charts/                     # BPLineChart (SVG responsive chart with target zone & tooltips)
│   ├── doctor/                     # Dashboard, Patients, Alerts Inbox, Patient Detail, Patient Review
│   ├── patient/                    # Home, Record Reading, History & Trends, Alerts & Actions, Settings
│   └── layout/                     # DoctorLayout & PatientLayout (Responsive Sidebars & Topbars)
├── context/
│   └── AppContext.tsx              # Central reactive store & navigation controller
├── data/
│   └── mockData.ts                 # Full clinical dataset matching mockups
├── types/
│   └── index.ts                    # TypeScript models & types
├── App.tsx                         # Main Router & Dev Showcase Shell
├── main.tsx                        # App entry point
└── index.css                       # Tailwind v4 configuration, font styling & animations
```

---

## 🛠️ Getting Started

### 1. Install Dependencies
```bash
cd Frontend
bun install
# or
npm install
```

### 2. Run the Development Server
```bash
bun run dev
# or
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Build for Production
```bash
bun run build
# or
npm run build
```

---

## 💡 Interactive Showcase Bar (`DevNavBar`)
A persistent top bar allows switching with a single click between:
1. **Doctor Portal:** Home, Patients List, Alerts Inbox, Marc Dupuis Detail, 14-Day Summary.
2. **Patient Portal:** Patient Home, Record Reading, History & Trends, Alerts & Actions, Device Sync Detail, Settings.
3. **Auth & Onboarding:** Splash Screen, Login Screen, Sign Up Doctor, Sign Up Patient.
