"""
Quick test to verify the field validation logic
"""

def validate_user_fields(response_data, field_assertions):
    """
    Validate that a user with specified fields exists in the response.
    Supports type-flexible comparison (string "1" matches int 1).
    """
    def values_match(actual_value, expected_value):
        """Compare values with type flexibility."""
        # Direct string comparison
        if str(actual_value) == expected_value:
            return True
        # Try numeric comparison if expected is numeric
        try:
            if isinstance(actual_value, (int, float)):
                return actual_value == float(expected_value)
        except (ValueError, TypeError):
            pass
        # Try boolean comparison
        if isinstance(actual_value, bool):
            return str(actual_value).lower() == expected_value.lower()
        return False
    
    # If response is a single object
    if isinstance(response_data, dict):
        return all(values_match(response_data.get(key), value) for key, value in field_assertions.items())
    
    # If response is an array
    if isinstance(response_data, list):
        for item in response_data:
            if isinstance(item, dict):
                if all(values_match(item.get(key), value) for key, value in field_assertions.items()):
                    return True
    
    return False


# Test cases
if __name__ == "__main__":
    # Mock response from JSONPlaceholder
    mock_response = [
        {
            "id": 1,
            "name": "Leanne Graham",
            "username": "Bret",
            "email": "Sincere@april.biz"
        },
        {
            "id": 2,
            "name": "Ervin Howell",
            "username": "Antonette",
            "email": "Shanna@melissa.tv"
        }
    ]
    
    # Test 1: Valid user with correct fields
    assertions1 = {"name": "Leanne Graham", "username": "Bret"}
    result1 = validate_user_fields(mock_response, assertions1)
    print(f"Test 1 (Valid user): {result1}")  # Should be True
    assert result1 == True, "Should find Leanne Graham with username Bret"
    
    # Test 2: Invalid - wrong username
    assertions2 = {"name": "Leanne Graham", "username": "WrongUser"}
    result2 = validate_user_fields(mock_response, assertions2)
    print(f"Test 2 (Wrong username): {result2}")  # Should be False
    assert result2 == False, "Should NOT find user with wrong username"
    
    # Test 3: Invalid - wrong name
    assertions3 = {"name": "John Doe", "username": "Bret"}
    result3 = validate_user_fields(mock_response, assertions3)
    print(f"Test 3 (Wrong name): {result3}")  # Should be False
    assert result3 == False, "Should NOT find user with wrong name"
    
    # Test 4: Valid - different user
    assertions4 = {"name": "Ervin Howell", "username": "Antonette"}
    result4 = validate_user_fields(mock_response, assertions4)
    print(f"Test 4 (Valid different user): {result4}")  # Should be True
    assert result4 == True, "Should find Ervin Howell"
    
    # Test 5: Single field validation
    assertions5 = {"name": "Leanne Graham"}
    result5 = validate_user_fields(mock_response, assertions5)
    print(f"Test 5 (Single field): {result5}")  # Should be True
    assert result5 == True, "Should find user by name only"
    
    # Test 6: Partial match should fail (all fields must match)
    assertions6 = {"name": "Leanne Graham", "username": "Bret", "id": "999"}
    result6 = validate_user_fields(mock_response, assertions6)
    print(f"Test 6 (Partial match with wrong id): {result6}")  # Should be False
    assert result6 == False, "Should NOT match if any field is wrong"
    
    # Test 7: String "1" should match int 1 (TYPE FLEXIBILITY TEST)
    assertions7 = {"id": "1", "name": "Leanne Graham"}
    result7 = validate_user_fields(mock_response, assertions7)
    print(f"Test 7 (String id='1' matches int id=1): {result7}")  # Should be True
    assert result7 == True, "String '1' should match int 1"
    
    # Test 8: String "2" should match int 2
    assertions8 = {"id": "2", "username": "Antonette"}
    result8 = validate_user_fields(mock_response, assertions8)
    print(f"Test 8 (String id='2' matches int id=2): {result8}")  # Should be True
    assert result8 == True, "String '2' should match int 2"
    
    # Test 9: Wrong numeric string should fail
    assertions9 = {"id": "999", "name": "Leanne Graham"}
    result9 = validate_user_fields(mock_response, assertions9)
    print(f"Test 9 (Wrong numeric id): {result9}")  # Should be False
    assert result9 == False, "Wrong numeric id should not match"
    
    print("\n✅ All tests passed! Field validation logic is correct with type flexibility.")
