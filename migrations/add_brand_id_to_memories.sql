-- Add brand_id column to memories table
ALTER TABLE memories
ADD COLUMN brand_id UUID REFERENCES brands(id);

-- Add index for better performance
CREATE INDEX idx_memories_brand_id ON memories(brand_id);

-- Comment to explain the column
COMMENT ON COLUMN memories.brand_id IS 'Optional reference to a specific brand this memory is associated with'; 