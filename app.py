import pandas as pd
import streamlit as st
import pdfkit
import plotly.graph_objects as go
import io
import base64
import subprocess

# التحقق من وجود wkhtmltopdf
def check_wkhtmltopdf():
    try:
        result = subprocess.run(['which', 'wkhtmltopdf'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

st.write("Path to wkhtmltopdf:", check_wkhtmltopdf())

# إعداد البيانات والمخرجات
st.title("تحليل نتائج الطلاب")

# إضافة الحقول المطلوبة
school_name = st.text_input("اسم المدرسة")
academic_year = st.text_input("العام الدراسي")
report_type = st.text_input("نوع التقرير")
grade = st.text_input("الصف")
class_section = st.text_input("الفصل")
period = st.text_input("الفترة")

# استيراد ملف CSV
uploaded_file = st.file_uploader("تحميل ملف CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # تقسيم الطلاب حسب الدرجات
    labels = ['غير مجتاز', 'متمكن', 'متقدم', 'متفوق']
    bins = [0, 50, 65, 85, 100]
    df['التقدير'] = pd.cut(df['الدرجة'], bins=bins, labels=labels, right=False)

    # جداول التحليل
    summary_table = df.groupby(['المادة', 'التقدير']).size().unstack(fill_value=0)
    percentage_table = summary_table.div(summary_table.sum(axis=1), axis=0) * 100
    non_passed_students = df[df['التقدير'] == 'غير مجتاز']

    # إضافة الجداول في التقرير
    col1, col2 = st.columns(2)
    with col1:
        st.write("### عدد الطلاب الحاصلين على تقدير معين")
        st.write(summary_table)
    with col2:
        st.write("### نسبة الطلاب الحاصلين على تقدير معين")
        st.write(percentage_table)

    st.write("### الطلاب الحاصلين على تقدير غير مجتاز")
    st.write(non_passed_students)

    # إحصائية التحليل - إنشاء جدول باستخدام Plotly
    analysis_data = {
        " ": ["مجموع الدرجات", "عدد الطلبة", "المتوسط الحسابي", "اعلى درجة", "اقل درجة"],
        "القيم": [530, 14, 37.86, 40, 25],
        " ": ["الأكثر تكراراً", "الوسيط", "نسبة التفوق", "نسبة الضعف", ""],
        "القيم": [40, 40, "78.57%", "0.00%", ""]
    }

    analysis_df = pd.DataFrame(analysis_data)
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=["", "القيم", "", "القيم"],
                    align='center',
                    fill_color='paleturquoise',
                    font=dict(color='black', size=14)),
        cells=dict(values=[analysis_df[" "], analysis_df["القيم"], analysis_df[" "], analysis_df["القيم"]],
                   align='center',
                   fill_color='lavender',
                   font=dict(color='black', size=12))
    )])

    st.write("### إحصائية التحليل")
    st.plotly_chart(fig)

    # تصدير التقرير إلى PDF
    st.write("### تصدير التقرير بصيغة PDF")
    
    if st.button("تصدير إلى PDF"):
        def fig_to_base64(fig):
            buf = io.BytesIO()
            fig.write_image(buf, format='png')
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode()

        # تحويل الجدول إلى صورة Base64
        table_image = fig_to_base64(fig)
        
        # تحويل التقرير إلى HTML
        report_html = f"""
        <html>
        <head><meta charset="utf-8"></head>
        <body style="direction: rtl;">
        <h1>تقرير نتائج الطلاب</h1>
        <p><strong>اسم المدرسة:</strong> {school_name}</p>
        <p><strong>العام الدراسي:</strong> {academic_year}</p>
        <p><strong>نوع التقرير:</strong> {report_type}</p>
        <p><strong>الصف:</strong> {grade}</p>
        <p><strong>الفصل:</strong> {class_section}</p>
        <p><strong>الفترة:</strong> {period}</p>
        <h2>عدد الطلاب الحاصلين على تقدير معين لكل مادة</h2>
        {summary_table.to_html()}
        <h2>نسبة الطلاب الحاصلين على تقدير معين لكل مادة</h2>
        {percentage_table.to_html()}
        <h2>الطلاب الحاصلين على تقدير غير مجتاز</h2>
        {non_passed_students.to_html()}
        <h2>إحصائية التحليل</h2>
        <img src="data:image/png;base64,{table_image}" alt="Analysis Table">
        </body>
        </html>
        """
        
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdf_output = pdfkit.from_string(report_html, False, configuration=config)
        st.download_button("تحميل التقرير بصيغة PDF", pdf_output, "تقرير_الطلاب.pdf", mime="application/pdf")
