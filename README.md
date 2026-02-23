# 📄 README.md

```markdown
# 🛒 AI-Enhanced Price Comparator

An intelligent multi-marketplace price comparison web application built using Flask, Web Scraping, and Machine Learning.

This system fetches real-time product prices from multiple e-commerce platforms and uses AI to predict missing prices when data is unavailable.

---

## 🚀 Features

- 🔍 Multi-marketplace price comparison
- ⚡ Concurrent scraping using ThreadPoolExecutor
- 🤖 AI-based missing price prediction (Polynomial Ridge Regression)
- 💾 Smart caching (15-minute expiry)
- 📊 Savings & percentage calculation
- 📈 Trending products API
- 🩺 Health monitoring endpoint
- 🌍 RESTful API architecture

---

## 🛠️ Technologies Used

- Python
- Flask
- BeautifulSoup (Web Scraping)
- Requests
- NumPy
- Scikit-learn (Ridge Regression)
- ThreadPoolExecutor
- Fake-UserAgent
- CORS

---

## 🏪 Supported Marketplaces

- Amazon
- eBay
- Walmart
- Target

---

## 🧠 AI Gap Filling System

If price data from any marketplace is unavailable:

1. The system collects available prices
2. Trains a Polynomial Ridge Regression model
3. Predicts missing price
4. Applies statistical fallback if insufficient data

This makes the system smarter than traditional price comparators.

---

## 📡 API Endpoints

### 🔹 1. Search Product
```

GET /api/search?q=product_name

```

Returns:
- Sorted price results
- Savings calculation
- AI prediction info
- Cached status

---

### 🔹 2. Trending Products
```

GET /api/trends

```

Returns trending product searches.

---

### 🔹 3. Health Check
```

GET /api/health

```

Returns:
- System status
- Model info
- Version

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```

git clone [https://github.com/yourusername/price-comparator.git](https://github.com/yourusername/price-comparator.git)
cd price-comparator

```

### 2️⃣ Create Virtual Environment (Recommended)

```

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

```

### 3️⃣ Install Dependencies

```

pip install -r requirements.txt

```

If requirements file not available, install manually:

```

pip install flask flask-cors requests beautifulsoup4 lxml numpy scikit-learn fake-useragent

```

---

## ▶️ Run Application

```

python app.py

```

Server will start at:

```

[http://localhost:5000](http://localhost:5000)

```

---

## 📂 Project Structure

```

price-comparator/
│
├── app.py
├── templates/
│   └── index.html
├── static/
├── README.md
└── requirements.txt

```

---

## 🔒 Caching Mechanism

- Results are cached for 15 minutes
- Reduces repeated scraping
- Improves response speed

---

## 📊 How It Works

1. User searches for a product
2. App scrapes multiple marketplaces concurrently
3. Extracts prices using multiple CSS selectors
4. Sorts prices (lowest first)
5. Calculates savings
6. Uses AI if data is missing
7. Returns structured JSON response

---

## ⚡ Performance Optimization

- Multi-threaded scraping
- Smart caching
- Synchronous Flask routing
- Lightweight ML model

---

## 📌 Version

Current Version: **2.1.0**

---

## 👨‍💻 Author

Muhammad Jahanzaib  
BS IT  

---

## 📜 License

This project is for educational and learning purposes.
```
