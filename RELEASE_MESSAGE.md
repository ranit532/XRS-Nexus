Subject: [Share] XRS NEXUS: Next-Gen AI Integration Platform POC (Hybrid Cloud/Local AI)

Hi Team,

I’m excited to share the repository for **XRS NEXUS**, our new AI-driven integration platform POC.

**🔗 Repo Link:** [Insert Link Here]

**🚀 What is it?**
A cloud-agnostic, metadata-driven platform that uses GenAI to automate ETL pipelines, ensuring data governance and privacy. It revolutionizes how we handle enterprise data by replacing static pipelines with dynamic, AI-generated flows.

**🔥 Key Technical Highlights:**
*   **Hybrid AI Architecture**: We implemented a unique local/cloud hybrid model using **Ollama (Phi-3 Mini)** for local inference, bypassing Azure OpenAI quota limits and ensuring zero-cost operation during development.
*   **Real-Time "Human-in-the-Loop" Privacy**: The pipeline automatically detects PII (email, phone, etc.) and pauses for manual confirmation.
*   **Secure Data Movement**: Uses SHA-256 masking to anonymize sensitive fields before pushing *only* the validated sample to the **Azure Gold Layer**.
*   **Modern Stack**: Built with **Azure Data Factory**, **Microsoft Fabric**, **Python**, and a **React** real-time dashboard.

**💡 Why check it out?**
This project demonstrates how to build enterprise-grade AI solutions that are both secure and cost-effective. The codebase includes a full simulation mode, so you can run the entire end-to-end flow on your local machine.

Check out the **README.md** for the full architecture breakdown, setup guide, and our decision matrix for choosing Ollama over other providers.

Best,
[Your Name]
