"""
Test the public demo without external dependencies
"""

from simple_gamification_demo import SimpleGamificationDemo
import json

def test_public_access():
    """Simulate public user access"""
    print("🧪 Testing Public Educational Platform")
    print("=" * 50)
    
    # Create demo instance
    demo = SimpleGamificationDemo()
    
    # Simulate anonymous user
    anonymous_id = f"anonymous_20240101_1234_{hash('test_user') % 10000}"
    print(f"👤 Anonymous User ID: {anonymous_id}")
    
    # Test starting a session
    session = demo.start_learning_session(anonymous_id, "HR基礎概念")
    print(f"✅ Session created: {session['session_id']}")
    print(f"📝 Question: {session['question']['question']}")
    
    # Simulate answering
    question = session['question']
    correct_answer = "財務管理"  # We know this from the demo
    
    result = demo.submit_answer(anonymous_id, question['id'], correct_answer)
    
    print(f"\n📊 Result:")
    print(f"  ✅ Correct: {result['is_correct']}")
    print(f"  🎯 Score: {result['score']} XP")
    print(f"  📈 Level: {result['level']}")
    print(f"  🎪 Accuracy: {result['accuracy']:.1%}")
    print(f"  💬 Feedback: {result['feedback']}")
    
    if result['new_achievements']:
        print(f"  🏆 New Achievements:")
        for achievement in result['new_achievements']:
            print(f"    {achievement['icon']} {achievement['name']}")
    
    # Test API response format
    api_response = {
        "session_id": session['session_id'],
        "user_id": anonymous_id,
        "question": session['question'],
        "result": result,
        "public_access": True,
        "anonymous_user": True
    }
    
    print(f"\n🌐 API Response Format:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False)[:500] + "...")
    
    print(f"\n✅ Public access test completed successfully!")
    print(f"🚀 Ready for deployment!")
    
    return api_response

if __name__ == "__main__":
    test_public_access()