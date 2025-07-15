// Create LPRCache node constraints
CREATE CONSTRAINT lpr_cache_id IF NOT EXISTS
FOR (c:LPRCache)
REQUIRE c.id IS UNIQUE;

// Create indexes for faster querying
CREATE INDEX lpr_cache_patient_id IF NOT EXISTS
FOR (c:LPRCache)
ON (c.patient_id);

CREATE INDEX lpr_cache_timestamp IF NOT EXISTS
FOR (c:LPRCache)
ON (c.timestamp);

// Define relationship constraint
CREATE CONSTRAINT has_lpr_cache IF NOT EXISTS
FOR ()-[r:HAS_LPR_CACHE]->()
REQUIRE r.created_at IS NOT NULL;
