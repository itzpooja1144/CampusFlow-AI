\# CampusFlow AI 🏫🤖



An AI-powered campus facility management and decision-support system that helps monitor occupancy, predict future demand, and identify overcrowding risks across campus facilities.



\## 📌 Project Overview



CampusFlow AI is designed to make campus facilities smarter and more efficient.



The system monitors current occupancy and uses Machine Learning to:



\* Predict future facility demand

\* Detect overcrowding risk

\* Monitor real-time occupancy

\* Provide facility-level analytics

\* Support better campus resource planning



\## 🚀 Key Features



\### 👥 Occupancy Monitoring



Track the current number of students/users in campus facilities such as:



\* Library

\* Canteen

\* Parking

\* Lab

\* Admin Office



\### 📈 Future Occupancy Prediction



A \*\*Linear Regression\*\* model is used to predict upcoming facility demand based on historical occupancy and flow data.



\### ⚠️ Overcrowding Risk Prediction



A \*\*Logistic Regression\*\* model classifies whether a facility is likely to become overcrowded.



\### 📊 Analytics Dashboard



The dashboard provides useful information about:



\* Current occupancy

\* Facility capacity

\* Occupancy percentage

\* Predicted demand

\* Crowd-risk status



\### 🎓 Student Check-in / Check-out



Students can check into and out of facilities, allowing the system to maintain updated occupancy information.



\### 🗄️ Database Management



CampusFlow AI uses a local database to manage:



\* Facilities

\* Occupancy records

\* Student sessions

\* Check-in / check-out information



\## 🤖 Machine Learning



\### 1. Linear Regression



\*\*Purpose:\*\* Future demand prediction



The model learns patterns from historical facility flow data and predicts the next expected demand/flow.



\### 2. Logistic Regression



\*\*Purpose:\*\* Overcrowding-risk classification



The model predicts whether the current facility condition represents a potential overcrowding situation.



\## 📂 Dataset



The project uses campus occupancy data along with the \*\*CalIt2 building people-count dataset\*\* for machine-learning experimentation.



Data preprocessing includes:



\* Data cleaning

\* Feature creation

\* Occupancy calculations

\* Flow calculations

\* Train/test preparation



\## 🛠️ Technologies Used



\* Python

\* Flask

\* HTML

\* CSS

\* JavaScript

\* SQLite

\* Pandas

\* NumPy

\* Scikit-learn

\* Linear Regression

\* Logistic Regression

\* Git \& GitHub



\## 📁 Project Structure



```text

CampusFlow-AI/

│

├── app.py

├── requirements.txt

├── add\_occupancy.py

├── seed\_data.py

├── seed\_students.py

├── setup\_database.py

│

├── data/

│   ├── calit2\_clean.csv

│   ├── calit2\_ml.csv

│   ├── calit2\_processed.csv

│   ├── campus\_occupancy.csv

│   └── logistic\_dataset.csv

│

├── ml/

│   ├── linear\_model.py

│   ├── linear\_model.pkl

│   ├── logistic\_model.py

│   ├── logistic\_model.pkl

│   ├── logistic\_predict.py

│   ├── predict.py

│   └── predict\_crowd\_risk.py

│

├── static/

│   ├── css/

│   └── images/

│

└── templates/

&#x20;   ├── index.html

&#x20;   ├── admin.html

&#x20;   ├── analytics.html

&#x20;   ├── checkin.html

&#x20;   ├── checkout.html

&#x20;   └── student.html

```



\## ⚙️ How to Run



\### 1. Clone the repository



```bash

git clone https://github.com/itzpooja1144/CampusFlow-AI.git

cd CampusFlow-AI

```



\### 2. Install dependencies



```bash

pip install -r requirements.txt

```



\### 3. Run the Flask application



```bash

python app.py

```



\### 4. Open in browser



```text

http://127.0.0.1:5000

```



\## 🎯 Project Objective



The main objective of CampusFlow AI is to provide an intelligent campus facility management system that can help institutions:



\* Reduce overcrowding

\* Improve facility utilization

\* Predict demand

\* Monitor student movement

\* Support resource planning

\* Make data-driven decisions



\## 🔮 Future Scope



Future improvements can include:



\* Real-time IoT sensor integration

\* QR-based student check-in

\* Mobile application

\* Live occupancy updates

\* Alternative facility recommendations

\* Best-time recommendations

\* What-if simulation

\* Advanced forecasting models

\* Cloud deployment

\* Admin alerts and notifications



\## 👩‍💻 Author



\*\*Pooja\*\*



B.Tech Artificial Intelligence \& Data Science



CampusFlow AI — Machine Learning Based Campus Decision Support System



