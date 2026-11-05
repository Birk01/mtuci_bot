from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas("pdfs/test.pdf", pagesize=A4)
c.setFont("Helvetica-Bold", 18)
c.drawString(100, 750, "Правила проживания в общежитии МТУСИ")

c.setFont("Helvetica-Bold", 14)
c.drawString(100, 700, "Глава 1. Общие положения")
c.setFont("Helvetica", 12)
c.drawString(100, 670, "1.1. Правила регулируют порядок проживания студентов.")
c.drawString(100, 650, "1.2. Тишина с 23:00 до 7:00.")

c.setFont("Helvetica-Bold", 14)
c.drawString(100, 600, "Глава 2. Стипендия")
c.setFont("Helvetica", 12)
c.drawString(100, 570, "2.1. Стипендия выплачивается ежемесячно.")
c.drawString(100, 550, "2.2. Размер: 2000 рублей.")
c.drawString(100, 530, "2.3. Повышенная: 3500 рублей за отличную учёбу.")

c.setFont("Helvetica-Bold", 14)
c.drawString(100, 480, "Глава 3. Выселение")
c.setFont("Helvetica", 12)
c.drawString(100, 450, "3.1. При отчислении из университета.")
c.drawString(100, 430, "3.2. При нарушении правил.")

c.save()
print("✅ Тестовый PDF создан: pdfs/test.pdf")