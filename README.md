# SkillSwap AI ⚡
> **Next-Gen Peer-to-Peer AI Skill Exchange Platform**

![SkillSwap AI Platform Banner](https://raw.githubusercontent.com/Kandarp089/SkillSwap-AI-Platform/main/screenshots/banner.png)

## 🌐 Live Platform Demo
- 🚀 **Vercel Live Host**: [https://skillswap-black-two.vercel.app](https://skillswap-black-two.vercel.app)
- 📦 **GitHub Repository**: [https://github.com/Kandarp089/SkillSwap-AI-Platform](https://github.com/Kandarp089/SkillSwap-AI-Platform)

---

## ⚡ Key Features

- **🤖 AI Synergy Skill Matcher**: Dynamic compatibility scoring, preference calculation, and personalized match recommendations.
- **💬 Real-Time WebSockets Chat**: Built with Django Channels, Channels-Redis, and hybrid HTTP/AJAX fallback for instant peer messaging.
- **🔄 Complete Exchange Lifecycle**: Proposal creation, acceptance, rejection, cancellation, completion, automated **+150 XP** awards, and **+25 credit** transfers.
- **🏆 Gamification & Rewards**: Global mentor leaderboard, achievements showcase, and verified completion certificates with unique verification IDs.
- **🎨 Glassmorphism Dark Theme**: Modern UI crafted with Outfit + Plus Jakarta Sans typography, vibrant neon gradients (`#8b5cf6`, `#06b6d4`), and glowing glass cards.
- **☁️ Production Ready**: Pre-configured with Render Infrastructure Blueprint (`render.yaml`) for Gunicorn + UvicornWorker ASGI server, PostgreSQL database, and Redis.

---

## 🔑 1-Click Demo Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Demo Learner** | `demo_user` | `SkillSwap123!` |
| **Python Mentor** | `alex_chen` | `SkillSwap123!` |
| **UI/UX Mentor** | `sarah_jenkins` | `SkillSwap123!` |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Django 4.2+, Django Channels, ASGI, WSGI
- **Database & Cache**: PostgreSQL, SQLite3, Redis Channel Layer
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
- **Production Server**: Gunicorn, UvicornWorker, WhiteNoise, Render Blueprint

---

## 🚀 Quick Local Installation

```bash
# Clone the repository
git clone https://github.com/Kandarp089/SkillSwap-AI-Platform.git
cd SkillSwap-AI-Platform/skillswap

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations and start dev server
python manage.py migrate
python manage.py runserver
```

---

## 👤 Author

**Kandarp Upadhyay**
- MCA Student | Django Full-Stack Architect
- GitHub: [@Kandarp089](https://github.com/Kandarp089)
