# Groww Assist — Suggested Questions

This document lists the factual questions that the Groww Assist AI can answer based on the current 19-URL corpus. These queries are optimized for the RAG pipeline and will bypass the safety guardrails.

---

## ✅ High-Performance Factual Queries

### 📊 NAV (Net Asset Value)
1. `What is the NAV of SBI Gold Fund?`
2. `What is the current NAV of SBI Contra Fund Direct Growth?`
3. `What is the NAV of HDFC Mid Cap Fund?`
4. `What is the NAV of ICICI Prudential Large Cap Fund?`
5. `What is the NAV of Nippon India Large Cap Fund?`

### 💰 Expense Ratio
6. `What is the expense ratio of SBI Gold Fund?`
7. `What is the expense ratio of SBI Contra Fund Direct Growth?`
8. `What is the expense ratio of HDFC Equity Fund?`
9. `What is the expense ratio of ICICI Prudential Dynamic Plan?`
10. `What is the expense ratio of Nippon India Multi Cap Fund?`

### 🚪 Exit Load
11. `What is the exit load for SBI Small Cap Fund?`
12. `Tell me about the exit load for HDFC Mid Cap Fund.`
13. `What is the exit load of ICICI Prudential Bharat 22 FOF?`
14. `What is the exit load of Nippon India Growth Mid Cap Fund?`

### 📈 Returns (Performance)
15. `What are the 1 year returns of SBI PSU Fund?`
16. `What are the 3 year returns of HDFC Focused Fund?`
17. `What are the 5 year returns of SBI Contra Fund?`
18. `What are the returns of ICICI Prudential Silver ETF FOF?`

### 🏦 Portfolio & Holdings
19. `What are the top holdings of SBI Gold Fund?`
20. `What are the top holdings of ICICI Prudential Large Cap Fund?`
21. `What are the top holdings of HDFC Equity Fund?`
22. `What is the AUM of SBI Mutual Fund?`
23. `What is the AUM of HDFC Mid Cap Fund?`

### 💵 Investment Minimums
24. `What is the minimum SIP amount for SBI Gold Fund?`
25. `What is the minimum lumpsum investment for HDFC Equity Fund?`
26. `What is the minimum investment for Nippon India Large Cap Fund?`

### 👤 Fund Management
27. `Who is the fund manager of SBI Contra Fund?`
28. `Who manages HDFC Mid Cap Fund?`
29. `Who is the CEO of ICICI Prudential Mutual Fund?`
30. `Who is the fund manager for Nippon India Large Cap Fund?`
31. `Tell me about the fund management team of HDFC Mutual Fund.`

### 🛠️ Process & Services
32. `How can I download my SBI Mutual Fund account statement?`
33. `What is the process to update my mobile number in HDFC Mutual Fund?`
34. `How to link Aadhaar with ICICI Prudential Mutual Fund?`
35. `What is the cut-off time for mutual fund transactions on Groww?`
36. `How can I redeem my units in Nippon India Multi Cap Fund?`

---

## 🚫 Prohibited / Blocked Queries

These queries will trigger the **Policy Safety Guardrails** and return a refusal message.

| Type | Example Trigger | Reason |
| :--- | :--- | :--- |
| **Advisory** | `Should I invest in...` | Financial recommendation (SEBI compliance) |
| **Recommendation** | `Which is the best fund?` | Objective ranking not allowed |
| **Comparison** | `Is SBI better than HDFC?` | Subjective comparison |
| **PII** | `My phone number is 9988...` | Privacy protection |
| **Out-of-scope** | `What is the stock price of Apple?` | Not within Mutual Fund corpus |

---

## 🏛️ Supported Mutual Funds (Full List)

The assistant contains deep knowledge of these specific schemes:

### SBI Mutual Fund
- SBI Gold Fund
- SBI PSU Fund
- SBI Small Cap Fund
- SBI Contra Fund

### ICICI Prudential Mutual Fund
- ICICI Prudential Dynamic Plan
- ICICI Prudential Large Cap Fund
- ICICI Prudential Bharat 22 FOF
- ICICI Prudential Silver ETF FOF

### HDFC Mutual Fund
- HDFC Mid Cap Fund
- HDFC Equity Fund
- HDFC Focused Fund

### Nippon India Mutual Fund
- Nippon India Growth Mid Cap Fund
- Nippon India Multi Cap Fund
- Nippon India Multi Asset Omni FOF
- Nippon India Large Cap Fund
