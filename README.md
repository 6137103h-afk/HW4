# Visual-Storytelling-STEAM-ESL-Study (N=80)
### A Study on the Impact of Visual Storytelling Teaching on Enhancing STEAM Education for ESL Kindergarten Learners
### Instructor: [Mia Wang](https://github.com/6137103h-afk)

## 📝 Project Overview
This repository contains the dataset and analysis for a quasi-experimental study investigating how visual storytelling–mediated instruction functions as a cognitive and pedagogical scaffold for ESL kindergarten learners in STEAM education.

Situated in Taiwan—within the context of the 2030 New Southbound Policy emphasizing internationalization and multicultural learning—this study addresses the dual challenge of subject complexity and language barriers faced by young ESL learners. A five-week study was conducted with 80 participants, divided into experimental and control groups.

The study evaluates the intervention’s impact on multiple dimensions, including STEAM knowledge acquisition, learning motivation, hands-on performance, engagement, and collaborative behaviors. Data were collected using standardized instruments (CELF-5), researcher-developed assessments, motivation scales (IMMS), performance rubrics (CPAM), and behavioral coding, and analyzed using ANCOVA, t-tests, effect sizes, and lag sequential analysis.

## 📊 Key Findings (Combined N=80)

### 1. Enhanced STEAM Learning Outcomes ($p < .001$)
* Cognitive Scaffolding: Learners in the visual storytelling group showed significant improvement in STEAM knowledge and task performance.
* So What? Visual storytelling reduces both language and conceptual complexity, helping young learners translate abstract STEAM concepts into concrete understanding.

### 2. TIncreased Learning Motivation and Engagement ($p < .01$)
* Affective Impact: The experimental group demonstrated significantly higher learning motivation and sustained engagement compared to the lecture-based group ($F = 6.82,\ p < .01,\ \eta^2 = .08$).
* So What? Narrative and visual elements create an immersive learning context that naturally maintains attention and interest.

### 3. Improved Hands-on Performance ($p < .01$)
* kill Development: Students receiving visual storytelling instruction performed significantly better in construction-based STEAM tasks ($t = 2.94,\ p < .01,\ d = 0.65$).
* So What? Multisensory input supports procedural understanding, enabling learners to more effectively translate knowledge into action.

---

## 🔬 Methodology & Statistics
* Participants: N = 80 ($n_{exp}=40, n_{ctrl}=40$)
* Design: Five-week quasi-experimental study comparing visual storytelling and lecture-based instruction
* Analysis: ANCOVA and independent samples t-tests
* Results: Significant differences were found in STEAM knowledge and learning motivation ($p < .05$)
* Reliability: Acceptable internal consistency across measures (Cronbach’s $\alpha$: 0.75–0.85)

## 📖 中文摘要
本研究採準實驗設計（N=80），探討視覺化故事教學對ESL幼兒STEAM學習成效之影響。核心發現如下：
1.  **學習效能提升**：視覺化故事教學顯著提升STEAM知識與實作表現，強化學習理解與應用能力。
2.  **降低學習障礙**：透過圖像與情境敘事，有效減少語言限制對概念理解的影響，提升學習可近性。
3.  **動機與投入提升**：故事化與多感官學習提升學習動機與專注力，促進持續參與。
4.  **實作能力強化**：多感官與建構式活動促進學生將知識轉化為實際操作能力。
5.  **教學模式價值**：研究結果提供多語言情境下STEAM教學設計之實證依據，具推廣應用潛力。
 
 -Visual storytelling significantly enhances ESL kindergarten learners’ STEAM learning by improving understanding, motivation, hands-on performance, and participation while reducing language barriers.
---

## 🛠️ Usage
Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

Optional (export Plotly figures to PNG in addition to HTML):

```bash
pip install -U kaleido
```

## Run

Place your Excel file in the repo root (default: `data_all.xlsx`) and run:

```bash
python analysis.py
```

## 📜 Reference
[Analysis Code](https://github.com/peculab/genai-psafety)# -
