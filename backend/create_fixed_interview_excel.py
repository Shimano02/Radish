#!/usr/bin/env python3
"""
Create comprehensive interview question Excel sheet with proper encoding and error handling
"""
import pandas as pd
from datetime import datetime
import os

def create_interview_excel():
    """YouTube動画分析に基づく面接官質問想定シートを作成（修正版）"""
    
    basic_questions = [
        {
            "Category": "自己紹介・基本情報",
            "Question": "まず、簡単に自己紹介をお願いします。お名前、年齢、現在の状況を教えてください。",
            "Purpose": "基本情報の確認、コミュニケーション能力の初期評価",
            "Expected_Answer": "名前、年齢、現在の職業・状況を明確に説明",
            "Evaluation_Points": "話し方の明確さ、情報整理能力、第一印象",
            "Follow_Up": "現在のお仕事について詳しく教えてください",
            "Notes": "緊張をほぐし、リラックスした雰囲気作りを心がける"
        },
        {
            "Category": "職歴・経験",
            "Question": "これまでの職歴について、具体的な業務内容と期間を教えてください。",
            "Purpose": "実務経験の深度、継続性、成長過程の確認",
            "Expected_Answer": "具体的な職種、業務内容、期間、成果を含む説明",
            "Evaluation_Points": "経験の具体性、成長実績、継続性",
            "Follow_Up": "その中で最も印象に残っている仕事は何ですか？",
            "Notes": "転職理由についても自然に聞き出す"
        },
        {
            "Category": "志望動機",
            "Question": "なぜ弊社を志望されたのですか？弊社について調べたことがあれば教えてください。",
            "Purpose": "企業研究の深度、志望度の真剣さ、価値観の適合性",
            "Expected_Answer": "具体的な企業研究結果、明確な志望理由、将来ビジョン",
            "Evaluation_Points": "事前準備、志望度の高さ、企業理解度",
            "Follow_Up": "弊社で実現したいことは何ですか？",
            "Notes": "表面的な回答の場合は深掘りが必要"
        },
        {
            "Category": "強み・スキル",
            "Question": "ご自身の強みや得意なことについて教えてください。具体的なエピソードがあれば併せてお聞かせください。",
            "Purpose": "自己分析能力、強みの活用方法、具体性の確認",
            "Expected_Answer": "明確な強みの説明、具体的なエピソード、業務への活用方法",
            "Evaluation_Points": "自己理解度、具体性、業務適用可能性",
            "Follow_Up": "その強みを弊社でどのように活かせると思いますか？",
            "Notes": "抽象的な回答の場合は具体例を求める"
        },
        {
            "Category": "弱み・改善点",
            "Question": "ご自身の弱みや改善したい点があれば教えてください。それに対してどのような取り組みをしていますか？",
            "Purpose": "自己認識能力、成長意欲、改善への取り組み姿勢",
            "Expected_Answer": "具体的な弱みの認識、改善への具体的な取り組み",
            "Evaluation_Points": "自己客観視能力、成長意欲、具体的行動力",
            "Follow_Up": "その改善のために具体的にどのような努力をしていますか？",
            "Notes": "弱みを強みに転換する視点があるかも確認"
        },
        {
            "Category": "チームワーク",
            "Question": "チームで働く際に大切にしていることや、これまでのチームワーク経験について教えてください。",
            "Purpose": "協調性、コミュニケーション能力、チーム貢献度",
            "Expected_Answer": "具体的なチーム経験、協調性の発揮方法、貢献実績",
            "Evaluation_Points": "協調性、リーダーシップ、コミュニケーション能力",
            "Follow_Up": "チーム内で意見が対立した時はどのように対処しますか？",
            "Notes": "具体的なエピソードを通じて協調性を確認"
        },
        {
            "Category": "問題解決能力",
            "Question": "これまでに直面した困難な状況や問題を、どのように解決したか具体例を教えてください。",
            "Purpose": "問題解決能力、論理的思考力、困難への対処法",
            "Expected_Answer": "具体的な問題状況、解決プロセス、結果と学び",
            "Evaluation_Points": "論理的思考、創意工夫、結果への責任感",
            "Follow_Up": "その経験から学んだことを今後どう活かしますか？",
            "Notes": "問題解決のプロセスを詳しく聞く"
        },
        {
            "Category": "学習意欲・成長志向",
            "Question": "新しいことを学ぶ際の取り組み方や、自己成長のために心がけていることを教えてください。",
            "Purpose": "学習能力、成長意欲、自己啓発への取り組み",
            "Expected_Answer": "具体的な学習方法、継続的な取り組み、成長実績",
            "Evaluation_Points": "学習意欲、継続性、自己啓発能力",
            "Follow_Up": "最近新しく学んだことや挑戦したことはありますか？",
            "Notes": "具体的な学習事例を確認"
        },
        {
            "Category": "ストレス管理",
            "Question": "仕事でストレスを感じる時はどのような時ですか？また、どのように対処していますか？",
            "Purpose": "ストレス耐性、自己管理能力、対処法の確認",
            "Expected_Answer": "ストレス要因の認識、具体的な対処法、予防策",
            "Evaluation_Points": "ストレス耐性、自己管理能力、対処法の妥当性",
            "Follow_Up": "プレッシャーの大きい状況での経験はありますか？",
            "Notes": "ストレス対処の具体性を確認"
        },
        {
            "Category": "将来ビジョン",
            "Question": "5年後、10年後のご自身のキャリアビジョンについて教えてください。",
            "Purpose": "キャリア意識、長期的視点、企業との適合性",
            "Expected_Answer": "具体的なキャリアプラン、成長目標、企業での貢献イメージ",
            "Evaluation_Points": "キャリア意識、計画性、企業との適合性",
            "Follow_Up": "そのビジョン実現のために今何をしていますか？",
            "Notes": "企業のキャリアパスとの整合性を確認"
        }
    ]
    
    evaluation_criteria = [
        {
            "Evaluation_Item": "コミュニケーション能力",
            "Description": "話し方の明確さ、聞く姿勢、相手への配慮",
            "Excellent": "明確で分かりやすい説明、適切な質問、良好な対話",
            "Good": "概ね明確な説明、基本的な対話能力",
            "Average": "説明に一部不明確な点、対話は可能",
            "Poor": "説明が不明確、対話に困難",
            "Weight": "20%"
        },
        {
            "Evaluation_Item": "職務経験・スキル",
            "Description": "業務経験の深度、スキルレベル、実績",
            "Excellent": "豊富な経験、高いスキル、優秀な実績",
            "Good": "十分な経験、適切なスキル、良好な実績",
            "Average": "基本的な経験、標準的なスキル",
            "Poor": "経験不足、スキル不足",
            "Weight": "25%"
        },
        {
            "Evaluation_Item": "志望動機・企業理解",
            "Description": "志望理由の明確さ、企業研究の深度",
            "Excellent": "明確で具体的な志望理由、深い企業理解",
            "Good": "適切な志望理由、基本的な企業理解",
            "Average": "一般的な志望理由、表面的な企業理解",
            "Poor": "不明確な志望理由、企業理解不足",
            "Weight": "15%"
        },
        {
            "Evaluation_Item": "人格・価値観",
            "Description": "人柄、価値観、企業文化との適合性",
            "Excellent": "優秀な人格、価値観が企業文化と高度に適合",
            "Good": "良好な人格、価値観が企業文化と適合",
            "Average": "標準的な人格、価値観に大きな問題なし",
            "Poor": "人格や価値観に問題、企業文化と不適合",
            "Weight": "15%"
        },
        {
            "Evaluation_Item": "チームワーク・協調性",
            "Description": "チーム内での協調性、他者との連携能力",
            "Excellent": "優秀な協調性、チームリーダーシップ",
            "Good": "良好な協調性、チーム貢献能力",
            "Average": "基本的な協調性、チーム参加可能",
            "Poor": "協調性に問題、チームワーク困難",
            "Weight": "10%"
        },
        {
            "Evaluation_Item": "問題解決能力",
            "Description": "論理的思考力、創意工夫、困難への対処",
            "Excellent": "優秀な問題解決能力、創造的思考",
            "Good": "適切な問題解決能力、論理的思考",
            "Average": "基本的な問題解決能力",
            "Poor": "問題解決能力不足",
            "Weight": "10%"
        },
        {
            "Evaluation_Item": "学習意欲・成長志向",
            "Description": "新しいことへの学習意欲、自己成長への取り組み",
            "Excellent": "強い学習意欲、継続的な自己成長",
            "Good": "適切な学習意欲、成長への取り組み",
            "Average": "基本的な学習意欲",
            "Poor": "学習意欲不足、成長志向なし",
            "Weight": "5%"
        }
    ]
    
    ng_words = [
        {
            "Category": "前職批判",
            "NG_Examples": "前の会社は最悪だった、上司が無能、同僚が使えない",
            "Risk_Level": "高",
            "Impact": "協調性・適応性に疑問、トラブルメーカーの可能性",
            "Alternative_Response": "前職での学びや成長、新しい環境での挑戦意欲"
        },
        {
            "Category": "条件面のみ重視",
            "NG_Examples": "給料が良いから、休みが多いから、楽そうだから",
            "Risk_Level": "中",
            "Impact": "仕事への意欲・責任感に疑問",
            "Alternative_Response": "業務内容への興味、企業理念への共感、成長機会"
        },
        {
            "Category": "責任転嫁",
            "NG_Examples": "○○のせいで失敗した、環境が悪かった、運が悪かった",
            "Risk_Level": "高",
            "Impact": "責任感の欠如、問題解決能力不足",
            "Alternative_Response": "自分の改善点、学んだこと、今後の対策"
        },
        {
            "Category": "準備不足",
            "NG_Examples": "特に調べていない、よく分からない、何でも大丈夫",
            "Risk_Level": "中",
            "Impact": "志望度の低さ、準備能力不足",
            "Alternative_Response": "具体的な企業研究、明確な志望理由、質問の準備"
        },
        {
            "Category": "協調性の欠如",
            "NG_Examples": "一人で仕事したい、チームは苦手、指示されるのは嫌",
            "Risk_Level": "高",
            "Impact": "チームワーク困難、組織適応性に問題",
            "Alternative_Response": "チーム貢献への意欲、協力的な姿勢、柔軟性"
        }
    ]
    
    interview_flow = [
        {
            "Stage": "導入",
            "Duration": "5分",
            "Objective": "緊張緩和、基本情報確認",
            "Key_Questions": "自己紹介、現在の状況",
            "Evaluation_Focus": "第一印象、コミュニケーション能力",
            "Notes": "リラックスした雰囲気作り、アイスブレイク"
        },
        {
            "Stage": "職歴・経験",
            "Duration": "10分",
            "Objective": "実務経験の確認、スキル評価",
            "Key_Questions": "職歴詳細、業務内容、実績",
            "Evaluation_Focus": "経験の深度、スキルレベル、継続性",
            "Notes": "具体的なエピソードを聞き出す"
        },
        {
            "Stage": "志望動機・企業理解",
            "Duration": "10分",
            "Objective": "志望度確認、企業適合性評価",
            "Key_Questions": "志望理由、企業研究、将来ビジョン",
            "Evaluation_Focus": "志望度、企業理解度、価値観適合性",
            "Notes": "表面的な回答の場合は深掘り"
        },
        {
            "Stage": "人格・適性確認",
            "Duration": "10分",
            "Objective": "人柄、価値観、適性の確認",
            "Key_Questions": "強み・弱み、チームワーク、価値観",
            "Evaluation_Focus": "人格、協調性、企業文化適合性",
            "Notes": "具体的なエピソードで人柄を確認"
        },
        {
            "Stage": "問題解決・成長志向",
            "Duration": "10分",
            "Objective": "問題解決能力、学習意欲の確認",
            "Key_Questions": "困難な経験、学習への取り組み、ストレス対処",
            "Evaluation_Focus": "問題解決能力、成長意欲、ストレス耐性",
            "Notes": "具体的な問題解決事例を聞く"
        },
        {
            "Stage": "質疑応答・クロージング",
            "Duration": "5分",
            "Objective": "候補者の質問対応、次のステップ説明",
            "Key_Questions": "候補者からの質問、今後の流れ",
            "Evaluation_Focus": "質問の質、関心度、理解度",
            "Notes": "候補者の関心度を最終確認"
        }
    ]
    
    overall_evaluation = [
        {
            "Overall_Rating": "S評価(即戦力)",
            "Score_Range": "40-50点",
            "Criteria": "全項目で優秀、即戦力として期待",
            "Hiring_Decision": "積極的に採用",
            "Assignment_Proposal": "重要なプロジェクトや責任あるポジション",
            "Training_Plan": "最小限の導入研修、早期の実務投入"
        },
        {
            "Overall_Rating": "A評価(優秀)",
            "Score_Range": "32-39点",
            "Criteria": "多くの項目で優秀、高い成長期待",
            "Hiring_Decision": "採用推奨",
            "Assignment_Proposal": "適性に応じた部署配属",
            "Training_Plan": "標準研修+専門スキル研修"
        },
        {
            "Overall_Rating": "B評価(標準)",
            "Score_Range": "24-31点",
            "Criteria": "基準を満たす、標準的な成長期待",
            "Hiring_Decision": "条件次第で採用",
            "Assignment_Proposal": "基本業務からスタート",
            "Training_Plan": "標準研修+フォローアップ"
        },
        {
            "Overall_Rating": "C評価(要検討)",
            "Score_Range": "16-23点",
            "Criteria": "一部基準を満たさない、要検討",
            "Hiring_Decision": "慎重に検討",
            "Assignment_Proposal": "サポート体制の整った部署",
            "Training_Plan": "長期研修+メンター制度"
        },
        {
            "Overall_Rating": "D評価(不適合)",
            "Score_Range": "8-15点",
            "Criteria": "基準を満たさない、採用困難",
            "Hiring_Decision": "不採用",
            "Assignment_Proposal": "-",
            "Training_Plan": "-"
        }
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Interview_Questions_Sheet_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            pd.DataFrame(basic_questions).to_excel(writer, sheet_name='BasicQuestions', index=False)
            pd.DataFrame(evaluation_criteria).to_excel(writer, sheet_name='EvaluationCriteria', index=False)
            pd.DataFrame(ng_words).to_excel(writer, sheet_name='NGWords', index=False)
            pd.DataFrame(interview_flow).to_excel(writer, sheet_name='InterviewFlow', index=False)
            pd.DataFrame(overall_evaluation).to_excel(writer, sheet_name='OverallEvaluation', index=False)
        
        if os.path.exists(filename):
            test_xl = pd.ExcelFile(filename)
            print(f"✅ 面接官質問想定シートを作成しました: {filename}")
            print(f"📊 含まれるシート: {test_xl.sheet_names}")
            print(f"  - BasicQuestions ({len(basic_questions)}問)")
            print(f"  - EvaluationCriteria ({len(evaluation_criteria)}項目)")
            print(f"  - NGWords ({len(ng_words)}カテゴリ)")
            print(f"  - InterviewFlow ({len(interview_flow)}段階)")
            print(f"  - OverallEvaluation ({len(overall_evaluation)}レベル)")
            return filename
        else:
            print(f"❌ File creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Excel creation error: {e}")
        return None

if __name__ == "__main__":
    create_interview_excel()
