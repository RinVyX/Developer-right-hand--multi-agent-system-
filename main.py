from database.neo4j_connector import Neo4jConnector
from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.documentation import DocumentationAgent
import time

MAX_ATTEMPTS = 3

def run_workflow(prompt):
    print("🚀 Starting multi-agent workflow...")
    
    # Initialize database
    # db = Neo4jConnector("bolt://localhost:7687", "neo4j", "inf8790equipe1")
    db = Neo4jConnector("bolt://127.0.0.1:7687", "neo4j", "inf8790equipe1")

    try:
        # Create agents 
        planner = PlannerAgent(db)
        coder = CoderAgent(db)
        tester = TesterAgent(db)
        doc_writer = DocumentationAgent(db)
        
        # 1. Create task and initial input
        task_id, input_artifact_id = db.create_task(prompt)
        print(f"\n📌 Task ID: {task_id}")
        print(f"💡 User request: {prompt[:100]}...")
        
        # 2. Planner creates subtasks
        print("\n🧠 Running PlannerAgent...")
        start_time = time.time()
        plan_result = planner.create_plan(input_artifact_id, prompt)
        print(f"⏱️ Planner took {time.time()-start_time:.1f}s")
        print("📋 Generated subtasks:")
        print(plan_result["content"])
        
        # 3. Coder-Tester loop
        final_code = None
        for attempt in range(MAX_ATTEMPTS):
            print(f"\n🔄 Attempt {attempt+1}/{MAX_ATTEMPTS}")
            
            # Generate code
            print("💻 Running CoderAgent...")
            start_time = time.time()
            code_result = coder.generate_code(
                plan_result["artifact_id"], 
                plan_result["content"],
                attempt
            )
            print(f"⏱️ Coding took {time.time()-start_time:.1f}s")
            
            # Test code
            print("🔍 Running TesterAgent...")
            start_time = time.time()
            test_result = tester.test_code(
                code_result["artifact_id"],
                code_result["content"],
                prompt
            )
            print(f"⏱️ Testing took {time.time()-start_time:.1f}s")
            
            print(f"✅ Test verdict: {test_result['verdict']}")
            if test_result["error"]:
                print("❌ Error output:")
                print(test_result["error"][:500] + "...")
            else:
                print("📤 Execution output:")
                print(test_result["output"][:500] + ("..." if len(test_result["output"]) > 500 else ""))
            
            if test_result["verdict"] == "APPROVED":
                final_code = code_result["content"]
                break
            elif test_result["verdict"] == "MINOR_ISSUES" and attempt == MAX_ATTEMPTS-1:
                final_code = code_result["content"]
        
        if not final_code:
            final_code = code_result["content"]
            print("⚠️ Using final code despite issues")
        
        # 4. Documentation
        print("\n📝 Running DocumentationAgent...")
        start_time = time.time()
        doc_result = doc_writer.create_docs(
            test_result["artifact_id"],
            final_code
        )
        print(f"⏱️ Documentation took {time.time()-start_time:.1f}s")
        
        return {
            "task_id": task_id,
            "code": final_code,
            "documentation": doc_result["content"],
            "execution_output": test_result.get("output", ""),
            "execution_error": test_result.get("error", "")
        }
    
    finally:
        db.close()

if __name__ == "__main__":
    print("="*50)
    print("Multi-Agent Code Generation System")
    print("="*50)
    
    prompt = input("\nEnter your coding request (e.g., 'Process CSV to calculate stats'): ")
    
    result = run_workflow(prompt)
    
    print("\n" + "="*50)
    print("🎉 WORKFLOW COMPLETE")
    print("="*50)
    print(f"\n📦 Task ID: {result['task_id']}")
    
    print("\n💻 FINAL CODE:")
    print(result["code"])
    
    print("\n📚 DOCUMENTATION:")
    print(result["documentation"])
    
    if result["execution_error"]:
        print("\n❌ EXECUTION ERROR:")
        print(result["execution_error"][:1000])
    elif result["execution_output"]:
        print("\n✅ EXECUTION OUTPUT:")
        print(result["execution_output"])
    
    print("\n🔗 View complete history in Neo4j at http://localhost:7474")
    print("Query: MATCH path=(t:Task {task_id: '" + result["task_id"] + "'})-[:HAS_ARTIFACT|PROCESSED_BY*]->(a) RETURN path")