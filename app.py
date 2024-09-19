import pandas as pd
import streamlit as st
import pdfkit
import matplotlib.pyplot as plt
import io
import base64
from matplotlib import font_manager
from matplotlib import rcParams
import subprocess

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

    # تحديد مسار الخط العربي
    arabic_font_path = r'NotoNaskhArabic-VariableFont_wght.ttf'  # قم بتحديث هذا المسار إلى مسار الخط العربي الصحيح

    # إعداد الخطوط في matplotlib
    font_properties = font_manager.FontProperties(fname=arabic_font_path)
    rcParams['font.sans-serif'] = ['Amiri']  # استخدام الخط العربي لجميع النصوص
    rcParams['font.family'] = 'sans-serif'

    # رسم بياني بناءً على عدد الطلاب لكل تقدير
    st.write("### رسم بياني حسب عدد الطلاب لكل مادة")
    fig, ax = plt.subplots()
    summary_table.plot(kind='bar', stacked=True, ax=ax)
    plt.title('عدد الطلاب لكل تقدير حسب المادة', fontproperties=font_properties)
    plt.xlabel('المادة', fontproperties=font_properties)
    plt.ylabel('عدد الطلاب', fontproperties=font_properties)
    plt.xticks(rotation=45, ha='right', fontproperties=font_properties)
    plt.tight_layout()
    st.pyplot(fig)

    # رسم بياني بناءً على نسبة الطلاب لكل تقدير
    st.write("### رسم بياني حسب نسبة الطلاب لكل مادة")
    fig, ax = plt.subplots()
    percentage_table.plot(kind='bar', stacked=True, ax=ax)
    plt.title('نسبة الطلاب لكل تقدير حسب المادة', fontproperties=font_properties)
    plt.xlabel('المادة', fontproperties=font_properties)
    plt.ylabel('نسبة الطلاب (%)', fontproperties=font_properties)
    plt.xticks(rotation=45, ha='right', fontproperties=font_properties)
    plt.tight_layout()
    st.pyplot(fig)

    # رسم بياني دائري (ثنائي الأبعاد)
    st.write("### رسم بياني دائري لتوزيع الدرجات")
    fig, ax = plt.subplots()
    sizes_pie = summary_table.sum()  # مجموع الطلاب لكل تقدير
    labels_pie = summary_table.columns
    ax.pie(sizes_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90, textprops=dict(fontproperties=font_properties))
    plt.title('توزيع الطلاب حسب التقدير', fontproperties=font_properties)
    st.pyplot(fig)

    # تصدير التقرير إلى PDF
    st.write("### تصدير التقرير بصيغة PDF")
    
    if st.button("تصدير إلى PDF"):
        # تحويل الرسوم البيانية إلى صور Base64
        def fig_to_base64(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode()

        # تحويل الرسوم البيانية إلى Base64
        bar_chart_image = fig_to_base64(fig)
        pie_chart_image = fig_to_base64(fig)
        
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
        <img src="data:image/png;base64,{bar_chart_image}" alt="Bar Chart">
        <h2>رسم بياني حسب نسبة الطلاب لكل مادة</h2>
        <img src="data:image/png;base64,{bar_chart_image}" alt="Bar Chart">
        <h2>رسم بياني دائري لتوزيع الدرجات</h2>
        <img src="data:image/png;base64,{pie_chart_image}" alt="Pie Chart">
        </body>
        </html>
        """
        
        # إعداد مسار ملف wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        
        # إنشاء PDF من HTML
        pdf_output = pdfkit.from_string(report_html, False, configuration=config)
        
        # تقديم ملف PDF للتنزيل
        st.download_button("تحميل التقرير بصيغة PDF", pdf_output, "تقرير_الطلاب.pdf", mime="application/pdf")
