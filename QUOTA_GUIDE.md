# 🛑 Azure OpenAI Quota & Testing Guide

## ❓ Current Status: "Live Architecture, Zero Quota"

You asked: *"Do you mean to say I would not be able to use any GPT model now to test this flow?"*

**Answer: Correct.** You cannot currently test the **GPT model response** because your Azure subscription has **0 quota** for GPT-4/GPT-3.5 models.

### Why is this happening?
1.  **Plumbing is Live ✅**:
    - The **Azure Function** is running.
    - The **Prompt Flow** endpoint is deployed.
    - The **Connection** works.
    - The code *attempts* to call GPT every time you run a test.

2.  **Quota is Missing 🚫**:
    - When the code calls GPT, **Azure rejects the request** with a `429 Quota Exceeded` error.
    - This is standard behavior for new Azure subscriptions (Free/Pay-As-You-Go) to prevent abuse.
    - Our system catches this error and **automatically switches to Fallback Mode** (Regex/Pattern Matching) so the pipeline doesn't crash.

---

## 🚀 How to Enable GPT Testing

To test the real AI flow, you must **manually request quota** from Microsoft. This usually takes **24–48 hours** for approval.

### Step-by-Step Instructions

1.  **Go to Azure OpenAI Studio**
    - Link: [https://oai.azure.com/](https://oai.azure.com/)
    - Select your subscription and resource (`xrs-nexus-dev-openai`).

2.  **Navigate to Quotas**
    - Click on **Management** -> **Quotas** in the left sidebar.
    - Ensure you are in the **East US** region (where we deployed).

3.  **Request Quota**
    - Look for **"gpt-4o-mini"** or **"gpt-35-turbo"** in the list.
    - If the "Quota" column shows `0`, select the model.
    - Click **Request Quota**.
    - Fill in the form (Reason: "Testing RAG application development").

4.  **Wait for Approval**
    - Once approved (status changes to "Approved"), the quota will increase (e.g., to 10K Tokens Per Minute).

### After Approval
**No code changes are needed!**
Once quota is available:
1.  The Azure Function will retry calling GPT.
2.  Azure will accept the request.
3.  The function will return `ai_powered: true`.
4.  You will see intelligent PII detection instead of Regex.

---

## 🛠 Temporary Workaround (Not Recommended)

If you absolutely need to test *now* and cannot wait:
- If you have an **OpenAI API Key** (from [platform.openai.com](https://platform.openai.com)), we can modify the code to use that instead of Azure OpenAI temporarily.
- **Warning**: This requires changing `ai_validator.py` to use `OpenAI` client instead of `AzureOpenAI`, which deviates from the enterprise architecture.

**Recommendation**: Wait for the Azure quota approval to keep the architecture clean.
