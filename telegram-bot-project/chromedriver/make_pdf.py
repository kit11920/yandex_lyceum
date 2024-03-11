import img2pdf

a4_page_size = [img2pdf.in_to_pt(8.3), img2pdf.in_to_pt(11.7)]
layout_function = img2pdf.get_layout_fun(a4_page_size)

pdf = img2pdf.convert(['data\\manga\\berserk-26-240\\berserk-26-242\\page-2.bmp',
                       'data\\manga\\berserk-26-240\\berserk-26-242\\page-3.bmp'], layout_fun=layout_function)
with open('data/pdf.pdf', 'wb') as f:
     f.write(pdf)














# # инфа отсюда https://python-scripts.com/create-pdf-pyfpdf
# from fpdf import FPDF
#
#
# def add_image(image_path):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.image(image_path, x=10, y=8, w=180)
#     pdf.set_font("Arial", size=12)
#     pdf.ln(85)  # ниже на 85
#     pdf.cell(200, 10, txt="{}".format(image_path), ln=1)
#     pdf.output("data/manga_pdf/add_image.pdf")
#
#
# if __name__ == '__main__':
#     add_image('data/manga/page-1.bmp')