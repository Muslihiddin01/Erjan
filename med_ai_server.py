# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = """Ты - профессиональный медицинский ИИ-консультант клиники "ОЛИМП". Твоя задача:

1. Анализировать результаты лабораторных анализов пациента
2. Давать медицинские рекомендации на основе норм
3. Объяснять результаты простым языком
4. Отвечать на вопросы о здоровье, анализах, симптомах, подготовке к анализам

Нормы для взрослых:
- Гемоглобин: мужчины 130-170 г/л, женщины 120-150 г/л
- Лейкоциты: 4-9 × 10⁹/л
- Эритроциты: мужчины 4.0-5.5 × 10¹²/л, женщины 3.5-5.0 × 10¹²/л
- Тромбоциты: 150-400 × 10⁹/л
- Глюкоза: 3.9-6.1 ммоль/л
- Холестерин: до 5.2 ммоль/л

ВАЖНЫЕ ПРАВИЛА:
- Всегда добавляй дисклеймер: '⚠️ Данная информация носит ознакомительный характер и не заменяет консультацию врача.'
- Никогда не ставь диагноз
- Говори доброжелательно и профессионально
- Если показатели критические - рекомендуй срочно обратиться к врачу"""


@app.route("/ai/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    context = data.get("context", "")

    full_prompt = message
    if context:
        full_prompt = f"Контекст предыдущего разговора: {context}\n\nВопрос: {message}"

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-5-haiku",
            max_tokens=1200,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ]
        )

        return jsonify({
            "success": True,
            "response": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/ai/analyze", methods=["POST"])
def analyze():
    data = request.json
    patient_name = data.get("name", "Пациент")
    gender = data.get("gender", "мужской")
    age = data.get("age", "взрослый")
    
    results = {
        "hemoglobin": data.get("hemoglobin"),
        "leukocytes": data.get("leukocytes"),
        "erythrocytes": data.get("erythrocytes"),
        "platelets": data.get("platelets"),
        "sugar": data.get("sugar"),
        "cholesterol": data.get("cholesterol")
    }

    analysis_text = f"""
Пациент: {patient_name}
Пол: {gender}
Возраст: {age}

Результаты анализов:
"""

    for key, value in results.items():
        if value:
            analysis_text += f"- {key}: {value}\n"

    analysis_text += """
Проведи полный анализ этих показателей и дай:
1. Оценку каждого показателя (норма, повышен, понижен)
2. Общее заключение
3. Рекомендации по дальнейшим действиям
4. Советы по улучшению здоровья
"""

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-5-haiku",
            max_tokens=1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": analysis_text}
            ]
        )

        return jsonify({
            "success": True,
            "analysis": response.choices[0].message.content,
            "patient": patient_name
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    print("=" * 50)
    print("[OLIMP] AI Med Assistant")
    print("=" * 50)
    print("Server started at http://127.0.0.1:8000")
    print("Set ANTHROPIC_API_KEY if needed")
    print("=" * 50)
    app.run(host="127.0.0.1", port=8000, debug=True)
