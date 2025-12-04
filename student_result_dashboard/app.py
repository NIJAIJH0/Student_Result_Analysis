from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ✅ Use non-GUI backend to avoid Tkinter errors
import matplotlib.pyplot as plt
import os
import uuid
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ----------------- Folder Setup -----------------
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)


# ----------------- Helper: Plot Chart -----------------
def plot_subject_averages(df, save_path='static/subject_avg.png'):
    """
    Automatically detect subject columns and plot their averages.
    Excludes Name, Total, Average, and Result.
    """
    exclude_cols = {'Name', 'Total', 'Average', 'Result'}
    subjects = [col for col in df.columns if col not in exclude_cols]

    averages = df[subjects].mean()
    plt.figure(figsize=(6, 4))
    plt.bar(averages.index, averages.values, color='skyblue')
    plt.ylabel('Average Marks')
    plt.title('Average Marks by Subject')
    plt.tight_layout()
    plt.ylim(0, 100)
    plt.savefig(save_path)
    plt.close()


# ----------------- Home / Upload Page -----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# ----------------- CSV Upload Result -----------------
@app.route('/result', methods=['POST'])
def result():
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return "No file selected", 400

    # Read CSV
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()  # Remove extra spaces

    # Automatically detect subject columns (exclude Name)
    subject_cols = [col for col in df.columns if col.lower() != 'name']

    # Calculate totals and results
    df['Total'] = df[subject_cols].sum(axis=1)
    df['Average'] = df['Total'] / len(subject_cols)
    df['Result'] = df['Average'].apply(lambda x: 'Pass' if x >= 40 else 'Fail')

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Save chart and Excel
    chart_path = os.path.join('static', f'{file_id}_chart.png')
    plot_subject_averages(df, save_path=chart_path)

    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}_results.xlsx')
    df.to_excel(excel_path, index=False)

    # Style the result table
    styled_table = df.style.applymap(
        lambda x: 'color: green;' if x == 'Pass' else ('color: red;' if x == 'Fail' else '')
    ).set_table_attributes('class="table table-striped table-bordered"').to_html()

    # Compute stats
    topper = df.loc[df['Average'].idxmax(), 'Name']
    avg_score = round(df['Average'].mean(), 2)
    pass_percent = round((df['Result'].value_counts().get('Pass', 0) / len(df)) * 100, 2)

    return render_template(
        'result.html',
        table=styled_table,
        topper=topper,
        avg_score=avg_score,
        pass_percent=pass_percent,
        excel_file=os.path.basename(excel_path),
        chart_file=os.path.basename(chart_path)
    )


# ----------------- Manual Entry Result -----------------
@app.route('/manual_result', methods=['POST'])
def manual_result():
    names = request.form.getlist('name[]')

    # Dynamically detect subjects
    subject_keys = [key for key in request.form.keys() if key.endswith('[]') and key != 'name[]']
    subjects = [key.replace('[]', '') for key in subject_keys]

    data = {'Name': names}
    for subject in subjects:
        values = request.form.getlist(f'{subject}[]')
        data[subject.capitalize()] = [int(v) for v in values]

    df = pd.DataFrame(data)

    # Compute totals and results
    df['Total'] = df.iloc[:, 1:].sum(axis=1)
    df['Average'] = df['Total'] / (len(df.columns) - 1)
    df['Result'] = df['Average'].apply(lambda x: 'Pass' if x >= 40 else 'Fail')

    file_id = str(uuid.uuid4())

    # Save chart and Excel
    chart_path = os.path.join('static', f'{file_id}_chart.png')
    plot_subject_averages(df, save_path=chart_path)

    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}_results.xlsx')
    df.to_excel(excel_path, index=False)

    # Styled table
    styled_table = df.style.applymap(
        lambda x: 'color: green;' if x == 'Pass' else ('color: red;' if x == 'Fail' else '')
    ).set_table_attributes('class="table table-striped table-bordered"').to_html()

    # Compute stats
    topper = df.loc[df['Average'].idxmax(), 'Name']
    avg_score = round(df['Average'].mean(), 2)
    pass_percent = round((df['Result'].value_counts().get('Pass', 0) / len(df)) * 100, 2)

    return render_template(
        'result.html',
        table=styled_table,
        topper=topper,
        avg_score=avg_score,
        pass_percent=pass_percent,
        excel_file=os.path.basename(excel_path),
        chart_file=os.path.basename(chart_path)
    )


# ----------------- Excel Download -----------------
@app.route('/download_excel', methods=['POST'])
def download_excel():
    file_name = request.form.get('file_name')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True, download_name='student_results.xlsx')


# ----------------- PDF Download -----------------
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    file_name = request.form.get('file_name')
    chart_name = request.form.get('chart_name')

    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    chart_path = os.path.join('static', chart_name)

    if not os.path.exists(excel_path):
        return "File not found", 404

    df = pd.read_excel(excel_path)

    pdf_bytes = BytesIO()
    doc = SimpleDocTemplate(pdf_bytes, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("📊 Student Result Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Table content
    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data, hAlign='CENTER')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Add chart
    if os.path.exists(chart_path):
        elements.append(Paragraph("Average Marks by Subject", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Image(chart_path, width=400, height=300))

    doc.build(elements)
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, download_name='student_results.pdf', as_attachment=True)


# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(debug=True)
