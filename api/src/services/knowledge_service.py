import numpy as np
import json
from models import db, KnowledgeBase, KnowledgeItem
from .llm_service import LLMService

class KnowledgeService:
    def __init__(self):
        self.llm_service = LLMService()
    
    def create_knowledge_base(self, name, organization_id, chatbot_id=None):
        """Create a new knowledge base"""
        knowledge_base = KnowledgeBase(
            name=name,
            organization_id=organization_id,
            chatbot_id=chatbot_id
        )
        
        db.session.add(knowledge_base)
        db.session.commit()
        
        return knowledge_base
    
    def add_knowledge_item(self, knowledge_base_id, question, answer):
        """Add a new item to knowledge base"""
        # Generate embedding for the question
        embedding = self._generate_embedding(question)
        
        knowledge_item = KnowledgeItem(
            knowledge_base_id=knowledge_base_id,
            question=question,
            answer=answer,
            embedding=embedding
        )
        
        db.session.add(knowledge_item)
        db.session.commit()
        
        return knowledge_item
    
    def bulk_import(self, knowledge_base_id, items):
        """Bulk import knowledge items"""
        for item in items:
            question = item.get('question')
            answer = item.get('answer')
            
            if question and answer:
                embedding = self._generate_embedding(question)
                
                knowledge_item = KnowledgeItem(
                    knowledge_base_id=knowledge_base_id,
                    question=question,
                    answer=answer,
                    embedding=embedding
                )
                
                db.session.add(knowledge_item)
        
        db.session.commit()
    
    def search_knowledge_base(self, knowledge_base_id, query, threshold=0.7):
        """Search knowledge base for relevant items"""
        # Generate embedding for the query
        query_embedding = self._generate_embedding(query)
        
        # Get knowledge items
        items = KnowledgeItem.query.filter_by(knowledge_base_id=knowledge_base_id).all()
        
        if not items:
            return []
        
        # Calculate similarity scores
        similarities = []
        for item in items:
            if item.embedding:
                item_embedding = item.embedding
                similarity = self._calculate_similarity(query_embedding, item_embedding)
                similarities.append((item, similarity))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return items above threshold
        results = [
            {
                'id': item.id,
                'question': item.question,
                'answer': item.answer,
                'similarity': score
            }
            for item, score in similarities if score >= threshold
        ]
        
        return results
    
    def _generate_embedding(self, text):
        """Generate embedding for text using OpenAI API"""
        try:
            # This is a simplified version. In a real implementation, 
            # you would use OpenAI's Embedding API or similar
            prompt = "Generate an embedding representation of the following text:\n\n" + text
            result = self.llm_service.get_completion(prompt)
            
            # For now, let's just return a simplified mock embedding
            # This would be replaced with actual embedding API calls
            # Generating a random vector for demonstration purposes
            return np.random.rand(384).tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def _calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between embeddings"""
        if not embedding1 or not embedding2:
            return 0
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def get_knowledge_base(self, knowledge_base_id):
        """Get knowledge base by ID"""
        return KnowledgeBase.query.get(knowledge_base_id)
    
    def get_knowledge_bases(self, organization_id, chatbot_id=None):
        """Get knowledge bases for organization"""
        query = KnowledgeBase.query.filter_by(organization_id=organization_id)
        
        if chatbot_id:
            query = query.filter_by(chatbot_id=chatbot_id)
        
        return query.all()
    
    def get_knowledge_items(self, knowledge_base_id):
        """Get all items in a knowledge base"""
        return KnowledgeItem.query.filter_by(knowledge_base_id=knowledge_base_id).all()
    
    def update_knowledge_base(self, knowledge_base_id, name=None, chatbot_id=None):
        """Update knowledge base"""
        knowledge_base = KnowledgeBase.query.get(knowledge_base_id)
        
        if not knowledge_base:
            return None
        
        if name:
            knowledge_base.name = name
        
        if chatbot_id is not None:
            knowledge_base.chatbot_id = chatbot_id
        
        db.session.commit()
        
        return knowledge_base
    
    def update_knowledge_item(self, item_id, question=None, answer=None):
        """Update knowledge item"""
        item = KnowledgeItem.query.get(item_id)
        
        if not item:
            return None
        
        if question:
            item.question = question
            # Update embedding when question changes
            item.embedding = self._generate_embedding(question)
        
        if answer:
            item.answer = answer
        
        db.session.commit()
        
        return item
    
    def delete_knowledge_base(self, knowledge_base_id):
        """Delete knowledge base"""
        knowledge_base = KnowledgeBase.query.get(knowledge_base_id)
        
        if not knowledge_base:
            return False
        
        db.session.delete(knowledge_base)
        db.session.commit()
        
        return True
    
    def delete_knowledge_item(self, item_id):
        """Delete knowledge item"""
        item = KnowledgeItem.query.get(item_id)
        
        if not item:
            return False
        
        db.session.delete(item)
        db.session.commit()
        
        return True
