from neo4j import GraphDatabase

# CONNECTION
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "cloudpassword123")

def load_advanced_rules():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    print("☁️  Connecting to Cloud Logic Core...")

    # We run these as separate, independent transactions to ensure variables aren't needed across lines
    queries = [
        # 1. Clear old data
        "MATCH (n) DETACH DELETE n",

        # 2. Create Hazards
        "CREATE (:Hazard {keyword: 'fire', category: 'CRITICAL'})",
        "CREATE (:Hazard {keyword: 'smoke', category: 'HIGH'})",
        "CREATE (:Hazard {keyword: 'roof', category: 'SEVERE'})",
        "CREATE (:Hazard {keyword: 'collapse', category: 'CATASTROPHIC'})",
        "CREATE (:Hazard {keyword: 'spill', category: 'MODERATE'})",

        # 3. Create Protocols
        "CREATE (:Protocol {action: 'ACTIVATE_SPRINKLERS', code: 'RED-FIRE'})",
        "CREATE (:Protocol {action: 'EVACUATE_SECTOR', code: 'RED-EVAC'})",
        "CREATE (:Protocol {action: 'STRUCTURAL_LOCKDOWN', code: 'BLACK-COLLAPSE'})",
        "CREATE (:Protocol {action: 'DEPLOY_HAZMAT', code: 'AMBER-SPILL'})",

        # 4. Link Logic (MATCH by properties, don't assume variables)
        """
        MATCH (h:Hazard {keyword: 'fire'}), (p:Protocol {code: 'RED-FIRE'})
        MERGE (h)-[:TRIGGERS]->(p)
        """,
        """
        MATCH (h:Hazard {keyword: 'smoke'}), (p:Protocol {code: 'RED-EVAC'})
        MERGE (h)-[:TRIGGERS]->(p)
        """,
        """
        MATCH (h:Hazard {keyword: 'roof'}), (p:Protocol {code: 'BLACK-COLLAPSE'})
        MERGE (h)-[:TRIGGERS]->(p)
        """,
        """
        MATCH (h:Hazard {keyword: 'collapse'}), (p:Protocol {code: 'BLACK-COLLAPSE'})
        MERGE (h)-[:TRIGGERS]->(p)
        """,
        """
        MATCH (h:Hazard {keyword: 'spill'}), (p:Protocol {code: 'AMBER-SPILL'})
        MERGE (h)-[:TRIGGERS]->(p)
        """
    ]

    try:
        with driver.session() as session:
            for q in queries:
                # Run each query cleanly
                session.run(q)
        print("✅ Advanced Rules Ingested Successfully!")
        print("   (Roof/Collapse) now DEFINITELY links to (Structural Lockdown)")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    load_advanced_rules()