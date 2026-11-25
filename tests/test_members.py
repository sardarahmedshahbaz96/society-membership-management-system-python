import pytest
import sqlite3

# The path to your test database
TEST_DB = "db/test_members.db"

def add_member(client, student_id="S001"):
    """Helper function to add a member via the web interface"""
    data = {
        "action": "add",
        "first_name": "John",
        "last_name": "Doe",
        "gender": "Male",
        "student_id": student_id,
        "society": "UMT IEEE",
        "date_joined": "2025-12-24",
        "position": "Volunteer"
    }
    return client.post("/home", data=data, follow_redirects=True)

# ---------- 1. ADD MEMBER TESTS ----------

def test_add_member_success(client):
    response = add_member(client, "S_ADD_01")
    html = response.get_data(as_text=True)
    assert "Member added successfully" in html

def test_add_duplicate_member(client):
    add_member(client, "S_DUP")
    response = add_member(client, "S_DUP") # Attempt to add same ID again
    html = response.get_data(as_text=True)
    assert "Error: Student ID already exists!" in html

# ---------- 2. SEARCH TESTS ----------

def test_find_by_student_id(client):
    unique_id = "S_FIND_03"
    add_member(client, unique_id)
    
    # Search for specific ID
    response = client.post("/home", data={"action":"find_id","student_id": unique_id}, follow_redirects=True)
    html = response.get_data(as_text=True)
    
    # Verify the ID and common name appear in the results table
    assert unique_id in html
    assert "John" in html

def test_find_by_society(client):
    unique_id = "S_SOC_TEST"
    add_member(client, unique_id)
    
    # Search for the society
    response = client.post("/home", data={"action":"find_society","society":"UMT IEEE"}, follow_redirects=True)
    html = response.get_data(as_text=True)
    
    assert unique_id in html
    assert "UMT IEEE" in html

# ---------- 3. UI & DISPLAY TESTS ----------

def test_position_displayed(client):
    add_member(client, "S_POS_01")
    response = client.post("/home", data={"action":"find_id","student_id":"S_POS_01"}, follow_redirects=True)
    html = response.get_data(as_text=True)
    assert "Volunteer" in html

def test_collapsible_forms_exist(client):
    response = client.get("/home")
    html = response.get_data(as_text=True)
    assert "Add Member" in html
    assert "Find by ID" in html
    assert "Find by Society" in html

def test_find_nonexistent_student(client):
    response = client.post("/home", data={"action":"find_id","student_id":"XYZ999"}, follow_redirects=True)
    html = response.get_data(as_text=True)
    # The ID should not appear in a table row
    assert "<td>XYZ999</td>" not in html

# ---------- 4. THE FOR-LOOP (POSITION) TEST ----------

def test_add_member_with_all_positions(client):
    positions = ["Volunteer", "President", "Vice President", "Treasurer", "Secretary"]
    
    for i, pos in enumerate(positions):
        unique_id = f"S_LOOP_{i}"
        data = {
            "action": "add",
            "first_name": f"Test{i}",
            "last_name": f"User{i}",
            "gender": "Male",
            "student_id": unique_id,
            "society": "UMT ACM",
            "date_joined": "2025-12-24",
            "position": pos
        }
        response = client.post("/home", data=data, follow_redirects=True)
        html = response.get_data(as_text=True)
        
        assert "Member added successfully" in html
        assert unique_id in html
        assert pos in html

# ---------- 5. SORT, GRAPH, UPDATE, DELETE ----------

def test_sort_members_by_id_desc(client):
    add_member(client, "S888")
    add_member(client, "S999")

    response = client.post("/sort_results", data={"sort_by": "student_id", "order": "desc"}, follow_redirects=True)
    html = response.get_data(as_text=True)
    # S999 should appear before S888 in the source code
    assert html.find("S999") < html.find("S888")

def test_view_graph_data_integrity(client):
    add_member(client, "S_GRAPH_01") 
    response = client.get("/view_graph")
    json_data = response.get_json()
    assert "labels" in json_data
    assert "values" in json_data

def test_update_member_partial(client):
    """Tests the 'for' loop in the Model that filters empty update fields"""
    add_member(client, "S_UPDATE_ME")
    
    client.post("/update_member", data={
        "current_id": "S_UPDATE_ME",
        "new_student_id": "S_UPDATE_ME",
        "first_name": "NewName",
        "last_name": "", # This should be skipped by the loop
        "position": "President"
    }, follow_redirects=True)

    response = client.post("/home", data={"action": "find_id", "student_id": "S_UPDATE_ME"}, follow_redirects=True)
    html = response.get_data(as_text=True)
    assert "NewName" in html
    assert "President" in html
    assert "Doe" in html # Original value preserved

def test_delete_member_flow(client):
    add_member(client, "S_DEL")
    client.post("/delete_member", data={"student_id": "S_DEL"}, follow_redirects=True)
    
    response = client.post("/home", data={"action": "find_id", "student_id": "S_DEL"}, follow_redirects=True)
    html = response.get_data(as_text=True)
    assert "<td>S_DEL</td>" not in html