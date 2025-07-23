farmer-assistant-mvp/
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py
├── utils/
│   ├── __init__.py
│   ├── gemini_client.py
│   └── firestore_client.py
├── agents/
│   ├── __init__.py
│   ├── manager.py
│   └── disease_detection.py
├── cloud_functions/
│   └── main.py
├── webapp/
│   ├── app.py
│   ├── static/
│   │   ├── style.css
│   │   └── app.js
│   └── templates/
│       └── index.html
└── tests/
    └── test_basic.py