from transformers import pipeline

class QueryRewriter:
    def __init__(self):
        self.generator = pipeline('text2text-generation', model='facebook/bart-large')
    
    def rewrite_query(self, original_query: str) -> list[str]:
        """生成多个改写后的查询"""
        prompts = [
            f"Rephrase: {original_query}",
            f"Generate a specific question: {original_query}",
            f"Make this more detailed: {original_query}"
        ]
        
        rewritten_queries = []
        for prompt in prompts:
            result = self.generator(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
            rewritten_queries.append(result)
            
        return [original_query] + rewritten_queries 