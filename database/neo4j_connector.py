from neo4j import GraphDatabase, basic_auth
import uuid
from datetime import datetime

class Neo4jConnector:
    def __init__(self, uri, user, password):
        try:
            print(f"🌐 Connecting to Neo4j at {uri} as {user}...")
            self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
            self._initialize_db()
            print("✅ Connected to Neo4j.")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise

    def _initialize_db(self):
        with self.driver.session() as session:
            session.execute_write(self._create_schema)

    @staticmethod
    def _create_schema(tx):
        tx.run("""
        MERGE (:Agent {name: 'planner', description: 'Creates initial plans'})
        MERGE (:Agent {name: 'coder', description: 'Writes code based on plans'})
        MERGE (:Agent {name: 'tester', description: 'Tests the code'})
        MERGE (:Agent {name: 'documentation', description: 'Creates documentation'})
        """)

    def log_operation(self, agent_name, input_artifact_id, output_content, output_type, execution_result=None, metadata=None):
        with self.driver.session() as session:
            return session.execute_write(
                self._log_operation,
                agent_name, input_artifact_id, output_content, output_type, execution_result, metadata
            )

    @staticmethod
    def _log_operation(tx, agent_name, input_artifact_id, output_content, output_type, execution_result, metadata):
        artifact_id = str(uuid.uuid4())
        result = tx.run("""
        MATCH (input:Artifact {artifact_id: $input_id})
        MATCH (agent:Agent {name: $agent_name})
        CREATE (output:Artifact {
            artifact_id: $artifact_id,
            content: $content,
            type: $type,
            timestamp: datetime(),
            version: 1,
            execution_result: $execution_result,
            metadata: $metadata
        })
        CREATE (input)-[:PROCESSED_BY]->(output)
        CREATE (output)-[:GENERATED_BY]->(agent)
        WITH output, input
        OPTIONAL MATCH (input)-[:NEXT_AGENT]->(next:Agent)
        FOREACH (_ IN CASE WHEN next IS NOT NULL THEN [1] ELSE [] END |
            CREATE (output)-[:NEXT_AGENT]->(next)
        )
        RETURN output.artifact_id AS artifact_id
        """,
        input_id=input_artifact_id,
        agent_name=agent_name,
        artifact_id=artifact_id,
        content=str(output_content)[:10000],
        type=output_type,
        execution_result=str(execution_result)[:1000] if execution_result else None,
        metadata=str(metadata) if metadata else None)
        return result.single()["artifact_id"]

    def create_task(self, prompt):
        with self.driver.session() as session:
            return session.execute_write(self._create_task, prompt)

    @staticmethod
    def _create_task(tx, prompt):
        task_id = str(uuid.uuid4())
        artifact_id = str(uuid.uuid4())
        tx.run("""
        CREATE (t:Task {
            task_id: $task_id,
            initial_prompt: $prompt,
            created_at: datetime()
        })
        CREATE (a:Artifact {
            artifact_id: $artifact_id,
            content: $prompt,
            type: 'input',
            timestamp: datetime(),
            version: 0
        })
        CREATE (t)-[:HAS_ARTIFACT]->(a)
        WITH a
        MATCH (agent:Agent {name: 'planner'})
        CREATE (a)-[:NEXT_AGENT]->(agent)
        """,
        task_id=task_id,
        prompt=prompt,
        artifact_id=artifact_id)
        return task_id, artifact_id

    def close(self):
        self.driver.close()
