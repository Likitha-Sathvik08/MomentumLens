# MomentumLens

**AI-powered tactical shift explainer for soccer matches.**  
Built for the IBM June Innovation Challenge.

---

## 🏟️ The Problem

During a World Cup match, viewers often notice that the game suddenly changes: one team starts dominating possession, a substitution shifts the tempo, or a card alters the balance of play. Traditional statistics tell us *what* happened, but they do not explain *why* the momentum changed or which tactical decision mattered most.

## 💡 Our Solution

MomentumLens is an AI-powered tactical explainer that helps humans understand soccer matches. It ingests match event data, automatically detects momentum shifts, ranks the most likely tactical causes, and uses **IBM Granite** to generate a clear, human-friendly explanation for fans and analysts.

## 🤖 AI & Technical Approach

Our pipeline runs through 5 stages to turn raw data into explainable AI insights:

1. **Feature Extraction**: We convert raw event streams (passes, shots, fouls) into rolling metrics like possession %, pressure indices, and shot frequency.
2. **Momentum Detection**: An algorithm calculates a continuous momentum score and detects sharp "turning points" where the game state flips.
3. **Cause Ranking**: We analyze the events leading up to the turning point (e.g., a substitution, a red card) and rank them by their momentum weight.
4. **Context Retrieval**: We build a structured prompt containing the turning point data, the top ranked causes, and tactical knowledge base references.
5. **Generative Explanation**: **IBM Granite** (via WatsonX) acts as the expert analyst, consuming the context and generating a 2-3 paragraph explanation in plain language.

## ⚽ Why This Matters

The World Cup is watched by billions, many of whom are new to the deeper tactics of the game. MomentumLens makes soccer more accessible by explaining *why* things happen. It improves fan engagement, builds trust in tactical decisions, and demonstrates how **explainable AI** can be used to decode complex human performances under pressure.

## 🛠️ Technology Stack

- **AI Model**: IBM Granite (via `ibm-watsonx-ai` SDK)
- **Backend**: FastAPI, Python, SQLAlchemy, Pandas
- **Frontend**: Streamlit, Plotly
- **Data**: JSON Event Data (StatsBomb compatible)

---

## 🚀 Quickstart

### 1. Backend Setup

```bash
cd backend
cp .env.example .env
# Open .env and fill in your IBM WatsonX credentials

pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs available at `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` and click **"Load Sample Match"** in the sidebar to see the demo.

### 3. Tests

```bash
cd backend
pytest ../tests/ -v
```

---

## 🔮 Future Roadmap

This prototype demonstrates the core reasoning engine. Future enhancements will fully utilize the IBM ecosystem:

- **LangChain / LangFlow Orchestration**: Wrap the Granite calls in a robust agentic chain to support multi-step reasoning (e.g., verifying its own tactical explanations).
- **Docling Integration**: Use Docling to ingest and structure PDF match reports, FIFA rulebooks, and tactical blogs to feed into a true RAG (Retrieval-Augmented Generation) pipeline for context retrieval.
- **Multilingual Support**: Translate explanations live for global World Cup audiences.
- **Context Forge**: Register the app as an MCP tool so other agents can query match momentum.

---

## 📺 Demo Video

[[Link to YouTube](https://www.youtube.com/watch?v=odQ85rqv50s&t=61s)]

## 👥 Team

Built for the June Innovation Challenge & Learning Lab.

Likitha Sathvik Potineni, 
Himanshu Pant, 
Sri Rupin Potula
