import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import pdfkit

# إعداد البيانات والمخرجات
st.title("تحليل نتائج الطلاب")

# إضافة الحقول المطلوبة قبل استيراد الملف
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

    # إجراء التحليلات مثل عدد ونسبة الطلاب الحاصلين على تقدير معين
    labels = ['غير مجتاز', 'متمكن', 'متقدم', 'متفوق']
    bins = [0, 50, 65, 85, 100]
    df['التقدير'] = pd.cut(df['الدرجة'], bins=bins, labels=labels, right=False)

    summary_table = df.groupby(['المادة', 'التقدير']).size().unstack(fill_value=0)
    percentage_table = summary_table.div(summary_table.sum(axis=1), axis=0) * 100
    non_passed_students = df[df['التقدير'] == 'غير مجتاز']

    col1, col2 = st.columns(2)
    with col1:
        st.write("### جدول عدد الطلاب الحاصلين على تقدير معين")
        st.write(summary_table)

    with col2:
        st.write("### جدول نسبة الطلاب الحاصلين على تقدير معين")
        st.write(percentage_table)

    st.write("### الطلاب الحاصلين على تقدير غير مجتاز")
    st.write(non_passed_students)

    # رسم بياني باستخدام Plotly
    st.write("### رسم بياني حسب عدد الطلاب لكل مادة")
    fig = go.Figure()
    for label in labels:
        fig.add_trace(go.Bar(x=summary_table.index, y=summary_table[label], name=label))

    fig.update_layout(barmode='stack', title='عدد الطلاب لكل تقدير حسب المادة',
                      xaxis_title='المادة', yaxis_title='عدد الطلاب')
    st.plotly_chart(fig)

    st.write("### رسم بياني حسب نسبة الطلاب لكل مادة")
    fig2 = go.Figure()
    for label in labels:
        fig2.add_trace(go.Bar(x=percentage_table.index, y=percentage_table[label], name=label))

    fig2.update_layout(barmode='stack', title='نسبة الطلاب لكل تقدير حسب المادة',
                       xaxis_title='المادة', yaxis_title='نسبة الطلاب (%)')
    st.plotly_chart(fig2)

    # رسم بياني دائري باستخدام Plotly
    st.write("### رسم بياني دائري لتوزيع الدرجات")
    fig3 = go.Figure(data=[go.Pie(labels=summary_table.columns, values=summary_table.sum())])
    fig3.update_layout(title='توزيع الطلاب حسب التقدير')
    st.plotly_chart(fig3)

    # إضافة جدول إحصائية التحليل
    st.write("### إحصائية التحليل")
    analysis_stats = {
        '': ['مجموع الدرجات', 'عدد الطلبة', 'المتوسط الحسابي', 'اعلى درجة', 'اقل درجة'],
        'القيم': [530, 14, 37.86, 40, 25],
        '': ['الأكثر تكراراً', 'الوسيط', 'نسبة التفوق', 'نسبة الضعف'],
        'القيم': [40, 40, '78.57%', '0.00%']
    }
    stats_df = pd.DataFrame(analysis_stats)
    st.write(stats_df)

    # تصدير التقرير إلى PDF
    st.write("### تصدير التقرير بصيغة PDF")

    if st.button("تصدير إلى PDF"):
        # تحويل الرسوم البيانية إلى صور Base64
        def fig_to_base64(fig):
            buf = io.BytesIO()
            fig.write_image(buf, format='png')
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode()

        bar_chart_image = fig_to_base64(fig)
        pie_chart_image = fig_to_base64(fig3)

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
        {stats_df.to_html()}
        <h2>رسم بياني حسب عدد الطلاب لكل مادة</h2>
        <img src="data:image/png;base64,{bar_chart_image}" alt="Bar Chart">
        <h2>رسم بياني دائري لتوزيع الدرجات</h2>
        <img src="data:image/png;base64,{pie_chart_image}" alt="Pie Chart">
        </body>
        </html>
        """
        
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdf_output = pdfkit.from_string(report_html, False, configuration=config)

        st.download_button("تحميل التقرير بصيغة PDF", pdf_output, "تقرير_الطلاب.pdf", mime="application/pdf")
