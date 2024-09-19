import weasyprint
import base64
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
    total_score = df['الدرجة'].sum()
    num_students = len(df)
    mean_score = df['الدرجة'].mean()
    max_score = df['الدرجة'].max()
    min_score = df['الدرجة'].min()
    mode_score = df['الدرجة'].mode().values[0]
    
    # حساب النسب
    passed_students = len(df[df['التقدير'] != 'غير مجتاز'])
    failed_students = len(df[df['التقدير'] == 'غير مجتاز'])
    pass_percentage = (passed_students / num_students) * 100
    fail_percentage = (failed_students / num_students) * 100
    
    # إنشاء جدول إحصائي
    analysis_stats = pd.DataFrame({
        'الإحصائية': ['مجموع الدرجات', 'عدد الطلبة', 'المتوسط الحسابي', 'أعلى درجة', 'أقل درجة', 'الأكثر تكراراً', 'الوسيط', 'نسبة التفوق', 'نسبة الضعف'],
        'القيمة': [total_score, num_students, mean_score, max_score, min_score, mode_score, mean_score, f'{pass_percentage:.2f}%', f'{fail_percentage:.2f}%']
    })

    # رسم بياني ثلاثي الأبعاد حسب عدد الطلاب لكل مادة
    st.write("### رسم بياني ثلاثي الأبعاد حسب عدد الطلاب لكل مادة")

    # فلتر لاختيار المادة
    subject_filter = st.selectbox('اختر المادة', df['المادة'].unique())
    filtered_df = df[df['المادة'] == subject_filter]

    if not filtered_df.empty:
        fig = go.Figure()
        for grade_label in labels:
            grade_df = filtered_df[filtered_df['التقدير'] == grade_label]
            fig.add_trace(go.Bar(
                x=grade_df['المادة'],
                y=grade_df['الدرجة'],
                name=grade_label,
                marker_color={
                    'غير مجتاز': 'red',
                    'متمكن': 'purple',
                    'متقدم': 'green',
                    'متفوق': 'blue'
                }[grade_label]
            ))
        
        fig.update_layout(
            title=f'توزيع الدرجات للمادة: {subject_filter}',
            xaxis_title='المادة',
            yaxis_title='عدد الطلاب',
            barmode='stack'
        )

        st.plotly_chart(fig, use_container_width=True)

    # تحويل الرسوم البيانية إلى HTML
    bar_chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
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
    <h2>إحصائية التحليل</h2>
    {analysis_stats.to_html()}
    <h2>رسم بياني حسب عدد الطلاب لكل مادة</h2>
    {bar_chart_html}
    </body>
    </html>
    """

    # تحويل HTML إلى PDF باستخدام weasyprint
    try:
        pdf_file = '/tmp/report.pdf'
        weasyprint.HTML(string=report_html).write_pdf(pdf_file)

        # تحميل الملف PDF
        with open(pdf_file, 'rb') as f:
            PDFbyte = f.read()
            b64 = base64.b64encode(PDFbyte).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="report.pdf">تحميل التقرير بصيغة PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"حدث خطأ أثناء إنشاء ملف PDF: {e}")
