import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
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

    # إضافة جدول إحصائية التحليل بجانب جدول الطلاب الحاصلين على تقدير غير مجتاز
    col3, col4 = st.columns(2)

    # جدول للطلاب الحاصلين على تقدير غير مجتاز
    non_passed_students = df[df['التقدير'] == 'غير مجتاز']
    with col3:
        st.write("### الطلاب الحاصلين على تقدير غير مجتاز")
        st.write(non_passed_students)

    # جدول إحصائية التحليل
    with col4:
        st.write("### إحصائية التحليل")
        st.write("""
        | المؤشر           | القيمة       | المؤشر           | القيمة        |
        |------------------|--------------|------------------|---------------|
        | مجموع الدرجات     | 530          | الأكثر تكراراً   | 40            |
        | عدد الطلبة       | 14           | الوسيط           | 40            |
        | المتوسط الحسابي   | 37.86        | نسبة التفوق      | 78.57%        |
        | أعلى درجة        | 40           | نسبة الضعف       | 0.00%         |
        | أقل درجة         | 25           |                  |               |
        """)

    # رسم بياني بناءً على عدد الطلاب لكل تقدير باستخدام Plotly
    st.write("### رسم بياني ثلاثي الأبعاد حسب عدد الطلاب لكل مادة")
    fig_bar = go.Figure()

    for grade, color in zip(labels, ['red', 'purple', 'green', 'blue']):
        fig_bar.add_trace(go.Bar(
            x=summary_table.index,
            y=summary_table[grade],
            name=grade,
            marker_color=color
        ))

    fig_bar.update_layout(
        barmode='stack',
        title='عدد الطلاب لكل تقدير حسب المادة',
        scene=dict(
            xaxis_title='المادة',
            yaxis_title='عدد الطلاب',
            zaxis_title='التقدير'
        ),
        font=dict(family="Majllan", size=18),
        height=600
    )

    st.plotly_chart(fig_bar)

    # رسم بياني بناءً على نسبة الطلاب لكل تقدير باستخدام Plotly
    st.write("### رسم بياني ثلاثي الأبعاد حسب نسبة الطلاب لكل مادة")
    fig_percentage = go.Figure()

    for grade, color in zip(labels, ['red', 'purple', 'green', 'blue']):
        fig_percentage.add_trace(go.Bar(
            x=percentage_table.index,
            y=percentage_table[grade],
            name=grade,
            marker_color=color
        ))

    fig_percentage.update_layout(
        barmode='stack',
        title='نسبة الطلاب لكل تقدير حسب المادة',
        scene=dict(
            xaxis_title='المادة',
            yaxis_title='نسبة الطلاب (%)',
            zaxis_title='التقدير'
        ),
        font=dict(family="Majllan", size=18),
        height=600
    )

    st.plotly_chart(fig_percentage)

    # رسم بياني دائري لتوزيع الدرجات باستخدام Plotly
    st.write("### رسم بياني دائري لتوزيع الدرجات")
    fig_pie = px.pie(names=summary_table.columns, values=summary_table.sum(),
                     title='توزيع الطلاب حسب التقدير', color_discrete_sequence=['red', 'purple', 'green', 'blue'])
    fig_pie.update_traces(textfont_size=18, textposition='inside')
    st.plotly_chart(fig_pie)

    # إضافة خيار لاختيار المادة
    subject_selected = st.selectbox("اختر المادة لعرض الطلاب الضعاف:", df['المادة'].unique())

    # تحديد الحد الأدنى للدرجة لتصنيف الطالب كضعيف
    weak_grade_threshold = 50

    # استخراج الطلاب الضعاف في المادة المحددة
    weak_students = df[(df['المادة'] == subject_selected) & (df['الدرجة'] < weak_grade_threshold)]

    # عرض الطلاب الضعاف
    st.write(f"### الطلاب الضعاف في مادة {subject_selected}")
    st.write(weak_students[['اسم الطالب', 'الدرجة']])

    # تصدير التقرير إلى PDF
    st.write("### تصدير التقرير بصيغة PDF")

    if st.button("تصدير إلى PDF"):
        # تحويل الرسوم البيانية إلى HTML
        bar_chart_html = fig_bar.to_html(full_html=False, include_plotlyjs='cdn')
        pie_chart_html = fig_pie.to_html(full_html=False, include_plotlyjs='cdn')

        # تحويل التقرير إلى HTML لاستخدامه في التصدير
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
        {bar_chart_html}
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
