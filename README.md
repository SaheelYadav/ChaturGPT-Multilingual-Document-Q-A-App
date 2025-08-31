# Chatur GPT – Multilingual Document Q&A App

📌 ChaturGPT

ChaturGPT is an AI-powered multilingual chatbot built to support Indian languages. It uses Sarvam API for language understanding and generation, making it lightweight, fast, and effective for real-world use cases.

🚀 Features

🌐 Multilingual Support – Chat seamlessly in Indian languages.

⚡ Lightweight & Fast – Optimized for low-latency responses.

🔒 Secure – Uses .env file for API key and config.

🛠 Easy to Run – Minimal setup required.

📖 Open Source – Contribute and make it better.

🗂 Project Structure
ChaturGPT/
│── app.py              # Main Flask app  
│── requirements.txt    # Python dependencies  
│── .env                # Environment variables (not shared in repo)  
│── README.md           # Project documentation  
│── static/             # Frontend assets (if any)  
│── templates/          # HTML templates (if any)  

⚙️ Setup Instructions

Clone the repository

1. **Clone the repository**
   ```bash
   git clone https://code.swecha.org/SaheelYadav06/chaturgpt.git
   cd chaturgpt


Create a virtual environment

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt


Configure environment variables
Create a .env file in the project root:

SARVAM_API_KEY=your_api_key_here


Run the app

python app.py

💡 Usage

Open browser and go to: http://127.0.0.1:5000

Start chatting in any supported language!

🤝 Contributing

Fork the repo

Create a new branch (feature/xyz)

Commit changes

Submit a Pull Request

📜 License

This project is open-source under the MIT License.

