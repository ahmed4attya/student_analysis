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

    # عرض الجداول
    col1, col2 = st.columns(2)
    with col1:
        st.write("### عدد الطلاب الحاصلين على تقدير معين")
        st.write(summary_table)
    with col2:
        st.write("### نسبة الطلاب الحاصلين على تقدير معين")
        st.write(percentage_table)

    st.write("### الطلاب الحاصلين على تقدير غير مجتاز")
    st.write(non_passed_students)

    # رسم بياني باستخدام Plotly - عدد الطلاب لكل تقدير حسب المادة
    fig1 = go.Figure()
    for column in summary_table.columns:
        fig1.add_trace(go.Bar(
            x=summary_table.index,
            y=summary_table[column],
            name=column
        ))

    fig1.update_layout(
        barmode='stack',
        title='عدد الطلاب لكل تقدير حسب المادة',
        xaxis_title='المادة',
        yaxis_title='عدد الطلاب',
        xaxis_tickangle=-45
    )

    st.write("### رسم بياني حسب عدد الطلاب لكل مادة")
    st.plotly_chart(fig1)

    # رسم بياني باستخدام Plotly - نسبة الطلاب لكل تقدير حسب المادة
    fig2 = go.Figure()
    for column in percentage_table.columns:
        fig2.add_trace(go.Bar(
            x=percentage_table.index,
            y=percentage_table[column],
            name=column
        ))

    fig2.update_layout(
        barmode='stack',
        title='نسبة الطلاب لكل تقدير حسب المادة',
        xaxis_title='المادة',
        yaxis_title='نسبة الطلاب (%)',
        xaxis_tickangle=-45
    )

    st.write("### رسم بياني حسب نسبة الطلاب لكل مادة")
    st.plotly_chart(fig2)

    # رسم بياني دائري باستخدام Plotly - توزيع الطلاب حسب التقدير
    sizes_pie = summary_table.sum()
    labels_pie = summary_table.columns

    fig3 = go.Figure(data=[go.Pie(labels=labels_pie, values=sizes_pie, hole=.3)])
    fig3.update_layout(title='توزيع الطلاب حسب التقدير')

    st.write("### رسم بياني دائري لتوزيع الدرجات")
    st.plotly_chart(fig3)

    # تصدير التقرير إلى PDF
    st.write("### تصدير التقرير بصيغة PDF")
    
    if st.button("تصدير إلى PDF"):
        def fig_to_base64(fig):
            buf = io.BytesIO()
            fig.write_image(buf, format='png')
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode()

        # تحويل الرسوم البيانية إلى Base64
        bar_chart_image = fig_to_base64(fig1)
        percentage_chart_image = fig_to_base64(fig2)
        pie_chart_image = fig_to_base64(fig3)
        
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
        <h2>رسم بياني حسب عدد الطلاب لكل مادة</h2>
        <img src="data:image/png;base64,{bar_chart_image}" alt="Bar Chart">
        <h2>رسم بياني حسب نسبة الطلاب لكل مادة</h2>
        <img src="data:image/png;base64,{percentage_chart_image}" alt="Percentage Chart">
        <h2>رسم بياني دائري لتوزيع الدرجات</h2>
        <img src="data:image/png;base64,{pie_chart_image}" alt="Pie Chart">
        </body>
        </html>
        """
        
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdf_output = pdfkit.from_string(report_html, False, configuration=config)
        st.download_button("تحميل التقرير بصيغة PDF", pdf_output, "تقرير_الطلاب.pdf", mime="application/pdf")
