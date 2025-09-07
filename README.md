🤖 ChaturGPT – Multilingual Document Q&A App

ChaturGPT is an AI-powered multilingual chatbot designed to support Indian languages.
It uses Sarvam API for language understanding and generation, making it lightweight, fast, and perfect for real-world use cases.

🚀 Features

🌐 Multilingual Support – Chat seamlessly in Indian languages

⚡ Lightweight & Fast – Optimized for low-latency responses

🔒 Secure – Uses .env for API keys and config

🛠 Easy to Run – Minimal setup required

📖 Open Source – Contribute and improve the project

🗂 Project Structure
ChaturGPT/
│── app.py              # Main Flask app  
│── requirements.txt    # Python dependencies  
│── .env                # Environment variables (not committed)  
│── README.md           # Project documentation  
│── static/             # Frontend assets (if any)  
│── templates/          # HTML templates (if any)  

⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://code.swecha.org/SaheelYadav06/chaturgpt.git
cd chaturgpt

2️⃣ Create a Virtual Environment
python -m venv venv
# Activate the venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file in the root folder and add your API key:

SARVAM_API_KEY=your_api_key_here

5️⃣ Run the App
python app.py

💡 Usage

Open your browser and go to:
http://127.0.0.1:5000

Start chatting in any supported language! 🌐💬

🤝 Contributing

We welcome contributions!

Fork the repo

Create a new branch: git checkout -b feature/xyz

Make your changes and commit: git commit -m "Add feature xyz"

Push to your fork and submit a Pull Request

📜 License

This project is licensed under the MIT License.
