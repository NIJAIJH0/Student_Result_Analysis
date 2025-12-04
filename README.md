# 📊 Student Result Processing Web App

This is a **Flask-based web application** that allows users to upload a CSV file or manually enter student marks, and then automatically generates:

✔ Student Total & Average  
✔ Pass/Fail Results  
✔ Interactive Table with Styling  
✔ Subject-wise Average Marks Chart  
✔ Downloadable Excel & PDF Reports  

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| CSV Upload | Upload student marks in `.csv` format |
| Manual Entry | Dynamically add student details and subject marks |
| Automatic Result Processing | Calculates Total, Average & Pass/Fail status |
| Data Visualization | Bar chart of average marks by subject |
| Export Options | Download results as **Excel** or **PDF** |
| UUID File Management | Prevents file overwrite issues |

---

## 🛠️ Technologies Used

- Python
- Flask
- Pandas
- Matplotlib
- ReportLab
- HTML / CSS
- Bootstrap *(optional if used)*

---

## 📂 Project Structure

student_result_dashboard/
│── app.py
│── templates/
│ ├── index.html
│ ├── result.html
│── static/
│── uploads/
│── requirements.txt
│── README.md

yaml
Copy code

---

## 📥 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2️⃣ Create a virtual environment
bash
Copy code
python -m venv env
Activate the environment:

Windows:

bash
Copy code
env\Scripts\activate
Mac/Linux:

bash
Copy code
source env/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
▶️ Run the App
bash
Copy code
python app.py
Open in your browser:
👉 http://127.0.0.1:5000/

📊 Input CSV Format
Name	Math	Science	English
John	78	82	90
Emma	55	60	58
Liam	35	38	40

⚠️ First column must be Name.

📄 Output Includes
✔ Student result table
✔ Highest scoring student (Topper)
✔ Class average performance
✔ Pass % statistics
✔ Subject-wise average chart
✔ Excel export
✔ PDF report export with chart

🏆 Future Improvements
Authentication system

Database storage (SQLite/MySQL)

Additional charts & analytics

Fully mobile responsive design

🙌 Contributing
Contributions are welcome!
For major changes, please open an issue first to discuss what you would like to improve.
