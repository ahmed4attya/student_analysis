import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import pdfkit
import io
import base64

# التحقق من مسار wkhtmltopdf
def check_wkhtmltopdf():
    try:
        result = subprocess.run(['which', 'wkhtmltopdf'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

# تحقق من مسار wkhtmltopdf
st.write("Path to wkhtmltopdf:", check_wkhtmltopdf())

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
    st.write("### عدد الطلاب الحاصلين على تقدير معين في كل مادة")
    
    labels = ['غير مجتاز', 'متمكن', 'متقدم', 'متفوق']
    bins = [0, 50, 65, 85, 100]
    
    # إجراء التحليل بناءً على الدرجات
    df['التقدير'] = pd.cut(df['الدرجة'], bins=bins, labels=labels, right=False)

    # عرض الجدول الذي يحتوي على عدد الطلاب لكل تقدير حسب كل مادة
    summary_table = df.groupby(['المادة', 'التقدير']).size().unstack(fill_value=0)
    
    # عرض الجدول الذي يحتوي على نسبة الطلاب لكل تقدير حسب كل مادة
    percentage_table = summary_table.div(summary_table.sum(axis=1), axis=0) * 100

    # عرض الجداول بجانب بعضهما البعض
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### جدول عدد الطلاب الحاصلين على تقدير معين")
        st.write(summary_table)
    
    with col2:
        st.write("### جدول نسبة الطلاب الحاصلين على تقدير معين")
        st.write(percentage_table)

    # جدول للطلاب الحاصلين على تقدير غير مجتاز
    non_passed_students = df[df['التقدير'] == 'غير مجتاز']
    st.write("### الطلاب الحاصلين على تقدير غير مجتاز")
    st.write(non_passed_students)

    # إحصائية التحليل
    stats = {
        'مجموع الدرجات': df['الدرجة'].sum(),
        'عدد الطلبة': len(df),
        'المتوسط الحسابي': df['الدرجة'].mean(),
        'أعلى درجة': df['الدرجة'].max(),
        'أقل درجة': df['الدرجة'].min(),
        'الأكثر تكراراً': df['الدرجة'].mode()[0],
        'الوسيط': df['الدرجة'].median(),
        'نسبة التفوق': (len(df[df['الدرجة'] > 40]) / len(df)) * 100,
        'نسبة الضعف': (len(df[df['الدرجة'] < 50]) / len(df)) * 100
    }
    stats_df = pd.DataFrame(stats, index=[0])

    # رسم بياني بناءً على عدد الطلاب لكل تقدير
    st.write("### رسم بياني حسب عدد الطلاب لكل مادة")
    fig_bar_chart = go.Figure()

    colors = ['red', 'purple', 'green', 'blue']
    
    for label, color in zip(labels, colors):
        fig_bar_chart.add_trace(go.Bar(
            x=summary_table.index,
            y=summary_table[label],
            name=label,
            marker=dict(color=color),
        ))
    
    fig_bar_chart.update_layout(
        title='عدد الطلاب لكل تقدير حسب المادة',
        xaxis_title='المادة',
        yaxis_title='عدد الطلاب',
        barmode='stack',
        font=dict(family="Majllan", size=14),
        scene=dict(camera=dict(eye=dict(x=1.25, y=1.25, z=0.5)))  # تحويل الأعمدة إلى 3D
    )
    st.plotly_chart(fig_bar_chart)

    # رسم بياني بناءً على نسبة الطلاب لكل تقدير
    st.write("### رسم بياني حسب نسبة الطلاب لكل مادة")
    fig_percentage_chart = go.Figure()

    for label, color in zip(labels, colors):
        fig_percentage_chart.add_trace(go.Bar(
            x=percentage_table.index,
            y=percentage_table[label],
            name=label,
            marker=dict(color=color),
        ))
    
    fig_percentage_chart.update_layout(
        title='نسبة الطلاب لكل تقدير حسب المادة',
        xaxis_title='المادة',
        yaxis_title='نسبة الطلاب (%)',
        barmode='stack',
        font=dict(family="Majllan", size=14),
        scene=dict(camera=dict(eye=dict(x=1.25, y=1.25, z=0.5)))  # تحويل الأعمدة إلى 3D
    )
    st.plotly_chart(fig_percentage_chart)

    # رسم بياني دائري (ثنائي الأبعاد)
    st.write("### رسم بياني دائري لتوزيع الدرجات")
    fig_pie_chart = go.Figure(data=[go.Pie(
        labels=labels,
        values=summary_table.sum(),
        hole=.3,
        marker=dict(colors=colors)
    )])
    fig_pie_chart.update_layout(
        title='توزيع الطلاب حسب التقدير',
        font=dict(family="Majllan", size=14)
    )
    st.plotly_chart(fig_pie_chart)

    # تصدير التقرير إلى PDF
    st.write("### تصدير التقرير بصيغة PDF")

    if st.button("تصدير إلى PDF"):
        # تحويل الرسوم البيانية إلى HTML
        bar_chart_html = fig_bar_chart.to_html(full_html=False, include_plotlyjs='cdn')
        percentage_chart_html = fig_percentage_chart.to_html(full_html=False, include_plotlyjs='cdn')
        pie_chart_html = fig_pie_chart.to_html(full_html=False, include_plotlyjs='cdn')

        # إنشاء التقرير HTML لتضمين الرسوم البيانية
        report_html = f"""
        <html>
        <head><meta charset="utf-8"></head>
        <body style="direction: rtl; font-family: 'Majllan';">
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
        {bar_chart_html}
        
        <h2>رسم بياني حسب نسبة الطلاب لكل مادة</h2>
        {percentage_chart_html}
        
        <h2>رسم بياني دائري لتوزيع الدرجات</h2>
        {pie_chart_html}
        
        </body>
        </html>
        """

        # إعداد مسار ملف wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

        # إنشاء PDF من HTML
        pdf_output = pdfkit.from_string(report_html, False, configuration=config)

        # تقديم ملف PDF للتنزيل
        st.download_button("تحميل التقرير بصيغة PDF", pdf_output, "تقرير_الطلاب.pdf", mime="application/pdf")
