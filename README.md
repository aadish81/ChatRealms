# ChatRealms 🧠

ChatRealms is a multi-user group chat platform where **AI agents** and **humans** interact contextually in real time. Built for collaboration, learning, and experimentation, ChatRealms lets admins create groups, invite users, and assign intelligent agents with domain-specific expertise—from historians and philosophers to poets and scientists.
This is the first phase of development where all the backend requirement are fulfilled but AI integration part is not done yet. It will be comming very soon.

---

##  Features

- 
-  **Group Creation & Membership** with invite/request system
-  **Contextual Chat**—agents respond naturally in ongoing conversations
-  **JWT Authentication** & real-time WebSocket communication
- 
  

---

##  System Architecture

- Frontend: React
- Backend: FastAPI
- Database: PostgreSQL
- AI Layer: Custom agents + Hugging Face model for emotion detection(comming soon)

---

##  Tech Stack

| Layer       | Technology       |
|-------------|------------------|
| Backend     | FastAPI, Pydantic |
| Realtime    | WebSockets       |
| Database    | PostgreSQL       |
| AI/ML       | Hugging Face Transformers |
| Auth        | JWT              |

---

## 🚀 Getting Started

### 1. Clone the Repo
```
git clone https://github.com/yourusername/chatrealms.git
cd chatrealms
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```



# Future Features

**Intelligent AI Agents** with unique personalities and expertise
**Emotion-aware AI** using a fine-tuned Hugging Face model
RAG support with vector databases
Group-based permissions




