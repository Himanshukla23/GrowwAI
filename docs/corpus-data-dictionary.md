# GrowwAI Corpus Data Dictionary

This document serves as the persistent reference for the data points fetched, processed, and indexed in the **GrowwAI Mutual Fund FAQ Assistant**.

## 1. Source URLs (The 19-URL Base)
The system fetches data from these specific Groww Mutual Fund pages:

### 🏛️ AMC Institutional Pages
1.  **SBI Mutual Fund**: `https://groww.in/mutual-funds/amc/sbi-mutual-funds`
2.  **ICICI Prudential**: `https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds`
3.  **HDFC Mutual Fund**: `https://groww.in/mutual-funds/amc/hdfc-mutual-funds`
4.  **Nippon India**: `https://groww.in/mutual-funds/amc/nippon-india-mutual-funds`

### 📈 SBI Schemes
5.  `SBI Gold Fund Direct Growth`
6.  `SBI PSU Fund Direct Growth`
7.  `SBI Small Cap Fund Direct Growth`
8.  `SBI Contra Fund Direct Growth`

### 📈 ICICI Prudential Schemes
9.  `ICICI Prudential Dynamic Plan Direct Growth`
10. `ICICI Prudential Large Cap Fund Direct Growth`
11. `ICICI Prudential Bharat 22 FOF Direct Growth`
12. `ICICI Prudential Silver ETF FOF Direct Growth`

### 📈 HDFC Schemes
13. `HDFC Mid Cap Fund Direct Growth`
14. `HDFC Equity Fund Direct Growth`
15. `HDFC Focused Fund Direct Growth`

### 📈 Nippon India Schemes
16. `Nippon India Growth Mid Cap Fund Direct Growth`
17. `Nippon India Multi Cap Fund Direct Growth`
18. `Nippon India Multi Asset Omni FOF Direct Growth`
19. `Nippon India Large Cap Fund Direct Growth`

---

## 2. Extracted Financial Attributes
For every URL above, the system extracts and normalizes the following data points:

| Attribute | Category | Description |
| :--- | :--- | :--- |
| `NAV` | Performance | The current Net Asset Value (per unit price). |
| `1Y/3Y/5Y Returns` | Performance | Annualized performance returns over specific periods. |
| `Expense Ratio` | Fees | The annual fee deducted for fund management. |
| `Exit Load` | Fees | Redemption charges based on time of withdrawal. |
| `AUM` | Scale | Total Assets Under Management for the scheme/AMC. |
| `Min SIP/Lumpsum` | Investment | Minimum entry amounts for investors. |
| `Holdings` | Portfolio | Top equity/debt instruments held by the fund. |
| `Fund Management` | People | Names and backgrounds of the specific Fund Managers. |
| `Riskometer` | Risk | Risk rating (e.g., "Very High", "Moderate"). |
| `AMC Personnel` | Corporate | MD, CEO, CIO, and Compliance Officer information. |

---

## 3. Data Processing Schema
When data is fetched, it is transformed into the following JSON structure:

### `documents.json` (Phase 2 & 4)
*   `document_id`: Unique ID (e.g., `groww-001`).
*   `url`: The source link.
*   `clean_text`: Stripped of HTML, preserving newlines for headers.
*   `amc_name`: The associated Fund House.
*   `scheme_name`: The specific scheme (if applicable).
*   `content_hash`: Used to detect changes in data.

### `chunks.json` (Phase 4 Final)
*   `chunk_id`: UUID for the vector index.
*   `chunk_text`: ~500 token segments with **10% context overlap**.
*   `metadata`: Persistent link to the original URL and fetched timestamp.

---

## 4. Freshness Policy
*   **Update Frequency:** Daily at 09:15 IST.
*   **Verification:** Every fetch includes a `timestamp` and `content_hash` to ensure the AI uses the most current data available via the Scraping Service.
