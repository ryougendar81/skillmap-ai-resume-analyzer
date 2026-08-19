from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Analysis
from .utils import analyze_resume_with_ai, chatbot_response
import pdfplumber
import docx

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text


def extract_text_from_docx(file):
    document = docx.Document(file)
    text = "\n".join([para.text for para in document.paragraphs])
    return text


def landing_view(request):
    return render(request, "analyzer/landing.html")


def payment_view(request):
    return render(request, "analyzer/payment.html")


@login_required
def dashboard_view(request):
    result = None
    chat_history = request.session.get("chat_history", [])

    if request.method == "POST":

        if "clear_chat" in request.POST:
            request.session["chat_history"] = []
            return redirect("dashboard")

        if "chat_question" in request.POST:
            question = request.POST.get("chat_question")
            analysis_context = request.POST.get("analysis_context")

            last_analysis = Analysis.objects.filter(user=request.user).last()

            reply = chatbot_response(question, analysis_context)

            chat_history.append({
                "user": question,
                "ai": reply
            })

            request.session["chat_history"] = chat_history

            all_analyses = Analysis.objects.filter(user=request.user)
            total_analyses = all_analyses.count()

            highest_score = 0
            average_score = 0

            if total_analyses > 0:
                scores = [a.match_score for a in all_analyses]
                highest_score = max(scores)
                average_score = sum(scores) // len(scores)

            return render(request, "analyzer/dashboard.html", {
                "chat_history": chat_history,
                "result": last_analysis,
                "total_analyses": total_analyses,
                "highest_score": highest_score,
                "average_score": average_score
            })

        resume_text = request.POST.get("resume", "").strip()
        job = request.POST.get("job", "").strip()
        uploaded_file = request.FILES.get("resume_file")

        if not resume_text and uploaded_file:
            filename = uploaded_file.name.lower()

            if filename.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)

            elif filename.endswith(".docx"):
                resume_text = extract_text_from_docx(uploaded_file)

        if not resume_text:
            return render(request, "analyzer/dashboard.html", {
                "error": "Please paste resume text or upload a PDF/DOCX file."
            })

        ai_result = analyze_resume_with_ai(resume_text, job)

        analysis = Analysis.objects.create(
            user=request.user,
            resume_text=resume_text,
            job_description=job,
            match_score=ai_result["match_score"],
            matched_skills=", ".join(ai_result["matched_skills"]),
            missing_skills=", ".join(ai_result["missing_skills"]),
            recommendations=ai_result["recommendations"]
        )

        request.session["chat_history"] = []
        result = analysis

    all_analyses = Analysis.objects.filter(user=request.user)
    total_analyses = all_analyses.count()

    highest_score = 0
    average_score = 0

    if total_analyses > 0:
        scores = [a.match_score for a in all_analyses]
        highest_score = max(scores)
        average_score = sum(scores) // len(scores)

    return render(request, "analyzer/dashboard.html", {
    "result": result,
    "chat_history": chat_history,
    "total_analyses": total_analyses,
    "highest_score": highest_score,
    "average_score": average_score,
    "username": request.user.username
})


@login_required
def history_view(request):
    analyses = Analysis.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "analyzer/history.html", {
        "analyses": analyses
    })


@login_required
def detail_view(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)

    return render(request, "analyzer/detail.html", {
        "analysis": analysis
    })


@login_required
def delete_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    analysis.delete()
    return redirect("history")


@login_required
def download_pdf(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="resume_analysis_report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AI Resume Analysis Report", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"Match Score: {analysis.match_score}%", styles["Heading2"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Matched Skills:", styles["Heading3"]))
    story.append(Paragraph(analysis.matched_skills, styles["BodyText"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Missing Skills:", styles["Heading3"]))
    story.append(Paragraph(analysis.missing_skills, styles["BodyText"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Recommendations:", styles["Heading3"]))
    story.append(Paragraph(analysis.recommendations, styles["BodyText"]))

    doc.build(story)

    return response