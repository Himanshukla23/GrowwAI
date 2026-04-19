# Groww Assist — Frontend

The Groww Assist frontend is a modern, high-performance web application built with **Next.js 14** and **Tailwind CSS v4**. It follows the **Material 3 Design System** to provide a premium financial analysis experience.

## 🎨 Design System
-   **Styling**: Powered by Tailwind v4 (CSS-first approach).
-   **Typography**: Plus Jakarta Sans (Headlines) and Inter (Body).
-   **Color Tokens**: Uses semantic tokens like `primary-container`, `surface-variant`, etc., defined in `app/globals.css`.

## 📁 Key Directories
-   `app/`: Contains the main layout and the home page.
-   `components/`: Modular UI components:
    *   `AssistantPanel.js`: The AI chat interface.
    *   `DashboardWorkspace.js`: Fund overview and metrics.
    *   `ComparisonWorkspace.js`: Comparative analysis.
    *   `Sidebar.js`: Navigation and health metrics.
-   `lib/`: Utility functions and API configurations.
-   `context/`: (Optional) React Context providers.

## 🚀 Development
```bash
npm install
npm run dev
```

## 🛠️ Modifying the UI
-   **Theme**: Open `app/globals.css` and modify the `@theme` block.
-   **Chat Logic**: Edit `app/page.js` (API communication) and `components/AssistantPanel.js` (UI rendering).
-   **Dashboard Data**: Modify `components/DashboardWorkspace.js` to change how fund data is visualized.

## 🔗 Backend Connection
API endpoints are configured in `lib/api-config.js`. Ensure the backend server is running on port 8000.
