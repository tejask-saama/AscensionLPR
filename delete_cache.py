import asyncio
from src.services.knowledge_graph import KnowledgeGraphService

async def delete_cache():
    kg_service = KnowledgeGraphService()
    await kg_service.initialize()
    
    try:
        # Delete the cache node for James Robertson
        query = """
        MATCH (c:LPRCache)
        WHERE c.patient_id = '992dbaa2-966e-426b-b78a-803828931d21'
        DETACH DELETE c
        """
        result = await kg_service.run_query(query)
        print("Cache deleted successfully")
    except Exception as e:
        print(f"Error deleting cache: {str(e)}")
    finally:
        await kg_service.close()

if __name__ == "__main__":
    asyncio.run(delete_cache())

# 'b452d3ec-ce76-424d-87cb-7849422dbf92' - James Robertson          done
# '29378b30-61c1-4e91-a731-443cabd4ae48' - Linda Chen               done
# '992dbaa2-966e-426b-b78a-803828931d21' - Robert Anderson          done
# 'a4a2eaf4-3e41-471c-aea5-89497add41d9' - John Doe                 done
# 'patient-1015' - Ian Russell                                      optional               