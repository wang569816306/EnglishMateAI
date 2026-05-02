"""
初始化推荐问题数据
"""
from app.core.database import SessionLocal
from app.models.user import SuggestedQuestion

def init_suggested_questions():
    """初始化英语学习相关的推荐问题"""
    db = SessionLocal()
    
    try:
        # 清空现有数据
        db.query(SuggestedQuestion).delete()
        db.commit()
        print("已清空现有推荐问题数据")
        
        # 英语学习相关的推荐问题（中文）
        questions = [
            {"question": "英语零基础先学单词还是语法？", "category": "grammar", "sort_order": 1},
            {"question": "记单词总是忘，有没有高效方法？", "category": "vocabulary", "sort_order": 2},
            {"question": "不敢开口说英语，怎么克服心理障碍？", "category": "speaking", "sort_order": 3},
            {"question": "语法太杂看不懂，新手如何简易入门？", "category": "grammar", "sort_order": 4},
            {"question": "听力完全听不懂，怎么一步步练？", "category": "speaking", "sort_order": 5},
            {"question": "每天学多久英语？怎么合理安排时间？", "category": "grammar", "sort_order": 6},
            {"question": "零基础要不要报网课？自学能学好吗？", "category": "grammar", "sort_order": 7},
            {"question": "看美剧听英文歌能提升英语吗？", "category": "speaking", "sort_order": 8},
            {"question": "学英语坚持不下来，怎么养成习惯？", "category": "grammar", "sort_order": 9},
            {"question": "学会日常交流要多久？有进阶步骤吗？", "category": "speaking", "sort_order": 10},
        ]
        
        # 插入数据
        for q in questions:
            question = SuggestedQuestion(
                question=q["question"],
                category=q["category"],
                sort_order=q["sort_order"]
            )
            db.add(question)
        
        db.commit()
        print(f"✅ 成功初始化 {len(questions)} 条推荐问题")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化推荐问题失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_suggested_questions()
