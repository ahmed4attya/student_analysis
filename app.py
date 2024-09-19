import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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
    
    # إجراء التحليلات
    st.write("### عدد الطلاب الحاصلين على تقدير معين في كل مادة")
    
    labels = ['غير مجتاز', 'متمكن', 'متقدم', 'متفوق']
    bins = [0, 50, 65, 85, 100]
    
    df['التقدير'] = pd.cut(df['الدرجة'], bins=bins, labels=labels, right=False)
    
    summary_table = df.groupby(['المادة', 'التقدير']).size().unstack(fill_value=0)
    percentage_table = summary_table.div(summary_table.sum(axis=1), axis=0) * 100

    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### جدول عدد الطلاب الحاصلين على تقدير معين")
        st.write(summary_table)
    
    with col2:
        st.write("### جدول نسبة الطلاب الحاصلين على تقدير معين")
        st.write(percentage_table)

    non_passed_students = df[df['التقدير'] == 'غير مجتاز']
    st.write("### الطلاب الحاصلين على تقدير غير مجتاز")
    st.write(non_passed_students)
    
    # إنشاء رسم بياني ثلاثي الأبعاد
    st.write("### رسم بياني ثلاثي الأبعاد حسب عدد الطلاب لكل مادة")
    selected_subject = st.selectbox('اختر المادة لعرض الرسم البياني ثلاثي الأبعاد', summary_table.index)
    
    fig_3d = go.Figure()
    
    for grade_label in labels:
        fig_3d.add_trace(go.Bar(
            x=summary_table.columns,
            y=summary_table.loc[selected_subject],
            name=grade_label,
            marker_color={
                'غير مجتاز': 'red',
                'متمكن': 'purple',
                'متقدم': 'green',
                'متفوق': 'blue'
            }[grade_label]
        ))

    fig_3d.update_layout(
        barmode='stack',
        title=f'توزيع الطلاب حسب التقدير في مادة {selected_subject}',
        xaxis_title='الدرجة',
        yaxis_title='عدد الطلاب',
        scene=dict(
            zaxis_title='عدد الطلاب',
            xaxis_title='الدرجة',
            yaxis_title='المادة'
        )
    )
    st.plotly_chart(fig_3d)

    # رسم بياني دائري مع ألوان مخصصة
    st.write("### رسم بياني دائري لتوزيع الدرجات")
    fig_pie = go.Figure(data=[go.Pie(
        labels=labels,
        values=summary_table.sum(),
        marker=dict(
            colors=['red', 'purple', 'green', 'blue']  # الألوان المخصصة
        )
    )])

    fig_pie.update_layout(
        title='توزيع الطلاب حسب التقدير'
    )
    st.plotly_chart(fig_pie)
    
    # تحويل الرسوم البيانية إلى HTML
    def fig_to_html(fig):
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    # تحويل الرسوم البيانية إلى HTML
    bar_chart_html = fig_to_html(fig_3d)
    pie_chart_html = fig_to_html(fig_pie)
    
    # إنشاء التقرير بصيغة HTML
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
    <h2>رسم بياني ثلاثي الأبعاد حسب عدد الطلاب لكل مادة</h2>
    {bar_chart_html}
    <h2>رسم بياني دائري لتوزيع الدرجات</h2>
    {pie_chart_html}
    </body>
    </html>
    """

    # تصدير التقرير إلى PDF باستخدام WeasyPrint
    st.write("### تصدير التقرير بصيغة PDF")
    
    if st.button("تصدير إلى PDF"):
        from weasyprint import HTML
        pdf_output = HTML(string=report_html).write_pdf()
        st.download_button("تحميل التقرير بصيغة PDF", pdf_output, "تقرير_الطلاب.pdf", mime="application/pdf")
