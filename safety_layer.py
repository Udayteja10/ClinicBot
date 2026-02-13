"""
Safety Layer - Emergency Detection and Response
Monitors user input for emergency situations and provides immediate guidance
"""

from medical_knowledge import check_emergency, EMERGENCY_RESPONSES

class SafetyLayer:
    """Monitors conversations for emergency situations"""
    
    def __init__(self):
        self.emergency_detected = False
        self.emergency_level = None
    
    def scan_message(self, message):
        """
        Scan a message for emergency keywords
        Returns: (is_emergency, emergency_level, response)
        """
        emergency_level = check_emergency(message)
        
        if emergency_level:
            self.emergency_detected = True
            self.emergency_level = emergency_level
            response = self._generate_emergency_response(emergency_level)
            return True, emergency_level, response
        
        return False, None, None
    
    def _generate_emergency_response(self, level):
        """Generate appropriate emergency response based on severity"""
        template = EMERGENCY_RESPONSES.get(level, EMERGENCY_RESPONSES['urgent'])
        
        response = f"{template['message']}\n\n"
        response += "IMMEDIATE ACTIONS:\n"
        for action in template['actions']:
            response += f"{action}\n"
        response += f"\n{template['additional']}"
        
        return response
    
    def reset(self):
        """Reset emergency state"""
        self.emergency_detected = False
        self.emergency_level = None
    
    def get_status(self):
        """Get current emergency status"""
        return {
            'emergency_detected': self.emergency_detected,
            'emergency_level': self.emergency_level
        }
