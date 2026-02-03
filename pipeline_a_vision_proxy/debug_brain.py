from neo4j import GraphDatabase

# Connection details
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "cloudpassword123")

def diagnose():
    print("🩺 STARTING BRAIN DIAGNOSTIC...")
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        with driver.session() as session:
            # CHECK 1: List all Hazards
            result = session.run("MATCH (h:Hazard) RETURN h.keyword AS key")
            keywords = [r['key'] for r in result]
            print(f"   📂 Database contains {len(keywords)} Keywords: {keywords}")

            if not keywords:
                print("   ❌ ERROR: Database is EMPTY! Rerun init_cloud_rules.py")
                return

            # CHECK 2: Test the Query Logic
            test_phrase = "significant roof damage detected"
            print(f"   🧪 Testing phrase: '{test_phrase}'")

            query = """
            MATCH (h:Hazard)-[:TRIGGERS]->(p:Protocol)
            WHERE $text CONTAINS toLower(h.keyword)
            RETURN h.keyword as match, p.action as action
            """

            test = session.run(query, text=test_phrase).data()
            if test:
                print(f"   ✅ SUCCESS! Logic works. Matches: {test}")
            else:
                print("   ⚠️ FAILURE. No match found (Check Case/Spelling).")

    except Exception as e:
        print(f"   🔥 CONNECTION ERROR: {e}")
        print("   (Did you stop the old Neo4j container from the previous project?)")

if __name__ == "__main__":
    diagnose()